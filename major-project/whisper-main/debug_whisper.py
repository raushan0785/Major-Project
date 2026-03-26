
import sys
import traceback

try:
    import whisper
    print("Whisper imported successfully")
except Exception:
    with open("whisper_error.txt", "w") as f:
        traceback.print_exc(file=f)
    print("Whisper import failed. Traceback written to whisper_error.txt")
