#!/usr/bin/env python3
"""Private, resource-limited PDF candidate segmentation. Requires Linux and pypdf>=6,<7."""
import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone

RULES = {
    "form700": r"\bStatement\s+of\s+Economic\s+Interests\b",
    "settlement": r"\bSettlement\s+Agreement\b",
    "oah": r"\bOffice\s+of\s+Administrative\s+Hearings\b",
    "board": r"\bBoard\s+of\s+Trustees\b",
}
PAGE_ONE = r"(?im)^\s*(?:[-–—]\s*)?Page\s+1(?:\s+of\s+\d+)?\s*(?:[-–—])?\s*$"


def digest(path):
    h = hashlib.sha256()
    with open(path, "rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def worker(job):
    import resource
    ceiling = job["memory_mb"] * 1024 * 1024
    resource.setrlimit(resource.RLIMIT_AS, (ceiling, ceiling))
    cpu = max(1, math.ceil(job["timeout"]))
    resource.setrlimit(resource.RLIMIT_CPU, (cpu, cpu + 1))
    resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
    from importlib.metadata import version
    if version("pypdf").split(".")[0] != "6":
        raise RuntimeError("Install pypdf>=6,<7 in the processing virtual environment")
    from pypdf import PdfReader, PdfWriter
    with open(job["input"], "rb") as stream:
        reader = PdfReader(stream, strict=False)
        if reader.is_encrypted:
            raise ValueError("Encrypted parents are not supported")
        pages = len(reader.pages)
        if job["operation"] == "inspect":
            return {"pages": pages}
        if job["operation"] == "scan":
            compiled = {name: re.compile(pattern, re.I) for name, pattern in job["rules"].items()}
            result = []
            for position in range(job["first"], job["last"] + 1):
                try:
                    text = reader.pages[position - 1].extract_text() or ""
                    lines = text.splitlines()
                    header = "\n".join(lines[:job["header_lines"]])
                    edges = header + "\n" + "\n".join(lines[-8:])
                    result.append({
                        "page": position,
                        "labels": [name for name, pattern in compiled.items() if pattern.search(header)],
                        "page_one_marker": bool(re.search(PAGE_ONE, edges)),
                        "text_characters": len(text.strip()),
                        "text_status": "available" if text.strip() else "no_extractable_text",
                    })
                except Exception as error:
                    result.append({"page": position, "labels": [], "page_one_marker": False,
                                   "text_status": "extraction_failed", "error_type": type(error).__name__})
            return result
        if job["operation"] != "split":
            raise ValueError("Unknown worker operation")
        first, last = job["first"], job["last"]
        if not 1 <= first <= last <= pages:
            raise ValueError("Invalid physical page range")
        writer = PdfWriter()
        try:
            for position in range(first - 1, last):
                writer.add_page(reader.pages[position])
            with open(job["destination"], "xb") as target:
                writer.write(target)
        finally:
            writer.close()
    path = Path(job["destination"])
    return {"sha256": digest(path), "file_size_bytes": path.stat().st_size}


def run_worker(base, operation, **fields):
    job = dict(base, operation=operation, **fields)
    try:
        result = subprocess.run(
            [sys.executable, str(Path(__file__).resolve()), "--_worker"],
            input=json.dumps(job), capture_output=True, text=True,
            timeout=base["timeout"], check=False,
        )
    except subprocess.TimeoutExpired as error:
        raise RuntimeError("Worker wall-clock timeout") from error
    if result.returncode != 0:
        raise RuntimeError("Worker failed (exit " + str(result.returncode) + "): " + result.stderr[-1200:])
    return json.loads(result.stdout)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--parent-external-id", required=True)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--memory-mb", type=int, default=1536)
    parser.add_argument("--worker-timeout", type=float, default=180)
    parser.add_argument("--scan-batch", type=int, default=16)
    parser.add_argument("--header-lines", type=int, default=32)
    parser.add_argument("--min-pages", type=int, default=1)
    parser.add_argument("--rule", action="append", default=[], metavar="NAME=REGEX")
    args = parser.parse_args()
    if not sys.platform.startswith("linux"):
        parser.error("Resource-controlled processing requires Linux, such as a Codespace")
    if args.memory_mb < 256 or not math.isfinite(args.worker_timeout) or args.worker_timeout <= 0:
        parser.error("Use memory-mb >= 256 and a positive finite worker-timeout")
    if min(args.scan_batch, args.header_lines, args.min_pages) < 1:
        parser.error("Batch size, header lines and min-pages must be positive")
    if not args.parent_external_id.strip():
        parser.error("Use an actual archive parent external ID")
    rules = dict(RULES)
    for custom in args.rule:
        name, separator, pattern = custom.partition("=")
        if not separator or not name.strip() or not pattern:
            parser.error("Custom rules must be NAME=REGEX")
        rules[name.strip()] = pattern
    try:
        for pattern in rules.values():
            re.compile(pattern, re.I)
    except re.error as error:
        parser.error("Invalid rule: " + str(error))
    source = args.input.expanduser().resolve(strict=True)
    if not source.is_file():
        parser.error("Input is not a file")
    requested_output = args.output.expanduser()
    if requested_output.is_symlink():
        parser.error("Output must not be a symlink")
    output = requested_output.absolute()
    if output.exists():
        parser.error("Output already exists; use a new private output directory")
    os.umask(0o077)
    output.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    before = digest(source)
    parent_bytes = source.stat().st_size
    base = {"input": str(source), "memory_mb": args.memory_mb,
            "timeout": args.worker_timeout, "rules": rules, "header_lines": args.header_lines}
    count = run_worker(base, "inspect")["pages"]
    if count < 1:
        raise ValueError("Parent contains no pages")
    audit = []
    for first in range(1, count + 1, args.scan_batch):
        last = min(count, first + args.scan_batch - 1)
        try:
            batch = run_worker(base, "scan", first=first, last=last)
        except (RuntimeError, ValueError):
            batch = [{"page": position, "text_status": "extraction_failed"}
                     for position in range(first, last + 1)]
        for entry in batch:
            if entry["text_status"] == "extraction_failed":
                try:
                    entry = run_worker(base, "scan", first=entry["page"], last=entry["page"])[0]
                    entry["retried_individually"] = True
                except (RuntimeError, ValueError):
                    entry = {"page": entry["page"], "labels": [], "page_one_marker": False,
                             "text_status": "extraction_failed", "retried_individually": True}
            audit.append(entry)
        print(f'Scanned physical pages {first}-{last}/{count}', file=sys.stderr)
    if [item["page"] for item in audit] != list(range(1, count + 1)):
        raise ValueError("Scan audit does not cover every parent page")
    starts, reasons, suppressed, previous = [1], {1: ["parent_first_page"]}, [], set()
    for entry in audit:
        position = entry["page"]
        labels = set(entry.get("labels", []))
        marker = entry.get("page_one_marker", False)
        triggers = sorted(labels) + (["printed_page_one"] if marker else [])
        if position == 1:
            reasons[1].extend(triggers)
        elif triggers:
            if labels and labels == previous and not marker:
                suppressed.append({"page": position, "reasons": triggers, "basis": "repeated_consecutive_heading"})
            elif position - starts[-1] < args.min_pages:
                suppressed.append({"page": position, "reasons": triggers, "basis": "min_pages"})
            else:
                starts.append(position)
                reasons[position] = triggers
        previous = labels
    stage = Path(tempfile.mkdtemp(prefix=".pdf-segments-", dir=output.parent))
    try:
        slug = re.sub(r"[^A-Za-z0-9_-]+", "-", args.parent_external_id).strip("-")[:80] or "parent"
        children = []
        for number, first in enumerate(starts, 1):
            last = starts[number] - 1 if number < len(starts) else count
            filename = f"{slug}_child_{number:05d}_p{first:06d}-{last:06d}.pdf"
            receipt = run_worker(base, "split", first=first, last=last, destination=str(stage / filename))
            children.append(dict(receipt, parent_external_id=args.parent_external_id,
                                 child_file_name=filename, page_start=first, page_end=last,
                                 page_count=last-first+1,
                                 page_numbering="1-based inclusive parent PDF positions",
                                 boundary_reasons=reasons[first],
                                 boundary_status="heuristic_candidate_needs_review"))
            print(f'Wrote child {number}/{len(starts)}: pages {first}-{last}', file=sys.stderr)
        if digest(source) != before:
            raise RuntimeError("Parent changed; staged derivatives discarded")
        manifest = {
            "schema_version": "209.bundle-segmentation.v1",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "parent_external_id": args.parent_external_id,
            "parent_file_name": source.name, "parent_sha256": before,
            "parent_file_size_bytes": parent_bytes, "parent_page_count": count,
            "child_count": len(children), "children": children,
            "detection": {"rules": rules, "printed_page_one_regex": PAGE_ONE,
                          "header_lines": args.header_lines, "min_pages": args.min_pages,
                          "page_audit": audit, "suppressed_candidates": suppressed},
            "resource_controls": {"sequential_workers": True, "memory_mb_per_worker": args.memory_mb,
                                  "memory_limit_kind": "RLIMIT_AS address space, not constant-memory streaming",
                                  "cpu_seconds_per_worker": math.ceil(args.worker_timeout),
                                  "wall_seconds_per_worker": args.worker_timeout,
                                  "scan_batch_pages": args.scan_batch},
            "limitations": [
                "Boundaries are heuristic candidates, not certified instrument identities.",
                "Image-only pages require separate OCR; no OCR is performed here.",
                "Extraction failures can hide boundaries; all physical pages are retained and flagged.",
                "Two instruments sharing one physical page cannot be separated by page slicing.",
                "Children are rewritten derivatives; original digital signatures are not claimed valid.",
                "pypdf may allocate substantial memory; capped workers can fail without producing output.",
                "No network, database writes, uploads, redactions or publication are performed.",
            ],
            "publication_status": "private_unreviewed",
        }
        with open(stage / "manifest.json", "x", encoding="utf-8") as target:
            json.dump(manifest, target, ensure_ascii=False, indent=2)
            target.write("\n")
        if output.exists() or output.is_symlink():
            raise FileExistsError("Output appeared during processing")
        os.rename(stage, output)
        print(json.dumps({"output": str(output), "manifest": str(output / "manifest.json"),
                          "children": len(children), "parent_sha256": before}))
    finally:
        if stage.exists():
            shutil.rmtree(stage)


if __name__ == "__main__":
    if sys.argv[1:] == ["--_worker"]:
        try:
            print(json.dumps(worker(json.load(sys.stdin))))
        except Exception as error:
            print(type(error).__name__ + ": " + str(error), file=sys.stderr)
            raise SystemExit(2)
    else:
        try:
            main()
        except (OSError, ValueError, RuntimeError) as error:
            raise SystemExit(str(error))
