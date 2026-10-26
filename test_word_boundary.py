import asyncio
import edge_tts

async def check_chunks():
    comm = edge_tts.Communicate("Hello world, this is a test.", "en-US-ChristopherNeural")
    types = set()
    async for chunk in comm.stream():
        types.add(chunk["type"])
        if chunk["type"] != "audio":
            print("Non-audio chunk:", chunk)
    print("All types:", types)

asyncio.run(check_chunks())
