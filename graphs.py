import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
import networkx as nx
import matplotlib.pyplot as plt
from collections import deque
import plotly.graph_objects as go
import plotly.express as px
import json
import pandas as pd

from website_data import get_location

# Gets the links to traverse as well as the IP Address and returns them.
def get_links(url):
    response = requests.get(url, stream=True)
    ip_address = response.raw._connection.sock.getpeername()
    soup = BeautifulSoup(response.text, 'lxml')
    return [urljoin(url, a['href']) for a in soup.find_all('a', href=True)], ip_address



def bfs_traversal(start_url, num_layers, graph):
    visited = []
    visited_ip_addresses = []
    queue = deque([(start_url, 0)])

    attrs = {}
    while queue:
        url, layer = queue.popleft()
        if layer > num_layers:
            # add our attrs
            for url, ip_address in zip(visited, visited_ip_addresses):
                attrs[url] = ip_address

            # Need to set the node attributes manually see below
            nx.set_node_attributes(graph, values=attrs, name='ip_address')

            break

        if url not in visited:
            visited.append(url)
            connections, ip_address = get_links(url)
            visited_ip_addresses.append(ip_address)

            # No longer seems to work hence the above code
            graph.add_node(url, ip_address=ip_address)
            # throws error graph.add_node(url, {'ip_address':ip_address})

            if layer < num_layers:
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

    # Get our keys
    keys = list(graph.nodes().keys())

    ip_addresses = []
    for node in graph.nodes(data=True):
        print(node,  '\n')
        ip_address = node[1]['ip_address'][0]
        ip_addresses.append(ip_address)

    url_ip_address_data = pd.DataFrame({
        'url': keys,
        'ip_address': ip_addresses
    })

    node_trace = go.Scatter(
        x=node_x,
        y=node_y,
        mode='markers',
        customdata=url_ip_address_data,
        hoverinfo='text',
        hovertemplate='URL: %{customdata[0]} <br>'
                      'IP Address: %{customdata[1]}',
        marker=dict(
            showscale=True,
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
                    showlegend=False,
                    hovermode='closest',
                    margin=dict(b=20, l=5, r=5, t=40),
                    xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                    yaxis=dict(showgrid=False, zeroline=False, showticklabels=False))
                    )
    return fig.to_json()


def create_location_map(location_data):
    print(location_data)

    location_data = pd.DataFrame(location_data, index=[0])

    fig = px.choropleth(location_data,
                        locations="country_code_iso3",
                        color="value",  # lifeExp is a column of gapminder
                        hover_name="country"  # column to add to hover information
                        )

    return fig.to_json()
