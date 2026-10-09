# 1.9 Testing and release

## Repositories

| Repository | Role | Work in this plan |
| --- | --- | --- |
| [freenet-appkit](https://github.com/glesage/freenet-appkit) | Modified | AppKit tests, developer package and signed River test builds |
| [river](https://github.com/freenet/river) | Modified | River test fixtures, invite-only rooms and tester support |
| [freenet-core](https://github.com/freenet/freenet-core) | Used | Pinned Core build and compatibility |
| [freenet-migrate](https://github.com/freenet/freenet-migrate) | Used | River component migration fixtures |
| [freenet-test-network](https://github.com/freenet/freenet-test-network) | Used | Isolated test networks |

## Purpose

Use River as the end-to-end AppKit test application on real iOS and Android phones in the thin-peer role from [1.8 Thin-peer protocol](08-thin-peer.md). River runs its signed web UI in one WebView, served by the installation's embedded node. Its room contracts and chat delegate prove joining, messaging, recovery and upgrades.

Deliver signed River test builds through TestFlight on iOS and Play internal testing on Android. Release the [developer package](#developer-package) when the tests pass. EVY's native application coverage and production gates belong to [2.10 Testing and release](../2-evy-on-freenet/10-testing-and-release.md).

## River scope

- Pin the River website container, publisher, archive reference, room contract, chat delegate and original parameter bytes for every run. Preserve predecessor artifacts needed by upgrade tests.
- Instantiate River's chat delegate on the pinned Core in a compatibility fixture. Verify that its freenet-stdlib host-function imports match that Core build ([#5617](https://github.com/freenet/freenet-core/issues/5617), [#5719](https://github.com/freenet/freenet-core/issues/5719), [#5717](https://github.com/freenet/freenet-core/issues/5717)).
- Drive River's own UI for invite, join, read, send and reconnect tests. Use real embedded Core, contract validation and delegate signing. Deterministic fixtures isolate transport or fault cases alongside these end-to-end runs.
- Run prompt and notification tests with the node in network mode to exercise delegate prompts and contract notifications ([#5273](https://github.com/freenet/freenet-core/issues/5273)).
- Build isolated test networks with [freenet-test-network](https://github.com/freenet/freenet-test-network), whose Docker NAT simulation covers carrier-NAT cases. It pins freenet-stdlib 0.1.29, so check it against the pinned Core before the first run.
- Each isolated node gets its gateways with `--gateway` and `--skip-load-from-network` ([#4264](https://github.com/freenet/freenet-core/pull/4264)). Supply a nonempty gateway list and verify that every node's peers belong to the isolated network ([#5552](https://github.com/freenet/freenet-core/issues/5552)).
- Exercise the supported Swift/Kotlin APIs with the same protocol fixtures. [1.1 Mobile feasibility and supported profiles](01-feasibility.md) published native-route coverage for the iPhone 13 mini, iOS Simulator and Android emulator in the [support matrix](https://github.com/glesage/freenet-appkit/blob/1988c5cbdfc5c1f88065382de2a4f86093948b6e/docs/support-matrix.md#operations). Add the Android phone column to it.
- Label observations by their source: the local cache or an independent network read. Keep signed bytes with the draft until Core answers, under [1.6 Application protocols, data and operations](06-data-and-operations.md).

River publishes a signed tar.xz website archive through its [web container contract](https://github.com/freenet/river/blob/8cf54dd7799514851da7eab051e4cc43f797208d/contracts/web-container-contract/src/lib.rs). Its [chat delegate protocol](https://github.com/freenet/river/blob/8cf54dd7799514851da7eab051e4cc43f797208d/common/src/chat_delegate.rs) includes `SignMember` and `SignResponse`, which River's UI calls when Alice invites Carol ([invitation_builder.rs](https://github.com/freenet/river/blob/8cf54dd7799514851da7eab051e4cc43f797208d/ui/src/components/members/invitation_builder.rs)). The delegate signing test uses that exchange to form an [authorized member](https://github.com/freenet/river/blob/8cf54dd7799514851da7eab051e4cc43f797208d/common/src/room_state/member.rs), as [calling a delegate in 1.6 Application protocols, data and operations](06-data-and-operations.md#calling-a-delegate) describes. River signs chat messages in the page. Check that Bob's [authorized message](https://github.com/freenet/river/blob/8cf54dd7799514851da7eab051e4cc43f797208d/common/src/room_state/message.rs) reaches the room's [recent messages](https://github.com/freenet/river/blob/8cf54dd7799514851da7eab051e4cc43f797208d/common/src/room_state.rs).

## River acceptance cases

| Scenario | Passing result |
| --- | --- |
| Install and invite | A clean install verifies River's signed archive. Opening Alice's invite validates its app and room references, shows trusted consent and joins the intended room. Invalid or substituted references fail visibly. |
| Notifications at first run | Bob runs River for the first time. The host asks for `notifications` once and stores his answer in the installation's trusted permission records. The notification modal's Enable button and Bob's first send then show the stored answer with no new prompt. After a denial, River's alerts stay in-app. |
| Read and refresh | Bob reads the joined room, sees cached observation time while offline and receives verified updates after reconnect. |
| Missing network copy | Remove remote copies of a River room Alice owns in an isolated test network. River PUTs the node's copy back under [lost network state in 1.6 Application protocols, data and operations](06-data-and-operations.md#lost-network-state). Verify readback through an independent peer. An interrupted or repeated PUT leaves each message in the room once. |
| Send and sign | River signs Bob's message in the page with his room signing key, saves it with its draft, sends it and sees it in room state. An independent peer can retrieve the message. The on-device chat delegate answers `SignMember` for Alice's invitation of Carol. Its signature verifies with Alice's key. |
| Offline and interrupted send | Send with no signal, on Wi-Fi with no internet, and with River terminated before and after Core answers. With the room state retained within Core's hosting budget, the message reaches an independent peer after reconnect, and a resend leaves one copy in the room. Retention scope follows [Core retention and offline delivery in 1.6 Application protocols, data and operations](06-data-and-operations.md#core-retention-and-offline-delivery). |
| Changed room authority | Write a draft offline, change membership or rotate the room secret, then reconnect. River keeps the draft and applies its protocol's conflict/repair rules. |
| Foreground lifecycle | Lock, background, terminate and resume during startup, signing, submission and refresh. Retain committed drafts, keys and sent messages, invalidate old callbacks and release ports/store locks. Alerts follow the foreground scope that [1.1 Mobile feasibility and supported profiles](01-feasibility.md#message-alerts) confirmed. |
| Connectivity | Change Wi-Fi/cellular paths and remove the serving peer. Reconnect restores demand. |
| Compatible web update | Install a verified new version while an open session stays on the version it started with. Activate it under the [rules in 1.3 Single-application host](03-host.md#activating-a-release) and keep drafts and signed messages waiting to be sent. |
| Interrupted component upgrade | Upgrade from an older River release on iOS and Android and kill the app during the migration. The next start finishes it, and the checks in [1.7 Upgrades and migration](07-migration.md#acceptance) pass. |
| Protected data | Test permission revocation, locked or invalidated keys through [1.5 Identity, keys and local protection](05-identity.md) and encrypted export/import through [1.10 Backup and restore](10-backup-and-restore.md). Show coverage and keep drafts. |
| Interrupted restore | On iOS and Android, restore over an existing identity and inject storage, migration and process failures before and after activation. Recovery selects one complete generation, as [1.10 Backup and restore](10-backup-and-restore.md#staged-restore-transaction) requires. |
| Device limits and usability | Storage exhaustion, large records and rapid updates remain within the [device limits in 1.1 Mobile feasibility and supported profiles](01-feasibility.md#device-limits) and the mobile limits in [Running Wasm in 1.2 Embedded node and mobile SDK](02-sdk.md#running-wasm). Keyboard, focus, large text and screen-reader flows work on both platforms. River tracks two mobile layout gaps in [river#714](https://github.com/freenet/river/issues/714) and [river#718](https://github.com/freenet/river/issues/718). |

Use a separate test contract for destructive migration cases. Use bounded River room records to test canonical encoding, request matching, subscription delivery and binding costs. Run River upgrades through its real delegate and migration path. Its [room predecessor registry](https://github.com/freenet/river/blob/8cf54dd7799514851da7eab051e4cc43f797208d/common/legacy_room_contracts.toml), [delegate registry](https://github.com/freenet/river/blob/8cf54dd7799514851da7eab051e4cc43f797208d/legacy_delegates.toml) and [migration build rules](https://github.com/freenet/river/blob/8cf54dd7799514851da7eab051e4cc43f797208d/.claude/rules/delegate-migration.md) provide the recorded source evidence.

## Developer package

Provide these materials for River test builds and EVY native integration on iOS and Android:

- A River WebView starter, and Swift and Kotlin SDK examples for native screens
- The supported-version matrix and pinned dependencies
- iOS and Android setup, build and distribution instructions, covering artifact verification, fixture setup and lifecycle integration
- Diagnostic export and the release checklist

## Store requirements

Deliver River to controlled testers through TestFlight on iOS and Play internal testing on Android. Pin one River publication and use invite-only test rooms with a named room owner and a monitored tester-support channel. Record the distribution review and declarations required by the selected testing channel before inviting testers.

| Requirement | Evidence |
| --- | --- |
| Application identity | Signed River website container and current, predecessor and migration-only component hashes match the [execution policy in 1.4 Application bundles](04-bundles.md#execution-policy). |
| Device access | Review notes list the notifications, clipboard, file, external-link and navigation adapters enabled by [1.3 Single-application host](03-host.md#shell-bridge-messages), their caller checks and consent rules. |
| Tester support | Test invitations identify the room owner, support contact and test-data handling. The owner can remove a participant using River's room controls. |
| Distribution review | Record approval for the actual River test build and testing channel, including applicable content, privacy and native-bridge requirements. Use the [App Store Review Guidelines](https://developer.apple.com/app-store/review/guidelines/) and [Google Play policy centre](https://play.google.com/about/developer-content-policy/) as the review sources. |
| Runtime | Pulley runs the pinned contracts and delegate on iOS and Android. Review notes describe the embedded node, website container and enabled bridge adapters. |
| Privacy | The testing checklist records public room data, peer-visible keys and IP addresses, private device records, and the declarations required by the distribution channel. |
| Encryption | The checklist records X25519, AES-GCM, ChaCha20, XChaCha20-Poly1305, Ed25519, BLAKE3, HKDF-SHA256 and SHA-256, following [Encryption export regulations](https://developer.apple.com/documentation/security/complying-with-encryption-export-regulations). Record distribution territories and any required declarations. |

EVY's application moderation, payment and production launch requirements are defined in [2.10 Testing and release](../2-evy-on-freenet/10-testing-and-release.md#store-requirements).

### Store build checks

This plan owns the shared iOS and Android build-check interface. Pass application name, minimum OS values, exact component/code policy, merge-law contract set and cipher inventory from the consuming application. River uses iOS 16/Android API 28; EVY uses iOS 17/Android API 28. Fail packaging if an enabled check fails and record dated store/SDK requirement evidence before each submission.

| Check | iOS | Android |
| --- | --- | --- |
| Pulley only | No Cranelift native backend and no JIT entitlement | No Cranelift native backend for any ABI |
| No file sharing | `Info.plist` has no `UIFileSharingEnabled` | – |
| [16 KB pages](https://developer.android.com/guide/practices/page-sizes) | – | `zipalign -c -P 16 -v 4` passes on the APK, and every LOAD segment of each 64-bit `.so` has 16 KB alignment (`llvm-objdump -p`) |
| Build SDK | Xcode 26 and the iOS 26 SDK ([upcoming requirements](https://developer.apple.com/news/upcoming-requirements/)) | `targetSdk` is 36 or later ([target API](https://support.google.com/googleplay/android-developer/answer/11926878)) |
| Minimum OS | Deployment target iOS 16, as in [supported profiles in 1.1 Mobile feasibility and supported profiles](01-feasibility.md#supported-profiles) | `minSdk` is 28 (Android 9) |
| Release signing | Distribution certificate | Upload key, with Play App Signing |
| Privacy and encryption | `PrivacyInfo.xcprivacy` is in the `.app`, and `Info.plist` sets `ITSAppUsesNonExemptEncryption` | – |
| No test harness | The binary has no `appkit.scenario` or `APPKIT_RESULT` | `classes*.dex` and native libraries have no `appkit.scenario` or `APPKIT_RESULT` |
| Merge laws | `fdev verify-merge` passes on the application’s declared contract set (River room; every EVY contract) | Same |
| Core version | The release checklist records the pinned Core version and the network's `min-compatible-version` | Same |

From 2027-02-01, Play blocks app updates that lack 16 KB page support. The merge-law check follows [sending updates in 1.6 Application protocols, data and operations](06-data-and-operations.md#sending-updates). [#5725](https://github.com/freenet/freenet-core/issues/5725) tracks `fdev verify-merge` reporting a rejected merge of two valid states as inconclusive.

### Core version and the network

Peers refuse a node whose Core version is below the network's `min-compatible-version` ([#1360](https://github.com/freenet/freenet-core/pull/1360), [#3294](https://github.com/freenet/freenet-core/pull/3294)). The build derives its configured minimum from `FREENET_MIN_COMPATIBLE_VERSION`; record the resolved build value and independently observed network minimum at each release gate. Desktop nodes update themselves and reconnect ([#2521](https://github.com/freenet/freenet-core/pull/2521), [#2516](https://github.com/freenet/freenet-core/pull/2516)), and Core's maintainers want peers to update quickly during alpha ([D2918](https://github.com/freenet/freenet-core/discussions/2918)). The iOS and Android store builds keep their packaged Core version. Apply these release rules:

- Each iOS and Android store build records its Core version and the network's `min-compatible-version`.
- A new iOS and Android store build ships before the network's minimum passes the pinned Core version.
- A phone that falls behind gets "update the app" from the SDK ([typed errors in 1.2 Embedded node and mobile SDK](02-sdk.md#typed-errors)). River tells the user to install the new store build.

## Release tests

Run every release test on iOS and Android with the phone in the thin-peer role.

| Release test | Passing evidence |
| --- | --- |
| Independent build | A second developer builds and installs River from the starter instructions on iOS and Android. |
| River | The join, read, send, reconnect, restart and interrupted-upgrade cases in [River acceptance cases](#river-acceptance-cases) pass through River's UI and real chat delegate. |
| Thin role and budgets | The [acceptance in 1.8 Thin-peer protocol](08-thin-peer.md#acceptance) passes on the pinned Core build. |
| Safety and durability | Browser WebSocket and native SDK paths pass the caller-authority, reply-correlation, cancellation and connection-generation tests in [1.2 Embedded node and mobile SDK](02-sdk.md#application-connections). Locking destroys the application WebView and releases controlled plaintext copies. Consistent, authenticated backup snapshots, fallback-port storage, offline sends, staged restore and policy-admitted migrations pass their owning plans. |
| Local network | The local-network case in the [acceptance in 1.2 Embedded node and mobile SDK](02-sdk.md#acceptance) passes with River. |
| Device limits and accessibility | Startup, memory, battery, storage exhaustion, keyboard, focus, large text and screen-reader tests pass on the declared devices. The [release-profile evidence in 1.1 Mobile feasibility and supported profiles](01-feasibility.md#release-profile-evidence) records the exact release artifacts, runtime, ABI and real-device/carrier coverage. |
| Distribution | The TestFlight and Play internal-testing builds of River pass review for the actual bridge capability table and execution policy, and every [store requirement](#store-requirements) holds. Review evidence identifies the enabled adapters and consent rules. |
| Core version | The [Core version rule](#core-version-and-the-network) holds for both builds. A test peer that requires a newer Core gives "update the app" on iOS and Android. |
| Diagnostics | Reports identify versions, node role, lifecycle state, observation provenance and pending-operation status. Apply [host redaction in 1.3 Single-application host](03-host.md#diagnostics) to keys, tokens, message content and private references. |

## Acceptance evidence

For every applicable [decision gate in README.md](../README.md#decision-gates), link the accepted scope, approver, implementation commit and passing fixture result. Record conditional optimizations used by the release profile. River test delivery requires its mandatory Core and River gates to be complete on the packaged build for iOS and Android.

Publish results with exact revisions, devices, OS versions, network conditions and redacted logs.
