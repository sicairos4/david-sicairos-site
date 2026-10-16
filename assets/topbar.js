/* 209 shared toolbar — desktop nav + plain full-screen mobile overlay */
(() => {
  const script = document.currentScript;
  const base = new URL('../', script && script.src ? script.src : new URL('assets/topbar.js', location.href));
  const subscribe = 'https://209connect.beehiiv.com/?modal=signup';

  function ready() {
    const header = document.querySelector('header.top');
    if (!header || header.dataset.toolbarReady) return;
    const row = header.querySelector('.top-in');
    const nav = header.querySelector('.nav');
    if (!row || !nav) return;
    header.dataset.toolbarReady = 'true';
    header.classList.add('site-toolbar');

    const style = document.createElement('style');
    style.textContent = `
.site-toolbar{position:sticky;top:0;z-index:1000;background:var(--bg,#fff);color:var(--text,#183e30)}
.site-toolbar .top-in{position:relative;display:flex;align-items:center;justify-content:space-between;gap:10px;min-height:56px}
.site-toolbar .nav{display:flex;align-items:center;gap:4px;flex:1;min-width:0}
.site-toolbar .nav-left,.site-toolbar .nav-right{display:flex;align-items:center;gap:4px}
.site-toolbar .nav-right{margin-left:auto}
.site-toolbar .nav-left>a,.site-toolbar .nav-group>button{font:inherit;font-size:13px;color:inherit;background:transparent;border:0;border-radius:8px;min-height:40px;padding:8px;text-decoration:none;white-space:nowrap;cursor:pointer}
.site-toolbar .nav-group{position:relative}
.site-toolbar .dropdown{display:none;position:absolute;top:100%;left:0;min-width:210px;max-height:70vh;overflow:auto;padding:8px;background:var(--panel,#fff);border:1px solid var(--line,#dfe7e1);border-radius:10px;z-index:1001}
.site-toolbar .nav-group.open>.dropdown{display:block}
.site-toolbar .dropdown a{display:block;min-height:40px;padding:8px 10px;color:inherit;text-decoration:none;white-space:normal}
.site-toolbar .nav-burger{display:none;border:1px solid var(--line,#b8c8bf);background:var(--panel,#fff);color:inherit;border-radius:8px;width:44px;min-width:44px;height:44px;padding:0;font-size:22px;cursor:pointer}
.site-toolbar .theme-toggle{display:inline-flex;align-items:center;justify-content:center;width:40px;min-width:40px;height:40px;padding:0;color:inherit;background:var(--panel,#fff);border:1px solid var(--line,#b8c8bf);border-radius:8px;cursor:pointer}
.site-toolbar .theme-dot{width:14px;height:14px;border-radius:50%;background:#175c42;box-shadow:0 0 0 2px #fff inset}
.site-toolbar .nav-cta{display:inline-flex;align-items:center;justify-content:center;min-height:40px;padding:8px 12px;background:var(--accent,#175c42);color:#fff!important;border-radius:8px;text-decoration:none;font-size:13px}
.site-toolbar [aria-current=page]{text-decoration:underline;font-weight:700}
.site-toolbar :focus-visible{outline:3px solid #2786c6;outline-offset:3px}
/* --- Plain full-screen mobile overlay --- */
#mobile-menu{position:fixed;inset:0;top:52px;background:var(--bg,#fff);color:var(--text,#183e30);z-index:2000;display:none;flex-direction:column;overflow-y:auto;-webkit-overflow-scrolling:touch;padding:16px 16px calc(20px + env(safe-area-inset-bottom))}
#mobile-menu.open{display:flex}
#mobile-menu .mm-group{width:100%}
#mobile-menu .mm-group>button{display:flex;align-items:center;justify-content:space-between;width:100%;min-height:48px;padding:12px 10px;font:inherit;font-size:16px;text-align:left;color:inherit;background:transparent;border:0;border-radius:8px;cursor:pointer;touch-action:manipulation}
#mobile-menu .mm-group>button:hover{background:color-mix(in srgb,var(--accent,#175c42) 10%,transparent)}
#mobile-menu .mm-dropdown{display:none;width:100%;padding:2px 0 8px 14px;border-left:2px solid var(--line,#dfe7e1)}
#mobile-menu .mm-group.open .mm-dropdown{display:block}
#mobile-menu a{display:flex;align-items:center;min-height:48px;padding:10px 8px;font-size:16px;color:inherit;text-decoration:none;touch-action:manipulation}
#mobile-menu .mm-cta{display:flex;align-items:center;justify-content:center;min-height:48px;margin-top:16px;padding:12px 16px;background:var(--accent,#175c42);color:#fff!important;border-radius:10px;font-size:16px;text-decoration:none}
#mobile-menu .mm-theme{display:flex;align-items:center;justify-content:center;min-height:48px;margin-top:10px;padding:12px 16px;border:1px solid var(--line,#b8c8bf);border-radius:10px;background:var(--panel,#fff);color:inherit;font:inherit;font-size:15px;cursor:pointer}
@media(max-width:1100px){
  .site-toolbar .nav-burger{display:inline-flex!important;align-items:center;justify-content:center;order:2;margin-left:auto}
  .site-toolbar .nav{display:none!important}
}
@media(min-width:1101px){#mobile-menu{display:none!important}}
`;
    document.head.append(style);

    function link(label, path, parent) {
      const a = document.createElement('a');
      a.textContent = label;
      a.href = new URL(path, base).href;
      parent.append(a);
      return a;
    }

    nav.replaceChildren();
    nav.id = 'site-primary-navigation';
    nav.setAttribute('aria-label', 'Main navigation');
    const left = document.createElement('div');
    left.className = 'nav-left';
    nav.append(left);
    link('Home', 'index.html', left);

    const groups = [];
    function group(label, items) {
      const g = document.createElement('div');
      g.className = 'nav-group';
      const b = document.createElement('button');
      b.type = 'button';
      b.textContent = label + ' \u25BE';
      b.setAttribute('aria-expanded', 'false');
      const panel = document.createElement('div');
      panel.className = 'dropdown';
      panel.id = 'menu-' + label.toLowerCase().replace(/\W+/g, '-');
      b.setAttribute('aria-controls', panel.id);
      items.forEach(([text, path]) => link(text, path, panel));
      g.append(b, panel);
      left.append(g);
      b.onclick = () => {
        const open = !g.classList.contains('open');
        closeGroups();
        g.classList.toggle('open', open);
        b.setAttribute('aria-expanded', String(open));
      };
      groups.push([label, items]);
    }
    function closeGroups() {
      nav.querySelectorAll('.nav-group').forEach(g => {
        g.classList.remove('open');
        g.querySelector('button').setAttribute('aria-expanded', 'false');
      });
    }

    group('209 Media', [['209 Audit', '209-audit.html'], ['209 Signal', 'signal.html'], ['209 Intelligence', 'intelligence/'], ['How It Connects', 'how-it-connects.html'], ['Multimedia', 'multimedia/'], ['Media Library', 'library.html']]);
    group('209 Connect', [['209 Connect Studio', 'studio.html'], ['Resume Builder', 'resume-builder.html'], ['Business Builder Generator', 'studio.html#generator'], ['Personal Branding', 'sovereign-university/pathways.html#personal-brand'], ['Sovereign University', 'sovereign-university/experience.html']]);
    group('209 Tools', [['Master Tracker', 'index-tracker/'], ['CPRA Playbook', 'cpra-playbook/'], ['Public Records', 'public-files.html'], ['Start With AI', 'sovereign-university/pathways.html#ai-setup']]);
    group('dBeastco', [['Wellness', 'dbeastco.html'], ['Realignment Room', 'aura.html#realignment'], ['Lifestyle ID', 'aura.html']]);
    link('Support 209', 'donations.html', left);
    link('Store', 'store.html', left);
    link('Workspace', 'login.html', left);

    const right = document.createElement('div');
    right.className = 'nav-right';
    const theme = document.createElement('button');
    theme.type = 'button';
    theme.id = 'themeToggle';
    theme.className = 'theme-toggle';
    theme.innerHTML = '<span class="theme-dot"></span>';
    theme.setAttribute('aria-label', 'Change color theme');
    const themes = ['valley-light', 'midnight-ledger', 'civic-gold'];
    theme.onclick = () => {
      const current = document.documentElement.dataset.theme || 'valley-light';
      const idx = themes.indexOf(current);
      const next = themes[(idx + 1) % themes.length];
      document.documentElement.dataset.theme = next;
      const dot = theme.querySelector('.theme-dot');
      if (dot) dot.style.background = next === 'valley-light' ? '#175c42' : next === 'midnight-ledger' ? '#1a1a2e' : '#b8860b';
      try { localStorage.setItem('209-theme', next); } catch {}
    };
    const dot = theme.querySelector('.theme-dot');
    if (dot) dot.style.background = '#175c42';
    right.append(theme);
    const c = document.createElement('a');
    c.href = subscribe;
    c.target = '_blank';
    c.rel = 'noopener';
    c.className = 'nav-cta';
    c.textContent = 'Subscribe';
    right.append(c);
    nav.append(right);

    /* --- Plain mobile overlay --- */
    const overlay = document.createElement('div');
    overlay.id = 'mobile-menu';
    overlay.setAttribute('role', 'dialog');
    overlay.setAttribute('aria-modal', 'true');
    overlay.setAttribute('aria-label', 'Mobile navigation');
    groups.forEach(([label, items]) => {
      const g = document.createElement('div');
      g.className = 'mm-group';
      const b = document.createElement('button');
      b.type = 'button';
      b.textContent = label + ' \u25BE';
      b.setAttribute('aria-expanded', 'false');
      const panel = document.createElement('div');
      panel.className = 'mm-dropdown';
      items.forEach(([text, path]) => link(text, path, panel));
      b.onclick = () => {
        const open = !g.classList.contains('open');
        overlay.querySelectorAll('.mm-group').forEach(x => x.classList.remove('open'));
        g.classList.toggle('open', open);
        b.setAttribute('aria-expanded', String(open));
      };
      g.append(b, panel);
      overlay.append(g);
    });
    link('Support 209', 'donations.html', overlay);
    link('Store', 'store.html', overlay);
    link('Workspace', 'login.html', overlay);
    const mTheme = document.createElement('button');
    mTheme.type = 'button';
    mTheme.className = 'mm-theme';
    mTheme.textContent = '\u25D1 Change color theme';
    mTheme.onclick = () => theme.click();
    overlay.append(mTheme);
    const mCta = document.createElement('a');
    mCta.href = subscribe;
    mCta.target = '_blank';
    mCta.rel = 'noopener';
    mCta.className = 'mm-cta';
    mCta.textContent = 'Subscribe Free';
    overlay.append(mCta);
    document.body.append(overlay);

    const burger = document.createElement('button');
    burger.type = 'button';
    burger.className = 'nav-burger';
    burger.textContent = '\u2630';
    burger.setAttribute('aria-controls', 'mobile-menu');
    burger.setAttribute('aria-expanded', 'false');
    burger.setAttribute('aria-label', 'Open navigation');
    row.append(burger);

    const mq = matchMedia('(max-width:1100px)');
    let overflow = '';
    function setOpen(open) {
      open = open && mq.matches;
      overlay.classList.toggle('open', open);
      burger.setAttribute('aria-expanded', String(open));
      burger.setAttribute('aria-label', open ? 'Close navigation' : 'Open navigation');
      burger.textContent = open ? '\u00D7' : '\u2630';
      if (open) {
        overflow = document.body.style.overflow;
        document.body.style.overflow = 'hidden';
      } else {
        document.body.style.overflow = overflow;
        overlay.querySelectorAll('.mm-group').forEach(x => x.classList.remove('open'));
      }
    }
    burger.onclick = () => setOpen(!overlay.classList.contains('open'));
    overlay.addEventListener('click', e => { if (e.target.closest('a')) setOpen(false); });
    document.addEventListener('click', e => {
      if (!header.contains(e.target) && !overlay.contains(e.target) && overlay.classList.contains('open')) setOpen(false);
    });
    document.addEventListener('keydown', e => { if (e.key === 'Escape') setOpen(false); });
    mq.addEventListener('change', () => setOpen(false));

    const normal = p => p.replace(/index\.html$/, '').replace(/\/$/, '');
    nav.querySelectorAll('a').forEach(a => {
      const u = new URL(a.href);
      if (u.origin === location.origin && !u.hash && normal(u.pathname) === normal(location.pathname)) a.setAttribute('aria-current', 'page');
    });
    const brand = header.querySelector('.brand');
    if (brand) brand.href = new URL('index.html', base).href;
    if (!document.head.querySelector('link[rel="icon"]')) {
      const f = document.createElement('link');
      f.rel = 'icon';
      f.type = 'image/svg+xml';
      f.href = new URL('favicon.svg', base).href;
      document.head.append(f);
    }
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', ready, { once: true });
  else ready();
})();