/* Official Beehiiv V3 embed for existing on-site signup slots. */
(() => {
  'use strict';
  const FORM_ID = 'fc00071d-a7ff-4daf-8235-636925d9a6e6';
  const LOADER_SRC = 'https://subscribe-forms.beehiiv.com/v3/loader.js';
  const source = document.currentScript && document.currentScript.src;
  if (!source) return;
  const base = new URL('../', source);

  function renderSlot(slot) {
    if (slot.dataset.subscribeInitialized === 'true') return;
    slot.dataset.subscribeInitialized = 'true';
    slot.classList.add('subscribe-slot-ready');
    slot.replaceChildren();
    const mount = document.createElement('div');
    mount.className = 'subscribe-form-mount';
    mount.style.minWidth = '0';
    mount.style.maxWidth = '100%';
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
