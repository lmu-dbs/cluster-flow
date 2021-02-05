class DatasetInfoCard{
    constructor(project_id, dataset, parameter_dataset_image){
        this.project_id = project_id;
        this.dataset = dataset;
        this.parameter_dataset_image = parameter_dataset_image;
    }

    render(rendering_element){
        let row_element = document.createElement('div');
        row_element.classList.add('row');
        rendering_element.appendChild(row_element);

        this.card_element = document.createElement('div');
        row_element.appendChild(this.card_element);
        //this.card_element.classList.add('center_card');
        this.card_element.classList.add('filter');
        this.card_element.classList.add('card_no_status');

        let headline_element = document.createElement('h2');
        this.card_element.appendChild(headline_element);
        headline_element.innerText = "Original Dataset";

        let container_element = document.createElement('div');
        this.card_element.appendChild(container_element);
        //container_element.classList.add('container');

        let row_element_2 = document.createElement('div');
        container_element.appendChild(row_element_2);
        row_element_2.classList.add('row');

        let column_1 = document.createElement('div');
        row_element_2.appendChild(column_1);
        column_1.classList.add('col-md-7');

        let rendering_element_plot = document.createElement('div');
        column_1.appendChild(rendering_element_plot);
        rendering_element_plot.classList.add('card_plot');

        this.__render_plot(rendering_element_plot);

        let element_2 = document.createElement('div');
        row_element_2.appendChild(element_2);

        let column_2 = document.createElement('div');
        element_2.appendChild(column_2);
        column_2.classList.add('col-md-4');

        let rendering_element_legend = document.createElement('div');
        column_2.appendChild(rendering_element_legend);
        rendering_element_legend.classList.add('card_plot_legend');

        this.__render_legend(rendering_element_legend);
    }

     __render_plot(rendering_element){
        let plot = document.createElement('img');
        plot.classList.add('plot');
        rendering_element.appendChild(plot);

        if(this.parameter_dataset_image !== null){
            $.ajax({
              dataType: "json",
              type: 'GET',
              url: '/api/picture/' + this.parameter_dataset_image,
              success: function(data){
                  plot.setAttribute('src', data.picture);
              }
            });
        }
        else {
            plot.setAttribute('src', '/static/img/no_picture.png');
        }

        let buttons_row = document.createElement('div');
        rendering_element.appendChild(buttons_row);
        buttons_row.classList.add('row');

        let that = this;
        let data_dimension = this.dataset.number_of_dimensions;

        if(data_dimension === 2){
            let button = document.createElement('button');
            buttons_row.appendChild(button);
            button.innerText = '2d view';
            button.addEventListener('click', function () {
                that.__show_plot(plot, '/api/picture/project/'+ that.project_id + '/dataset', {})
            });
        }
        if(data_dimension === 3){
            let button = document.createElement('button');
            buttons_row.appendChild(button);
            button.innerText = '3d view';
            button.addEventListener('click', function () {
                that.__show_plot(plot, '/api/picture/project/'+ that.project_id + '/dataset', {})
            });
        }
        if(data_dimension > 2){
            let button = document.createElement('button');
            buttons_row.appendChild(button);
            button.innerText = 'PCA n=2';
            button.addEventListener('click', function () {
                that.__show_plot(plot, '/api/picture/project/'+ that.project_id + '/dataset', {'PCA': 2})
            });
        }
        if(data_dimension > 3){
            let button = document.createElement('button');
            buttons_row.appendChild(button);
            button.innerText = 'PCA n=3';
            button.addEventListener('click', function () {
                that.__show_plot(plot, '/api/picture/project/'+ that.project_id + '/dataset', {'PCA': 3})
            });
        }
        if(data_dimension > 2){
            let button = document.createElement('button');
            buttons_row.appendChild(button);
            button.innerText = 'Projection to 2D plane';
            button.addEventListener('click', function () {
                let axis_a = parseInt(prompt("Which axis should be the x-axis?", "0"));
                let axis_b = parseInt(prompt("Which axis should be the y-axis?", "0"));
                that.__show_plot(plot, '/api/picture/project/'+ that.project_id + '/dataset', {'projection': JSON.stringify([axis_a, axis_b])})
            });
        }
        if(data_dimension > 3){
            let button = document.createElement('button');
            buttons_row.appendChild(button);
            button.innerText = 'Projection to 3D plane';
            button.addEventListener('click', function () {
                let axis_a = parseInt(prompt("Which axis should be the x-axis?", "0"));
                let axis_b = parseInt(prompt("Which axis should be the y-axis?", "0"));
                let axis_c = parseInt(prompt("Which axis should be the z-axis?", "0"));
                that.__show_plot(plot, '/api/picture/project/'+ that.project_id + '/dataset', {'projection': JSON.stringify([axis_a, axis_b, axis_c])})
            });
        }
    }

    __show_plot(rendering_element, url, parameter){
        $.ajax({
          dataType: "json",
          type: 'POST',
          url: url,
          data: parameter,
          success: function(data){
              rendering_element.setAttribute('src', data.picture);
          }
        });
    }

    __render_legend(rendering_element){
        let table = document.createElement('table');
        //table.classList.add('table-hover');
        rendering_element.appendChild(table);

        let table_body = document.createElement('tbody');
        table.appendChild(table_body);

        let legend_title = ['name of data set:', 'dimensionality:', 'number of instances:'];
        let legend_value = [this.dataset.name, this.dataset.number_of_dimensions, this.dataset.number_of_rows];

        for(let i=0; i < legend_value.length; i++){
            let row = document.createElement('tr');
            table_body.appendChild(row);

            let legend_title_element = document.createElement('th');
            legend_title_element.innerText = legend_title[i];
            row.appendChild(legend_title_element);

            let legend_value_element = document.createElement('td');
            legend_value_element.innerText = legend_value[i];
            row.appendChild(legend_value_element);
        }
    }
}
