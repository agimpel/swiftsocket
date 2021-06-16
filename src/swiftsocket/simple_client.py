import functools
import logging
import types


from .base_wrapper import BaseWrapper
from .client import Client
from .protocol import Protocol

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)



class SimpleClient(BaseWrapper):

    @classmethod
    def from_config(cls, config):
        instance = cls(host=config['host'], port=config['port'])
        
        for request in config['requests']:
            instance.register_request(request['command'], data_definition=request['data'], enabled_responses=request['responses'])

        for response in config['responses']:
            instance.register_response(response['command'], data_definition=response['data'], enabled_requests=response['requests'])

        instance.build_requests()
        return instance

    
    def __init__(self, host='127.0.0.1', port=8001):

        self._client = Client(host = host, port = port)

        # this will hold all function references to defined request endpoints
        self.requests = types.SimpleNamespace()

        # call the init function of the base wrapper
        super().__init__()


    async def _base_handler_function(self, cmd, request_type, **kwargs):            

        request_protocol = Protocol(command=cmd, data=kwargs)
        request_protocol.sanitize_data(request_type.data_definition)

        logger.debug(f"Sending message '{request_protocol.to_message()}'.")
        raw_response = await self._client.send(request_protocol.to_message())
        logger.debug(f"Raw response received for command '{cmd}' is '{raw_response}'.")

        if raw_response:
            response_protocol = Protocol.from_message(raw_response)

            if response_protocol.command not in self._responses:
                logger.error(f"A response definition with command '{response_protocol.command}' does not exist.")
                raise KeyError(f"A response definition with command '{response_protocol.command}' does not exist.")

            if len(request_type.enabled_responses)>0 and response_protocol.command not in request_type.enabled_responses:
                logger.error(f"A response definition with command '{response_protocol.command}' is not enabled for the request type '{cmd}'.")
                raise KeyError(f"A response definition with command '{response_protocol.command}' is not enabled for the request type '{cmd}'.")

            response_type = self._responses[response_protocol.command]
            response_protocol.sanitize_data(response_type.data_definition)

            logger.debug(f"Received valid response of type '{response_protocol.command}'.")
            return response_protocol.to_object()
        else:
            logger.debug(f"Received no response.")
            return None



    def build_requests(self):

        for command, request_type in self._requests.items():

            logger.debug(f"Building request function for command '{command}'.")
            cmd_function = functools.partial(self._base_handler_function, command, request_type)        

            setattr(self.requests, command, cmd_function)




