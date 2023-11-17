from PySide6 import QtWebChannel, QtCore
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWidgets import QVBoxLayout, QWidget, QApplication
from PySide6.QtCore import QObject, Signal, Property, Slot
import pandas as pd
import network_graph.graph_objects as go


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

        # Dummy choropleth data
        interest_data = pd.DataFrame({'Code': ["USA", 'FR', "GB", "BRA", "DEU"], "Value": [1, 2, 3, 5, 10]})

        fig = go.Figure(data=go.Choropleth(
            z=interest_data['Value'],
            locations=interest_data["Code"],
            zmin=-2,
            zmax=12
        ))

        # convert it to JSON
        fig_json = fig.to_json()

        # a simple HTML template
        template = """<html>
        <head>
            <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
            <script src="qrc:///qtwebchannel/qwebchannel.js"></script>
        </head>
        <body>
            <div id='myPlot'></div>
            <script>
                var plotly_data = """ + fig_json + \
                   """
                var myPlot = document.getElementById('myPlot')
                Plotly.newPlot(myPlot, plotly_data.data, plotly_data.layout);
                var backend = null;
                new QWebChannel(qt.webChannelTransport, function (channel) {
                    backend = channel.objects.backend;
                });
                myPlot.on('plotly_click', function(data) {
                    backend.value = plotly_data.data[0].locations[data.points[0].pointNumber];
                })
            </script>
        </body>
        </html>"""

        # Create our webview and register our backend
        self.browser = QWebEngineView()

        # Create our backend
        backend = PlotlyBackend(self)
        backend.valueChanged.connect(self.get_country_table)
        self.channel = QtWebChannel.QWebChannel()
        self.channel.registerObject("backend", backend)
        self.browser.page().setWebChannel(self.channel)

        # Set the webview to have the html and set it in the view
        self.browser.setHtml(template)

        layout = QVBoxLayout(self)
        layout.addWidget(self.browser)

    @Slot()
    def get_country_table(self, data):
        import pycountry
        country = pycountry.countries.get(alpha_3=data).name
        print(country)


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    gp = GraphPage()
    gp.show()
    sys.exit(app.exec())
