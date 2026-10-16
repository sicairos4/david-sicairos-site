import contextlib
import datetime as dt
import io
import json
import os
import unittest
import urllib.error
from unittest.mock import patch
import importlib.util
from pathlib import Path

spec = importlib.util.spec_from_file_location('youtube_sync', Path(__file__).with_name('youtube-sync.py'))
w = importlib.util.module_from_spec(spec)
spec.loader.exec_module(w)

ID = 'QlYtvk7clgI'
SECOND = 'VhsVd3Zb7rU'

def feed(entries=None, channel=w.CHANNEL):
    if entries is None:
        entries = [(ID, '2026-10-16T12:00:00Z')]
    return ('<feed xmlns="http://www.w3.org/2005/Atom" xmlns:yt="http://www.youtube.com/xml/schemas/2015"><yt:channelId>' + channel + '</yt:channelId>' + ''.join('<entry><yt:videoId>' + i + '</yt:videoId><published>' + d + '</published></entry>' for i, d in entries) + '</feed>').encode()

def meta(video_id=ID, title='Fixture', provider='YouTube'):
    return json.dumps({'provider_name': provider, 'title': title, 'html': '<iframe src="https://www.youtube.com/embed/' + video_id + '"></iframe>'}).encode()

class CatalogTests(unittest.TestCase):
    def test_valid(self):
        with patch.object(w, 'request', side_effect=[feed(), meta()]):
            self.assertEqual(w.collect()[0]['id'], ID)
    def test_dedup(self):
        with patch.object(w, 'request', side_effect=[feed([(ID, '2026-10-16T12:00:00Z')] * 2), meta()]) as req:
            self.assertEqual(len(w.collect()), 1)
            self.assertEqual(req.call_count, 2)
    def test_channel(self):
        with patch.object(w, 'request', return_value=feed(channel='wrong')):
            with self.assertRaises(ValueError):
                w.collect()
    def test_empty(self):
        with patch.object(w, 'request', return_value=feed([])):
            with self.assertRaises(ValueError):
                w.collect()
    def test_id(self):
        with patch.object(w, 'request', return_value=feed([('bad', '2026-10-16T12:00:00Z')])):
            with self.assertRaises(ValueError):
                w.collect()
    def test_unavailable(self):
        error = urllib.error.HTTPError('fixture', 404, 'unavailable', {}, None)
        with patch.object(w, 'request', side_effect=[feed([(ID, '2026-10-16T12:00:00Z'), (SECOND, '2026-10-16T11:00:00Z')]), error, meta(SECOND)]):
            self.assertEqual(w.collect()[0]['id'], SECOND)
    def test_transient_no_write(self):
        error = urllib.error.HTTPError('fixture', 503, 'unavailable', {}, None)
        with patch.dict(os.environ, {'SUPABASE_URL': w.PROJECT, 'SUPABASE_SERVICE_KEY': 'fixture'}, clear=True), patch.object(w, 'request', side_effect=[feed(), error]) as req:
            with self.assertRaises(urllib.error.HTTPError):
                w.main()
            self.assertEqual(req.call_count, 2)
    def test_provider(self):
        with patch.object(w, 'request', side_effect=[feed(), meta(provider='Other')]):
            with self.assertRaises(ValueError):
                w.collect()
    def test_invalid_date(self):
        with self.assertRaises(ValueError):
            w.timestamp('invalid')
    def test_timezone_required(self):
        with patch.object(w, 'request', side_effect=[feed([(ID, '2026-10-16T12:00:00')]), meta()]):
            with self.assertRaises(ValueError):
                w.collect()
    def test_sort_offsets(self):
        with patch.object(w, 'request', side_effect=[feed([(ID, '2026-10-16T12:00:00+02:00'), (SECOND, '2026-10-16T11:00:00Z')]), meta(), meta(SECOND)]):
            rows = w.collect()
            self.assertEqual(rows[0]['id'], SECOND)
            self.assertTrue(all(r['published_at'].endswith('+00:00') for r in rows))
    def test_missing_credentials(self):
        with patch.dict(os.environ, {}, clear=True), patch.object(w, 'request') as req:
            with self.assertRaises(ValueError):
                w.main()
            req.assert_not_called()
    def test_wrong_project(self):
        with patch.dict(os.environ, {'SUPABASE_URL': 'https://wrong.invalid', 'SUPABASE_SERVICE_KEY': 'fixture'}, clear=True), patch.object(w, 'request') as req:
            with self.assertRaises(ValueError):
                w.main()
            req.assert_not_called()
    def test_success_expiry(self):
        with patch.dict(os.environ, {'SUPABASE_URL': w.PROJECT, 'SUPABASE_SERVICE_KEY': 'fixture'}, clear=True), patch.object(w, 'request', side_effect=[feed(), meta(), b'[{"key":"youtube_catalog"}]']) as req, contextlib.redirect_stdout(io.StringIO()) as out:
            w.main()
            self.assertEqual(json.loads(out.getvalue())['status'], 'CATALOG_STORED')
            c = json.loads(req.call_args.args[1])['value']
            self.assertEqual((dt.datetime.fromisoformat(c['expires_at']) - dt.datetime.fromisoformat(c['collected_at'])).total_seconds(), 172800)
    def test_bad_receipt(self):
        with patch.dict(os.environ, {'SUPABASE_URL': w.PROJECT, 'SUPABASE_SERVICE_KEY': 'fixture'}, clear=True), patch.object(w, 'request', side_effect=[feed(), meta(), b'[]']):
            with self.assertRaises(ValueError):
                w.main()
    def test_title_bound(self):
        with patch.object(w, 'request', side_effect=[feed(), meta(title='x' * 600)]):
            self.assertEqual(len(w.collect()[0]['title']), 500)
    def test_dry_run_no_write(self):
        with patch.dict(os.environ, {}, clear=True), patch.object(w, 'request', side_effect=[feed(), meta()]) as req, contextlib.redirect_stdout(io.StringIO()) as out:
            w.main(dry_run=True)
            self.assertEqual(json.loads(out.getvalue())['status'], 'DRY_RUN_NO_WRITE')
            self.assertEqual(req.call_count, 2)

if __name__ == '__main__':
    unittest.main(verbosity=2)
