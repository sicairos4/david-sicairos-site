import datetime as dt
import json
import os
import re
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

CHANNEL = 'UCDMa9oEWj4i6KFOkjF79qLg'
PROJECT = 'https://uwidjnnhdgtrpsymuhwp.supabase.co'
NS = {'a': 'http://www.w3.org/2005/Atom', 'yt': 'http://www.youtube.com/xml/schemas/2015'}

def request(url, data=None, headers=None):
    req = urllib.request.Request(url, data=data, headers={'User-Agent': '209ConnectCatalog/1.0', **(headers or {})})
    with urllib.request.urlopen(req, timeout=25) as response:
        return response.read()

def collect():
    feed = ET.fromstring(request('https://www.youtube.com/feeds/videos.xml?channel_id=' + CHANNEL))
    if feed.findtext('yt:channelId', namespaces=NS) != CHANNEL:
        raise ValueError('Unexpected channel feed')
    entries = feed.findall('a:entry', NS)
    if not entries:
        raise ValueError('Empty feed; retaining prior catalog')
    videos, seen = [], set()
    for entry in entries[:15]:
        video_id = entry.findtext('yt:videoId', namespaces=NS) or ''
        if not re.fullmatch(r'[A-Za-z0-9_-]{11}', video_id):
            raise ValueError('Invalid video ID')
        if video_id in seen:
            continue
        seen.add(video_id)
        endpoint = 'https://www.youtube.com/oembed?' + urllib.parse.urlencode({'url': 'https://www.youtube.com/watch?v=' + video_id, 'format': 'json'})
        try:
            meta = json.loads(request(endpoint))
        except urllib.error.HTTPError as error:
            if error.code in (401, 403, 404, 410):
                continue
            raise
        if meta.get('provider_name') != 'YouTube' or ('/embed/' + video_id) not in meta.get('html', ''):
            raise ValueError('Unexpected oEmbed response')
        title = meta.get('title')
        if not isinstance(title, str) or not title.strip():
            raise ValueError('Missing title')
        published = entry.findtext('a:published', namespaces=NS)
        dt.datetime.fromisoformat(published.replace('Z', '+00:00'))
        videos.append({'id': video_id, 'title': title[:500], 'published_at': published, 'thumbnail': 'https://i.ytimg.com/vi/' + video_id + '/hqdefault.jpg', 'availability_check': 'public_feed_and_oembed_not_runtime_playback'})
    if not videos:
        raise ValueError('No usable videos; retaining prior catalog')
    videos.sort(key=lambda v: v['published_at'], reverse=True)
    return videos

def main():
    url = os.environ.get('SUPABASE_URL', '').rstrip('/')
    key = os.environ.get('SUPABASE_SERVICE_KEY', '')
    if url != PROJECT or not key:
        raise ValueError('Missing credentials or unexpected project')
    videos = collect()
    now = dt.datetime.now(dt.timezone.utc)
    catalog = {'version': 1, 'channel_id': CHANNEL, 'source': 'YouTube public upload feed and oEmbed', 'collected_at': now.isoformat(), 'expires_at': (now + dt.timedelta(hours=48)).isoformat(), 'videos': videos}
    payload = json.dumps({'key': 'youtube_catalog', 'value': catalog, 'updated_at': now.isoformat()}).encode()
    receipt = json.loads(request(url + '/rest/v1/site_content?on_conflict=key&select=key', payload, {'apikey': key, 'Authorization': 'Bearer ' + key, 'Content-Type': 'application/json', 'Prefer': 'resolution=merge-duplicates,return=representation'}))
    if not isinstance(receipt, list) or len(receipt) != 1 or receipt[0].get('key') != 'youtube_catalog':
        raise ValueError('Catalog write receipt missing')
    print(json.dumps({'status': 'CATALOG_STORED', 'video_count': len(videos), 'collected_at': catalog['collected_at']}))

if __name__ == '__main__':
    try:
        main()
    except Exception as error:
        print('YouTube sync failed; previous catalog retained. Error type: ' + type(error).__name__)
        raise SystemExit(1)
