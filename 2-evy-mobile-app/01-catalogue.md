# Plan 2.1: EVY shell and curated catalogue

## Purpose

Own home, app switching, settings, the fixed River-and-Atlas catalogue and its host-release process. Each app supplies its own ordinary signed website archive and controls its own UI and orchestration.

## Prerequisites

Milestone 1 release acceptance in [1.9](../1-freenet-mobile-appkit/09-release.md) and host interfaces [2.2](02-sessions.md), [2.3](03-installation-and-updates.md) and [2.4](04-permissions.md). Shell development can use pinned fixtures while those gates complete.

## Catalogue and shell

Record River's and Atlas's verified full website container IDs and supported protocol profiles in the release configuration. Ship those identities as hardcoded catalogue entries. Resolve each to a verified signed website in its own isolated in-app WebView session. Apps share one embedded thin node. App-specific native screens arrive through installed-app releases.

| Home area | Behavior |
| --- | --- |
| Curated apps | Open River or Atlas and show installation/update state. |
| Recent activity | Resume a retained app route with lock-screen privacy controls. |
| Open a reference | Validate a supported app link or inspect a contract reference under [2.6](06-navigation.md). |
| Account and settings | Show app grants, storage, recovery coverage, foreground alert scope and cellular budget status. |

Atlas runs as a hosted application in this milestone. [Discovery 5.4](../5-optional-extensions/04-discovery.md) separately adds search providers to EVY's home, including Atlas, and signed catalogue updates. Optional [SDUI](../README.md#4-optional-sdui) belongs to milestone 4.

## Acceptance

A clean installation verifies and opens River and Atlas, switches between their own UIs and resumes a compatible cached release offline. Publisher identity and access decisions appear in host-controlled screens. Both verified website container IDs and tested release profiles are required release inputs.
