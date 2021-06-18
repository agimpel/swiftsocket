import logging
import asyncio


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


# number of bytes to read from stream at most, set to -1 for all until EOF
READ_BYTES = 1000



class Client():

    def __init__(self, host='127.0.0.1', port=8001):

        self.host = host
        self.port = port



    async def send(self, message):

        logger.debug(f"Connecting to {self.host}:{self.port}.")
        reader, writer = await asyncio.open_connection(self.host, self.port)

        logger.debug(f"Sending {message!r} to {self.host}:{self.port}.")
        writer.write(message.encode())
        await writer.drain()

        data = await reader.read(READ_BYTES)
        if data:
            logger.debug(f"Received {data.decode()!r} from {self.host}:{self.port}.")
        else:
            logger.debug(f"Received no response from {self.host}:{self.port}.")
            data = None

        logger.debug(f"Closing the connection to {self.host}:{self.port}.")
        writer.close()

        return data.decode()
