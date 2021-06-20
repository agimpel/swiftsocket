import logging
import asyncio


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


# number of bytes to read from stream at most, set to -1 for all until EOF
READ_BYTES = 1000



class Server():


    def __init__(self, host='127.0.0.1', port=8001):

        self.host = host
        self.port = port

        self.is_running = False
        self.task = None
        self.callback = None


    def serve(self, callback):

        if not self.is_running:
            self.callback = callback
            loop = asyncio.get_event_loop()
            self.task = loop.create_task(self._main())
            self.is_running = True
        else:
            raise RuntimeError(f"Async socket server was already started.")


    def stop(self):

        if self.is_running:
            self.task.cancel()
            logger.info(f"Server task was cancelled.")
        else:
            raise RuntimeError(f"Async socket server not started.")

        self.is_running = False
        self.task = None


    async def _main(self):

        server = await asyncio.start_server(self._handle, self.host, self.port)
        logger.info(f"Serving socket server on {self.host}:{self.port}.")

        async with server:
            await server.serve_forever()


    async def _handle(self, reader, writer):

        try:
            addr = writer.get_extra_info('peername')
            logger.debug(f"Accepted connection from {addr[0]}:{addr[1]}.")

            data = await reader.read(READ_BYTES)
            message = data.decode()

            logger.debug(f"Received {message!r} from {addr[0]}:{addr[1]}.")

            response = await self.callback(message)

            if response:
                logger.debug(f"Responding to {addr[0]}:{addr[1]} with {response!r}.")
                writer.write(response.encode())
                await writer.drain()

        except Exception as e:
            logger.exception(f"Handling of the request failed due to {e}.")

        finally:
            logger.debug(f"Closing the connection to {addr[0]}:{addr[1]}.")
            writer.close()
