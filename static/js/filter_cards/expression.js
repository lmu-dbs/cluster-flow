class Expression{
    constructor(app, dataset, data){
        this.app = app;
        this.dataset = dataset;
        this.filters = [];

        // Parameter
        this.expression_id = data.id;
        this.selected_image_parameter = data.selected_image;
        this.required_filter = data.required_filter;
        for(let i=0; i < data.filters.length; i++) {
            this.filters.push(new Filter(this, this.dataset, data.filters[i]));
        }
        this.status = data.status;

        // Links
        this.next_expression_card = null;
        this.last_expression_card = null;

        // DOM elements
        this.row_element = null;
        this.card_element = null;
        this.plot_element = null;
        this.recalculate_button = null;
        this.recalculate_all_button = null;
        this.download_button = null;
        this.reset_button = null;
        this.expression_operation_card = null;

        // DOM elements
        this.plot_buttons = [];
        this.control_elements = [];

        this.show_add_filter_card = false;
    }

    get_image_parameters(){
        return {'graph': '', 'highlight_components': ''};
    }

    append_expression(next_expression_card){
        if(this.next_expression_card == null){
            this.next_expression_card = next_expression_card;
            next_expression_card.last_expression_card = this;
            return;
        }
        this.next_expression_card.append_expression(next_expression_card);
    }

    filter_applied(){
        this.set_status(0);
        if(this.next_expression_card !== null && this.next_expression_card !== undefined){
            this.next_expression_card.trigger_update();
        }
    }

    trigger_update(){
        this.set_status(0);
        for(let i=0; i < this.filters.length; i++){
            this.filters[i].set_status(0);
        }
        if(this.next_expression_card !== null && this.next_expression_card !== undefined){
            this.next_expression_card.trigger_update();
        }
    }

    filter_removed_applied(filter){
        let that = this;
        if(this.filters.length === 1){
            // remove expression
            $.ajax({
              dataType: "json",
              type: 'DELETE',
              url: '/api/expression/' + this.expression_id,
              success: function(data){
                    that.app.remove_expression(that.row_element);
              }
            });
        }
        else{
            $.ajax({
              dataType: "json",
              type: 'DELETE',
              url: '/api/filter/' + filter.filter_id,
              success: function(data){
                    let new_filters = [];
                    for(let i=0; i < that.filters.length; i++){
                        if(that.filters[i].filter_id !== filter.filter_id){
                            new_filters.push(that.filters[i]);
                        }
                    }
                    that.filters = new_filters;
                    that.update_gui();
              }
            });
        }
        this.filter_applied();
    }

    render(rendering_element) {
        this.row_element = document.createElement('div');
        this.row_element.classList.add('row');
        rendering_element.appendChild(this.row_element);

        this.update_gui();
    }

    add_filter_card(){
        this.show_add_filter_card = true;
        this.update_gui();
    }

    remove_add_filter_card(){
        if(this.filters.length === 0){
            // remove expression
            let that = this;
            $.ajax({
              dataType: "json",
              type: 'DELETE',
              url: '/api/expression/' + this.expression_id,
              success: function(data){
                    that.app.remove_expression(that.row_element);
              }
            });
        }
        else {
            this.show_add_filter_card = false;
            this.update_gui();
        }
    }

    update_gui(){
        if(this.row_element.firstChild !== null) {
            this.row_element.removeChild(this.row_element.firstChild);
        }

        this.card_element = document.createElement('div');
        this.row_element.appendChild(this.card_element);

        if(this.filters.length === 0) {
            let add_filter_card = new AddNewFilterCard(this);
            add_filter_card.render(this.card_element);
            this.card_element.classList.add('expression_single');
        }
        else if(this.filters.length === 1 && this.show_add_filter_card === false) {
            this.card_element.classList.add('expression_single');
            this.filters[0].render(this.card_element);
        }
        else{
            this.card_element.classList.add('expression_two');

            let headline_element = document.createElement('h2');
            this.card_element.appendChild(headline_element);
            headline_element.innerText = 'Result Combination';

            let scroll_area = document.createElement('div');
            scroll_area.classList.add('scroll_area');
            this.card_element.appendChild(scroll_area);

            let filter_area = document.createElement('div');
            filter_area.classList.add('filter_area');
            scroll_area.appendChild(filter_area);

            let spacer = document.createElement('div');
            spacer.classList.add('spacer');
            filter_area.appendChild(spacer);

            for(let i=0; i < this.filters.length; i++){
                this.filters[i].render(filter_area);

                let spacer = document.createElement('div');
                spacer.classList.add('spacer');
                filter_area.appendChild(spacer);
            }

            if (this.show_add_filter_card){
                let add_filter_card = new AddNewFilterCard(this);
                add_filter_card.render(filter_area);

                let spacer = document.createElement('div');
                spacer.classList.add('spacer');
                filter_area.appendChild(spacer);
            }

            this.__render_expression_card(this.card_element);
        }
    }

    __render_expression_card(rendering_element){
        this.expression_operation_card = document.createElement('div');
        this.expression_operation_card.classList.add('expression_operation_card');
        this.expression_operation_card.classList.add('center_card');
        rendering_element.appendChild(this.expression_operation_card);

        let row_element_2 = document.createElement('div');
        this.expression_operation_card.appendChild(row_element_2);
        row_element_2.classList.add('row');
        row_element_2.classList.add('position_relative');

        let column_1 = document.createElement('div');
        row_element_2.appendChild(column_1);
        column_1.classList.add('col-md-7');

        let rendering_element_plot = document.createElement('div');
        column_1.appendChild(rendering_element_plot);
        rendering_element_plot.classList.add('card_plot');

        this.__render_plot(rendering_element_plot);

        this.__render_expression_card_legend(row_element_2);

        this.set_status(this.status);

        this.__on_click_button_reset();
    }

    __render_expression_card_legend(rendering_element){
        let column_2 = document.createElement('div');
        rendering_element.appendChild(column_2);
        column_2.classList.add('col-md-4');
        column_2.classList.add('full_height');

        this.__render_tooltip(column_2);

        let button_section = document.createElement('div');
        rendering_element.appendChild(button_section);

        let card_legend = document.createElement('div');
        card_legend.classList.add('card_plot_legend');
        column_2.appendChild(card_legend);

        let table = document.createElement('table');
        card_legend.appendChild(table);

        let table_body = document.createElement('tbody');
        table.appendChild(table_body);

        // Selection of Operation
        let row = document.createElement('tr');
        table_body.appendChild(row);

        let legend_title_element = document.createElement('th');
        legend_title_element.innerText = 'Required filters:';
        row.appendChild(legend_title_element);

        let legend_value_element = document.createElement('td');
        row.appendChild(legend_value_element);

        let selection_element = document.createElement('input');
        selection_element.setAttribute('type', 'number');
        selection_element.setAttribute('min', 1);
        let that = this;
        selection_element.addEventListener("change", function (){ that.__check_on_change(); });
        this.control_elements.push(selection_element);
        legend_value_element.appendChild(selection_element);

        this.__render_legend_buttons(button_section);
    }

    __render_tooltip(rendering_element){
        rendering_element.appendChild(document.createElement('br'));
        rendering_element.appendChild(document.createElement('br'));
        let tooltip_element = document.createElement('div');
        tooltip_element.classList.add('tooltipXX');
        tooltip_element.innerText = 'The combination of results of single filters is an powerful tool. The parameter "required filter" describes how many filters had to classify an edge as unwanted so that his classification is adopted in the combination result.';
        rendering_element.appendChild(tooltip_element);
        rendering_element.appendChild(document.createElement('br'));
    }

    __check_on_change(){
        if(this.status === 0){
                // pass
        }
        else {
            if (this.__parameters_changed()) {
                this.set_status(1);
            } else {
                this.set_status(3);
            }
        }
        this.__toggle_enabling_plot_buttons();
    }

    __render_legend_buttons(rendering_element){
        var that = this;
        var legend_controls_button_container = document.createElement('div');
        legend_controls_button_container.classList.add('legend_control_buttons');
        rendering_element.appendChild(legend_controls_button_container);

        let table = document.createElement('table');
        legend_controls_button_container.appendChild(table);

        let table_body = document.createElement('tbody');
        table.appendChild(table_body);

        let row_1 = document.createElement('tr');
        let row_1_space = document.createElement('td');
        row_1_space.classList.add('legend_control_buttons_to_right');
        row_1.appendChild(row_1_space);
        table.appendChild(row_1);

        let row_2 = document.createElement('tr');
        let row_2_space = document.createElement('td');
        row_2_space.classList.add('legend_control_buttons_to_right');
        row_2.appendChild(row_2_space);
        table.appendChild(row_2);

        this.downlaod_button = document.createElement('button');
        this.downlaod_button.classList.add('btn');
        this.downlaod_button.classList.add('btn-default');
        this.downlaod_button.classList.add('btn-md');
        this.downlaod_button.classList.add('bottom_button');
        this.downlaod_button.setAttribute('type', 'button');
        this.downlaod_button.innerHTML = '<span class="glyphicon glyphicon-download"></span> download result';
        this.downlaod_button.addEventListener('click', function () { that.__on_click_button_download_result(); });
        row_1_space.appendChild(this.downlaod_button);

        this.recalculate_button = document.createElement('button');
        this.recalculate_button.classList.add('btn');
        this.recalculate_button.classList.add('btn-default');
        this.recalculate_button.classList.add('btn-md');
        this.recalculate_button.classList.add('bottom_button');
        this.recalculate_button.setAttribute('type', 'button');
        this.recalculate_button.innerHTML = '<span class="glyphicon glyphicon-refresh"></span> calculate';
        this.recalculate_button.addEventListener('click', function () { that.__on_click_recalculate(); });
        row_2_space.appendChild(this.recalculate_button);

        this.recalculate_all_button = document.createElement('button');
        this.recalculate_all_button.classList.add('btn');
        this.recalculate_all_button.classList.add('btn-default');
        this.recalculate_all_button.classList.add('btn-md');
        this.recalculate_all_button.classList.add('bottom_button');
        this.recalculate_all_button.setAttribute('type', 'button');
        this.recalculate_all_button.innerHTML = '<span class="glyphicon glyphicon-refresh"></span> calculate All';
        this.recalculate_all_button.addEventListener('click', function () { that.trigger_apply_all(); });
        row_2_space.appendChild(this.recalculate_all_button);

        this.reset_button = document.createElement('button');
        this.reset_button.classList.add('btn');
        this.reset_button.classList.add('btn-default');
        this.reset_button.classList.add('btn-md');
        this.reset_button.classList.add('bottom_button');
        this.reset_button.setAttribute('type', 'button');
        this.reset_button.innerHTML = '<span class="glyphicon glyphicon-erase"></span> reset parameters';
        this.reset_button.addEventListener('click', function () { that.__on_click_button_reset(); });
        row_1_space.appendChild(this.reset_button);
    }

    __on_click_button_download_result(){
        var link = document.createElement("a");
        link.name = 'blub';
        link.href = this.__get_urls().download;
        link.hidden = true;
        this.card_element.appendChild(link);
        link.click();
    }

    __on_click_recalculate(){
        let required_filter = this.control_elements[0].value;
        this.required_filter = required_filter;
        let that = this;
        this.set_status(2);
        $.ajax({
          dataType: "json",
          type: 'POST',
          data: {'required_filter': required_filter},
          url: '/api/project/' + that.expression_id + '/apply',
          success: function(data){
              that.set_status(3);
              if(that.next_expression_card !== null && that.next_expression_card !== undefined){
                 that.next_expression_card.trigger_update();
              }

              if(that.selected_image_parameter !== null && that.selected_image_parameter !== undefined){
                  that.__show_plot(that.selected_image_parameter);
              }
              else {
                  if(that.dataset.number_of_dimensions <= 3){
                      that.selected_image_parameter = that.get_image_parameters();
                  }
                  else{
                      that.selected_image_parameter = Object.assign({}, that.get_image_parameters(), {'PCA': 3});
                  }
                  that.__show_plot(that.selected_image_parameter);
              }
          }
        });
    }

    apply(){
        if(this.filters.length > 1) {
            this.__on_click_recalculate();
        }
        this.app.calculate_all();
    }

    trigger_apply_all(){
        this.apply();

        if(this.next_expression_card !== null && this.next_expression_card !== undefined){
            this.app.recalculation_array = this.next_expression_card.generate_recalculation_list();
        }
        this.app.calculate_all();
    }

    generate_recalculation_list(){
        let return_array = [];
        for(let i=0; i < this.filters.length; i++){
            return_array.push(this.filters[i]);
        }
        return_array.push(this);
        if(this.next_expression_card !== null && this.next_expression_card !== undefined){
            return_array = return_array.concat(this.next_expression_card.generate_recalculation_list());
        }
        return return_array;
    }

    __on_click_button_reset(){
        this.control_elements[0].value = this.required_filter;
        this.__check_on_change();
    }

    __parameters_changed(){
        return this.control_elements[0].value != this.required_filter;
    }

    __show_plot(parameter){
        this.plot_element.setAttribute('src', '/static/img/loading.gif');
        this.plot_element.classList.add('loading_image');
        for(let i=0; i < this.plot_buttons.length; i++){
            this.plot_buttons[i].disabled = true;
        }
        let that = this;
        $.ajax({
          dataType: "json",
          type: 'POST',
          url: '/api/picture/expression/' + that.expression_id,
          data: parameter,
          success: function(data){
              that.plot_element.classList.remove('loading_image');
              that.plot_element.setAttribute('src', data.picture);
              for(let i=0; i < that.plot_buttons.length; i++){
                 that.plot_buttons[i].disabled = false;
              }
          }
        });
    }

    __render_plot(rendering_element){
        this.plot_element = document.createElement('img');
        this.plot_element.classList.add('plot');
        rendering_element.appendChild(this.plot_element);
        var that = this;
        if(this.selected_image_parameter !== null && this.selected_image_parameter !== undefined){
            that.__show_plot(this.selected_image_parameter);
        }
        else {
            this.plot_element.setAttribute('src', '/static/img/no_picture.png');
        }

        let plot_button_row = document.createElement('div');
        rendering_element.appendChild(plot_button_row);
        plot_button_row.classList.add('row');

        let data_dimension = this.dataset.number_of_dimensions;

        if(data_dimension === 2){
            let button = document.createElement('button');
            plot_button_row.appendChild(button);
            this.plot_buttons.push(button);
            button.innerText = '2d view';
            button.addEventListener('click', function () {
                that.selected_image_parameter = that.get_image_parameters();
                that.__show_plot(that.selected_image_parameter);
            });
        }
        if(data_dimension === 3){
            let button = document.createElement('button');
            plot_button_row.appendChild(button);
            this.plot_buttons.push(button);
            button.innerText = '3d view';
            button.addEventListener('click', function () {
                that.selected_image_parameter = that.get_image_parameters();
                that.__show_plot(that.selected_image_parameter);
            });
        }
        if(data_dimension > 2){
            let button = document.createElement('button');
            plot_button_row.appendChild(button);
            this.plot_buttons.push(button);
            button.innerText = 'PCA n=2';
            button.addEventListener('click', function () {
                that.selected_image_parameter = Object.assign({}, that.get_image_parameters(), {'PCA': 2});
                that.__show_plot(that.selected_image_parameter);
            });
        }
        if(data_dimension > 3){
            let button = document.createElement('button');
            plot_button_row.appendChild(button);
            this.plot_buttons.push(button);
            button.innerText = 'PCA n=3';
            button.addEventListener('click', function () {
                that.selected_image_parameter = Object.assign({}, that.get_image_parameters(), {'PCA': 3});
                that.__show_plot(that.selected_image_parameter);
            });
        }
        if(data_dimension > 2){
            let button = document.createElement('button');
            plot_button_row.appendChild(button);
            this.plot_buttons.push(button);
            button.innerText = 'Projection to 2D plane';
            button.addEventListener('click', function () {
                let axis_a = parseInt(prompt("Which axis should be the x-axis?", "0"));
                let axis_b = parseInt(prompt("Which axis should be the y-axis?", "0"));
                that.selected_image_parameter = Object.assign({}, that.get_image_parameters(), {'projection': JSON.stringify([axis_a, axis_b])});
                that.__show_plot(that.selected_image_parameter);
            });
        }
        if(data_dimension > 3){
            let button = document.createElement('button');
            plot_button_row.appendChild(button);
            this.plot_buttons.push(button);
            button.innerText = 'Projection to 3D plane';
            button.addEventListener('click', function () {
                let axis_a = parseInt(prompt("Which axis should be the x-axis?", "0"));
                let axis_b = parseInt(prompt("Which axis should be the y-axis?", "0"));
                let axis_c = parseInt(prompt("Which axis should be the z-axis?", "0"));
                that.selected_image_parameter = Object.assign({}, that.get_image_parameters(), {'projection': JSON.stringify([axis_a, axis_b, axis_c])});
                that.__show_plot(that.selected_image_parameter);
            });
        }
    }

    set_status(status) {
        this.status = status;
        if(this.filters.length > 1) {
            switch (status) {
                case 0:
                case 1:
                    this.expression_operation_card.classList.remove('card_running');
                    this.expression_operation_card.classList.remove('card_ready');
                    this.expression_operation_card.classList.add('card_waiting');
                    break;
                case 2:
                    this.expression_operation_card.classList.remove('card_waiting');
                    this.expression_operation_card.classList.remove('card_ready');
                    this.expression_operation_card.classList.add('card_running');
                    break;
                case 3:
                    this.expression_operation_card.classList.remove('card_running');
                    this.expression_operation_card.classList.remove('card_waiting');
                    this.expression_operation_card.classList.add('card_ready');
                    break;
                default:
                    alert('Falscher Status: ' + status);
                    break
            }
        }
        this.__toggle_enabling_plot_buttons();
    }

    __toggle_enabling_plot_buttons() {
        switch (this.status) {
            case 0:
                // disable plot buttons
                for(let i=0; i < this.plot_buttons.length; i++){
                   this.plot_buttons[i].disabled = true;
                }
                if (this.recalculate_button != null){ this.recalculate_button.disabled = false; }
                if (this.recalculate_all_button != null){ this.recalculate_all_button.disabled = false; }
                if (this.reset_button != null){ this.reset_button.disabled = false; }
                if (this.downlaod_button != null){ this.downlaod_button.disabled = true; }
                break;
            case 1:
                // disable plot buttons
                for(let i=0; i < this.plot_buttons.length; i++){
                   this.plot_buttons[i].disabled = true;
                }
                if (this.recalculate_button != null){ this.recalculate_button.disabled = false; }
                if (this.recalculate_all_button != null){ this.recalculate_all_button.disabled = false; }
                if (this.reset_button != null){ this.reset_button.disabled = false; }
                if (this.downlaod_button != null){ this.downlaod_button.disabled = true; }
                break;
            case 2:
                // disable plot buttons
                for(let i=0; i < this.plot_buttons.length; i++){
                   this.plot_buttons[i].disabled = true;
                }
                if (this.recalculate_button != null){ this.recalculate_button.disabled = true; }
                if (this.recalculate_all_button != null){ this.recalculate_all_button.disabled = true; }
                if (this.recalculate_button != null){ this.reset_button.disabled = true; }
                if (this.downlaod_button != null){ this.downlaod_button.disabled = true; }
                break;
            case 3:
                for(let i=0; i < this.plot_buttons.length; i++){
                    this.plot_buttons[i].disabled = false;
                }
                for(let i=0; i < this.control_elements.length; i++){
                    this.control_elements[i].disabled = false;
                }
                if (this.recalculate_button != null){ this.recalculate_button.disabled = true; }
                if (this.recalculate_all_button != null){ this.recalculate_all_button.disabled = true; }
                if (this.reset_button != null){ this.reset_button.disabled = true; }
                if (this.downlaod_button != null){ this.downlaod_button.disabled = true; }
                break;
        }
    }

    add_filter(filter_name){
        let that = this;
        this.show_add_filter_card = false;
        $.ajax({
          dataType: "json",
          type: 'POST',
          data: {'filter_name': filter_name},
          url: '/api/project/' + that.expression_id + '/new_filter',
          success: function(data){
                let new_filter = new Filter(that, that.dataset, data);
                that.filters.push(new_filter);
                that.update_gui();
          }
        });
    }
}


class AddNewFilterCard{
    constructor(expression){
        this.expression = expression;

        // DOM elements
        this.card_element = null;


    }

    render(rendering_element){
        this.card_element = document.createElement('div');
        rendering_element.appendChild(this.card_element);
        this.card_element.classList.add('filter');
        this.card_element.classList.add('card_no_status');

        let headline_element = document.createElement('h2');
        this.card_element.appendChild(headline_element);
        headline_element.innerText = 'Filter Selection';

        let container_element = document.createElement('div');
        container_element.classList.add('container_new_filter_buttons');
        this.card_element.appendChild(container_element);

        let filters = [];
        filters.push({'title': 'Edge-betweeness filter', 'id': 'Filter:EdgeBetweeness'});
        filters.push({'title': 'Edge distance filter', 'id': 'Filter:EdgeDistance'});
        filters.push({'title': 'Inter-density connection filter', 'id': 'Filter:InterDensityConnection'});
        filters.push({'title': 'Min points filter', 'id': 'Filter:MinPoints'});
        filters.push({'title': 'Distance of incoming edges filter', 'id': 'Filter:DistanceOfInboundEdges'});

        for(let i=0; i < filters.length; i++){
            let button = document.createElement('button');
            button.classList.add('btn');
            button.classList.add('btn-default');
            button.classList.add('btn-md');
            button.classList.add('bottom_button');
            button.setAttribute('type', 'button');
            button.setAttribute('filter_id', filters[i].id);
            button.appendChild(document.createTextNode(filters[i].title));
            let that = this;
            button.addEventListener('click', function () {
                let filter_name = this.getAttribute('filter_id');
                that.card_element.style.display = "none";
                that.expression.add_filter(filter_name);
            });
            container_element.appendChild(button);

            if(i % 3 === 0){
                container_element.appendChild(document.createElement('br'));
            }
        }

        container_element.appendChild(document.createElement('br'));
        container_element.appendChild(document.createElement('br'));

        // Delete Button
        let delete_button = document.createElement('button');
        delete_button.classList.add('btn');
        delete_button.classList.add('btn-default');
        delete_button.classList.add('btn-md');
        delete_button.classList.add('bottom_button');
        delete_button.setAttribute('type', 'button');
        delete_button.innerHTML = '<span class="glyphicon glyphicon-trash"></span> remove filter';
        let that = this;
        delete_button.addEventListener('click', function () { that.expression.remove_add_filter_card(); });
        container_element.appendChild(delete_button);
    }
}
