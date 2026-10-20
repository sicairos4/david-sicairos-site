import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
import zipfile

SPEC = importlib.util.spec_from_file_location("publisher", Path(__file__).resolve().parents[1] / "scripts" / "prepare_android_preview.py")
MOD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MOD)
SHA = "a" * 40

class PreviewValidation(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.source = self.root / "source"
        self.source.mkdir()
        self.output = self.root / "ready"
        self.apk = self.source / ("209-workstation-debug-" + SHA[:12] + ".apk")
        with zipfile.ZipFile(self.apk, "w") as z:
            z.writestr("AndroidManifest.xml", "fixture-not-a-real-manifest")
            z.writestr("classes.dex", "fixture-not-real-dex")
        self.receipt = {"source_sha": SHA, "run_url": "https://github.com/sicairos4/david-sicairos-site/actions/runs/123", "version_name": "0.3.4", "version_code": 7, "variant": "debug", "application_id": "com.sicairos.workstation.debug", "production_signed": False, "device_install_verified": False}
        self.write_receipt()
        self.write_sum()
    def tearDown(self): self.temp.cleanup()
    def write_receipt(self): (self.source / "build-receipt.json").write_text(json.dumps(self.receipt))
    def write_sum(self): (self.source / "SHA256SUMS.txt").write_text(hashlib.sha256(self.apk.read_bytes()).hexdigest() + "  " + self.apk.name + "\n")
    def reject(self):
        with self.assertRaises((ValueError, zipfile.BadZipFile)):
            MOD.prepare(self.source, self.output, SHA)
        self.assertFalse(self.output.exists())
    def test_valid_and_no_unknown_receipt_fields_published(self):
        self.receipt["private_extra"] = "must not publish"
        self.write_receipt()
        result = MOD.prepare(self.source, self.output, SHA)
        self.assertTrue((self.output / MOD.ASSET).is_file())
        self.assertNotIn("private_extra", result)
        self.assertFalse(result["production_signed"])
    def test_wrong_source(self): self.receipt["source_sha"] = "b" * 40; self.write_receipt(); self.reject()
    def test_checksum_mismatch(self): self.apk.write_bytes(b"tampered"); self.reject()
    def test_production_claim(self): self.receipt["production_signed"] = True; self.write_receipt(); self.reject()
    def test_wrong_account_application(self): self.receipt["application_id"] = "other.app"; self.write_receipt(); self.reject()
    def test_wrong_run_origin(self): self.receipt["run_url"] = "https://evil.example/runs/123"; self.write_receipt(); self.reject()
    def test_invalid_version(self): self.receipt["version_name"] = "version\nInjected"; self.write_receipt(); self.reject()
    def test_multiple_apks(self): (self.source / "extra.apk").write_bytes(b"extra"); self.reject()
    def test_missing_android_entries(self):
        with zipfile.ZipFile(self.apk, "w") as z: z.writestr("unrelated.txt", "x")
        self.write_sum(); self.reject()
    def test_wrong_trigger_run(self):
        with self.assertRaises(ValueError): MOD.prepare(self.source, self.output, SHA, "456")
        self.assertFalse(self.output.exists())
    def test_bad_sha_argument(self):
        with self.assertRaises(ValueError): MOD.prepare(self.source, self.output, "not-a-sha")

if __name__ == "__main__": unittest.main()
