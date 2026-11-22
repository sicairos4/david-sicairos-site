/* Analytics read-only view (2026-11-21, David order).
   Reads ONLY the already-published data/analytics.json and renders it as
   plain tables. No controls, no writes, no dashboard logic, no ranges —
   the working dashboard (coordinator 6fe9bba7) owns live health, steering
   and range switches. The page re-reads the file on every load
   (`cache: no-store`) and prints the file's own generated time, so the
   number shown is always the latest published one — it cannot disagree
   with the dashboard's copy of the same file. A null figure renders as
   "—": unmeasured, not zero. */
(function () {
  'use strict';
  var $ = function (id) { return document.getElementById(id); };
  function fmt(v) {
    if (v === null || v === undefined || v === '') return '—';
    if (typeof v === 'number') return v.toLocaleString('en-US');
    return String(v);
  }
  function el(tag, text) {
    var n = document.createElement(tag);
    if (text !== undefined) n.textContent = text;
    return n;
  }
  function cell(text) { return el('td', text); }
  function link(url, label) {
    var a = document.createElement('a');
    a.href = url;
    a.textContent = label;
    a.target = '_blank';
    a.rel = 'noopener';
    return a;
  }
  function table(headers, rows) {
    var t = document.createElement('table');
    t.style.cssText = 'border-collapse:collapse;width:100%;margin:12px 0';
    var head = document.createElement('thead');
    var hr = document.createElement('tr');
    headers.forEach(function (h) {
      var th = el('th', h);
      th.style.cssText = 'text-align:left;padding:8px;border-bottom:1px solid var(--line)';
      hr.append(th);
    });
    head.append(hr);
    t.append(head);
    var body = document.createElement('tbody');
    rows.forEach(function (r) {
      var tr = document.createElement('tr');
      r.forEach(function (c) {
        var td = c && c.nodeType ? c : cell(fmt(c));
        td.style.cssText = 'padding:8px;border-bottom:1px solid var(--line);vertical-align:top';
        tr.append(td);
      });
      body.append(tr);
    });
    t.append(body);
    return t;
  }
  function fail() {
    var asof = $('analyticsAsOf');
    if (asof) asof.textContent = 'Analytics file unavailable right now — nothing is shown rather than guessing.';
    ['analytics90', 'analyticsVerified', 'analyticsChannels', 'analyticsRecs'].forEach(function (id) {
      var m = $(id);
      if (m) m.replaceChildren(el('p', '—'));
    });
  }
  function render90(p90) {
    var host = $('analytics90');
    if (!host || !p90) return;
    var win = $('analyticsWindow');
    if (win && p90.window) win.textContent = p90.window.label || '';
    var per = p90.per_platform || {};
    var keys = Object.keys(per).sort();
    if (!keys.length) { host.replaceChildren(el('p', 'No per-platform 90-day data in this file.')); return; }
    host.replaceChildren(table(
      ['Platform', 'Followers', 'Views', 'Reach', 'Likes', 'Comments'],
      keys.map(function (k) {
        var p = per[k] || {};
        return [k, fmt(p.followers), fmt(p.views), fmt(p.reach), fmt(p.likes), fmt(p.comments)];
      })
    ));
    keys.forEach(function (k) {
      var posts = (per[k] || {}).top_posts;
      if (!Array.isArray(posts) || !posts.length) return;
      host.append(el('h3', 'Top posts — ' + k));
      var ul = document.createElement('ul');
      posts.slice(0, 3).forEach(function (post) {
        var li = document.createElement('li');
        var label = (post.likes !== null && post.likes !== undefined ? post.likes + ' likes' : 'likes not measured') +
          (post.views ? ' · ' + fmt(post.views) + ' views' : '') +
          (post.note ? ' — ' + post.note : '');
        if (typeof post.url === 'string' && /^https:\/\//.test(post.url)) {
          li.append(link(post.url, 'Open post'));
          li.append(document.createTextNode(' · ' + label));
        } else {
          li.textContent = label;
        }
        ul.append(li);
      });
      host.append(ul);
    });
    if (p90.caveat) host.append(el('p', p90.caveat));
  }
  function renderVerified(v) {
    var host = $('analyticsVerified');
    if (!host || !v) return;
    var dl = document.createElement('dl');
    [['Verified in the last 24 hours', v.verified_24h],
     ['Verified in the last 7 days', v.verified_7d],
     ['Collected at', v.collected_at]].forEach(function (pair) {
      dl.append(el('dt', pair[0]));
      dl.append(el('dd', fmt(pair[1])));
    });
    host.replaceChildren(dl);
    if (Array.isArray(v.caveats) && v.caveats.length) {
      var ul = document.createElement('ul');
      v.caveats.forEach(function (c) { ul.append(el('li', String(c))); });
      host.append(ul);
    }
  }
  function renderChannels(d) {
    var host = $('analyticsChannels');
    if (!host) return;
    var meta = d.meta || {}, yt = d.youtube || {}, bh = d.beehiiv || {}, ga = d.ga4 || {};
    host.replaceChildren(table(
      ['Channel', 'Figure', 'Note'],
      [
        ['Facebook pages', fmt(meta.post_engagements_28d) + ' post engagements (28d)', fmt(meta.source)],
        ['Facebook pages', fmt(meta.followers_total_5_pages) + ' followers, 5 pages', 'Collected ' + fmt(meta.collected_at)],
        ['YouTube', fmt(yt.subscribers_last_known) + ' subscribers', 'Last known ' + fmt(yt.last_known_as_of) + ' — stale, token dead since Oct 19, 2026'],
        ['YouTube', fmt(yt.views_lifetime_last_known) + ' lifetime views', 'Last known ' + fmt(yt.last_known_as_of)],
        ['Beehiiv', fmt(bh.subscribers) + ' subscribers', fmt(bh.note)],
        ['Website (GA4)', fmt(ga.sessions_28d) + ' sessions (28d)', fmt(ga.note)]
      ]
    ));
  }
  function renderRecs(list) {
    var host = $('analyticsRecs');
    if (!host) return;
    if (!Array.isArray(list) || !list.length) {
      host.replaceChildren(el('p', 'No recommendations in this file.'));
      return;
    }
    var ol = document.createElement('ol');
    list.forEach(function (r) { ol.append(el('li', String(r))); });
    host.replaceChildren(ol);
  }
  function boot() {
    var y = $('y');
    if (y) y.textContent = String(new Date().getFullYear());
    fetch('../data/analytics.json', { credentials: 'omit', cache: 'no-store' })
      .then(function (res) { if (!res.ok) throw new Error('http ' + res.status); return res.json(); })
      .then(function (d) {
        var asof = $('analyticsAsOf');
        if (asof) asof.textContent = 'Published ' + fmt(d.generated_at_pt) + '. ' + fmt(d.freshness_note);
        render90(d.platform_90d);
        renderVerified(d.verified_publishes);
        renderChannels(d);
        renderRecs(d.recommendations);
      })
      .catch(fail);
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot, { once: true });
  else boot();
})();
