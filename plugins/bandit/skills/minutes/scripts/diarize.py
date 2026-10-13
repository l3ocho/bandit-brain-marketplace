# sherpa-onnx==1.13.8, soundfile
"""Speaker diarization: who spoke when. Outputs JSON turns [{start,end,speaker}]."""
import json, sys
import sherpa_onnx, soundfile as sf

def build(seg_model, emb_model, threshold, num_speakers):
    config = sherpa_onnx.OfflineSpeakerDiarizationConfig(
        segmentation=sherpa_onnx.OfflineSpeakerSegmentationModelConfig(
            pyannote=sherpa_onnx.OfflineSpeakerSegmentationPyannoteModelConfig(model=seg_model), num_threads=2),
        embedding=sherpa_onnx.SpeakerEmbeddingExtractorConfig(model=emb_model, num_threads=2),
        clustering=sherpa_onnx.FastClusteringConfig(num_clusters=num_speakers, threshold=threshold),  # -1 = auto
        min_duration_on=0.3, min_duration_off=0.5)
    if not config.validate():
        raise RuntimeError("invalid diarization config")
    return sherpa_onnx.OfflineSpeakerDiarization(config)

def diarize(wav, out, threshold=0.5, num_speakers=-1):
    audio, sr = sf.read(wav, dtype="float32", always_2d=True)
    sd = build("sherpa-onnx-pyannote-segmentation-3-0/model.onnx", "emb_en.onnx", threshold, num_speakers)
    assert sr == sd.sample_rate
    result = sd.process(audio[:, 0]).sort_by_start_time()
    turns = [{"start": round(r.start, 2), "end": round(r.end, 2), "speaker": int(r.speaker)} for r in result]
    talk = {}
    for t in turns:
        talk[t["speaker"]] = talk.get(t["speaker"], 0) + t["end"] - t["start"]
    print("speakers (min):", {k: round(v / 60, 1) for k, v in sorted(talk.items())})
    json.dump(turns, open(out, "w"))

if __name__ == "__main__":
    diarize(sys.argv[1], sys.argv[2], float(sys.argv[3]) if len(sys.argv) > 3 else 0.5,
            int(sys.argv[4]) if len(sys.argv) > 4 else -1)
