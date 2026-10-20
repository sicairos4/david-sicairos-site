"""Validate trusted Android CI output before preparing public preview assets."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import zipfile

REPO = "sicairos4/david-sicairos-site"
ASSET = "209-workstation-preview.apk"

def prepare(source, output, expected_sha, expected_run_id=None):
    source, output = Path(source), Path(output)
    if not re.fullmatch(r"[0-9a-f]{40}", expected_sha):
        raise ValueError("Invalid expected source SHA")
    if source.resolve() == output.resolve() or output.is_symlink():
        raise ValueError("Output must be a separate, non-symlink directory")
    receipt_path = source / "build-receipt.json"
    if receipt_path.is_symlink() or receipt_path.stat().st_size > 65536:
        raise ValueError("Invalid receipt file")
    raw = json.loads(receipt_path.read_text())
    if raw.get("source_sha") != expected_sha:
        raise ValueError("Receipt source does not match the triggering build")
    if not re.fullmatch(r"https://github\.com/" + re.escape(REPO) + r"/actions/runs/[0-9]+", str(raw.get("run_url", ""))):
        raise ValueError("Unexpected build URL")
    if expected_run_id is not None and (not str(expected_run_id).isdigit() or raw.get("run_url") != "https://github.com/" + REPO + "/actions/runs/" + str(expected_run_id)):
        raise ValueError("Receipt does not match the triggering workflow run")
    if raw.get("variant") != "debug" or raw.get("application_id") != "com.sicairos.workstation.debug":
        raise ValueError("Unexpected application or variant")
    if raw.get("production_signed") is not False or raw.get("device_install_verified") is not False:
        raise ValueError("Preview receipt must not claim production signing or device acceptance")
    version = raw.get("version_name")
    if not isinstance(version, str) or not re.fullmatch(r"[A-Za-z0-9.+-]{1,64}", version):
        raise ValueError("Invalid version name")
    code = raw.get("version_code")
    if type(code) is not int or code < 1:
        raise ValueError("Invalid version code")
    apks = list(source.glob("*.apk"))
    expected_name = "209-workstation-debug-" + expected_sha[:12] + ".apk"
    if len(apks) != 1 or apks[0].name != expected_name or apks[0].is_symlink():
        raise ValueError("Expected exactly one source-named APK")
    apk = apks[0]
    if not 0 < apk.stat().st_size <= 200 * 1024 * 1024:
        raise ValueError("Unexpected APK size")
    sums = source / "SHA256SUMS.txt"
    if sums.is_symlink() or sums.stat().st_size > 4096:
        raise ValueError("Invalid checksum file")
    match = re.fullmatch(r"([0-9a-f]{64})[ \t]+\*?" + re.escape(expected_name) + r"\s*", sums.read_text())
    with apk.open("rb") as handle:
        digest = hashlib.file_digest(handle, "sha256").hexdigest()
    if not match or match.group(1) != digest:
        raise ValueError("APK checksum mismatch")
    with zipfile.ZipFile(apk) as archive:
        if not {"AndroidManifest.xml", "classes.dex"}.issubset(archive.namelist()):
            raise ValueError("APK does not contain expected Android entries")
    receipt = {key: raw[key] for key in ["source_sha", "run_url", "version_name", "version_code", "variant", "application_id", "production_signed", "device_install_verified"]}
    receipt["artifact_sha256"] = digest
    receipt["delivery_channel"] = "public-debug-preview"
    output.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(apk, output / ASSET)
    (output / "SHA256SUMS.txt").write_text(digest + "  " + ASSET + "\n")
    (output / "build-receipt.json").write_text(json.dumps(receipt, indent=2) + "\n")
    notes = ("209 Workstation Android preview " + version + " (" + str(code) + ")\n\n"
             "Source: " + expected_sha + "\nBuild: " + receipt["run_url"] + "\n\n"
             "DEBUG TEST BUILD. Not production signed; device installation and login have not been verified. "
             "Debug signing identity can differ across builds, so updates are not guaranteed to install over an earlier preview. "
             "This delivery pipeline does not convert the current browser-backed app into a native app. "
             "Keep SHA256SUMS.txt and build-receipt.json with the download.\n")
    (output / "INSTALL.txt").write_text(notes)
    return receipt

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--expected-sha", required=True)
    parser.add_argument("--expected-run-id", required=True)
    args = parser.parse_args()
    receipt = prepare(args.source, args.output, args.expected_sha, args.expected_run_id)
    print(json.dumps({"status": "validated", "source_sha": receipt["source_sha"], "version": receipt["version_name"]}))
