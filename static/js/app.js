"use strict";

class App{

    constructor(project_id){
        this.project_id = project_id;
        this.preclustering_expression = null;
        this.first_expression = null;
        this.add_filter_card = null;
        this.rendering_element_filter_cards = null;
        this.rendering_element_addfilter_card = null;
        this.dataset = null;
        this.recalculation_array = [];
    }


    render(rendering_element){
        let that = this;
        that.rendering_element_filter_cards = document.createElement('div');
        that.rendering_element_addfilter_card = document.createElement('div');

        $.ajax({
          dataType: "json",
          url: '/api/project/' + this.project_id,
          success: function(data){
              // render headline
              that.__render_headline(rendering_element, data.name);

              that.dataset = data.dataset;

              rendering_element.appendChild(that.rendering_element_filter_cards);
              rendering_element.appendChild(that.rendering_element_addfilter_card);

              // Data set Info
              let dataset_info_card = new DatasetInfoCard(data.id, data.dataset, data.parameter_dataset_image);
              dataset_info_card.render(that.rendering_element_filter_cards);

              // Generate kNN-graph expression
              that.preclustering_expression = new RockExpression(that, that.project_id, data.dataset, data.rock);
              that.preclustering_expression.render(that.rendering_element_filter_cards);

              // Generate kNN-graph expression
              that.first_expression = new KnnGraphGenerationExpression(that, that.project_id, data.dataset, data.knn_graph_generation);
              that.preclustering_expression.append_expression(that.first_expression);
              that.first_expression.render(that.rendering_element_filter_cards);

              // Filter Cards
              for(let i=0; i < data.expressions.length; i++){
                  let filter_new = new Expression(that, data.dataset, data.expressions[i]);
                  that.first_expression.append_expression(filter_new);
                  filter_new.render(that.rendering_element_filter_cards);
              }

              // Add Filter Card
              that.add_filter_card = new AddFilterCard(that, data.dataset, function (new_filter_card) { that.__add_filter_callback(new_filter_card); });
              that.add_filter_card.render(that.rendering_element_addfilter_card);
          }
        });
    }

    __render_headline(rendering_element, project_name){
        let headline = document.createElement('h1');
        headline.classList.add('proejct_headline');
        headline.innerText = 'Project: ' + project_name;
        rendering_element.appendChild(headline);
    }

    __on_click_generate_init_knn_graph(parameter){
        // delete old add_filter_card
        this.rendering_element_addfilter_card.removeChild(this.rendering_element_addfilter_card.firstChild);

        var that = this;

        //  create and render new one
        this.add_filter_card = new AddFilterCard(this, this.dataset, function (expression_card) { that.__add_filter_callback(expression_card); });
        this.add_filter_card.render(this.rendering_element_addfilter_card);

        // render
        let generation_card = new KnnGraphGenerationCard(this, this.dataset, parameter, null);
        generation_card.render(this.rendering_element_filter_cards);
        this.first_expression = generation_card;

        // apply filter
        generation_card.apply();
    }

    __add_filter_callback(new_expression){
        // called when a new filter is added
        this.first_expression.append_expression(new_expression);

        new_expression.render(this.rendering_element_filter_cards);
    }

    remove_expression(expression_dom_element){
        this.rendering_element_filter_cards.removeChild(expression_dom_element);
    }

    calculate_all(){
        if(this.recalculation_array.length > 0){
            let item = this.recalculation_array.shift();
            item.apply();
        }
    }
}




