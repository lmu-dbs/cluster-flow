class KnnGraphGenerationExpression extends Expression{
    constructor(app, project_id, dataset, data){
        super(app, dataset, {
            'id': null,
            'selected_image': null,
            'required_filter': 1,
            'filters': [],
            'status': data.status
        });

        this.filters.push(new KnnGraphGenerationFilter(this, project_id, dataset, data));
    }
}

class KnnGraphGenerationFilter extends Filter{
    constructor(expression, project_id, dataset, data){
        super(expression, dataset, Object.assign({}, data, {
            'controls': [
                {'title': 'type of kNN graph', 'id': 'graph-type', 'type': 'selection', 'values': [
                        {'value': 'MkNN-Graph', 'title': 'mutual kNN-Graph'},
                        {'value': 'sym kNN-Graph', 'title': 'symmetric kNN-Graph'}
                    ]},
                 {'title': 'parameter k', 'id': 'k', 'type': 'int', 'min': 2, 'max': dataset.number_of_rows}
            ],
            'gui_name': 'kNN Graph Generation'
        }));
        this.project_id = project_id;
    }

    __get_urls(){
        return {
            'pictures': '/api/picture/project/'+ this.project_id + '/graph_generation',
            'apply': '/api/project/' + this.project_id + '/generate_knn_graph',
            'download': '/api/project/' + this.project_id + '/knn_graph/result',
        }
    }

    __show_add_compare_filter(){
        return false;
    }

    __show_delete_button(){
        return false;
    }


}
