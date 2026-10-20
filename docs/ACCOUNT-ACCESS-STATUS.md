# Account access and next build work

Updated 2026-10-20. Product: 209. Connect Workspace; dashboard: Workstation.

## User-reported done
- Custom-domain/DNS cleanup and domain/HTTPS item.
- New-domain Google sign-in item.
These are user confirmations, not independent end-to-end test receipts.

## This source batch
- Eight-character frontend minimum across signup, recovery and signed-in password settings. Existing passwords are not changed. Backend strength rules still apply.
- Specific safe error messages for common signup/email/provider/password/rate-limit failures; raw server messages are not rendered.
- Explicit progress states, signup confirmation resend, one-minute per-browser email-request cooldown, and password visibility controls.
- Reuse the member account client for password updates rather than creating another client.
- Add tests/auth-access.test.cjs. Run node --test tests/auth-access.test.cjs. Tests are authored, not asserted passed by this document.

## Still required before closing signup
- Inspect Supabase Auth configuration: email signup enabled, backend password minimum, confirmation enabled, actual SMTP/email-hook configuration and allowed redirects. No server policy is changed in this batch.
- Built-in Supabase SMTP is not a production public-signup delivery service. Configure a verified transactional sender if required; do not disable confirmation to conceal delivery failures.
- Verify sender-domain DNS using provider-issued records. Preserve existing mail and verification records. Do not publish SMTP passwords or tokens.
- Confirm links return to https://209connect.com/members/app.html for signup and https://209connect.com/recover.html for recovery. Preserve old destinations until testing succeeds.
- Complete new-address signup, confirmation delivery, confirmation click, sign-in, resend, expired-link recovery, password update, sign-out and two-account isolation acceptance.
- Frontend cooldown does not replace server rate limits. Provider acceptance is not proof of inbox delivery.

## Remaining next batch
1. Task-to-schedule prefill and explicit timeline/editor destinations.
2. Consistent save/error/unsaved-change handling and day-switch acceptance.
3. Current APK build/install/signing evidence, mobile sizing and navigation.
4. Full-account backup/restore and verified deletion/retention process.
5. Muse runtime discovery, scoped read-only health/status tools, proposal approval and execution receipts.
6. Remaining store/learning delivery and real Public Files collection.

Domain and Google sign-in completion does not close email signup, SMTP, Google branding approval, APK installation or data-isolation testing. No live email was sent or account created by this source batch.
