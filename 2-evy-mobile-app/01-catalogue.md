# 2.1 EVY shell and curated catalogue

## Repositories

| Repository | Role | Work in this plan |
| --- | --- | --- |
| [evy](https://github.com/EVY-Platform/evy) | Modified | `ios/` app rebuilt on the AppKit host and a new `android/` app: home, curated catalogue, settings, release configuration, store index and age gate |
| `freenet-appkit` | Used | WebView host, installation interface and Swift and Kotlin SDK from milestone 1 (Freenet mobile AppKit) |
| [freenet-core](https://github.com/freenet/freenet-core) | Used | Session authority in `crates/mobile` from milestone 1 (Freenet mobile AppKit) |
| [river](https://github.com/freenet/river) | Used | Verified website container ID as a hardcoded catalogue entry |
| [atlas](https://github.com/freenet/atlas) | Modified | Website packaged with host metadata under 1.4 Application bundles; verified website container ID as a hardcoded catalogue entry; filtering, reporting and blocking for submitted records in Atlas's own UI |

## Purpose

Own the EVY shell: home, the hardcoded River and Atlas catalogue entries, settings, the release configuration and the store requirements for a host with a catalogue of apps. Open each app through the [1.3 Single-application host](../1-freenet-mobile-appkit/03-host.md). Each app supplies its own ordinary signed website archive and controls its own UI and orchestration.

## Prerequisites

[1.9 Testing and release](../1-freenet-mobile-appkit/09-testing-and-release.md), with the [1.3 Single-application host](../1-freenet-mobile-appkit/03-host.md) and [1.4 Application bundles](../1-freenet-mobile-appkit/04-bundles.md) it accepts.

## Catalogue and shell

Record River's and Atlas's verified full website container IDs and supported protocol profiles in the release configuration. Ship those identities as hardcoded catalogue entries. Resolve each to a verified signed website and open it in an in-app WebView through the 1.3 Single-application host. Apps share one embedded thin node. App-specific native screens arrive through installed-app releases.

| Home area | Behavior |
| --- | --- |
| Curated apps | Open River or Atlas and show installation/update state. |
| Recent activity | Resume a retained app route with lock-screen privacy controls. |
| Open a reference | Validate a supported app link or inspect a contract reference under [2.6 Navigation and application management](06-navigation.md). |
| Account and settings | Show recovery coverage and foreground alert scope. Hold the settings views that other plans in this milestone add. |

Atlas runs as a hosted application in this milestone. [5.4 Discovery and catalogue extensions](../5-optional-extensions/04-discovery.md) adds search providers to EVY's home, including Atlas, and signed catalogue updates.

## Atlas website packaging

Package Atlas's own `index.html`, browser code and assets as an ordinary signed website. Include required contract and delegate artifacts and host metadata under [1.4 Application bundles](../1-freenet-mobile-appkit/04-bundles.md). Verify installation and compatible updates through Atlas's own UI on iOS and Android.

## Store requirements

EVY downloads River and Atlas at run time and opens them, so [App Store Review Guideline 4.7](https://developer.apple.com/app-store/review/guidelines/) (mini apps and mini games) applies to it. On Google Play, River's and Atlas's web code runs as interpreted code in a WebView, which the [Device and Network Abuse policy](https://support.google.com/googleplay/android-developer/answer/9888379) allows. The user content rules in App Store Guideline 1.2 and the [Play User Generated Content policy](https://support.google.com/googleplay/android-developer/answer/9876937) apply to each app's messages and records. The rules EVY shares with River's own store build are in [store requirements in 1.9 Testing and release](../1-freenet-mobile-appkit/09-testing-and-release.md#store-requirements).

EVY does the following for each catalogue app on iOS and Android:

| Requirement | Source | What EVY does |
| --- | --- | --- |
| Index of apps | Guideline 4.7.4 | Generate the index from the release configuration. List each app's name, publisher, age rating, pinned website container ID and a universal link (iOS) or App Link (Android) that opens it through [2.6 Navigation and application management](06-navigation.md). Show the index in settings and attach it to the review notes. |
| Age rating and age gate | Guideline 4.7.5 | Record an age rating for each app in the release configuration. Mark apps rated above EVY's own rating on home. Open them only after the user's declared age meets the app's rating. |
| Moderation and reporting | Guidelines 1.2 and 4.7.1; Play User Generated Content policy | Each app filters objectionable content, lets users report content and block users, and answers reports in its own UI, as River does in 1.9 Testing and release. EVY lists an app only after these work on both platforms. |
| Native features | Guidelines 4.7.2 and 4.7.3 | Apps reach native features only through the host bridge. Each use passes the [permission prompt in 1.3 Single-application host](../1-freenet-mobile-appkit/03-host.md#asking-for-a-permission) for that app. List each bridged feature, such as notifications and clipboard, in the review notes to ask Apple's permission. |

## Acceptance

- A clean installation verifies and opens River and Atlas. Both verified website container IDs, age ratings and tested release profiles are required release inputs.
- On iOS and Android, the store index lists River and Atlas from the release configuration, and each link opens its app. An app rated above EVY's rating opens only after the age check. Reporting and blocking work in both apps' own UIs, and each native feature use reaches the 1.3 Single-application host prompt.
