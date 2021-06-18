import asyncio
import swiftsocket

server = swiftsocket.SimpleServer.from_config(swiftsocket.helpers.read_yaml_config("./helloworld.yml"))


@server.register_handler(command="helloworld")
def handler_helloworld(*args, **kwargs):
    print("Received a hello world!")
    return {'command': "helloworld", 'data': {'text': "Hello to you too!"}}


async def main():
    server.start()
    while True: 
        print("Waiting on connection ...")
        await asyncio.sleep(5)
    

try:
    asyncio.run(main())
except KeyboardInterrupt:
        server.stop()
        print("Server stopped.")