# 2.1 EVY shell and curated catalogue

## Repositories

| Repository | Role | Work in this plan |
| --- | --- | --- |
| [evy](https://github.com/EVY-Platform/evy) | Modified | `ios/` app rebuilt on the AppKit host and a new `android/` app: home, curated catalogue, settings and release configuration |
| `freenet-appkit` | Used | WebView host, installation interface and Swift and Kotlin SDK from milestone 1 (Freenet mobile AppKit) |
| [freenet-core](https://github.com/freenet/freenet-core) | Used | Session authority in `crates/mobile` from milestone 1 (Freenet mobile AppKit) |
| [river](https://github.com/freenet/river) | Used | Verified website container ID as a hardcoded catalogue entry |
| [atlas](https://github.com/freenet/atlas) | Modified | Website packaged with host metadata under 1.4 Application bundles; verified website container ID as a hardcoded catalogue entry |

## Purpose

Own the EVY shell: home, the hardcoded River and Atlas catalogue entries, settings and the release configuration. Open each app through the [1.3 Single-application host](../1-freenet-mobile-appkit/03-host.md). Each app supplies its own ordinary signed website archive and controls its own UI and orchestration.

## Prerequisites

[1.9 Developer package and release acceptance](../1-freenet-mobile-appkit/09-release.md), with the [1.3 Single-application host](../1-freenet-mobile-appkit/03-host.md) and [1.4 Application bundles](../1-freenet-mobile-appkit/04-bundles.md) it accepts.

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

## Acceptance

A clean installation verifies and opens River and Atlas. Both verified website container IDs and tested release profiles are required release inputs.
