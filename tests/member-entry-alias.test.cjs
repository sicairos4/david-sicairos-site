'use strict';
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const html = fs.readFileSync(path.join(__dirname, '../members/workspace.html'), 'utf8');
const script = html.match(/<script>([\s\S]*?)<\/script>/)[1];
for (const suffix of ['', '?mode=signup#learn', '?source=legacy#tasks']) {
  const source = new URL('https://example.test/project/members/workspace.html' + suffix);
  const link = {};
  let redirected;
  const context = { URL, document: { getElementById(id) { assert.equal(id, 'entry'); return link; } }, location: { href: source.href, search: source.search, hash: source.hash, replace(value) { redirected = value; } } };
  vm.runInNewContext(script, context);
  const expected = new URL('../login.html', source);
  expected.search = source.search;
  expected.hash = source.hash;
  assert.equal(redirected, expected.href);
  assert.equal(link.href, expected.href);
}
console.log('Member entry alias checks passed.');
