/* On-site Beehiiv subscribe form for 209 Signal (all pages).
 *
 * SETUP — one paste, one time:
 *   In Beehiiv, open Subscribers > Subscribe forms, open the 209 Signal form,
 *   click "Get embed code" and copy the iframe src URL
 *   (it looks like https://subscribe-forms.beehiiv.com/<form-id>).
 *   Paste that URL between the quotes below.
 *
 * Every element with [data-subscribe-form] on the site then renders the
 * official Beehiiv form inline, so visitors subscribe without leaving
 * 209connect.com. Until the URL is pasted, slots render an honest on-site
 * panel that points readers to the on-site archive instead of bouncing
 * them to beehiiv.com.
 */
(() => {
  'use strict';
  const BEEHIIV_EMBED_SRC = '';
  const source = document.currentScript && document.currentScript.src;
  if (!source) return;
  const base = new URL('../', source);

  function renderSlot(slot) {
    slot.classList.add('subscribe-slot-ready');
    slot.replaceChildren();
    if (BEEHIIV_EMBED_SRC) {
      const frame = document.createElement('iframe');
      frame.src = BEEHIIV_EMBED_SRC;
      frame.title = 'Subscribe to 209 Signal by email';
      frame.setAttribute('data-test-id', 'beehiiv-embed');
      frame.setAttribute('frameborder', '0');
      frame.setAttribute('scrolling', 'no');
      frame.loading = 'lazy';
      frame.className = 'subscribe-frame';
      slot.append(frame);
      if (!document.querySelector('script[data-beehiiv-embed-js]')) {
        const s = document.createElement('script');
        s.src = 'https://subscribe-forms.beehiiv.com/embed.js';
        s.async = true;
        s.dataset.beehiivEmbedJs = 'true';
        document.head.append(s);
      }
      return;
    }
    const panel = document.createElement('div');
    panel.className = 'subscribe-panel';
    const h = document.createElement('h3');
    h.textContent = 'Get 209 Signal in your inbox';
    const p = document.createElement('p');
    p.textContent = 'One free email a week: the public records, the reporting they feed, and what happens next. No spam, unsubscribe any time.';
    const note = document.createElement('p');
    note.className = 'subscribe-note';
    note.textContent = 'The on-site signup form is being switched on right now. Until it opens, read the latest editions here on the site:';
    const a = document.createElement('a');
    a.className = 'btn';
    a.href = new URL('signal-archive.html', base).href;
    a.textContent = 'Read past editions';
    panel.append(h, p, note, a);
    slot.append(panel);
  }

  function init() {
    for (const slot of document.querySelectorAll('[data-subscribe-form]')) renderSlot(slot);
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init, { once: true });
  else init();
})();
