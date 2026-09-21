# Freenet mobile app

Build a consumer application that discovers Freenet applications, renders compatible SDUI natively and offers an application's other declared targets. Bob opens the homepage, searches for nearby services and starts Marketplace. The installed mobile app supplies the trusted reader and permission screens. Marketplace supplies verified screens, action definitions and domain artifacts. The installed reader packages the native Rust SDK and generated platform bindings.

This is the consumer product built from [hosts](../appkit/hosts.md), [SDUI readers](../appkit/sdui.md), the [mobile SDK](../freenet-mobile/README.md) and [identity/recovery](../identity/README.md). [EVY Developer](../evy/README.md) provides authoring and contributor tools.

## 1. Homepage and discovery

Start with an installed curated bootstrap catalogue and a replaceable search-provider interface. Add Atlas as a provider after the [sample](../atlas-sample/README.md) passes its integration gates. Keep provider choice and catalogue updates visible in settings.

| Home area | Behavior |
| --- | --- |
| Search | Search a chosen provider and show source-labeled results. |
| Installed apps | Open trusted cached bundles and show pending updates. |
| Recent activity | Resume local app routes without exposing private order details on a locked device. |
| Open a reference | Accept an application or contract link, inspect it and report supported actions. |
| Account and recovery | Show identity coverage, device enrollment and recovery status. |

Search providers limit the number of results per page. Each result includes display metadata, a container reference and an optional exact publication reference. Treat titles, icons and rankings as untrusted hints. Resolve and verify the referenced container through the host before opening or granting access. Marketplace's listing search uses its own declared queries and domain delegates, and the homepage finds applications.

Opening an external deep link can select a route or proposed action. The host validates its arguments, verifies the app and obtains any required user action before spending money or sharing private information.

## 2. Opening an application

```mermaid
flowchart TD
    Link["Bob selects a result or pastes a link"] --> Inspect["Resolve reference and available targets"]
    Inspect --> Kind{"Supported application target?"}
    Kind -->|"Contract only"| Contract["Show contract identity and inspection"]
    Kind -->|"SDUI"| Compatible{"Reader steps and domain protocols compatible?"}
    Compatible -->|Yes| Access["Review access in the trusted host"]
    Access --> Run["Execute declared actions and render native SDUI"]
    Compatible -->|No| Alternatives["Explain missing support and offer other targets"]
    Kind -->|"Custom web"| Web["Open in the in-app web view served by the embedded node"]
    Kind -->|"Native"| Native["Show installed app or distribution link"]
    Alternatives --> Choice["User explicitly chooses web or native"]
    Choice --> Web
    Choice --> Native
```

Contract references open in an inspection view. Website containers open through Core's web shell inside the app. The [bundle plan](../appkit/bundles.md) defines compatibility requirements for web, SDUI and native targets.

Prefer compatible SDUI for the default in-app experience and keep an explicit Open web app action when a web target exists. Open web targets in an in-app web view served by the embedded node. The embedded node runs only while the app is in the foreground, and the iOS wrapper stops it when the scene backgrounds, so switching to the system browser would remove the loopback endpoint before the page loads. The existing Atlas demo uses an in-process web view for this reason. Opening the system browser works only against a remote or hosted node, which depends on [hosted mode #4381](https://github.com/freenet/freenet-core/issues/4381).

Web sessions have their own keys, sessions and grants. Ask for enrollment or authorization before handing access from the native app to a web session. Core's shell applies its existing capability-specific controls to the web target. AppKit's operation grants for web targets depend on the permission lifecycle gate in the [host plan](../appkit/hosts.md#3-browser-hosting).

A mobile-only application supplies a browser landing page alongside its SDUI. Label the landing page as information and offer compatible SDUI for use. A separately installed native application provides custom screens and packages the same native SDK as the reader. It may use compatible published definitions and delegates. If SDUI is unavailable, show the available web and native options. The user chooses which to open.

Show publisher identity, installed copy, requested access and update status in host-controlled screens. Display these outside publisher-authored UI. A valid publisher signature is evidence of origin, and grants and execution limits still apply.

## 3. Installation, updates and sessions

Installation retains verified bundle metadata, selected artifacts, permission decisions and local data schema state. Use the [host installation rules](../appkit/hosts.md#6-installing-and-updating-applications) for snapshot selection, observed versions, local migration and withdrawal.

- Open a trusted compatible cached bundle while checking for updates within a bounded budget.
- Explain stale observations, unavailable artifacts, withdrawn applications and incompatible updates separately.
- Ask for newly requested access through the trusted host. Keep a compatible working copy for an active application while an update awaits installation.
- Keep app storage and keys scoped to the signed-in user and app identity.
- Run several apps with separate sessions and resource budgets. Share the embedded node through the SDK coordinator.

Session demand, backgrounding and resume follow the [host lifecycle](../appkit/hosts.md#5-saving-work-and-reopening-an-app).

For example, Bob opens a cached pickup agreement in an underground car park. The app shows when it last checked the order, and leaves a new pickup proposal pending until the host obtains enough domain evidence to confirm it.

## 4. Identity, permissions and data controls

Onboarding creates or restores the user's host identity and explains recovery coverage. Applications obtain their own authorized identity context under the [identity plan](../identity/README.md#1-separate-identities-and-authority).

Provide screens for grants, storage use, recovery packages and enrolled devices. Revocation invalidates active privileged handles and rechecks queued operations that still require access.

For publisher transfers, show the verified predecessor and successor. Ask before moving private access, and save progress so an interrupted migration can resume. After an observed withdrawal, stop the application session and provide trusted export, removal and supported order-recovery controls.

Separate removing an app from deleting its retained data. Deletion uses the identity plan's [forget operation](../identity/README.md#2-protected-keys-and-records) and first shows the affected drafts, keys and pending orders, with a recovery export offered.

Native app links open through a trusted external-link action. Treat a publisher's link as a pointer only, and follow the identity plan for any enrollment or export.

## 5. Service surfaces and diagnostics

Marketplace opens checkout through the host's approved payment adapter. Its declared action refreshes signed payment state through the host after return. Consumer app management can show source-labeled contribution information, while EVY Developer owns detailed review and earnings workflows.

Diagnostics show the app and installed publication, compatibility, node state, last observation, pending operations and a readable reason for failure, exported under the [host redaction rules](../appkit/hosts.md#8-diagnostics).

The consumer application package contains reusable reader components, host adapters and the bootstrap catalogue. Marketplace supplies declarative actions and application delegates. The package opens new applications that meet its supported action, component and domain protocol versions. New executor primitives arrive through a reader update.

## 6. Delivery and acceptance

| Phase | Delivers | Done when |
| --- | --- | --- |
| 1. Product shell | Home, installed apps, account and diagnostics | A clean installation can open the Atlas sample from the bootstrap catalogue. |
| 2. Discovery | Replaceable provider and verified reference flow | Forged result metadata cannot substitute publisher authority or permissions. |
| 3. App management | Updates, storage, revocation and multiple sessions | One app's failure, closure or upgrade leaves other sessions isolated and usable. |
| 4. Recovery | Recovery setup, import and pending-operation restoration | A replacement phone resumes a declared recoverable operation without duplicate submission. |
| 5. Marketplace launch | Commercial adapters and final product acceptance | Buyer and seller complete the Marketplace flow on iOS and Android. |

Test custom-web-only apps, SDUI-only apps, combined web/SDUI bundles, native-linked targets, existing website containers, arbitrary contracts, invalid links, no connectivity, stale caches, withdrawn applications, missing permissions and unsupported components. Confirm that choosing web preserves its container boundary and requires its own grants. Run web handoff tests against the in-app web view, including backgrounding during a web session. Verify accessibility, focus, keyboard input, large text and screen-reader descriptions on real devices.

Apply the SDK's measured device and network budgets and the host's application isolation tests.
