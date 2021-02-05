from numpy import array
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.lines import Line2D
import io
import base64
import urllib.parse
import json
from libary.image import Image
from .connected_components import get_connected_components
import numpy as np
import networkx


class ImageCreator:
    pass

    def create_image(self, parameter: dict, data: array, knn_graph=None, outlier=set()):
        dimension_list = [x+1 for x in range(len(data[0]))]
        title = ''

        if 'projection' in parameter:
            dimension_list = sorted(json.loads(parameter['projection']))
            new_data = list()
            for point in data:
                new_point = list()
                for dim in dimension_list:
                    new_point.append(point[dim])
                new_data.append(new_point)
            data = new_data
            dimension_list = [x + 1 for x in range(len(data[0]))]

        if 'PCA' in parameter:
            n_components = int(parameter['PCA'])
            pca = PCA(n_components=n_components)
            data = pca.fit_transform(data)
            dimension_list = [x+1 for x in range(len(data[0]))]

        fig = plt.figure()
        if 'graph' in parameter:
            if 'highlight_components' in parameter:
                connected_components = get_connected_components(knn_graph)
                real_components = list()
                outliers = set()
                for component in connected_components:
                    component = connected_components[component]
                    if len(component) == 1:
                        outliers.add(component.pop())
                    else:
                        real_components.append(component)
                colors = [plt.cm.tab20(each) for each in np.linspace(0, 1, len(real_components))]
                color_dict = {x: colors[x] for x in range(len(real_components))}

                if len(dimension_list) == 2:
                    ax = fig.add_subplot(111)
                    for index, component in enumerate(real_components):
                        networkx.draw_networkx(knn_graph.subgraph(component), pos=data, node_size=5, arrows=False, with_labels=False, ax=ax, node_color=color_dict[index])
                    networkx.draw_networkx(knn_graph.subgraph(outliers), pos=data, node_size=5, arrows=False, with_labels=False, ax=ax, node_color='black')

                if len(dimension_list) == 3:
                    ax = fig.add_subplot(111, projection='3d')
                    # draw edges
                    for a, b in knn_graph.edges():
                        ax.plot([data[a][0], data[b][0]], [data[a][1], data[b][1]], [data[a][2], data[b][2]], linestyle='-', linewidth=1, color='black')
                    # draw points
                    for index, component in enumerate(real_components):
                        ax.plot([data[x][0] for x in component], [data[x][1] for x in component], [data[x][2] for x in component], '.', color=colors[index])
                    ax.plot([data[x][0] for x in outlier], [data[x][1] for x in outlier], [data[x][2] for x in outlier], '.', color='black')

            else:
                if len(dimension_list) == 2:
                    ax = fig.add_subplot(111)
                    networkx.draw_networkx(knn_graph, pos=data, node_size=5, arrows=False, with_labels=False, ax=ax)
                elif len(dimension_list) == 3:
                    ax = fig.add_subplot(111, projection='3d')
                    # draw edges
                    for a, b in knn_graph.edges():
                        ax.plot([data[a][0], data[b][0]], [data[a][1], data[b][1]], [data[a][2], data[b][2]], linestyle='-', linewidth=1, color='black')
                    # draw points
                    ax.plot([data[x][0] for x in knn_graph.nodes()], [data[x][1] for x in knn_graph.nodes()], [data[x][2] for x in knn_graph.nodes()], '.')
                else:
                    raise ValueError()
        else:
            if len(dimension_list) == 2:
                ax = fig.add_subplot(111)
                ax.plot([data[x][0] for x in range(len(data))], [data[x][1] for x in range(len(data))], '.')
            elif len(dimension_list) == 3:
                ax = fig.add_subplot(111, projection='3d')
                ax.plot([data[x][0] for x in range(len(data))], [data[x][1] for x in range(len(data))], [data[x][2] for x in range(len(data))], '.')
            else:
                raise Exception('AsdASDSD ' + str(len(dimension_list)))
        return Image(parameter=parameter, picture=self.__store_figure(figure=fig))

    def __store_figure(self, figure):
        buffer = io.BytesIO()
        figure.savefig(buffer, format='png', bbox_inches='tight', dpi=300)
        buffer.seek(0)
        string = base64.b64encode(buffer.read())
        return 'data:image/png;base64,' + urllib.parse.quote(string)
