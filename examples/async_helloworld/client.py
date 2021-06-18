import asyncio
import swiftsocket

client = swiftsocket.SimpleClient(host='127.0.0.1', port=8001)

client.register_request("helloworld")
client.register_response("helloworld", data_definition={"text": str})
client.build_requests()



async def main():
    response = await client.requests.helloworld()
    print(response.data.text)

asyncio.run(main())