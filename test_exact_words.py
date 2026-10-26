import asyncio
import edge_tts

async def test_word_boundary_option():
    comm = edge_tts.Communicate(
        text="What in the actual hell happens if you sit inside a room so quiet you can hear your own eyeballs moving?",
        voice="en-US-ChristopherNeural",
        rate="+5%",
        pitch="-1Hz",
        boundary="WordBoundary"
    )
    submaker = edge_tts.SubMaker()
    word_count = 0
    with open("test_wb.mp3", "wb") as f:
        async for chunk in comm.stream():
            if chunk["type"] == "audio":
                f.write(chunk["data"])
            elif chunk["type"] == "WordBoundary":
                submaker.feed(chunk)
                word_count += 1
                offset_sec = chunk["offset"] / 10_000_000
                dur_sec = chunk["duration"] / 10_000_000
                if word_count <= 8:
                    print(f"[{offset_sec:.3f}s - {offset_sec+dur_sec:.3f}s]: {chunk['text']}")
                    
    print(f"TOTAL WORDS CAPTURED: {word_count}")

asyncio.run(test_word_boundary_option())
