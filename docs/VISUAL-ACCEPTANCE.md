# Responsive interface and release acceptance

This batch styles the Workstation panel widths, seven-column month browser, task/step rows and review preview, plus Public Files organization/results cards. It changes layout only; no save, authentication or database behavior. CSS source is not a visual acceptance pass.

- [ ] Verify the styles appear on the deployed members/app.html and public-files.html pages.
- [ ] Check 320, 360, 390, 600, 768 and 1280 CSS-pixel widths for horizontal overflow and clipped controls.
- [ ] Confirm month buttons remain 44px tall; test keyboard focus, screen-reader labels and selected-day contrast in valley-light, midnight-ledger and civic-gold themes.
- [ ] Check Morning step editor, task carry-forward, notebook, restore panel, monthly navigation, Schedule sliders, save bar and auth forms.
- [ ] Check printable review and download preview on mobile and desktop.
- [ ] Verify Public Files long official names and URLs wrap without overflow.
- [ ] Separately inspect Android icon and in-app image on an installed 0.3.3/code 6 build; website CSS cannot fix an older APK.
- [ ] Separately confirm user-reported Google consent-screen branding appears to a new sign-in user; Google Cloud branding is not controlled by this CSS.

The running backlog remains open. Production signing, confirmed APK artifact/install, Google login acceptance, real Form 700 collection, full-account restore, website/store/learning and Muse/monitoring integrations remain separate.
