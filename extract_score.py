import json
import re
import glob
import os
import argparse
from collections import defaultdict

from utils import IMAGE_SCORE_KEYS, VIDEO_SCORE_KEYS


def _infer_media_type(sample: dict) -> str:
    """Infer media type from file extension (.png -> image, .mp4 -> video)."""
    path = sample.get('path', '')
    if path.endswith('.mp4'):
        return 'video'
    return 'image'


def _get_score_keys(media_type: str) -> list[str]:
    return VIDEO_SCORE_KEYS if media_type == "video" else IMAGE_SCORE_KEYS


def extract_scores(response_text: str, score_keys: list[str]) -> dict | None:
    """
    Extract scores from model response text.
    Try JSON parsing first, fall back to regex per-key matching.
    """
    match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", response_text, re.DOTALL)
    if match:
        json_str = match.group(1)
    else:
        bare = re.search(r"(\{.*\})", response_text, re.DOTALL)
        json_str = bare.group(1) if bare else response_text.strip()

    try:
        data = json.loads(json_str)
        scores = {k: data[k] for k in score_keys if k in data}
        if len(scores) == len(score_keys):
            return scores
    except json.JSONDecodeError:
        pass

    scores: dict[str, float] = {}
    for key in score_keys:
        m = re.search(
            rf'"{re.escape(key)}"\s*:\s*("?)(-?\d+(?:\.\d+)?)(\1)',
            json_str,
        )
        if not m:
            return None
        scores[key] = float(m.group(2))
    return scores


def process_file(json_path: str, media_type: str | None = None) -> None:
    """
    Read an inference result JSON, extract scores for each sample,
    and save as *_detailed.json.
    """
    with open(json_path, "r", encoding="utf-8") as f:
        samples = json.load(f)

    if media_type is None:
        media_type = _infer_media_type(samples[0]) if samples else "image"
    score_keys = _get_score_keys(media_type)

    success, failed = 0, 0
    for sample in samples:
        response = sample.get("response", "")
        if not response:
            print(f"[{os.path.basename(json_path)}] empty response: {sample.get('path')}")
            sample["score"] = None
            failed += 1
            continue
        scores = extract_scores(response, score_keys)
        if scores is not None:
            sample["score"] = scores
            success += 1
        else:
            print(f"[{os.path.basename(json_path)}] extraction failed: {response[:200]}")
            sample["score"] = None
            failed += 1

    base = os.path.splitext(json_path)[0]
    out_path = f"{base}_detailed.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(samples, f, ensure_ascii=False, indent=2)

    print(f"[{os.path.basename(json_path)}] total={len(samples)}, success={success}, failed={failed} -> {os.path.basename(out_path)}")
    return samples, score_keys


def print_edit_type_summary(samples: list[dict], score_keys: list[str],
                            title: str | None = None) -> None:
    """Print a summary table of average scores grouped by edit_type."""
    type_scores: dict[str, list[dict]] = defaultdict(list)
    for sample in samples:
        edit_type = sample.get("edit_type", "unknown")
        if sample.get("score") is not None:
            type_scores[edit_type].append(sample["score"])

    if not type_scores:
        print("\nNo valid scores to summarize.")
        return

    col_w = max(len(k) for k in score_keys)
    type_w = max(max(len(t) for t in type_scores), len("edit_type"), len("Overall"))

    header = f"{'edit_type':<{type_w}} | {'count':>5}"
    for key in score_keys:
        header += f" | {key:>{col_w}}"
    header += f" | {'average':>8}"
    sep = "-" * len(header)

    if title:
        print(f"\n{'=' * len(header)}")
        print(f"  Model: {title}")
        print(f"{'=' * len(header)}")
    else:
        print(f"\n{sep}")

    print(header)
    print(sep)

    all_vals: dict[str, list[float]] = defaultdict(list)
    total_count = 0

    for edit_type in sorted(type_scores):
        scores_list = type_scores[edit_type]
        count = len(scores_list)
        total_count += count

        row = f"{edit_type:<{type_w}} | {count:>5}"
        row_sum = 0.0
        for key in score_keys:
            vals = [s[key] for s in scores_list if key in s]
            avg = sum(vals) / len(vals) if vals else 0.0
            all_vals[key].extend(vals)
            row += f" | {avg:>{col_w}.2f}"
            row_sum += avg
        row += f" | {row_sum / len(score_keys):>8.2f}"
        print(row)

    overall = f"{'Overall':<{type_w}} | {total_count:>5}"
    overall_sum = 0.0
    for key in score_keys:
        vals = all_vals[key]
        avg = sum(vals) / len(vals) if vals else 0.0
        overall += f" | {avg:>{col_w}.2f}"
        overall_sum += avg
    overall += f" | {overall_sum / len(score_keys):>8.2f}"
    print(sep)
    print(overall)
    print(sep)


def print_per_model_summary(samples: list[dict], score_keys: list[str]) -> None:
    """Print a separate edit_type summary table for each edit_model."""
    model_groups: dict[str, list[dict]] = defaultdict(list)
    for sample in samples:
        model = sample.get("edit_model", "unknown")
        model_groups[model].append(sample)

    for model in sorted(model_groups):
        print_edit_type_summary(model_groups[model], score_keys, title=model)


def batch_process(directory: str = ".", media_type: str | None = None) -> None:
    """Process all non-detailed JSON files in the given directory."""
    json_files = [
        p for p in glob.glob(os.path.join(directory, "*.json"))
        if not p.endswith("_detailed.json")
    ]
    if not json_files:
        print(f"No JSON files found in {directory}")
        return

    all_samples: list[dict] = []
    final_score_keys = None
    for path in sorted(json_files):
        samples, score_keys = process_file(path, media_type=media_type)
        all_samples.extend(samples)
        final_score_keys = score_keys

    if final_score_keys:
        print_per_model_summary(all_samples, final_score_keys)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract scores from inference results")
    parser.add_argument("--input", type=str, default=None,
                        help="Path to a single JSON file. If not set, batch-process all JSONs in --dir")
    parser.add_argument("--dir", type=str, default=".",
                        help="Directory for batch processing (default: current dir)")
    parser.add_argument("--media_type", type=str, default=None, choices=["image", "video"],
                        help="Media type. Auto-inferred if not specified")
    args = parser.parse_args()

    if args.input:
        samples, score_keys = process_file(args.input, media_type=args.media_type)
        print_per_model_summary(samples, score_keys)
    else:
        batch_process(args.dir, media_type=args.media_type)
