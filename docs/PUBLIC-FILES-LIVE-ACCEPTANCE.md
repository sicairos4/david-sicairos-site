# Public Files live browser acceptance

The eight Public Files tables were applied to Supabase project uwidjnnhdgtrpsymuhwp and verified to exist with RLS on; all had zero rows on 2026-10-19. This batch connects public-files.html to read-only PostgREST queries using an enabled publishable key (not a service-role key). It does not seed records, publish PDFs, or authorize browser writes.

- [ ] Confirm GitHub Pages deploys the new page and script.
- [ ] Anonymous browser gets live count zero and incomplete coverage, with no account login.
- [ ] Network failures show unavailable rather than falsely asserting a zero count.
- [ ] Add a reviewed test filing in an isolated environment; ensure only visible organization/person, published filing and redaction-reviewed published document render.
- [ ] Verify withdrawn/draft rows never render or leak through API under anon and authenticated RLS.
- [ ] Verify search safely uses textContent for names and only HTTPS source links.
- [ ] Confirm publication and amendment review workflow before real intake.

The live interface is a read path. Collection of real Atwater and Merced County filings and durable reviewed document upload remain open.
