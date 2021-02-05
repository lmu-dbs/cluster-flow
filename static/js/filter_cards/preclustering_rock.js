class RockExpression extends Expression{
    constructor(app, project_id, dataset, data){
        super(app, dataset, {
            'id': null,
            'selected_image': null,
            'required_filter': 1,
            'filters': [],
            'status': data.status
        });

        this.filters.push(new RockFilter(this, project_id, dataset, data));
    }

    get_image_parameters(){
        return {};
    }
}

class RockFilter extends Filter{
    constructor(expression, project_id, dataset, data){
        super(expression, dataset, Object.assign({}, data, {
            'controls': [
                 {'title': 'parameter k', 'id': 'k', 'type': 'int', 'min': 0},
                 {'title': 'iterations', 'id': 'iterations', 'type': 'int', 'min': 0},
            ],
            'gui_name': 'Preclustering with Rock'
        }));
        this.project_id = project_id;
    }

     get_image_parameters(){
        return {};
    }

    __get_urls(){
        return {
            'pictures': '/api/picture/project/'+ this.project_id + '/rock',
            'apply': '/api/project/' + this.project_id + '/rock',
        }
    }

    __show_add_compare_filter(){
        return false;
    }

    __show_delete_button(){
        return false;
    }

    show_download_button(){
        return false;
    }
}
