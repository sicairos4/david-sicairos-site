const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const root = path.resolve(__dirname, '..');
const read = name => fs.readFileSync(path.join(root, name), 'utf8');
const auth = read('assets/workstation-auth.js');
const planner = read('assets/connect-app.js');

test('login and planner use the same intended Supabase project and public key', () => {
  const extract = source => {
    const match = source.match(/createClient\(\s*['"]([^'"]+)['"]\s*,\s*['"]([^'"]+)['"]/);
    assert.ok(match, 'Expected an inspectable account client configuration');
    return match.slice(1, 3);
  };
  const a = extract(auth);
  const b = extract(planner);
  assert.equal(a[0], 'https://uwidjnnhdgtrpsymuhwp.supabase.co');
  assert.ok(a[1].startsWith('sb_publishable_'), 'Expected a publishable browser key');
  assert.ok(a[0] === b[0] && a[1] === b[1], 'Login and planner account configuration differs');
});

test('authentication actions retain the Workstation and recovery return contracts', () => {
  assert.ok(auth.includes("new URL('members/app.html',base)"), 'Account actions must return to the current planner');
  assert.ok(auth.includes("new URL('recover.html',base)"));
  assert.match(auth, /provider:\s*['"]google['"]/);
  assert.match(auth, /redirectTo:\s*home/);
  assert.match(auth, /emailRedirectTo:\s*home/);
  assert.match(auth, /resetPasswordForEmail[\s\S]*redirectTo:\s*reset/);
  assert.match(auth, /signInWithPassword\(credentials\)/);
  assert.doesNotMatch(auth, /https?:\/\/[^'"\s]*(?:lovable\.app|lovableproject\.com)/i);
});

test('account library loads before the consuming controller on all auth entries', () => {
  for (const [file, controller] of [
    ['login.html', 'assets/workstation-auth.js'],
    ['recover.html', 'assets/workstation-auth.js'],
    ['members/workstation.html', '../assets/workstation-auth.js'],
    ['members/app.html', '../assets/connect-app.js']
  ]) {
    const html = read(file);
    const sdk = html.indexOf('@supabase/supabase-js@2');
    const consumer = html.indexOf(controller);
    assert.ok(sdk >= 0 && consumer > sdk, `${file}: account SDK must precede controller`);
  }
});

// Source contracts only: these tests cannot verify dashboard settings, email
// delivery, live credentials, deployed content, or Android OAuth return.
