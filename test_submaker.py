import edge_tts
import asyncio

async def test():
    comm = edge_tts.Communicate("Hello world this is a test.", "en-US-ChristopherNeural")
    submaker = edge_tts.SubMaker()
    with open("test.mp3", "wb") as f:
        async for chunk in comm.stream():
            if chunk["type"] == "audio":
                f.write(chunk["data"])
            elif chunk["type"] == "WordBoundary":
                submaker.feed(chunk)
    srt = submaker.get_srt()
    print("SRT output:\n", srt)

asyncio.run(test())
