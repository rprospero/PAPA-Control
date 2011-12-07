from ps import PowerSupply
from SimpleXMLRPCServer import SimpleXMLRPCServer
from SimpleXMLRPCServer import SimpleXMLRPCRequestHandler


# Restrict to a particular path.
class RequestHandler(SimpleXMLRPCRequestHandler):
    rpc_paths = ('/RPC2',)

# Create server
server = SimpleXMLRPCServer(("192.168.70.160", 7892),
                            requestHandler=RequestHandler)
server.register_introspection_functions()

server.register_instance(PowerSupply())

server.serve_forever()
