# 2.1 EVY shell and curated catalogue

## Repositories

| Repository | Role | Work in this plan |
| --- | --- | --- |
| [evy](https://github.com/EVY-Platform/evy) | Modified | `ios/` app rebuilt on the AppKit host and a new `android/` app: home, curated catalogue, settings and release configuration |
| `freenet-appkit` | Used | Host, sessions, installation interface and SDK from milestone 1 (Freenet mobile AppKit) |
| [river](https://github.com/freenet/river) | Used | Verified website container ID as a hardcoded catalogue entry |
| [atlas](https://github.com/freenet/atlas) | Used | Verified website container ID as a hardcoded catalogue entry |

## Purpose

Own home, app switching, settings, the fixed River-and-Atlas catalogue and its host-release process. Each app supplies its own ordinary signed website archive and controls its own UI and orchestration.

## Prerequisites

[1.9 Developer package and release acceptance](../1-freenet-mobile-appkit/09-release.md), and the host interfaces [2.2 Multi-application sessions and authority](02-sessions.md), [2.3 Installation and updates](03-installation-and-updates.md) and [2.4 Identity, permissions and device access](04-permissions.md). Shell development can use pinned fixtures while those gates complete.

## Catalogue and shell

Record River's and Atlas's verified full website container IDs and supported protocol profiles in the release configuration. Ship those identities as hardcoded catalogue entries. Resolve each to a verified signed website in its own isolated in-app WebView session. Apps share one embedded thin node. App-specific native screens arrive through installed-app releases.

| Home area | Behavior |
| --- | --- |
| Curated apps | Open River or Atlas and show installation/update state. |
| Recent activity | Resume a retained app route with lock-screen privacy controls. |
| Open a reference | Validate a supported app link or inspect a contract reference under [2.6 Navigation and application management](06-navigation.md). |
| Account and settings | Show app grants, storage, recovery coverage, foreground alert scope and cellular budget status. |

Atlas runs as a hosted application in this milestone. [5.4 Discovery and catalogue extensions](../5-optional-extensions/04-discovery.md) separately adds search providers to EVY's home, including Atlas, and signed catalogue updates. SDUI is optional and belongs to [milestone 4 (SDUI)](../README.md#4-sdui).

## Acceptance

A clean installation verifies and opens River and Atlas, switches between their own UIs and resumes a compatible cached release offline. Publisher identity and access decisions appear in host-controlled screens. Both verified website container IDs and tested release profiles are required release inputs.
