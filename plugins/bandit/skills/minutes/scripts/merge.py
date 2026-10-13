"""Label each transcript segment with the speaker of max time overlap; merge consecutive lines."""
import json, sys

def overlap(a0, a1, b0, b1):
    return max(0.0, min(a1, b1) - max(a0, b0))

def label_segments(segments, turns):
    j = 0
    for seg in segments:
        while j < len(turns) and turns[j]["end"] < seg["start"]:
            j += 1
        best, best_ov, k = None, 0.0, j
        while k < len(turns) and turns[k]["start"] <= seg["end"]:
            ov = overlap(seg["start"], seg["end"], turns[k]["start"], turns[k]["end"])
            if ov > best_ov:
                best, best_ov = turns[k]["speaker"], ov
            k += 1
        seg["speaker"] = best
    return segments

def fmt(t):
    return f"{int(t // 3600):d}:{int(t % 3600 // 60):02d}:{int(t % 60):02d}"

def write_transcript(segments, out):
    letters, blocks = {}, []
    for seg in segments:
        spk = seg["speaker"]
        name = "Unknown" if spk is None else letters.setdefault(spk, f"Speaker {chr(65 + len(letters))}")
        if blocks and blocks[-1][1] == name:
            blocks[-1][2].append(seg["text"])
        else:
            blocks.append([seg["start"], name, [seg["text"]]])
    with open(out, "w") as fh:
        for start, name, texts in blocks:
            fh.write(f"[{fmt(start)}] {name}: {' '.join(texts)}\n")

if __name__ == "__main__":
    tr, turns = json.load(open(sys.argv[1])), json.load(open(sys.argv[2]))
    write_transcript(label_segments(tr["segments"], turns), sys.argv[3])
