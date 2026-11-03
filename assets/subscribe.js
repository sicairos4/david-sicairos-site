/* Official Beehiiv V3 embed with website-owned responsive styling. */
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
      .subscribe-slot-ready{--signup-bg:#fffef8;--signup-line:#cfdbce;--signup-ink:#183e30;--signup-muted:#526459;--signup-accent:#174b37;width:100%;max-width:720px;min-width:0;box-sizing:border-box;margin:20px 0 28px;padding:clamp(12px,3vw,24px);border:1px solid var(--signup-line);border-top:4px solid var(--signup-accent);border-radius:16px;background:var(--signup-bg);color:var(--signup-ink);text-align:left;overflow-wrap:anywhere}
      [data-theme=midnight-ledger] .subscribe-slot-ready{--signup-bg:#1c2520;--signup-line:#415346;--signup-ink:#f3f1e7;--signup-muted:#b9c6bb;--signup-accent:#bbd7a6}
      [data-theme=civic-gold] .subscribe-slot-ready{--signup-bg:#fffaf0;--signup-line:#d6c79e;--signup-ink:#302d23;--signup-muted:#655d49;--signup-accent:#655021}
      .subscribe-slot-ready .subscribe-form-mount{display:block;min-width:0;max-width:100%;width:100%;box-sizing:border-box}
      .subscribe-slot-ready .subscribe-form-mount iframe{display:block;max-width:100%;box-sizing:border-box;border:0}
      .subscribe-slot-ready .subscribe-note{margin:14px 0 0;font-size:.875rem;line-height:1.6;color:var(--signup-muted);text-align:left}
      .subscribe-slot-ready .subscribe-note a{color:var(--signup-accent);text-decoration:underline;text-underline-offset:3px}
      .subscribe-slot-ready a:focus-visible{outline:3px solid var(--signup-accent);outline-offset:4px;border-radius:3px}
      .subscribe-slot-ready .subscribe-error{padding:12px;border:1px solid var(--signup-line);border-radius:10px;color:var(--signup-ink);line-height:1.6}
      @media(max-width:480px){.subscribe-slot-ready{margin:16px 0 24px;border-radius:12px;padding:12px}.subscribe-slot-ready .subscribe-note{font-size:.8125rem}}
      @media print{.subscribe-slot-ready{display:none!important}}
    `;
    document.head.append(style);
  }

  function renderSlot(slot) {
    if (slot.dataset.subscribeInitialized === 'true') return;
    slot.dataset.subscribeInitialized = 'true';
    slot.classList.add('subscribe-slot-ready');
    slot.replaceChildren();
    const mount = document.createElement('div');
    mount.className = 'subscribe-form-mount';
    const help = document.createElement('p');
    help.className = 'subscribe-note';
    help.append(document.createTextNode('If the form does not appear, reload this page or '));
    const contact = document.createElement('a');
    contact.href = new URL('support.html#newsletter', base).href;
    contact.textContent = 'contact newsletter support';
    help.append(contact, document.createTextNode('.'));
    slot.append(mount, help);
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
