# 209 intelligence interface integration

Source: sicairos4/209-intelligent-site. Source files inspected: index.html (8ec322791d93d38ae5fa6496d0e1330f962bcf11), app.js (6f2a66a197e1dc94b7851da0793d36e3408a1bda), styles.css (c0aaeafda0c2eb2b8bfc9d337d44994a6b46d60a), data/site.json (d4e045d036afed66e521902dfafe4861ba85eb23).

The interface is imported into intelligence/interface/ as actual local HTML, CSS, JavaScript and public content, not embedded from the other repository. The source repository and existing intelligence/index.html dashboard are preserved. This is a file integration, not a Git-history merge or repository deletion.

The imported page uses ../../assets/topbar.js and links back to the dashboard, website, Working Record and persistent tool workspace. Civic-paper styling is adapted to the site's valley-light/midnight-ledger/civic-gold theme identifiers. The original source had a missing local working-record.html target and a root / brand link; both now target the main website's existing pages.

Connection badges use the main data/pipeline.json rather than copying hardcoded connected/browser_fallback claims. No new credentials, analytics writers, AI calls or background jobs are introduced. Public text renders via textContent and links are restricted to HTTP(S). Content fetches check status and time out with readable fallback messages. Lens selection is only a local preference, not personalized analytics or AI behavior.

Imported records are a content snapshot. Their original newsletter-home links are preserved and are not claimed to identify individual articles. The tracker record is routed through ../../tools.html#tracker. Private journals and member records are not included.

After this import: verify rendering and links, then separately replace the dashboard's old external full-interface link with interface/. No existing dashboard markup is overwritten by this commit. Keep the old source deployment until the integrated route is accepted. Build/publication does not prove data integrations are live.
