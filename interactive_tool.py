from flask import(
    Flask,
    jsonify,
    render_template,
    abort,
    url_for,
    redirect,
    request,
    Response
    )
import os
import configparser
from libary.database import DBSESSION
from libary.filter import FilterStatus
import json
from helper.graph_creator import generate_initial_knn_graph
import pickle
from helper.rock_preclustering import RockPreclustering
from helper.image_creator import ImageCreator
import networkx
import numpy

from libary.database import BASE, ENGINE
from libary.project import Project
from libary.expression import Expression
from libary.filter import Filter
from libary.image import Image
from libary.dataset import Dataset
from libary.result import Result

########################################################################## Load Config
path_to_config = os.path.dirname(os.path.realpath(__file__)) + os.sep + 'config.ini'

# check if there is a config in not create one with default values

if not os.path.exists(path_to_config):
    with open(path_to_config, mode='w') as config_file:
        config_file.write("""[Config]
server_port: 5000
secret_key: DefaultKey
start_browser: Yes
""")

config = configparser.ConfigParser()
config.read(path_to_config)

SERVER_PORT = int(config['Config']['SERVER_PORT'])
SERVER_KEY = config['Config']['secret_key']
START_BROWSER = config['Config']['START_BROWSER']

########################################################################## 


app = Flask(__name__)
app.secret_key = SERVER_KEY


@app.route('/projects')
def view_project_overview():
    projects = list()
    database_session = DBSESSION()
    for project in database_session.query(Project):
        projects.append({'id': project.id, 'name': project.name, 'dataset': project.dataset.name})
    database_session.close()
    return render_template('project_overview.html', projects=projects)


@app.route('/datasets')
def view_datasets_overview():
    datasets = list()
    database_session = DBSESSION()
    for dataset in database_session.query(Dataset):
        datasets.append({'id': dataset.id, 'name': dataset.name, 'instances': dataset.number_of_rows, 'features': dataset.number_of_dimensions})
    database_session.close()
    return render_template('dataset_overview.html', datasets=datasets)


@app.route('/upload_dataset')
def upload_dataset():
    return render_template('upload_dataset.html')


@app.route('/new_project/')
def new_project():
    database_session = DBSESSION()
    datasets = list()
    for dataset in database_session.query(Dataset):
        datasets.append({'id': dataset.id, 'name':dataset.name})
    database_session.close()
    return render_template('new_project.html', datasets=datasets)


@app.route('/project/<int:project_id>')
def view_project(project_id: int):
    return render_template('project.html', project_id=project_id)


#################
# API
#################


@app.route('/api/new_project/', methods=['POST'])
def api_create_new_project():
    dataset_id = int(request.form.get('dataset'))
    project_name = request.form.get('name')

    database = DBSESSION()
    dataset = database.query(Dataset).get(dataset_id)
    if dataset is None:
        return abort(404)

    project = Project(name=project_name, dataset=dataset)
    database.add(project)

    database.commit()
    project_id = project.id
    database.close()
    return jsonify({'success': True, 'url_to_project': url_for('view_project', project_id=project_id)})


@app.route('/api/upload_dataset/', methods=['POST'])
def api_upload_dataset():
    dataset_raw = request.files.get('dataset').read().decode()
    dataset_name = request.form.get('name')

    data = list()
    for line in dataset_raw.split('\n'):
        line = line.strip()
        if len(line) == 0:
            continue
        point = list()
        for x in line.split(','):
            x = x.strip()
            x = float(x)
            point.append(x)
        data.append(point)
    data = numpy.array(data)

    database = DBSESSION()
    new_dataset = Dataset(name=dataset_name, data=data, number_of_rows=len(data), number_of_dimensions=len(data[0]))
    database.add(new_dataset)
    database.commit()
    database.close()
    return jsonify({'success': True, 'url_redirect': url_for('view_datasets_overview')})


@app.route('/api/picture/dataset/<int:dataset_id>', methods=['POST'])
def get_dataset_picture(dataset_id):
    database = DBSESSION()
    dataset = database.query(Dataset).get(dataset_id)
    if dataset is None:
        return abort(404)
    parameter = {x: request.form.get(x) for x in request.form}
    picture, picture_was_found = dataset.get_picture(parameter)
    if not picture_was_found:
        image = Image(parameter=parameter, picture=picture)
        dataset.image_list.append(image)
    database.commit()
    database.close()
    return jsonify({'picture': picture})


@app.route('/api/picture/project/<int:id>/graph_generation', methods=['POST'])
def get_project_picture_graph_generation(id):
    database = DBSESSION()
    project = database.query(Project).get(id)
    if project is None:
        return abort(404)
    parameter = {x: request.form.get(x) for x in request.form}
    image = project.get_picture(parameter)
    database.commit()
    picture = image.picture
    database.close()
    return jsonify({'picture': picture})


@app.route('/api/picture/project/<int:id>/dataset', methods=['POST'])
def get_project_picture_dataset(id):
    database = DBSESSION()
    project = database.query(Project).get(id)
    if project is None:
        return abort(404)
    dataset = project.dataset
    parameter = {x: request.form.get(x) for x in request.form}
    image = dataset.get_picture(parameter)
    project.parameter_dataset_image = image
    database.commit()
    picture = image.picture
    database.close()
    return jsonify({'picture': picture})


@app.route('/api/picture/project/<int:id>/rock', methods=['POST'])
def get_project_picture_preclustering_rock(id):
    database = DBSESSION()
    project = database.query(Project).get(id)
    if project is None:
        return abort(404)
    if project.preclustering_rock_data is None:
        dataset = project.dataset
        parameter = {x: request.form.get(x) for x in request.form}
        image = dataset.get_picture(parameter)
        project.parameter_dataset_image = image
        database.commit()
        picture = image.picture
        database.close()
        return jsonify({'picture': picture})
    parameter = {x: request.form.get(x) for x in request.form}
    project.preclustering_rock_image_parameters = json.dumps(parameter)
    image_creator = ImageCreator()
    image = image_creator.create_image(data=pickle.loads(project.preclustering_rock_data), knn_graph=None, parameter=parameter)
    project.preclustering_rock_image = image

    database.commit()
    picture = image.picture
    database.close()
    return jsonify({'picture': picture})


@app.route('/api/picture/filter/<int:filter_id>', methods=['POST'])
def get_filter_picture(filter_id):
    database = DBSESSION()
    filter = database.query(Filter).get(filter_id)
    if filter is None:
        return abort(404)
    parameter = {x: request.form.get(x) for x in request.form}
    if filter.get_current_result() is None:
        return abort(404)
    image = filter.get_picture(parameter)
    database.commit()
    picture = image.picture
    database.close()
    return jsonify({'picture': picture})


@app.route('/api/picture/expression/<int:expression_id>', methods=['POST'])
def get_expression_picture(expression_id):
    database = DBSESSION()
    expression = database.query(Expression).get(expression_id)
    if expression is None:
        return abort(404)
    parameter = {x: request.form.get(x) for x in request.form}
    image = expression.get_picture(parameter)
    database.commit()
    picture = image.picture
    database.close()
    return jsonify({'picture': picture})


@app.route('/api/picture/<int:id>', methods=['GET'])
def api_image(id):
    database = DBSESSION()
    image = database.query(Image).get(id)
    if image is None:
        return abort(404)
    picture = image.get_image()
    database.close()
    return jsonify({'picture': picture})


@app.route('/api/project/<int:id>', methods=['GET'])
def api_project(id):
    database = DBSESSION()
    project = database.query(Project).get(id)
    if project is None:
        return abort(404)
    return_dict = project.to_dict()
    database.commit()
    database.close()
    return jsonify(return_dict)


@app.route('/api/project/<int:project_id>/generate_knn_graph', methods=['POST'])
def api_generate_initial_knn_graph(project_id):
    database = DBSESSION()
    project = database.query(Project).get(project_id)
    if project is None:
        return abort(404)

    project.knn_graph_generation_status = FilterStatus.RUNNING
    database.commit()

    parameters = {x: request.form.get(x) for x in request.form}

    if project.preclustering_rock_data is None:
        input_data = project.dataset.data
    else:
        input_data = pickle.loads(project.preclustering_rock_data)

    initial_graph_creation_result = generate_initial_knn_graph(data=input_data, parameters=parameters)

    project.set_knn_graph_generation_parameters(parameters=parameters)

    result = Result(parameter=parameters,
                    intermediate_result=dict(),
                    directed_knn_graph=initial_graph_creation_result.directed_knn_graph,
                    undirected_knn_graph=initial_graph_creation_result.undirected_knn_graph,
                    deletion_set=set(),
                    data=input_data,
                    knn_distances=initial_graph_creation_result.distances)

    project.knn_graph_generation_status = FilterStatus.READY

    if len(project.expression_list) > 0:
        project.expression_list[0].new_calculation_required(database=database)

    project.results.clear()

    project.results.append(result)
    database.commit()
    return_dict = project.to_dict()
    database.close()
    return jsonify(return_dict)


@app.route('/api/project/<int:project_id>/rock', methods=['POST'])
def api_preclustering_rock(project_id):
    database = DBSESSION()
    project = database.query(Project).get(project_id)
    if project is None:
        return abort(404)

    parameters = {x: request.form.get(x) for x in request.form}

    project.preclustering_rock_parameters = json.dumps(parameters)
    project.preclustering_rock_status = FilterStatus.RUNNING

    new_positions = RockPreclustering.apply(input_data=project.dataset.data, parameters=parameters)

    project.preclustering_rock_data = pickle.dumps(new_positions)

    project.preclustering_rock_status = FilterStatus.READY

    project.knn_graph_generation_status = FilterStatus.RECALULATION_NEEDED

    print('len(project.expression_list)', len(project.expression_list))

    database.query(Result).filter(Result.project_id == project.id).delete()

    if len(project.expression_list) > 0:
        project.expression_list[0].new_calculation_required(database=database)

    database.commit()
    return_dict = project.to_dict()
    database.close()
    return jsonify(return_dict)


@app.route('/api/filter/<int:filter_id>/apply', methods=['POST'])
def api_filter_apply(filter_id):
    filter_parameter = {x: request.form.get(x) for x in request.form}

    database = DBSESSION()
    filter = database.query(Filter).get(filter_id)
    if filter is None:
        return abort(404)

    if filter_parameter is not None:
        filter.update_parameter(filter_parameter)

    filter.apply()
    filter.status = FilterStatus.READY

    expression = filter.expression
    expression.status = FilterStatus.RECALULATION_NEEDED
    expression.results.clear()

    if expression.child_expression is not None:
        expression.child_expression.new_calculation_required(database)

    database.commit()
    database.close()
    return jsonify({'success': True, 'filter_id': filter_id})


@app.route('/api/project/<int:project_id>/new_expression', methods=['POST'])
def api_generate_new_expression(project_id):
    database = DBSESSION()
    project = database.query(Project).get(project_id)
    if project is None:
        return abort(404)
    new_expression = Expression()
    if len(project.expression_list) > 0:
        new_expression.parent_expression = project.expression_list[len(project.expression_list) - 1]
        new_expression.parent_expression.child_expression = new_expression
    database.add(new_expression)
    project.expression_list.append(new_expression)
    database.commit()
    return_dict = new_expression.to_dict()
    database.close()
    return jsonify(return_dict)


@app.route('/api/project/<int:expression_id>/new_filter', methods=['POST'])
def api_add_filter(expression_id):
    database = DBSESSION()
    expression = database.query(Expression).get(expression_id)
    if expression is None:
        return abort(404)
    filter_name = request.form.get('filter_name')
    new_filter = Filter(name=filter_name)
    database.add(new_filter)
    expression.filter_list.append(new_filter)
    expression.status = FilterStatus.RECALULATION_NEEDED
    expression.results.clear()
    if expression.child_expression is not None:
        expression.child_expression.new_calculation_required(database)
    database.commit()
    return_dict = new_filter.to_dict()
    database.close()
    return jsonify(return_dict)


@app.route('/api/project/<int:expression_id>/apply', methods=['POST'])
def api_expression_apply(expression_id):
    database = DBSESSION()
    expression = database.query(Expression).get(expression_id)
    if expression is None:
        return abort(404)
    expression.required_filter = int(float(request.form.get('required_filter')))
    expression.apply()
    expression.status = FilterStatus.READY
    if expression.child_expression is not None:
        expression.child_expression.new_calculation_required(database)
    database.commit()
    return_dict = expression.to_dict()
    database.close()
    return jsonify(return_dict)


@app.route('/api/filter/<int:filter_id>', methods=['DELETE'])
def api_delete_filter(filter_id):
    database = DBSESSION()
    filter = database.query(Filter).get(filter_id)
    if filter is None:
        return abort(404)
    expression = filter.expression
    expression.filter_list.remove(filter)
    expression.status = FilterStatus.RECALULATION_NEEDED
    expression.results.clear()
    if expression.child_expression is not None:
        expression.child_expression.new_calculation_required(database)
    database.commit()
    database.close()
    return jsonify({'success': True, 'filter_id': filter_id})


@app.route('/api/expression/<int:expression_id>', methods=['DELETE'])
def api_delete_expression(expression_id):
    database = DBSESSION()
    expression = database.query(Expression).get(expression_id)
    if expression is None:
        return abort(404)
    project = expression.project
    project.expression_list.remove(expression)
    # fix linkage
    if expression.parent_expression is not None:
        expression.parent_expression.child_expression = expression.child_expression
    database.commit()
    database.close()
    return jsonify({'success': True, 'expression_id': expression_id})


@app.route('/api/filter/<int:filter_id>/result', methods=['GET'])
def api_download_result_filter(filter_id):
    database = DBSESSION()
    filter = database.query(Filter).get(filter_id)
    if filter is None:
        return abort(404)
    if filter.get_current_result() is None:
        return abort(404)
    undirected_knn_graph = filter.get_current_result().get_undirected_knn_graph()

    connected_components = networkx.algorithms.connected_components(undirected_knn_graph)
    alignment = dict()
    for cluster_index, x in enumerate(connected_components):
        if len(x) > 1:
            for point_index in x:
                alignment[point_index] = cluster_index
        else:
            alignment[x.pop()] = -1

    result = list()
    for point_index in range(len(filter.get_current_result().get_resulting_data())):
        result.append(str(alignment[point_index]))

    text_file = '\n'.join(result)

    name = filter.expression.project.name
    database.close()

    return Response(text_file, mimetype="text/plaintext", headers={"Content-disposition": "attachment; filename={}_clustering_result.csv".format(name)})


@app.route('/api/project/<int:project_id>/knn_graph/result', methods=['GET'])
def api_download_result_knn_graph(project_id):
    database = DBSESSION()
    project = database.query(Project).get(project_id)
    if project is None:
        return abort(404)
    if project.get_current_result() is None:
        return abort(404)
    undirected_knn_graph = project.get_current_result().get_undirected_knn_graph()

    connected_components = networkx.algorithms.connected_components(undirected_knn_graph)
    alignment = dict()
    for cluster_index, x in enumerate(connected_components):
        if len(x) > 1:
            for point_index in x:
                alignment[point_index] = cluster_index
        else:
            alignment[x[0]] = -1

    result = list()
    for point_index in range(len(project.get_current_result().get_resulting_data())):
        result.append(str(alignment[point_index]))

    text_file = '\n'.join(result)

    name = project.name
    database.close()

    return Response(text_file, mimetype="text/plaintext", headers={"Content-disposition": "attachment; filename={}_clustering_result.csv".format(name)})


@app.route('/api/expression/<int:expression_id>/result', methods=['GET'])
def api_download_result_expression(expression_id):
    database = DBSESSION()
    expression = database.query(Expression).get(expression_id)
    if expression is None:
        return abort(404)
    if expression.get_current_result() is None:
        return abort(404)
    undirected_knn_graph = expression.get_current_result().get_undirected_knn_graph()

    connected_components = networkx.algorithms.connected_components(undirected_knn_graph)
    alignment = dict()
    for cluster_index, x in connected_components:
        for point_index in x:
            alignment[point_index] = cluster_index

    result = list()
    for point_index in range(len(expression.get_current_result().get_resulting_data())):
        result.append(alignment[point_index])

    text_file = '\n'.join(result)

    name = expression.project.name
    database.close()

    return Response(text_file, mimetype="text/plaintext", headers={"Content-disposition": "attachment; filename={}_clustering_result.csv".format(name)})


@app.errorhandler(404)
def page_not_found(e):
    return redirect(url_for('view_project_overview'))


with app.app_context():
    if START_BROWSER:
        os.system('start http://127.0.0.1:{}'.format(SERVER_PORT))


if __name__ == "__main__":
    BASE.metadata.create_all(ENGINE)

    app.run(host='127.0.0.1', port=SERVER_PORT, debug=False, use_reloader=False)

