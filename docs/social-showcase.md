# Across the 209: display-only social showcase

Public page: social.html. This page has no publisher controls, private queue data, credentials or account mutations. The independent publishing repository and its workflows are not modified by this collection job.

Inputs: data/social-feed.json (existing published ledger export and selected videos), data/social-showcase.json (account directory, curated entries and public collections), data/newsletters.json (eligible imported Signal editions). Existing feed data and profile groups are retained.

New collector requests up to 30 public author-feed entries from davidsicairos.bsky.social, retaining up to 12 original non-reply/non-repost posts. YouTube uses the public Atom upload feed for channel UCDMa9oEWj4i6KFOkjF79qLg and retains the entries that source returns. These are recent collections, not complete archives. No new posting or platform API credentials are required for those public requests.

The collector replaces only its own public_bluesky/public_youtube entries, preserving other curated posts and the profile directory. If one collection fails, its previous entries remain; if both fail, the existing file is untouched. Source failures are recorded without inventing posts or resetting existing entries to zero.

Refresh configured every 30 minutes and on installation. Successful fetching, deployment and embedding are not asserted by committing this workflow. No tests or verification jobs are run. Existing repository workflows may still run on pushes.

Facebook, Instagram, Threads, LinkedIn, TikTok and X are not automatically discovered by this public collector. Their existing ledger entries or curated post URLs can appear in the same wall. Profile URLs alone do not create a post feed. Native embed availability depends on the specific public post and platform restrictions. LinkedIn requires a supplied compatible embed_url; otherwise its original-post link remains available. No guessed handles or substitute artwork are added.
