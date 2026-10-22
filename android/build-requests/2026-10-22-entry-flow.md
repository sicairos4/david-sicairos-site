# Fresh Android entry-flow build request

Requested by the owner on 2026-10-22 after the installed debug APK showed a welcome screen followed by the web login screen.

Build the current main revision using the existing Android APK build workflow. This request changes no application logic, signing configuration, authentication settings, or saved user data.

Purpose: obtain a fresh debug APK for owner installation and entry-flow testing. Google sign-in is still reported to stall on a blank page in full Chrome; this build request does not claim to fix it.

The existing delivery workflow may run its validation jobs and publish a public preview release. Build success, artifact availability, installation, and successful sign-in are separate outcomes. No device installation or acceptance is claimed by this request. Do not uninstall an existing app or erase local data automatically.
