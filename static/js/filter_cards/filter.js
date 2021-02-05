class Filter{
    constructor(expression, dataset, data){
        this.expression = expression;
        this.dataset = dataset;

        this.filter_id = data.id;
        this.selected_image_parameter = data.selected_image;
        this.parameter = data.parameter;
        this.controls = data.controls;
        this.status = data.status;
        this.headline = data.gui_name;
        this.tooltip = data.tooltip;

        this.current_selected_parameter = Object.assign({}, this.parameter);  // copies dict

        // DOM elements
        this.plot_element = null;
        this.recalculate_button = null;
        this.recalculate_all_button = null;
        this.reset_button = null;
        this.downlaod_button = null;
        this.add_compare_filter_button = null;
        this.delete_button = null;
        this.card_element = null;

        // DOM elements
        this.plot_buttons = [];
        this.control_elements = [];
    }

    get_image_parameters(){
        return {'graph': '', 'highlight_components': ''};
    }

    show_download_button(){
        return true;
    }

    render(rendering_element){
        this.card_element = document.createElement('div');
        rendering_element.appendChild(this.card_element);
        this.card_element.classList.add('filter');

        let headline_element = document.createElement('h2');
        this.card_element.appendChild(headline_element);
        headline_element.innerText = this.headline;

        let container_element = document.createElement('div');
        this.card_element.appendChild(container_element);

        let row_element_2 = document.createElement('div');
        container_element.appendChild(row_element_2);
        row_element_2.classList.add('row');
        row_element_2.classList.add('position_relative');

        let column_1 = document.createElement('div');
        row_element_2.appendChild(column_1);
        column_1.classList.add('col-md-7');

        let rendering_element_plot = document.createElement('div');
        column_1.appendChild(rendering_element_plot);
        rendering_element_plot.classList.add('card_plot');

        this.__render_plot(rendering_element_plot);

        let legend_element = document.createElement('div');
        row_element_2.appendChild(legend_element);

        this.__render_legend(legend_element);

        // restore the currently selected values
        for(let i=0; i < this.control_elements.length; i++){
            this.control_elements[i].value = this.current_selected_parameter[this.control_elements[i].getAttribute('parameter_id')];
        }

        this.set_status(this.status);
    }

    __render_legend(rendering_element) {
        let legend_element = document.createElement('div');
        rendering_element.appendChild(legend_element);

        legend_element.classList.add('col-md-4');
        legend_element.classList.add('full_height');

        let rendering_element_legend = document.createElement('div');
        legend_element.appendChild(rendering_element_legend);
        rendering_element_legend.classList.add('card_plot_legend');

        this.__render_tooltip(rendering_element_legend);
        this.__render_legend_controls(rendering_element_legend);
        this.__render_legend_buttons(rendering_element);
    }

    __render_tooltip(rendering_element){
        let tooltip_element = document.createElement('div');
        tooltip_element.classList.add('tooltipXX');
        tooltip_element.innerText = this.tooltip;
        rendering_element.appendChild(tooltip_element);
        rendering_element.appendChild(document.createElement('br'));
    }

    __render_legend_controls(rendering_element){
        let table = document.createElement('table');
        rendering_element.appendChild(table);

        let table_body = document.createElement('tbody');
        table.appendChild(table_body);

        for(let i=0; i < this.controls.length; i++){
            let row = document.createElement('tr');
            table_body.appendChild(row);

            let legend_title_element = document.createElement('th');
            legend_title_element.innerText = this.controls[i].title + ':';
            row.appendChild(legend_title_element);

            let legend_value_element = document.createElement('td');
            row.appendChild(legend_value_element);

            this.__render_legend_control_value_section(legend_value_element, this.controls[i]);
        }
    }

    __render_legend_control_value_section(rendering_element, control_parameter){
        switch (control_parameter.type) {
            case 'int':
                this.__render_legend_control_value_section_int(rendering_element, control_parameter);
                break;
            case 'float':
                this.__render_legend_control_value_section_float(rendering_element, control_parameter);
                break;
            case 'selection':
                this.__render_legend_control_value_section_selection(rendering_element, control_parameter);
                break;
        }
    }

    __render_legend_control_value_section_int(rendering_element, control_parameter){
        let that = this;
        let element = document.createElement('input');
        element.setAttribute('type', 'number');
        element.setAttribute('min', control_parameter.min);
        element.setAttribute('max', control_parameter.max);
        element.setAttribute('parameter_id', control_parameter.id);
        element.addEventListener("change", function (){ that.__save_parameters(); });
        this.control_elements.push(element);
        rendering_element.appendChild(element);
    }

    __render_legend_control_value_section_float(rendering_element, control_parameter){
        let that = this;
        let element = document.createElement('input');
        element.setAttribute('type', 'number');
        element.setAttribute('min', control_parameter.min);
        element.setAttribute('max', control_parameter.max);
        element.setAttribute('parameter_id', control_parameter.id);
        element.setAttribute('step', '0.01');
        element.addEventListener("change", function (){ that.__save_parameters(); });
        this.control_elements.push(element);
        rendering_element.appendChild(element);
    }

    __render_legend_control_value_section_selection(rendering_element, control_parameter){
        let that = this;
        let selection_element = document.createElement('select');
        selection_element.classList.add('btn');
        selection_element.classList.add('btn-default');
        selection_element.classList.add('dropdown-toggle');
        selection_element.classList.add('my_dropdown_box');
        selection_element.setAttribute('parameter_id', control_parameter.id);
        selection_element.addEventListener("change", function (){ that.__save_parameters(); });
        this.control_elements.push(selection_element);
        rendering_element.appendChild(selection_element);
        for(let i=0; i < control_parameter.values.length; i++){
            let option_element = document.createElement('option');
            option_element.setAttribute('value', control_parameter.values[i]['value']);
            option_element.innerText = control_parameter.values[i]['title'];
            selection_element.appendChild(option_element);
        }
    }

    __save_parameters(){
        let parameter = {};
        for(let i=0; i < this.control_elements.length; i++){
            parameter[this.control_elements[i].getAttribute('parameter_id')] = this.control_elements[i].value;
        }
        this.current_selected_parameter = parameter;
        this.__check_on_change();
    }

    __reset_parameters(){
        for(let i=0; i < this.control_elements.length; i++){
            this.control_elements[i].value = this.parameter[this.control_elements[i].getAttribute('parameter_id')];
        }
        this.current_selected_parameter = Object.assign({}, this.parameter);
    }

    __parameters_changed(){
        for(let i=0; i < this.control_elements.length; i++){
            if(this.control_elements[i].value !== this.parameter[this.control_elements[i].getAttribute('parameter_id')]){
                return true;
            }
        }
        return false;
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


        // called from subclasses
        this.recalculate_button = document.createElement('button');
        this.recalculate_button.classList.add('btn');
        this.recalculate_button.classList.add('btn-default');
        this.recalculate_button.classList.add('btn-md');
        this.recalculate_button.classList.add('bottom_button');
        this.recalculate_button.setAttribute('type', 'button');
        this.recalculate_button.innerHTML = '<span class="glyphicon glyphicon-refresh"></span> calculate';
        this.recalculate_button.addEventListener('click', function () { that.apply(); });
        row_2_space.appendChild(this.recalculate_button);

        this.recalculate_all_button = document.createElement('button');
        this.recalculate_all_button.classList.add('btn');
        this.recalculate_all_button.classList.add('btn-default');
        this.recalculate_all_button.classList.add('btn-md');
        this.recalculate_all_button.classList.add('bottom_button');
        this.recalculate_all_button.setAttribute('type', 'button');
        this.recalculate_all_button.innerHTML = '<span class="glyphicon glyphicon-refresh"></span> calculate all';
        this.recalculate_all_button.addEventListener('click', function () { that.apply_all(); });
        row_2_space.appendChild(this.recalculate_all_button);

        if(this.show_download_button()) {
            this.downlaod_button = document.createElement('button');
            this.downlaod_button.classList.add('btn');
            this.downlaod_button.classList.add('btn-default');
            this.downlaod_button.classList.add('btn-md');
            this.downlaod_button.classList.add('bottom_button');
            this.downlaod_button.setAttribute('type', 'button');
            this.downlaod_button.innerHTML = '<span class="glyphicon glyphicon-download"></span> download result';
            this.downlaod_button.addEventListener('click', function () {
                that.__on_click_button_download_result();
            });
            row_1_space.appendChild(this.downlaod_button);
        }

        this.reset_button = document.createElement('button');
        this.reset_button.classList.add('btn');
        this.reset_button.classList.add('btn-default');
        this.reset_button.classList.add('btn-md');
        this.reset_button.classList.add('bottom_button');
        this.reset_button.setAttribute('type', 'button');
        this.reset_button.innerHTML = '<span class="glyphicon glyphicon-erase"></span> reset parameters';
        this.reset_button.addEventListener('click', function () { that.__on_click_button_reset(); });
        row_1_space.appendChild(this.reset_button);

        this.add_compare_filter_button = document.createElement('button');
        this.add_compare_filter_button.classList.add('btn');
        this.add_compare_filter_button.classList.add('btn-default');
        this.add_compare_filter_button.classList.add('btn-md');
        this.add_compare_filter_button.classList.add('bottom_button');
        this.add_compare_filter_button.setAttribute('type', 'button');
        if(this.__show_add_compare_filter() === false){
            this.add_compare_filter_button.style.display = "none";
        }
        this.add_compare_filter_button.innerHTML = '<span class="glyphicon glyphicon-plus"></span> add filter to combine';
        this.add_compare_filter_button.addEventListener('click', function () { that.expression.add_filter_card(); });
        row_1_space.appendChild(this.add_compare_filter_button);


        this.delete_button = document.createElement('button');
        this.delete_button.classList.add('btn');
        this.delete_button.classList.add('btn-default');
        this.delete_button.classList.add('btn-md');
        this.delete_button.classList.add('bottom_button');
        this.delete_button.setAttribute('type', 'button');
        if(this.__show_delete_button() === false){
            this.delete_button.style.display = "none";
        }
        this.delete_button.innerHTML = '<span class="glyphicon glyphicon-trash"></span> remove filter';
        this.delete_button.addEventListener('click', function () { that.__remove_filter(); });
        row_2_space.appendChild(this.delete_button);
    }

    __remove_filter(){
        if (confirm('Do you want really delete this filter?')) {
            this.expression.filter_removed_applied(this);
        }
    }

    set_status(status) {
        this.status = status;
        switch (status) {
            case 0:
            case 1:
                this.card_element.classList.remove('card_running');
                this.card_element.classList.remove('card_ready');
                this.card_element.classList.add('card_waiting');
                break;
            case 2:
                this.card_element.classList.remove('card_waiting');
                this.card_element.classList.remove('card_ready');
                this.card_element.classList.add('card_running');
                break;
            case 3:
                this.card_element.classList.remove('card_running');
                this.card_element.classList.remove('card_waiting');
                this.card_element.classList.add('card_ready');
                break;
            default:
                alert('Falscher Status: ' +  status);
                break
        }
        this.__toggle_enabling_plot_buttons();
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
          url: this.__get_urls().pictures,
          data: parameter,
          success: function(data){
              that.plot_element.classList.remove('loading_image');
              that.plot_element.setAttribute('src', data.picture);
              for(let i=0; i < that.plot_buttons.length; i++){
                 that.plot_buttons[i].disabled = false;
              }
              that.expression.app.calculate_all();
          }
        });
    }

    __on_click_button_download_result(){
        var link = document.createElement("a");
        link.name = 'blub';
        link.href = this.__get_urls().download;
        link.hidden = true;
        this.card_element.appendChild(link);
        link.click();
    }

    apply_all(){
        let that = this;
        that.expression.filter_applied();
        if (that.selected_image_parameter !== null && that.selected_image_parameter !== undefined) {
            that.plot_element.setAttribute('src', '/static/img/loading.gif');
            that.plot_element.classList.add('loading_image');
        }
        that.__save_parameters();
        that.set_status(2);
        that.parameter = that.current_selected_parameter;
        $.ajax({
            dataType: "json",
            type: 'POST',
            url: that.__get_urls().apply,
            data: that.parameter,
            success: function (data) {
                that.set_status(3);

                if (that.selected_image_parameter !== null && that.selected_image_parameter !== undefined) {
                    that.__show_plot(that.selected_image_parameter);
                } else {
                    if (that.dataset.number_of_dimensions <= 3) {
                        that.selected_image_parameter = that.get_image_parameters();
                    } else {
                        that.selected_image_parameter = Object.assign({}, that.get_image_parameters(), {'PCA': 3});
                    }
                    that.__show_plot(that.selected_image_parameter);
                }
                that.expression.trigger_apply_all();
            }
        });
    }

    apply(){
        let that = this;
        this.expression.filter_applied();
        if(this.selected_image_parameter !== null && this.selected_image_parameter !== undefined) {
            this.plot_element.setAttribute('src', '/static/img/loading.gif');
            this.plot_element.classList.add('loading_image');
        }
        this.__save_parameters();
        this.set_status(2);
        this.parameter = this.current_selected_parameter;
        $.ajax({
          dataType: "json",
          type: 'POST',
          url: this.__get_urls().apply,
          data: this.parameter,
          success: function(data){
              that.set_status(3);

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

    __get_urls(){
        return {
            'pictures': '/api/picture/filter/'+ this.filter_id,
            'apply': '/api/filter/' + this.filter_id + '/apply',
            'download': '/api/filter/' + this.filter_id + '/result'
        }
    }

    __show_add_compare_filter(){
        return true;
    }

    __show_delete_button(){
        return true;
    }

    __toggle_enabling_plot_buttons(){
        switch (this.status) {
            case 0:
                // disable plot buttons
                for(let i=0; i < this.plot_buttons.length; i++){
                   this.plot_buttons[i].disabled = true;
                }
                if (this.recalculate_button != null){ this.recalculate_button.disabled = false; }
                if (this.recalculate_all_button != null){ this.recalculate_all_button.disabled = false; }
                if (this.reset_button != null){ this.reset_button.disabled = false; }
                if (this.delete_button != null){ this.delete_button.disabled = false; }
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
                if (this.delete_button != null){ this.delete_button.disabled = false; }
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
                if (this.recalculate_all_button != null){ this.recalculate_all_button.disabled = true; }
                if (this.delete_button != null){ this.delete_button.disabled = true; }
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
                if (this.delete_button != null){ this.delete_button.disabled = false; }
                if (this.downlaod_button != null){ this.downlaod_button.disabled = false; }
                break;
        }
    }

    __on_click_button_reset(){
        this.__reset_parameters();
        this.__check_on_change();
    }

    __show_default_plot(){
        if(this.selected_image_parameter !== null && this.selected_image_parameter !== undefined){
            this.__show_plot(this.selected_image_parameter);
        }
        else {
            this.plot_element.setAttribute('src', '/static/img/no_picture.png');
        }
    }

    __render_plot(rendering_element){
        this.plot_element = document.createElement('img');
        this.plot_element.classList.add('plot');
        rendering_element.appendChild(this.plot_element);
        var that = this;
        this.__show_default_plot();

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
}
