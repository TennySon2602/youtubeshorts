import inspect
import edge_tts.communicate

print("Communicate __init__ args:", inspect.signature(edge_tts.Communicate.__init__))
# inspect SubMaker
print("SubMaker:", inspect.getsource(edge_tts.SubMaker))
