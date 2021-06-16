import logging
import collections


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


Request = collections.namedtuple("Request", ['command', 'data_definition', 'enabled_responses'])
Response = collections.namedtuple("Response", ['command', 'data_definition', 'enabled_requests'])


class BaseWrapper():

    def __init__(self):

        self._requests = {}
        self._responses = {}


    def _sanitize_typing_definition(self, data):

        cleaned_data = {}
        for key, typing in data.items():
            if typing is None:
                logger.debug(f"Ignoring typing for data key '{key}'.")
            elif type(typing) is not type:
                logger.warning(f"The required typing of data key '{key}' is not a type, it's type is {type(typing)}. Ignoring.")
                typing = None
            else:
                logger.debug(f"Added typing {type(typing)} for data key '{key}'.")

            cleaned_data[key] = typing

        return cleaned_data


    def register_request(self, command, data_definition={}, enabled_responses=[]):

        command = str(command)

        if command in self._requests:
            raise RuntimeWarning(f"A request with the command '{command}' already exists.")

        data_definition = self._sanitize_typing_definition(data_definition)

        # enter the request into the collection dictionary
        self._requests[command] = Request(command, data_definition, enabled_responses)


    def register_response(self, command, data_definition={}, enabled_requests=[]):

        command = str(command)

        if command in self._responses:
            raise RuntimeWarning(f"A response with the command '{command}' already exists.")

        data_definition = self._sanitize_typing_definition(data_definition)

        # enter the response into the collection dictionary
        self._responses[command] = Response(command, data_definition, enabled_requests)

