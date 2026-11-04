/* Official Beehiiv V3 embed. Theme variables style the host card, not iframe fields. */
(() => {
  'use strict';
  const FORM_ID = 'fc00071d-a7ff-4daf-8235-636925d9a6e6';
  const LOADER_SRC = 'https://subscribe-forms.beehiiv.com/v3/loader.js';
  const source = document.currentScript && document.currentScript.src;
  if (!source) return;
  const base = new URL('../', source);
  if (!document.getElementById('subscribe-site-theme')) {
    const style = document.createElement('style');
    style.id = 'subscribe-site-theme';
    style.textContent = `
      .subscribe-slot-ready{--signup-bg:#fffef8;--signup-line:#cfdbce;--signup-ink:#183e30;--signup-muted:#526459;--signup-accent:#174b37;--signup-detail:#92733b;--signup-radius:20px;--signup-space:clamp(16px,3vw,28px);--signup-shadow:0 12px 32px rgba(24,62,48,.07);position:relative;isolation:isolate;width:100%;max-width:720px;min-width:0;box-sizing:border-box;margin:20px 0 28px;padding:var(--signup-space);border:1px solid var(--signup-line);border-radius:var(--signup-radius);background:var(--signup-bg);box-shadow:var(--signup-shadow);color:var(--signup-ink);text-align:left;overflow-wrap:anywhere}
      .subscribe-slot-ready::before{content:'';position:absolute;top:-1px;left:20px;right:20px;height:4px;border-radius:0 0 6px 6px;background:linear-gradient(90deg,var(--signup-accent) 0%,var(--signup-accent) 72%,var(--signup-detail) 100%);pointer-events:none}
      [data-theme=midnight-ledger] .subscribe-slot-ready{--signup-bg:#1c2520;--signup-line:#415346;--signup-ink:#f3f1e7;--signup-muted:#b9c6bb;--signup-accent:#bbd7a6;--signup-detail:#c5ad76;--signup-shadow:0 12px 32px rgba(0,0,0,.16)}
      [data-theme=civic-gold] .subscribe-slot-ready{--signup-bg:#fffaf0;--signup-line:#d6c79e;--signup-ink:#302d23;--signup-muted:#655d49;--signup-accent:#655021;--signup-detail:#92733b}
      .subscribe-slot-ready .subscribe-eyebrow{margin:0 0 8px;color:var(--signup-accent);font-size:.75rem;font-weight:750;line-height:1.5;letter-spacing:.12em;text-transform:uppercase}
      .subscribe-slot-ready .subscribe-intro{margin:0 0 18px;color:var(--signup-ink);font-size:clamp(1rem,2.5vw,1.15rem);line-height:1.6;max-width:54ch}
      .subscribe-slot-ready .subscribe-form-mount{display:block;min-width:0;max-width:100%;width:100%;box-sizing:border-box}
      .subscribe-slot-ready .subscribe-form-mount iframe{display:block;max-width:100%;width:100%;box-sizing:border-box;border:0}
      .subscribe-slot-ready .subscribe-links{display:flex;flex-wrap:wrap;align-items:center;gap:12px 20px;margin:18px 0 0;padding-top:16px;border-top:1px solid var(--signup-line)}
      .subscribe-slot-ready .subscribe-reading-link{display:inline-flex;align-items:center;min-height:44px;max-width:100%;font-weight:650;font-size:.9375rem;line-height:1.5}
      .subscribe-slot-ready .subscribe-note{margin:0;font-size:.8125rem;line-height:1.6;color:var(--signup-muted);text-align:left;flex:1 1 230px}
      .subscribe-slot-ready a{color:var(--signup-accent);text-decoration:underline;text-underline-offset:3px;text-decoration-thickness:1px}
      .subscribe-slot-ready a:hover{text-decoration-thickness:2px}
      .subscribe-slot-ready a:focus-visible{outline:3px solid var(--signup-accent);outline-offset:4px;border-radius:3px}
      .subscribe-slot-ready .subscribe-error{padding:12px;border:1px solid var(--signup-line);border-radius:10px;color:var(--signup-ink);line-height:1.6}
      @media(max-width:480px){.subscribe-slot-ready{--signup-radius:14px;margin:16px 0 24px}.subscribe-slot-ready .subscribe-links{gap:8px}.subscribe-slot-ready .subscribe-note{flex-basis:100%}}
      @media(forced-colors:active){.subscribe-slot-ready{border:2px solid CanvasText;box-shadow:none}.subscribe-slot-ready::before{background:Highlight}}
      @media print{.subscribe-slot-ready{display:none!important}}
    `;
    document.head.append(style);
  }

  function renderSlot(slot) {
    if (slot.dataset.subscribeInitialized === 'true') return;
    slot.dataset.subscribeInitialized = 'true';
    slot.classList.add('subscribe-slot-ready');
    slot.replaceChildren();
    const eyebrow = document.createElement('p');
    eyebrow.className = 'subscribe-eyebrow';
    eyebrow.textContent = '209 Signal · Email briefing';
    const intro = document.createElement('p');
    intro.className = 'subscribe-intro';
    intro.textContent = 'Public records and reporting, delivered to your inbox.';
    const mount = document.createElement('div');
    mount.className = 'subscribe-form-mount';
    const links = document.createElement('div');
    links.className = 'subscribe-links';
    const reading = document.createElement('a');
    reading.className = 'subscribe-reading-link';
    reading.href = new URL('signal.html', base).href;
    reading.textContent = 'Explore the articles →';
    const help = document.createElement('p');
    help.className = 'subscribe-note';
    help.append(document.createTextNode('Form not appearing? Reload this page or '));
    const contact = document.createElement('a');
    contact.href = new URL('support.html#newsletter', base).href;
    contact.textContent = 'contact newsletter support';
    help.append(contact, document.createTextNode('.'));
    links.append(reading, help);
    slot.append(eyebrow, intro, mount, links);
    const script = document.createElement('script');
    script.async = true;
    script.src = LOADER_SRC;
    script.setAttribute('data-beehiiv-form', FORM_ID);
    script.addEventListener('error', () => {
      const message = document.createElement('p');
      message.className = 'subscribe-error';
      message.setAttribute('role', 'status');
      message.textContent = 'The signup form could not be loaded. Please reload or use the support link below. Your email has not been submitted by this page.';
      mount.append(message);
    }, { once: true });
    mount.append(script);
  }

  function init() {
    document.querySelectorAll('[data-subscribe-form]').forEach(renderSlot);
  }
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init, { once: true });
  } else {
    init();
  }
})();
