# No-store-enrollment Workstation installation

This batch adds members/install.html and a distinct Workstation manifest without replacing the existing 209 Media manifest or Android packages. The manifest uses relative paths, a dedicated identity, the existing square SVG artwork and standalone display. The installed start page redirects to the planner when launched in standalone mode. Browser support and icon rendering vary; this is not proof that every platform's automatic install criteria have passed. Native raster icon assets/store packaging remain separate work.

The dedicated install page is the install entry. Existing app/login pages and authentication code are unchanged. Scope includes the same-origin website so ordinary same-origin login navigation remains within the declared app scope; browser/provider behavior and external OAuth may still open browser UI. No native OAuth callback or account-session transfer is implemented.

The worker is scoped to members, intercepts GET navigations only and always uses the network. Only a generic connection-error HTML response is supplied on network failure. There is no Cache API use, private API caching, attachment storage, offline account data, background synchronization or offline-save claim. Existing member workers with another script URL are not replaced automatically.

No store registration, paid build service, new backend project or paid dependency is purchased. Existing hosting/backend usage and quotas still apply. This does not finalize Android/iOS native projects, production signing, account-deletion flows, store privacy declarations or store submission. It does not remove the browser X from the old Custom Tab APK; users must launch the separately installed Home Screen web app. Do not tell users to uninstall existing apps or clear data as a prerequisite.

Android: open install page in Chrome and use the offered install or Home Screen option. iPhone/iPad: Safari > Share > Add to Home Screen > Open as Web App when available. Desktop browsers may offer installation too. No device installation, authentication-return or deployed acceptance is asserted by this source change.
