class AddFilterCard{
    constructor(app, dataset, callback){
        this.app = app;
        this.dataset = dataset;
        this.project_id = app.project_id;

        this.callback = callback;

        this.rendering_element_mother = null;
        this.rendering_element = null;
    }

    delete(){
        this.rendering_element_mother.remove(this.rendering_element);
    }

    render(rendering_element){
        this.rendering_element_mother = rendering_element;

        this.rendering_element = document.createElement('div');
        this.rendering_element.classList.add('row');
        rendering_element.appendChild(this.rendering_element);

        let card = document.createElement('div');
        card.classList.add('center_card');
        card.classList.add('addFilter');
        this.rendering_element.appendChild(card);

        let that = this;

        let button = document.createElement('button');
        button.classList.add('button_add_new_card');
        button.classList.add('btn');
        button.classList.add('btn-default');
        button.classList.add('btn-md');
        button.setAttribute('type', 'button');
        button.innerHTML = '<span class="glyphicon glyphicon-plus"></span> append new filter';
        button.addEventListener('click', function () {
            $.ajax({
              dataType: "json",
              type: 'POST',
              url: '/api/project/' + that.app.project_id + '/new_expression',
              success: function(data){
                    let new_expression = new Expression(that.app, that.dataset, {
                        'id': data.id,
                        'selected_image': null,
                        'operation': 'SINGLE_FILTER',
                        'filters': [],
                        'status': 0
                    });
                    that.callback(new_expression);
              }
            });
        });
        card.appendChild(button);
    }
}
