# Site-flow corrections: first batch

Prepared against ea313563de068dc95c9be8143a1b5d8a9d08f352. Source changes only. No tests, browser/device checks, backend migration, payments, publication or production build are performed by this batch. Existing workflows are unchanged. Homepage and shared toolbar files are untouched; the removed homepage Workstation card is not reintroduced.

## Changes

- studio.html: generator section uses #generator for existing toolbar, store and pathway links; #idea remains as a compatibility anchor at the same section. #store is a compatibility anchor inside the existing #services section. No new store, generator or service backend is created.
- sovereign-university.html: replace the generic Drive-root Start Free Course button with the actual planning.html#morning worksheet and accurately label it. Catalog introduction/search copy distinguish resources from enrollment/completion. The Public Files footer links directly to public-files.html. The credentials card leads to the actual guide and does not claim verification.
- sovereign-university/experience.html: generator replaces result children and creates its heading/paragraphs with DOM nodes and textContent/createTextNode. Entered interest, skills and audience are not interpreted as HTML. Existing result labels and formatting remain; whitespace-only entries receive a text prompt. No AI service or persistence is added.
- aura.html: credentials action goes to credentials.html, not a nonexistent University fragment, and describes the destination as a guide.
- credentials.html: retain the layout and existing anchor IDs, but distinguish a planning guide/badge concepts from a working verification, award or public-profile service. Next actions reach the existing resume builder, actual starter pathways and the valid Lifestyle ID credentials section.

## Not completed by this batch

Other older catalog cards still lead to broader topic pages; dedicated lessons, the Wellness/University loop, original course assets, learning return links, generator-output retention, newsletter consolidation, canonical-domain/sitemap cleanup and authenticated completion remain later work. This patch does not claim whole-site continuity or a complete security audit. It does not alter private data, account identities, provider destinations or payment configuration.
