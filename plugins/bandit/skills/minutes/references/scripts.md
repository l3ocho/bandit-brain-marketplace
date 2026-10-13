# 🐍 Scripts

> Read before transcribing: the three scripts, how to run them, and the diarization models.


The three scripts live in this skill's `scripts/` folder. Copy them into the working directory
before running; don't run them in place (they'd leave cache files in the skill folder).

Install once per session: `pip install --break-system-packages -q faster-whisper sherpa-onnx soundfile`.

| Script | Run | Does |
|---|---|---|
| `scripts/transcribe.py` | `python transcribe.py audio.wav transcript.json [small\|medium]` | Timestamped segments (JSON). Afterwards write a readable `plain.txt` (`[mm:ss] text` per segment) for reading |
| `scripts/diarize.py` (optional) | `python diarize.py audio.wav turns.json [threshold] [num_speakers]` | Who spoke when. Pass the headcount as `num_speakers` if the user knows it — much better than auto. Always run in the background: it exceeds the 10-minute shell timeout on long recordings |
| `scripts/merge.py` (optional) | `python merge.py transcript.json turns.json labelled.txt` | Labels each segment with the speaker of max overlap, merges consecutive lines |

`transcribe.py` defaults to English (`language="en"`); for non-English meetings, edit that line
in your working copy.

Diarization models (only if step 7 runs) come from GitHub releases; the pyannote models on
Hugging Face need a login, so they aren't used. Download them into the working directory:
`diarize.py` expects `sherpa-onnx-pyannote-segmentation-3-0/model.onnx` and `emb_en.onnx` there.
- `https://github.com/k2-fsa/sherpa-onnx/releases/download/speaker-segmentation-models/sherpa-onnx-pyannote-segmentation-3-0.tar.bz2`
- `https://github.com/k2-fsa/sherpa-onnx/releases/download/speaker-recongition-models/wespeaker_en_voxceleb_resnet34_LM.onnx` (English embeddings, saved as `emb_en.onnx`; the zh-cn default is worse for English)
