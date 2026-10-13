# faster-whisper==1.2.1
"""Transcribe a 16 kHz mono WAV into timestamped segments (JSON)."""
import json, sys, time
from faster_whisper import WhisperModel

def transcribe(wav_path, out_path, model_size="small"):
    model = WhisperModel(model_size, device="cpu", compute_type="int8", cpu_threads=2)
    segments, info = model.transcribe(
        wav_path, language="en", beam_size=1,  # greedy: ~2x faster on CPU
        vad_filter=True,                        # skip silences
        condition_on_previous_text=False,       # avoids repetition loops on long audio
    )
    rows, started = [], time.time()
    for seg in segments:
        rows.append({"start": round(seg.start, 2), "end": round(seg.end, 2), "text": seg.text.strip()})
        if len(rows) % 50 == 0:
            print(f"{seg.end/60:.1f} min done, {time.time()-started:.0f}s elapsed", flush=True)
    json.dump({"language": info.language, "duration": info.duration, "segments": rows},
              open(out_path, "w"), indent=1)
    print("DONE", len(rows), "segments", flush=True)

if __name__ == "__main__":
    transcribe(sys.argv[1], sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else "small")
