import asyncio
import swiftsocket

client = swiftsocket.SimpleClient.from_config(swiftsocket.helpers.read_yaml_config("./helloworld.yml"))


async def main():
    response = await client.requests.helloworld()
    print(response.data.text)

asyncio.run(main())