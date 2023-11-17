import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
import networkx as nx
import matplotlib.pyplot as plt
from collections import deque
import plotly.graph_objects as go



def get_links(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'lxml')
    return [urljoin(url, a['href']) for a in soup.find_all('a', href=True)]


def bfs_traversal(start_url, num_layers, graph):
    visited = set()
    queue = deque([(start_url, 0)])

    while queue:
        url, layer = queue.popleft()
        if layer > num_layers:
            break
        if url not in visited:
            visited.add(url)
            connections = get_links(url)

            graph.add_node(url)

            for x in connections:
                graph.add_edge(url, x)
                queue.append((x, layer + 1))

scan_layers = 1
entrance = "https://www.youtube.com/"

graph = nx.Graph()
seed = 0

bfs_traversal(entrance, scan_layers, graph)
pos = nx.spring_layout(graph, seed=seed)


# Add pos to the node
for n, p in pos.items():
    graph.nodes[n]['pos'] = p
    print(n, p)

def create_network_graph():
    edge_trace = go.Scatter(
        x=[],
        y=[],
        line=dict(width=0.5,color='#888'),
        hoverinfo='none',
        mode='lines')

    for edge in graph.edges():
        x0, y0 = graph.nodes[edge[0]]['pos']
        x1, y1 = graph.nodes[edge[1]]['pos']
        edge_trace['x'] += tuple([x0, x1, None])
        edge_trace['y'] += tuple([y0, y1, None])


    node_x = []
    node_y = []
    for node in graph.nodes():
        x, y = graph.nodes[node]['pos']
        node_x.append(x)
        node_y.append(y)

    node_trace = go.Scatter(
        x=node_x,
        y=node_y,
        mode='markers',
        customdata=list(graph.nodes().keys()),
        hoverinfo='text',
        hovertemplate='URL: %{customdata}',
        marker=dict(
            showscale=True,
            # colorscale options
            #'Greys' | 'YlGnBu' | 'Greens' | 'YlOrRd' | 'Bluered' | 'RdBu' |
            #'Reds' | 'Blues' | 'Picnic' | 'Rainbow' | 'Portland' | 'Jet' |
            #'Hot' | 'Blackbody' | 'Earth' | 'Electric' | 'Viridis' |
            colorscale='YlGnBu',
            reversescale=True,
            color=[],
            size=10,
            colorbar=dict(
                thickness=15,
                title='Node Connections',
                xanchor='left',
                titleside='right'
            ),
            line_width=2))

    node_adjacencies = []
    node_text = ""
    for node, adjacencies in enumerate(graph.adjacency()):
        node_adjacencies.append(len(adjacencies[1]))
        # node_text += '# of connections: ' + str(len(adjacencies[1])) + '\n'


    node_trace.marker.color = node_adjacencies
    node_trace.text = node_text

    fig = go.Figure(data=[edge_trace, node_trace],
                    layout=go.Layout(
                    title='<br>Network graph made with Python',
                    titlefont_size=16,
                    showlegend=False,
                    hovermode='closest',
                    margin=dict(b=20,l=5,r=5,t=40),
                    annotations=[ dict(
                        text="Python code: <a href='https://plotly.com/ipython-notebooks/network-graphs/'> https://plotly.com/ipython-notebooks/network-graphs/</a>",
                        showarrow=False,
                        xref="paper", yref="paper",
                        x=0.005, y=-0.002 ) ],
                    xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                    yaxis=dict(showgrid=False, zeroline=False, showticklabels=False))
                    )
    return fig.to_html()
