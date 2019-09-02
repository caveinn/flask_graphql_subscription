from flask import Flask, make_response
from flask_graphql import GraphQLView
from graphql.backend import GraphQLCoreBackend
from flask_sockets import Sockets
from graphql_ws.gevent import  GeventSubscriptionServer
from werkzeug.debug import DebuggedApplication
from gevent.pywsgi import WSGIServer
from geventwebsocket.handler import WebSocketHandler

from schema import schema
from werkzeug.serving import run_with_reloader
from overidenview import OveridenView



class CustomBackend(GraphQLCoreBackend):
    def __init__(self, executor=None):
        super().__init__(executor)
        self.execute_params['allow_subscriptions'] = True


app = Flask(__name__)
app.debug = True
app.add_url_rule('/graphql', view_func=OveridenView.as_view('graphql', schema=schema, backend=CustomBackend(), graphiql=True))

sockets = Sockets(app)
subscription_server = GeventSubscriptionServer(schema)
app.app_protocol = lambda environ_path_info: 'graphql-ws'


@sockets.route('/subscriptions')
def echo_socket(ws):
    print('working')
    subscription_server.handle(ws)
    return []


if __name__ == "__main__":
    from gevent import pywsgi
    from geventwebsocket.handler import WebSocketHandler
    server = pywsgi.WSGIServer(('', 5000), app, handler_class=WebSocketHandler)
    server.serve_forever()

