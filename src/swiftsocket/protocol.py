import logging
import json
import time
import dataclasses
import collections

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


@dataclasses.dataclass
class Protocol():
    command: str
    data: dict
    message: str = None
    timestamp: int = None


    @classmethod
    def from_message(cls, message):

        decoded_message = json.loads(str(message))

        instance = cls(
            decoded_message.get('cmd', None),
            decoded_message.get('data', None),
            decoded_message.get('timestamp', None),
            message
        )
        return instance


    def to_message(self):

        self.timestamp = int(time.time())
        decoded_message = {'cmd': self.command, 'data': self.data, 'timestamp': self.timestamp}
        self.message = json.dumps(decoded_message)
        logger.debug(f"Encoded message is '{self.message}'.")
        
        return self.message


    def to_object(self):
        object_tuple = collections.namedtuple("ResponseObject", ['command', 'data', 'timestamp'])
        data_tuple = collections.namedtuple("ResponseDataTuple", self.data.keys())

        return object_tuple(command=self.command, data=data_tuple(**self.data), timestamp=self.timestamp)



    def sanitize_data(self, typing_definition):
        clean_data = {}

        for key, typing in typing_definition.items():

            if key not in self.data:
                logger.error(f"There is no entry for '{key}' in the data block of the message for command '{self.command}'.")
                raise KeyError(f"There is no entry for '{key}' in the data block of the message for command '{self.command}'.")

            try:
                clean_data[key] = typing(self.data[key])
            except Exception as e:
                logger.exception(f"Unable to cast data of key '{key}' with value '{self.data[key]}' to type {typing}: {e}.")
                raise TypeError(f"Unable to cast data of key '{key}' with value '{self.data[key]}' to type {typing}: {e}.")

        self.data = clean_data
