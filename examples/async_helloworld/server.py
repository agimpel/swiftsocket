import asyncio
import swiftsocket

server = swiftsocket.SimpleServer(host='127.0.0.1', port=8001)

server.register_request("helloworld")
server.register_response("helloworld", data_definition={"text": str})
server.build_responses()

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