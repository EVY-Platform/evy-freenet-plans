# 2.2 Testing and release

## Repositories

| Repository | Role | Work in this plan |
| --- | --- | --- |
| [evy](https://github.com/EVY-Platform/evy) | Modified | iOS and Android tests and release builds |
| [freenet-appkit](https://github.com/glesage/freenet-appkit) | Used | Scenario harness and store checks |
| [freenet-core](https://github.com/freenet/freenet-core) | Used | Shared-node build and compatibility |
| [freenet-migrate](https://github.com/freenet/freenet-migrate) | Used | River migration fixture |
| [river](https://github.com/freenet/river) | Used | River update fixture |
| [atlas](https://github.com/freenet/atlas) | Used | Atlas catalogue fixture |

## Purpose

This plan tests milestone 2 (EVY mobile app) on real iOS and Android phones, then releases EVY to TestFlight and Play internal testing. [2.1 EVY catalogue and app hosting](01-catalogue-and-hosting.md) builds EVY and runs River and Atlas on one node in the thin-peer role.

Alice and Bob each have River and Atlas in EVY. Alice owns "Skate club" in River, and Bob joins it from her invite link. While River runs, Alice browses Atlas. Each case checks that what happens to one app leaves the other as it was.

EVY ships only after every [release test](#release-tests) in this plan passes. These are the only release tests of milestone 2 (EVY mobile app).

## What runs

| | River | Atlas |
| --- | --- | --- |
| Web UI | River's signed web UI in its own WebView | Atlas's signed web UI in its own WebView |
| What the user does | Alice and Bob read and send messages in "Skate club" and get message alerts | Alice browses the index, searches it, turns safe search off and taps Open on an entry |
| Node calls | Room contract and chat delegate | GET and SUBSCRIBE on the index contract, with no identity, writes or delegate ([ui/src/main.rs](https://github.com/freenet/atlas/blob/main/ui/src/main.rs)) |
| Web storage | The shell keeps River's notification consent as `freenet_notify:<website container key>`, as in [Web storage in 2.1 EVY catalogue and app hosting](01-catalogue-and-hosting.md#web-storage) | None. Safe search returns to on at each load, as in [Atlas in EVY in 2.1 EVY catalogue and app hosting](01-catalogue-and-hosting.md#atlas-in-evy) |
| Permissions | `notifications`, optional | None |

Atlas's UI build pins the index key in `ATLAS_INDEX_ID`, as [Atlas today and pinned identity in 1.9 Testing and release](../1-freenet-mobile-appkit/09-testing-and-release.md#atlas-today-and-pinned-identity) describes. When the index re-keys, Atlas publishes a new version that reads the new key. The Atlas update case uses a build against the separate test index from that section, so the published Atlas index stays as it is.

## Two-app cases

Every case runs on iOS and Android, with River and Atlas open in one EVY install.

| Case | Passing result |
| --- | --- |
| River cases with Atlas open | The [River acceptance cases in 1.9 Testing and release](../1-freenet-mobile-appkit/09-testing-and-release.md#river-acceptance-cases) pass inside EVY while Atlas stays open and subscribed to the index. |
| Invite links | With Atlas on screen, Bob taps Alice's invite once as an EVY link, once as a `freenet:` link and once as a freenet.org/open link, the three forms in [Opening links and alerts in 2.1 EVY catalogue and app hosting](01-catalogue-and-hosting.md#opening-links-and-alerts). EVY switches to River, and River shows its join screen for "Skate club". Atlas keeps its session. The universal link on iOS and the App Link on Android open EVY from the store builds. |
| Update one app | EVY installs a newer River release while Atlas is open. River runs its migration on first start and keeps "Skate club". A failed migration keeps the older release's data, and River runs it again on the next start. Atlas stays open throughout. A new Atlas version with a new index key leaves River's session and drafts as they were. |
| First run | Bob runs River for the first time in EVY. The host asks for `notifications` once. The notification modal's Enable button and Bob's first send then raise no prompt. Bob opens Atlas, and the host asks nothing. |
| Revoke one grant | Alice revokes River's `notifications` grant in EVY settings. River's alerts stop at once, and Atlas stays open. |
| Close or crash one app | The cases in [App lifecycle in 2.1 EVY catalogue and app hosting](01-catalogue-and-hosting.md#app-lifecycle) pass with "Skate club" open in River and Atlas refreshing its index. |
| Busy delegate | A fixture app's delegate watches a contract that updates many times a second. Bob's "Skate session Saturday?" still raises River's alert on time ([#5561](https://github.com/freenet/freenet-core/issues/5561)). A fixture delegate that adds to a secret on every notification stops at its quota ([#5560](https://github.com/freenet/freenet-core/issues/5560)), and River and Atlas keep running. |
| Kill EVY | Bob kills EVY while "Skate session Saturday?" is sending and Atlas is refreshing. After restart the message is in "Skate club" once and Atlas shows the index. |
| Forget River | Alice forgets River in EVY settings, as in [Forgetting one app in 2.1 EVY catalogue and app hosting](01-catalogue-and-hosting.md#forgetting-one-app). River's delegate records are unreadable at once, and Atlas opens and shows the index. |

## Store requirements

EVY downloads River and Atlas after it is installed, so [App Store Review Guideline 4.7](https://developer.apple.com/app-store/review/guidelines/) (mini apps) applies to their web UIs. River's and Atlas's contracts and River's chat delegate run as Wasm in Pulley outside the WebView, so Guideline 2.5.2 and [DPLA](https://developer.apple.com/support/terms/apple-developer-program-license-agreement/) 3.3.1(B) apply to them. On Google Play, the [Device and Network Abuse policy](https://support.google.com/googleplay/android-developer/answer/16559646) allows code that runs in a WebView or an interpreter. The policy sources are the versions published on 2026-09-30.

| Guideline | Rule | What EVY does |
| --- | --- | --- |
| 4.7.1 | Filter objectionable content, take reports, answer them in time and block abusive users | River keeps its moderation from [Store requirements in 1.9 Testing and release](../1-freenet-mobile-appkit/09-testing-and-release.md#store-requirements). Atlas has its safe search and Report button from [Atlas in EVY in 2.1 EVY catalogue and app hosting](01-catalogue-and-hosting.md#atlas-in-evy). |
| 4.7.2 | Expose no native API to downloaded software without Apple's permission | The review notes list each bridged native API, the `notifications` permission and clipboard writes, and ask Apple for permission. |
| 4.7.3 | Share no data or permission with an app without the user's consent each time | Each grant belongs to one app, as in [Permissions in 2.1 EVY catalogue and app hosting](01-catalogue-and-hosting.md#permissions). A grant for River never answers a request from Atlas. |
| 4.7.4 | Give an index of apps with universal links to each | The [store index in 2.1 EVY catalogue and app hosting](01-catalogue-and-hosting.md#store-index-and-age-check) lists River and Atlas, with a universal link on iOS and an App Link on Android to each. The review notes include the store index. |
| 4.7.5 | Mark apps above EVY's age rating and restrict access by age | The age mark and age check in [Store index and age check in 2.1 EVY catalogue and app hosting](01-catalogue-and-hosting.md#store-index-and-age-check). They compare each entry with `store_age_rating`, which comes from EVY's age rating answers. |

EVY shares the other rules with River's store build in [store requirements in 1.9 Testing and release](../1-freenet-mobile-appkit/09-testing-and-release.md#store-requirements). EVY's iOS and Android builds run every [store build check](../1-freenet-mobile-appkit/09-testing-and-release.md#store-build-checks) and follow the [Core version rule](../1-freenet-mobile-appkit/09-testing-and-release.md#core-version-and-the-network). These rows change for EVY:

| Row in 1.9 Testing and release | What changes for EVY |
| --- | --- |
| Downloaded code | EVY pins the website container keys of River and Atlas from `catalogue.json`. |
| Support URL and child safety | EVY's store listings link to EVY's support page. EVY declares River's child-safety standards in Play Console. |
| Large downloads | EVY asks before each app's first download and states its size. |
| Review notes | The notes also hold the store index and the list of bridged permissions. They cite Guideline 4.7 for River's and Atlas's web UIs, and Guideline 2.5.2 and DPLA 3.3.1(B) for their Wasm in Pulley. |
| Data safety | Declare what River and Atlas send to peers. Atlas sends only index requests and the phone's IP address. |
| EU trader status | Declare EVY's trader status for EU listings. |
| Age rating | Answer App Store Connect's updated age rating questions and Play's content rating questionnaire for EVY. The resulting rating is `store_age_rating` in `catalogue.json`. |
| Minimum OS | EVY's iOS deployment target is 17.0, for the per-app data store in [Web storage in 2.1 EVY catalogue and app hosting](01-catalogue-and-hosting.md#web-storage). EVY's Android `minSdk` stays 28. |
| Core version | On "update the app", EVY shows one message for the whole app, not one per app, with a button to EVY's App Store or Google Play listing. River and Atlas keep showing their stored data meanwhile. |

## Release tests

Every test runs on iOS and Android, with the phone in the thin-peer role. Prompt and notification tests run with the node in network mode, and isolated test networks set their gateways explicitly, as in [River scope in 1.9 Testing and release](../1-freenet-mobile-appkit/09-testing-and-release.md#river-scope).

| Release test | Passing evidence |
| --- | --- |
| Two-app cases | Every [two-app case](#two-app-cases) passes. |
| Catalogue and app hosting | The acceptance of [2.1 EVY catalogue and app hosting](01-catalogue-and-hosting.md#acceptance) passes on the same EVY build. |
| Thin role and budgets | The [acceptance in 1.8 Thin-peer role and cellular data budgets](../1-freenet-mobile-appkit/08-thin-peer.md#acceptance) passes with both apps subscribed, on the pinned Core build. |
| Accessibility | Keyboard, focus, large text and screen-reader flows work in River and Atlas inside EVY. |
| Distribution | EVY's TestFlight and Play internal-testing builds pass review and every store build check, and every [store requirement](#store-requirements) holds. |
| Core version | The [Core version rule in 1.9 Testing and release](../1-freenet-mobile-appkit/09-testing-and-release.md#core-version-and-the-network) holds for EVY's iOS and Android builds. A test peer that requires a newer Core gives "update the app" with River and Atlas open, and EVY shows its update message once. |

## Evidence

Publish results with EVY's build numbers, River's and Atlas's website container keys and versions, the Core revision and the network's `min-compatible-version`, devices, OS versions, network conditions and redacted logs.

## Acceptance

- On iOS and Android, every release test passes on one EVY build, and the results are published with the evidence above.
- EVY's TestFlight build on iOS and Play internal-testing build on Android pass review, with the store index, the bridged permissions and the interpreted-code citations in the review notes.
