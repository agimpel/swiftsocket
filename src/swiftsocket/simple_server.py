import logging
import asyncio
import types
import collections
import functools


from .base_wrapper import BaseWrapper
from .server import Server
from .protocol import Protocol

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)



class SimpleServer(BaseWrapper):

    HANDLE_FUNCTION_PREFIX = "handle_"

    @classmethod
    def from_config(cls, config):
        instance = cls(host=config['host'], port=config['port'])
        
        for request in config['requests']:
            instance.register_request(request['command'], data_definition=request['data'], enabled_responses=request['responses'])

        for response in config['responses']:
            instance.register_response(response['command'], data_definition=response['data'], enabled_requests=response['requests'])

        instance.build_responses()
        return instance

    
    def __init__(self, host='127.0.0.1', port=8001):

        self._server = Server(host = host, port = port)
 
        # this will hold all tuple references to defined response endpoints
        self.responses = types.SimpleNamespace()

        # call the init function of the base wrapper
        super().__init__()



    def build_responses(self):

        for command, response_type in self._responses.items():
            logger.debug(f"Building response tuple for command '{command}'.")

            namedtuple = collections.namedtuple(f"{command}ResponseTuple", response_type.data_definition.keys())
            setattr(self.responses, command, namedtuple)


    def register_handler(self, function=None, *, command=None):
        if function is None:
            return functools.partial(self.register_handler, command=command)
        
        function_name = f"{self.HANDLE_FUNCTION_PREFIX}{command}" if command else function.__name__
        logger.info(f"Registering function '{function.__name__}' as handler '{function_name}'.")
        setattr(self, function_name, function)

        return function



    def start(self):
        self._server.serve(self._callback_handler)


    def stop(self):
        self._server.stop()



    async def _callback_handler(self, message):

        request_protocol = Protocol.from_message(message)
        if request_protocol.command not in self._requests:
            logger.error(f"A request definition with command '{request_protocol.command}' does not exist.")
            raise KeyError(f"A request definition with command '{request_protocol.command}' does not exist.")
        request_type = self._requests[request_protocol.command]
        request_protocol.sanitize_data(request_type.data_definition)

        handle_function_name = f"{self.HANDLE_FUNCTION_PREFIX}{request_type.command}"
        if not hasattr(self, handle_function_name):
            logger.error(f"A handler for the request '{request_type.command}' with name '{handle_function_name}' was not found. You must implement it.")
            raise NotImplementedError(f"A handler for the request '{request_type.command}' with name '{handle_function_name}' was not found. You must implement it.")
        logger.debug(f"Calling function {handle_function_name} to handle the request.")

        response_handler = getattr(self, handle_function_name)
        if asyncio.iscoroutinefunction(response_handler):
            response_tuple = await response_handler(**request_protocol.data)
        else:
            response_tuple = response_handler(**request_protocol.data)

        if response_tuple:
            logger.debug(f"Sending out response {response_tuple}.")
            if response_tuple['command'] not in self._responses:
                raise RuntimeWarning(f"Supplied response of type '{response_tuple['command']}' is not a valid response.")

            if len(request_type.enabled_responses)>0 and response_tuple['command'] not in request_type.enabled_responses:
                raise RuntimeWarning(f"Supplied response of type '{response_tuple['command']}' is not a valid response for request '{request_type.command}'.")

            response_type = self._responses[response_tuple['command']]
            response_protocol = Protocol(command=response_tuple['command'], data=response_tuple['data'])
            response_protocol.sanitize_data(response_type.data_definition)

            logger.info(f"Responding with command '{response_tuple['command']}': {response_protocol.to_message()}.")
            return response_protocol.to_message()


        else:
            logger.debug("Did not receive a response. Returning.")
            return None