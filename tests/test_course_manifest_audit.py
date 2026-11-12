import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

spec = importlib.util.spec_from_file_location('site_audit', Path(__file__).resolve().parents[1] / 'scripts' / 'audit-static.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
HTML = '<html lang="en"><meta name="viewport" content="width=device-width"><h1 id="lesson">Lesson</h1></html>'

class CourseManifestAuditTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.su = self.root / 'sovereign-university'
        self.su.mkdir()
        (self.su / 'course-kits.html').write_text(HTML)
        (self.su / 'course-kit-templates.md').write_text('# Template')
        (self.su / 'lesson.html').write_text(HTML)
        self.data = {'entry_page': 'course-kits.html', 'blank_template_download': 'course-kit-templates.md', 'kits': [{'id': 'day', 'existing_resources': ['lesson.html#lesson']}]}
    def run_audit(self):
        (self.su / 'course-kit-manifest.json').write_text(json.dumps(self.data))
        return module.audit(self.root)
    def kinds(self):
        return [x['kind'] for x in self.run_audit()['issues']]
    def test_valid_manifest(self):
        result = self.run_audit()
        self.assertEqual(result['errors'], 0)
        self.assertEqual(result['course_manifests_checked'], 1)
    def test_missing_destination(self):
        self.data['kits'][0]['existing_resources'] = ['absent.html']
        self.assertIn('missing_local_target', self.kinds())
    def test_missing_anchor_is_warning(self):
        self.data['kits'][0]['existing_resources'] = ['lesson.html#absent']
        result = self.run_audit()
        self.assertEqual(result['errors'], 0)
        self.assertIn('anchor_not_in_static_html', [x['kind'] for x in result['issues']])
    def test_duplicate_identity(self):
        self.data['kits'].append(dict(self.data['kits'][0]))
        self.assertIn('duplicate_kit_id', self.kinds())
    def test_traversal(self):
        self.data['kits'][0]['existing_resources'] = ['../../outside.html']
        self.assertIn('outside_site_root', self.kinds())
    def test_external_not_checked(self):
        self.data['kits'][0]['existing_resources'] = ['https://example.com/external']
        self.assertEqual(self.run_audit()['errors'], 0)
    def test_optional_tool(self):
        self.data['kits'][0]['optional_tool'] = '../missing.html'
        self.assertIn('missing_local_target', self.kinds())
    def test_malformed_json(self):
        (self.su / 'course-kit-manifest.json').write_text('{')
        self.assertIn('invalid_course_manifest', [x['kind'] for x in module.audit(self.root)['issues']])
    def test_wrong_resource_shape(self):
        self.data['kits'][0]['existing_resources'] = 'lesson.html'
        self.assertIn('invalid_kit_resources', self.kinds())
    def test_existing_html_checks_retained(self):
        (self.root / 'index.html').write_text('<html><a href="missing.html">Missing</a></html>')
        kinds = self.kinds()
        self.assertIn('missing_local_target', kinds)
        self.assertIn('missing_lang', kinds)
        self.assertIn('missing_viewport', kinds)
    def test_directory_index(self):
        (self.su / 'lesson-dir').mkdir()
        (self.su / 'lesson-dir' / 'index.html').write_text(HTML)
        self.data['kits'][0]['existing_resources'] = ['lesson-dir/#lesson']
        self.assertEqual(self.run_audit()['errors'], 0)
    def test_skip_output(self):
        d = self.root / 'output'
        d.mkdir()
        (d / 'course-kit-manifest.json').write_text('{')
        self.assertEqual(self.run_audit()['course_manifests_checked'], 1)

if __name__ == '__main__':
    unittest.main()
