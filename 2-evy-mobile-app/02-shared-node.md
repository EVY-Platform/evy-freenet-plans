# 2.2 Two apps on one node

## Repositories

| Repository | Role | Work in this plan |
| --- | --- | --- |
| [freenet-core](https://github.com/freenet/freenet-core) | Modified | `crates/mobile` binds each app's session to its own website container key, routes replies and alerts to that session, keeps one secret scope per app for forget, and turns off the 30-day sweep. Core needs a user scope without hosted mode and in background runs ([#5736](https://github.com/freenet/freenet-core/issues/5736)) |
| `freenet-appkit` | Modified | WebView hosts give each app its own data store and its own container path on iOS and Android, and recover one WebView at a time. The installation interface refuses a delegate key that another installed app already uses |
| [evy](https://github.com/EVY-Platform/evy) | Modified | The iOS and Android apps open River and Atlas side by side, each in its own WebView and session, and forget one app without touching the other |
| [river](https://github.com/freenet/river) | Used | First app in the two-app tests, with its chat delegate |
| [atlas](https://github.com/freenet/atlas) | Used | Second app in the two-app tests. It has no delegate and subscribes to its index contract |

## Purpose

This plan runs River and Atlas on one embedded node in the thin-peer role from [1.8 Thin-peer role and cellular data budgets](../1-freenet-mobile-appkit/08-thin-peer.md). EVY is one app to the phone, so it gets one node, as [One node per app in 1.3 Single-application host](../1-freenet-mobile-appkit/03-host.md#one-node-per-app) allows. [2.1 EVY shell and curated catalogue](01-catalogue.md) lists the apps and opens each one. Each app follows the rules in [1.3 Single-application host](../1-freenet-mobile-appkit/03-host.md) unchanged.

Alice reads "Skate club" in River, then switches to Atlas to browse apps. Bob's "Skate session Saturday?" still reaches River, and River raises its alert. Atlas never sees River's storage, replies or secrets, and trouble in one app leaves the other running.

## Web storage

Each app runs in Core's shell page, inside a sandboxed frame with no web storage of its own, as [Browser and native hosts in 1.3 Single-application host](../1-freenet-mobile-appkit/03-host.md#browser-and-native-hosts) describes. Both apps' shells load from the node's one origin, `http://127.0.0.1:<port>`. The shell keeps per-contract records in that origin's storage, such as River's notification consent under `freenet_notify:<website container key>` ([shell_bridge.js](https://github.com/freenet/freenet-core/blob/main/crates/core/src/server/path_handlers/assets/shell_bridge.js)). So the WebView host gives each app its own persistent data store, named by its website container key. Each app's cookies, storage, cache and service worker stay in its own store, and EVY deletes one app's store without touching the other.

Core unpacks both apps into the node's own web-app cache folder from [Storage in 1.2 Embedded node and mobile SDK](../1-freenet-mobile-appkit/02-sdk.md#storage) ([#5706](https://github.com/freenet/freenet-core/issues/5706)).

| Platform | Data store per app | Supported versions |
| --- | --- | --- |
| iOS | `WKWebsiteDataStore(forIdentifier:)`, deleted with `WKWebsiteDataStore.remove(forIdentifier:)` | iOS 17 or later, the first version with `WKWebsiteDataStore(forIdentifier:)`. So EVY's iOS target is 17.0, above the iOS 16 floor in [Supported profiles in 1.1 Mobile feasibility and supported profiles](../1-freenet-mobile-appkit/01-feasibility.md#supported-profiles) |
| Android | An androidx.webkit `Profile` from `ProfileStore.getOrCreateProfile`, deleted with `deleteProfile` | Android 9 (API 28) or later, as in [Supported profiles in 1.1 Mobile feasibility and supported profiles](../1-freenet-mobile-appkit/01-feasibility.md#supported-profiles). androidx.webkit 1.9.0 or later (AppKit uses 1.15.0) and a System WebView that reports `WebViewFeature.MULTI_PROFILE`. EVY checks the feature at start and asks the user to update Android System WebView when it is missing |

## Sessions and routing

Each app gets its own session under [Trusted calls in 1.3 Single-application host](../1-freenet-mobile-appkit/03-host.md#trusted-calls). Two apps on one node add these cases:

| Case | What EVY and Core do | River and Atlas example |
| --- | --- | --- |
| Session admission | `crates/mobile` binds each WebView's connection to its own website container key, and Core attests that key to delegates as `MessageOrigin::WebApp`. Core still mints a token for any contract to any loopback client, as [Trusted calls in 1.3 Single-application host](../1-freenet-mobile-appkit/03-host.md#trusted-calls) describes, until [session admission #5264](https://github.com/freenet/freenet-core/issues/5264) lands | River's chat delegate keys every stored record and signing key by the calling container ([utils.rs](https://github.com/freenet/river/blob/main/delegates/chat-delegate/src/utils.rs)). A call from Atlas reaches an empty namespace |
| Opening another app | Each WebView loads only its own container's path. The WebView host hands any other `/v1/contract/web/<website container key>/` path to EVY, which routes it as [Opening links and alerts in 2.1 EVY shell and curated catalogue](01-catalogue.md#opening-links-and-alerts) describes | Atlas's Open link for River ([state.rs](https://github.com/freenet/atlas/blob/main/common/src/state.rs)) opens River in River's own WebView and data store |
| Replies | Core sends each reply only to the connection that sent the request. When both apps send the same GET, PUT, SUBSCRIBE or UPDATE, Core runs one network operation and replies to each connection ([#1825](https://github.com/freenet/freenet-core/pull/1825), [#2438](https://github.com/freenet/freenet-core/pull/2438)) | River's signing reply reaches only River's WebView |
| Alerts | `crates/mobile` tags each alert with its app's website container key and session, and posts it while another app is on screen | River's alert for Bob's message fires while Atlas is on screen. The tap opens River at "Skate club" |
| System permission | iOS and Android grant notifications to EVY once. Each app still needs its own grant in Core's table, under [Asking for a permission in 1.3 Single-application host](../1-freenet-mobile-appkit/03-host.md#asking-for-a-permission) | Bob allows River's notifications. Atlas has no notification grant |

## One app's trouble leaves the other running

| Event in River | River | Atlas |
| --- | --- | --- |
| Alice closes River | River's session ends, and the SDK releases its subscription handles as in [Ending subscriptions in 1.2 Embedded node and mobile SDK](../1-freenet-mobile-appkit/02-sdk.md#ending-subscriptions) | Keeps its session and its index subscription |
| A new River version arrives | Activates at River's next session boundary, as in [Activating a release in 1.3 Single-application host](../1-freenet-mobile-appkit/03-host.md#activating-a-release) | Keeps its session and version |
| River's web content process ends | EVY reloads River in a new session, on `webViewWebContentProcessDidTerminate` on iOS and `onRenderProcessGone` on Android | Keeps running. Android can run both WebViews in one renderer process, so check whether one loss reloads both apps there. Each app keeps its own web storage either way |
| Alice revokes River's `notifications` grant in EVY's settings | River's next alert request returns denied | Its grants are unchanged |

Two open Core issues let one app's delegate affect another app's delegate on the same node:

- All delegates share one node-wide notification queue of 1,000 entries. Core drops new entries without an error when it is full ([#5561](https://github.com/freenet/freenet-core/issues/5561)). A delegate that watches a busy contract can make River's chat delegate miss Bob's message.
- Core sets no quota on local-scope secrets ([#5560](https://github.com/freenet/freenet-core/issues/5560)). Background runs write in that scope, as [Core needs](#core-needs) describes. A delegate that adds to a secret on every notification can fill the phone's storage for both apps.

While EVY is in the foreground, both WebViews stay loaded and keep their sessions and subscriptions. When EVY goes to the background, the node stops for both apps, as [Foreground lifecycle in 1.1 Mobile feasibility and supported profiles](../1-freenet-mobile-appkit/01-feasibility.md#foreground-lifecycle) describes. Both apps count against the node-wide caps in [Cellular budget contract in 1.8 Thin-peer role and cellular data budgets](../1-freenet-mobile-appkit/08-thin-peer.md#cellular-budget-contract), and a cap pauses both apps together.

## Apps that bundle the same delegate

A delegate key comes from its code hash and parameters ([1.7 Upgrades and migration](../1-freenet-mobile-appkit/07-migration.md#component-identity-and-re-keying)). River's chat delegate has empty parameters, so any app that bundles it unchanged gets River's key. Core shares these by delegate key, whichever app made the call:

- delegate subscriptions, keyed by contract and delegate ([redb.rs](https://github.com/freenet/freenet-core/blob/main/crates/core/src/contract/storages/redb.rs))
- the context a delegate keeps between calls, cached by delegate key for 10 minutes ([#4049](https://github.com/freenet/freenet-core/pull/4049))
- wake-ups, lifecycle runs and notification runs, and the secrets they write, which all sit in one `SecretScope::Local` ([Core needs](#core-needs))

So in step 1 of [Installing a copy in 1.4 Application bundles](../1-freenet-mobile-appkit/04-bundles.md#installing-a-copy), the installation interface works out each delegate key from `components` in `app_definition.json`. It refuses an app whose delegate key matches an installed app's key, and names that app on the screen.

## Forgetting one app

[Forget in 1.5 Identity, keys and local protection](../1-freenet-mobile-appkit/05-identity.md#forget) deletes the node encryption key, which Atlas's records also depend on in EVY. So on EVY each app gets its own secret scope.

| Step | Who | Rule |
| --- | --- | --- |
| 1. Create | `crates/mobile` | On River's first start in EVY, create a random 32-byte secret for River. Store it in the iOS Keychain or Android Keystore with the settings in [Node encryption key in 1.5 Identity, keys and local protection](../1-freenet-mobile-appkit/05-identity.md#node-encryption-key) |
| 2. Run | Core | Run River's delegates under Core's existing `SecretScope::User`, built from River's secret. Its key derives only from that secret ([user.rs](https://github.com/freenet/freenet-core/blob/main/crates/core/src/wasm_runtime/secrets_store/user.rs), from hosted mode in [#4381](https://github.com/freenet/freenet-core/issues/4381)) |
| 3. Forget | `crates/mobile` and EVY | Delete River's secret first. River's `room:<vk>` slots and `rooms_meta` are unreadable at once, including copies the flash storage keeps. Then delete River's secret files, grants and WebView data store, and report failures<br>--> Produces an Atlas that still opens with its data and session |

Each app's scope follows these rules:

- `crates/mobile` sets Core's `per-user-inactive-ttl` setting to 0, which turns off hosted mode's 30-day sweep ([sweep.rs](https://github.com/freenet/freenet-core/blob/main/crates/core/src/wasm_runtime/secrets_store/sweep.rs), [#4561](https://github.com/freenet/freenet-core/issues/4561)). River keeps its data when Alice skips it for a month. Hosted nodes reclaim a user's secrets on purpose ([#5105](https://github.com/freenet/freenet-core/issues/5105)).
- Each app's scope keeps Core's 4 MiB per-user quota ([quota.rs](https://github.com/freenet/freenet-core/blob/main/crates/core/src/wasm_runtime/secrets_store/quota.rs)), set with Core's `per-user-secret-quota` setting or `SecretsStore::with_user_quota`. One hosted River user reached 3,998.5 KiB of it, from room copies in 27 delegate generations ([river#586](https://github.com/freenet/river/issues/586)). River stays under it by retiring old versions as [Retiring the old version in 1.7 Upgrades and migration](../1-freenet-mobile-appkit/07-migration.md#retiring-the-old-version) describes. Measure River's `room:<vk>` slots and `rooms_meta` against it.
- Host records in [What the key protects in 1.5 Identity, keys and local protection](../1-freenet-mobile-appkit/05-identity.md#what-the-key-protects) use a key from the node encryption key. Derive River's from River's secret, so forget covers them.
- Core writes every grant under `UserScope::Node`, as [Base authorization and device access in 1.3 Single-application host](../1-freenet-mobile-appkit/03-host.md#base-authorization-and-device-access) shows. Forget deletes River's grants by River's container key, because grants are not encrypted.
- On lock, [Locking and unlocking in 1.5 Identity, keys and local protection](../1-freenet-mobile-appkit/05-identity.md#locking-and-unlocking) wipes the node encryption key from memory. `crates/mobile` wipes the per-app secrets the same way. [The backup file in 1.5 Identity, keys and local protection](../1-freenet-mobile-appkit/05-identity.md#the-backup-file) needs to carry River's user-scope secrets.

### Core needs

- A user scope on a connection without hosted mode. Core builds the user scope only in hosted mode, from a `userToken` that it honors only from loopback with `X-Forwarded-Proto: https` ([websocket.rs](https://github.com/freenet/freenet-core/blob/main/crates/core/src/client_events/websocket.rs)). Hosted mode also turns delegate capabilities off.
- A per-app user scope in notification, lifecycle, wake-up and inter-delegate runs ([#5736](https://github.com/freenet/freenet-core/issues/5736)). Core runs all of these under `SecretScope::Local` ([contract.rs](https://github.com/freenet/freenet-core/blob/main/crates/core/src/contract.rs)). Until then, River's chat delegate sees none of River's per-app secrets when Bob's message wakes it.

## Acceptance

- On iOS and Android, River and Atlas run on one thin-peer node, each in its own data store. After a restart, River still has its notification consent, and Atlas's store does not hold it.
- On iOS and Android, Atlas's calls reach delegates as Atlas. Atlas never receives River's replies or reads Alice's `room:<vk>` slots, and its Open link for River opens River's own WebView. With Atlas on screen, Bob's "Skate session Saturday?" reaches River and raises River's alert.
- On iOS and Android, closing River, updating River, reloading River after its web content process ends, or revoking River's `notifications` grant leaves Atlas's session and index subscription running. The same holds with the apps swapped.
- On iOS and Android, Bob's "Skate session Saturday?" wakes River's chat delegate in River's own scope, and the delegate reads River's secrets.
- On iOS and Android, a fixture app whose delegate watches a contract that updates many times a second leaves River's alert for Bob's message on time. A fixture delegate that adds to a secret on every notification stops at its quota, and River and Atlas keep running.
- On iOS and Android, both apps together stay inside the node-wide caps from [1.8 Thin-peer role and cellular data budgets](../1-freenet-mobile-appkit/08-thin-peer.md#cellular-budget-contract), and a cap pauses both.
- On iOS and Android, a test app that bundles River's chat delegate unchanged is refused at installation.
- On iOS and Android, forgetting River makes River's secrets unreadable before any file is deleted, removes River's grants and data store, and leaves Atlas opening with its data.
