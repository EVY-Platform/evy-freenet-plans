# 2.3 Testing and release

## Repositories

| Repository | Role | Work in this plan |
| --- | --- | --- |
| [evy](https://github.com/EVY-Platform/evy) | Modified | Two-app case suite for the `ios/` and `android/` apps. TestFlight and Play internal-testing builds, store listing entries, App Review notes with the store index and bridged permissions, and published results |
| `freenet-appkit` | Used | Scenario harness and [store build checks](../1-freenet-mobile-appkit/09-testing-and-release.md#store-build-checks) from 1.9 Testing and release, run on EVY's builds |
| [freenet-core](https://github.com/freenet/freenet-core) | Used | Per-app sessions and per-app secret scope in `crates/mobile` from [2.2 Two apps on one node](02-shared-node.md), on the pinned Core build in the thin-peer role |
| [freenet-migrate](https://github.com/freenet/freenet-migrate) | Used | River's migration on the first start of a new version, as in [1.7 Upgrades and migration](../1-freenet-mobile-appkit/07-migration.md) |
| [river](https://github.com/freenet/river) | Used | River's own web UI, and a newer River version for the update case |
| [atlas](https://github.com/freenet/atlas) | Used | Atlas's own web UI, and an Atlas build that reads the separate test index from 1.9 Testing and release |

## Purpose

This plan tests milestone 2 (EVY mobile app) on real iOS and Android phones, then releases EVY to TestFlight and Play internal testing. [2.1 EVY shell and curated catalogue](01-catalogue.md) builds EVY, and [2.2 Two apps on one node](02-shared-node.md) runs River and Atlas on one node in the thin-peer role.

Alice and Bob each have River and Atlas in EVY. Alice owns "Skate club" in River, and Bob joins it from her invite link. While River runs, Alice browses Atlas. Each case checks that what happens to one app leaves the other as it was.

EVY ships only after every [release test](#release-tests) in this plan passes. These are the only release tests of milestone 2 (EVY mobile app).

## What runs

| | River | Atlas |
| --- | --- | --- |
| Web UI | River's signed web UI in its own WebView | Atlas's signed web UI in its own WebView |
| What the user does | Alice and Bob read and send messages in "Skate club" and get message alerts | Alice browses the index, searches it, turns safe search off and taps Open on an entry |
| Node calls | Room contract and chat delegate | GET and SUBSCRIBE on the index contract, with no identity, writes or delegate ([ui/src/main.rs](https://github.com/freenet/atlas/blob/main/ui/src/main.rs)) |
| Web storage | `river_receive_times` and `river_notification_prompted` in `localStorage` | `atlas.safe_search` in `localStorage` |
| Permissions | `notifications` and `clipboard`, both optional | None |

The Atlas UI build embeds the index key that [`atlasctl key`](https://github.com/freenet/atlas/blob/main/cli/src/main.rs) prints. When the index re-keys, Atlas publishes a new version that reads the new key. The Atlas update case uses a build against the separate test index from [1.9 Testing and release](../1-freenet-mobile-appkit/09-testing-and-release.md#atlas-today-and-pinned-identity), so the published Atlas index stays as it is.

## Two-app cases

Every case runs on iOS and Android, with River and Atlas open in one EVY install.

| Case | Passing result |
| --- | --- |
| River cases with Atlas open | The [River acceptance cases in 1.9 Testing and release](../1-freenet-mobile-appkit/09-testing-and-release.md#river-acceptance-cases) pass inside EVY while Atlas stays open and subscribed to the index. |
| Update one app | EVY installs River version 13 while Atlas is open. River runs its migration on first start and keeps "Skate club". A failed migration keeps the version 12 data, and River runs it again on the next start. Atlas stays open throughout. A new Atlas version with a new index key leaves River's session and drafts as they were. |
| Revoke one grant | Alice revokes River's `notifications` grant in EVY settings. River's alerts stop at once, and Atlas stays open. |
| Close or crash one app | The cases in [One app's trouble leaves the other running in 2.2 Two apps on one node](02-shared-node.md#one-apps-trouble-leaves-the-other-running) pass with "Skate club" open in River and Atlas refreshing its index. |
| Kill EVY | Bob kills EVY while "Skate session Saturday?" is sending and Atlas is refreshing. After restart the message is in "Skate club" once and Atlas shows the index. |
| Forget River | Alice forgets River in EVY settings, as in [Forgetting one app in 2.2 Two apps on one node](02-shared-node.md#forgetting-one-app). River's delegate records are unreadable at once, and Atlas opens with safe search as Alice left it. |

## Store requirements

EVY downloads River and Atlas after it is installed, so [App Store Review Guideline 4.7](https://developer.apple.com/app-store/review/guidelines/) (mini apps) applies. On Google Play, the apps' web code runs in a WebView, which the [Device and Network Abuse policy](https://support.google.com/googleplay/android-developer/answer/9888379) allows. The policy sources are the versions published on 2026-09-30.

| Guideline | Rule | What EVY does |
| --- | --- | --- |
| 4.7.1 | Filter objectionable content, take reports, answer them in time and block abusive users | River keeps its moderation from 1.9 Testing and release. Atlas has its safe search and Report button from [Atlas in EVY in 2.1 EVY shell and curated catalogue](01-catalogue.md#atlas-in-evy). |
| 4.7.2 | Expose no native API to downloaded software without Apple's permission | The review notes list each bridged permission, `notifications` and `clipboard`, and ask Apple for permission. |
| 4.7.3 | Share no data or permission with an app without the user's consent each time | Each grant belongs to one app, as in [Sessions and routing in 2.2 Two apps on one node](02-shared-node.md#sessions-and-routing). A grant for River never answers a request from Atlas. |
| 4.7.4 | Give an index of apps with universal links to each | The [store index in 2.1 EVY shell and curated catalogue](01-catalogue.md#store-index-and-age-check) lists River and Atlas, with a universal link on iOS and an App Link on Android to each. The review notes include the store index. |
| 4.7.5 | Mark apps above EVY's age rating and restrict access by age | The age mark and age check in [Store index and age check in 2.1 EVY shell and curated catalogue](01-catalogue.md#store-index-and-age-check). |

EVY shares the other rules and the store build checks with River's store build in [store requirements in 1.9 Testing and release](../1-freenet-mobile-appkit/09-testing-and-release.md#store-requirements). These rows change for EVY:

| Row in 1.9 Testing and release | What changes for EVY |
| --- | --- |
| Downloaded code | EVY pins the website container keys of River and Atlas from `catalogue.json`. |
| Support URL and child safety | EVY's store listings link to EVY's support page. EVY declares River's child-safety standards in Play Console. |
| Large downloads | EVY asks before each app's first download and states its size. |
| Review notes | The notes also hold the store index and the list of bridged permissions. |
| Data safety | Declare what River and Atlas send to peers. Atlas sends only index requests and the phone's IP address. |

## Release tests

Every test runs on iOS and Android, with the phone in the thin-peer role.

| Release test | Passing evidence |
| --- | --- |
| Two-app cases | Every [two-app case](#two-app-cases) passes. |
| Milestone 2 plans | The acceptance of [2.1 EVY shell and curated catalogue](01-catalogue.md#acceptance) and of [2.2 Two apps on one node](02-shared-node.md#acceptance) passes on the same EVY build. |
| Thin role and budgets | The [acceptance in 1.8 Thin-peer role and cellular data budgets](../1-freenet-mobile-appkit/08-thin-peer.md#acceptance) passes with both apps subscribed, on the pinned Core build. |
| Accessibility | Keyboard, focus, large text and screen-reader flows work in River and Atlas inside EVY. |
| Distribution | EVY's TestFlight and Play internal-testing builds pass review, and every [store requirement](#store-requirements) holds. |

## Evidence

Publish results with EVY's build numbers, River's and Atlas's website container keys and versions, the Core revision, devices, OS versions, network conditions and redacted logs.

## Acceptance

- On iOS and Android, every release test passes on one EVY build, and the results are published with the evidence above.
- EVY's TestFlight build on iOS and Play internal-testing build on Android pass review, with the store index and the bridged permissions in the review notes.
