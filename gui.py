from PySide6 import QtWebChannel, QtCore
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWidgets import QVBoxLayout, QWidget, QApplication
from PySide6.QtCore import QObject, Signal, Property, Slot
import plotly.graph_objects as go

from graphs import create_network_graph, create_location_map
from website_data import get_location


class PlotlyBackend(QObject):
    valueChanged = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._value = ""

    @Property(str)
    def value(self):
        return self._value

    @value.setter
    def value(self, v):
        self._value = v
        self.valueChanged.emit(v)


class GraphPage(QWidget):
    def __init__(self):
        super(GraphPage, self).__init__()

        # Set up browser2
        self.browser2 = None

        # convert it to JSON
        fig_json = create_network_graph()

        # a simple HTML template
        template = """<html>
        <head>
            <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
            <script src="qrc:///qtwebchannel/qwebchannel.js"></script>
        </head>
        <body>
            <div id='myPlot1'></div>
            <script>
                // Plot for network graph
                var plotly_data = """ + fig_json + \
                   """
                var myPlot1 = document.getElementById('myPlot1')
                Plotly.newPlot(myPlot1, plotly_data.data, plotly_data.layout);
                var backend = null;
                new QWebChannel(qt.webChannelTransport, function (channel) {
                    backend = channel.objects.backend;
                });
                myPlot1.on('plotly_click', function(data) {
                    backend.value = data.points[0].customdata[1];
                })
            
            </script>
        </body>
        </html>"""

        # Create our webview and register our backend
        self.browser = QWebEngineView()

        # Create our backend
        backend = PlotlyBackend(self)
        backend.valueChanged.connect(self.create_map_graph)
        self.channel = QtWebChannel.QWebChannel()
        self.channel.registerObject("backend", backend)
        self.browser.page().setWebChannel(self.channel)

        # Set the webview to have the html and set it in the view
        self.browser.setHtml(template)

        self.layout = QVBoxLayout(self)
        self.layout.addWidget(self.browser)

    @Slot()
    def create_map_graph(self, clicked_data):

        # Get our ip address data
        loc_data = get_location(clicked_data)

        fig_json = create_location_map(loc_data)

        # a simple HTML template
        template = """<html>
        <head>
            <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
            <script src="qrc:///qtwebchannel/qwebchannel.js"></script>
        </head>
        <body>
            <div id='myPlot1'></div>
            <script>
                // Plot for network graph
                var plotly_data = """ + fig_json + \
                   """
                var myPlot1 = document.getElementById('myPlot1')
                Plotly.newPlot(myPlot1, plotly_data.data, plotly_data.layout);
            </script>
        </body>
        </html>"""

        # Create our webview and register our backend
        self.browser2 = QWebEngineView()
        # Set the webview to have the html and set it in the view
        self.browser2.setHtml(template)

        self.layout.addWidget(self.browser2)


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    gp = GraphPage()
    gp.show()
    sys.exit(app.exec())
