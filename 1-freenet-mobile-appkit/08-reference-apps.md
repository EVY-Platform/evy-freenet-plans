# 1.8 Reference apps and compatibility fixtures

## Repositories

| Repository | Role | Work in this plan |
| --- | --- | --- |
| `freenet-appkit` | Modified | River scenario suite, Atlas compatibility fixtures, destructive-migration test contract and published results |
| [atlas](https://github.com/freenet/atlas) | Modified | Atlas's website packaged with host metadata under 1.4 Application bundles, iOS and Android WebView demos on its browser client and a separate test index |
| [river](https://github.com/freenet/river) | Used | Pinned container, publisher, room contract, chat delegate, registries and predecessor artifacts driven through River's own UI |
| [freenet-migrate](https://github.com/freenet/freenet-migrate) | Used | Pointer resolution for Atlas's re-keyed index |
| [freenet-stdlib](https://github.com/freenet/freenet-stdlib) | Used | TypeScript SDK and Rust browser build as protocol comparisons |

## Purpose

Prove one defined application on iOS and Android. Package River's signed web UI in an in-app WebView served by the embedded node. Application code coordinates River's existing contract and delegate protocols. Use small Atlas fixtures to isolate SDK and index-compatibility behavior.

Own reference application setup, pinned test artifacts, app-specific scenarios and captured results. 1.1 Mobile feasibility and supported profiles owns feasibility measurements, 1.2 Embedded node and mobile SDK owns APIs and packaging, and 1.9 Developer package and release acceptance owns the reproducible developer package and final release decision.

## Prerequisites

- Supported profiles in [1.1 Mobile feasibility and supported profiles](01-feasibility.md)
- SDK APIs in [1.2 Embedded node and mobile SDK](02-sdk.md)
- [1.3 Single-application host](03-host.md)
- Bundle tooling in [1.4 Application bundles](04-bundles.md)
- [1.5 Identity, keys and local protection](05-identity.md)
- [Durable operations in 1.6 Application protocols, data and operations](06-data-and-operations.md)
- [1.7 Upgrades and migration](07-migration.md)
- The [thin role in 1.10 Thin-peer role and cellular data budgets](10-thin-peer.md) for release runs

Controlled full-peer fixtures can support development.

| Use | Plan and gate |
| --- | --- |
| River end-to-end release application | Milestone 1 (Freenet mobile AppKit), through River's own UI and protocols |
| Atlas SDK and index compatibility | Bounded fixtures in this plan after 1.1 Mobile feasibility and supported profiles, 1.2 Embedded node and mobile SDK, 1.6 Application protocols, data and operations and 1.7 Upgrades and migration |
| Atlas hosted application | Later [2.1 EVY shell and curated catalogue](../2-evy-mobile-app/01-catalogue.md) and [2.7 Multi-application acceptance](../2-evy-mobile-app/07-acceptance.md), with a verified website container and bundle that passes [2.3 Installation and updates](../2-evy-mobile-app/03-installation-and-updates.md) |
| Optional reader comparison | [4.9 SDUI migration and conformance](../4-sdui/09-migration-and-conformance.md), after the relevant milestone 4 (SDUI) readers and protocols |
| Optional search provider | [5.4 Discovery and catalogue extensions](../5-optional-extensions/04-discovery.md), after verified installation and reference handling in milestone 2 (EVY mobile app) |

## River scope

- Pin the River website container, publisher, archive reference, room contract, chat delegate and original parameter bytes for every run. Preserve predecessor artifacts needed by upgrade tests.
- Drive River's own UI for invite, join, read, send and reconnect tests. Use real embedded Core, contract validation and delegate signing. Deterministic fixtures isolate transport or fault cases alongside these end-to-end runs.
- Exercise the supported Swift/Kotlin APIs with the same protocol fixtures. Publish native-route coverage in the support matrix of 1.1 Mobile feasibility and supported profiles.
- Label locally cached observations and independently retrieved network evidence separately. Retain exact submitted bytes and evidence for uncertain outcomes under 1.6 Application protocols, data and operations.

River publishes a signed tar.xz website archive through its [web container contract](https://github.com/freenet/river/blob/main/contracts/web-container-contract/src/lib.rs). Its [chat delegate protocol](https://github.com/freenet/river/blob/main/common/src/chat_delegate.rs) includes `SignMessage` and `SignResponse`. The signing test uses that exchange to form an [authorized message](https://github.com/freenet/river/blob/main/common/src/room_state/message.rs), then checks the room's [recent-message state](https://github.com/freenet/river/blob/main/common/src/room_state/version.rs).

## River acceptance cases

| Scenario | Passing result |
| --- | --- |
| Install and invite | A clean install verifies River's signed archive. Opening Alice's invite validates its app and room references, shows trusted consent and joins the intended room. Invalid or substituted references fail visibly. |
| Read and refresh | Bob reads the joined room, sees cached observation time while offline and receives verified updates after reconnect. |
| Missing network copy | Remove remote copies of an owned River room in an isolated test network. Use [bounded authorized repair in 1.6 Application protocols, data and operations](06-data-and-operations.md#owned-contract-state-inventory-and-repair) to restore the same contract identity from retained original code, exact parameters and verified signed state. Verify readback through an independent peer. Interrupted and repeated repair preserves operation IDs and signed payloads, with each domain effect present once. |
| Send through the delegate | The real chat delegate signs Bob's message on-device. The host journals the exact authorized bytes before submission. Readback establishes the domain outcome and an independent peer can retrieve the accepted message. |
| Uncertain send | Terminate or time out after submission. Restart retains the operation ID and bytes, checks room evidence and reconciles before retry. Duplicate delivery preserves one domain operation. |
| Changed room authority | Queue work offline, change membership or rotate the room secret, then reconnect. River preserves the draft and applies its protocol's conflict/repair rules. Changed payloads use successor operations. |
| Foreground lifecycle | Lock, background, terminate and resume during startup, signing, submission and refresh. Retain committed drafts, keys and journals, invalidate old callbacks and release ports/store locks. Alerts follow the foreground scope in 1.1 Mobile feasibility and supported profiles. |
| Connectivity and role | Change Wi-Fi/cellular paths and remove the serving peer. Reconnect preserves the thin role, restores demand and passes the separate upload/download and total-use limits in 1.10 Thin-peer role and cellular data budgets. |
| Compatible web update | Stage a verified archive while a session remains on its selected compatible archive. Activate through host rules and preserve pending work's originating release references. |
| Interrupted component upgrade | Exercise River's predecessor registry and application migration adapters. Interrupt contract carry-forward and delegate export/import, then resume with preserved parameters, authorized access and verified readback. |
| Protected data | Test permission revocation, locked or invalidated keys and app-specific encrypted export/import through 1.5 Identity, keys and local protection. Show coverage and preserve unresolved work. |
| Device limits and usability | Storage exhaustion, large records and rapid updates remain within the limits in 1.1 Mobile feasibility and supported profiles. Keyboard, focus, large text and screen-reader flows work on both platforms. |

Use a separate test contract for destructive migration cases and small Atlas records for canonical encoding, request correlation, subscriptions and binding costs. Preserve the published Atlas index identity. River upgrade runs still exercise River's actual delegate and migration path. Its [room predecessor registry](https://github.com/freenet/river/blob/main/common/legacy_room_contracts.toml), [delegate registry](https://github.com/freenet/river/blob/main/legacy_delegates.toml) and [migration build rules](https://github.com/freenet/river/blob/main/.claude/rules/delegate-migration.md) provide the recorded source evidence.

## Atlas recorded evidence and pinned identity

[Atlas](https://github.com/freenet/atlas) has a Rust browser UI. Recorded local `atlas-client` work exposes a browser Wasm client. Native application integration and delegate-backed signing need their own proof. These notes describe inspected development work. 1.1 Mobile feasibility and supported profiles builds fresh iOS and Android WebView demos on the browser client and records pinned revisions and real-device results for both platforms.

The recorded Atlas dependency is stdlib 0.8.3, while the inspected Core main uses 0.12.0. Align compatible dependencies or prove an adapter before measurement. Preserve published validator bytes while testing new builds separately.

Atlas re-keys its index contract when common or contract code changes. Resolve its stable pointer under the root verifying key through the [migration library](https://github.com/freenet/freenet-migrate). Fall back to the pinned index code hash when a fresh peer's pointer GET times out. Pin the author key, signed pointer record, index code hash, exact validator and original parameter bytes. Preserve canonical signed Atlas records. A new build's compatibility proof must account for its actual instance identity.

## Atlas fixture scope and acceptance

Use a bounded deterministic index first, then a separate test index. Keep the published Atlas index intact. Test `loadIndex`, search, refresh and `addProducts` through Atlas's own application code. Domain preparation and SDK transport get separate measurements.

| Fixture | Passing result |
| --- | --- |
| Canonical records and identity | Browser and supported Swift/Kotlin paths preserve signing inputs, record bytes and pinned index identity. Malformed records fail validation. |
| Reads and subscriptions | Known records and bounded queries return the expected results. Cached data shows observation time. Releasing one view preserves another's demand through tested SDK subscription ownership. |
| Correlation and cancellation | Interleaved responses reach the right request/session. Reopened sessions reject late callbacks, and uncertain mutations remain tracked. |
| Publication | Application domain code prepares canonical updates. The signing fixture uses an authorized on-device delegate with keys protected by Core. The host saves the operation ID and exact signed bytes, submits and verifies readback. |
| Restart and retry | Termination after preparation or uncertain submission retains the original operation and bytes. Reconciliation prevents duplicate domain effects. Changed content creates a successor operation. |
| Upgrade adapter | A separate test contract changes code, recovers predecessor state through the application adapter, resumes an interrupted migration and verifies successor readback. |
| Resource costs | Measurements separate transport/bindings, Core execution and UI work. Record large-record copying, delegate calls, subscription rate and elapsed time against the device limits in 1.1 Mobile feasibility and supported profiles and the cellular budgets in 1.10 Thin-peer role and cellular data budgets. |

The existing TypeScript SDK and Rust browser build provide protocol comparisons. Swift/Kotlin examples use the native SDK's supported APIs. Each application supplies its own domain codecs and delegate messages through [application operations in 1.6 Application protocols, data and operations](06-data-and-operations.md#delegate-requests-and-results). Milestone 4 (SDUI) owns generic typed views, declared-action schemas and reader execution.

## Atlas product flows for the later 2.7 Multi-application acceptance gate

Atlas's own web UI covers search, details, saved items and publisher submission. Application code owns orchestration and Atlas's domain protocol. The signed website can run in a browser or an isolated mobile WebView.

Pin Atlas's verified website container ID in the [catalogue in 2.1 EVY shell and curated catalogue](../2-evy-mobile-app/01-catalogue.md#catalogue-and-shell). Keep that application identity separate from the index pointer, author key and index contract identity recorded above. Run the compatibility fixtures against the pinned application release.

Through Atlas's own web UI on iOS and Android, test search, details, saved items and publisher submission to a separate test index. Saved items survive restart, subscriptions refresh displayed records, and interrupted submissions reconcile to their original operation and signed bytes. Preserve the published Atlas index throughout these tests.

These app-specific checks are defined here for reuse. Their hosted-product release gate is [2.7 Multi-application acceptance](../2-evy-mobile-app/07-acceptance.md), which owns cross-app isolation, concurrent lifecycle and shared cellular-budget tests. Milestone 1 (Freenet mobile AppKit) release acceptance covers River and the bounded Atlas compatibility fixtures above.

## Website packaging and later integrations

Package Atlas's own `index.html`, browser code and assets as an ordinary signed website. Include required contract/delegate artifacts and host metadata under [1.4 Application bundles](04-bundles.md). Verify installation and compatible updates with its own UI. Record native-build distribution separately when exercising custom native examples.

Full-peer fixtures are development-only. Mobile release tests use the [required thin-peer profile in 1.10 Thin-peer role and cellular data budgets](10-thin-peer.md). River remains the milestone 1 (Freenet mobile AppKit) end-to-end release application.

[4.9 SDUI migration and conformance](../4-sdui/09-migration-and-conformance.md) owns optional comparisons using these canonical records across web, iOS and Android. It also owns reader-only and embedded-reader variants, screen/action compatibility and their acceptance. [5.4 Discovery and catalogue extensions](../5-optional-extensions/04-discovery.md) owns provider adoption. Each extension has its own gate.

## Acceptance evidence

Publish results with exact revisions, devices, OS versions, network conditions and redacted logs. All release cases use the thin profile on both platforms. Apply the River and Atlas compatibility cases to 1.9 Developer package and release acceptance and the hosted Atlas product cases to the later 2.7 Multi-application acceptance gate.
