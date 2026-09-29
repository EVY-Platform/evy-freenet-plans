# 2.6 Navigation and application management

## Repositories

| Repository | Role | Work in this plan |
| --- | --- | --- |
| [evy](https://github.com/EVY-Platform/evy) | Modified | Deep-link validation, app management, notification routing and diagnostics export screens in the iOS and Android apps |
| `freenet-appkit` | Used | Host redaction rules and installation state |
| [freenet-core](https://github.com/freenet/freenet-core) | Used | Forget and export policy in `crates/mobile` from 1.5 Identity, keys and local protection; hosted mode [#4381](https://github.com/freenet/freenet-core/issues/4381) as the reference for external browser handoff |
| [river](https://github.com/freenet/river) | Used | Invite links as the route validation fixture |

## Purpose

Own validated deep-link routing, app management and app-scoped diagnostics.

## Prerequisites

The shell in [2.1 EVY shell and curated catalogue](01-catalogue.md) and canonical authority, installation and permission interfaces in [2.2 Multi-application sessions and authority](02-sessions.md), [2.3 Installation and updates](03-installation-and-updates.md) and [2.4 Identity, permissions and device access](04-permissions.md).

## Routes, handoffs and management

- Treat links as proposed routes or actions. Verify the destination app and arguments, then obtain required consent before private access. A River invite selects a room and asks the user to join. Arbitrary contract references open an inspection view.
- Keep local-node websites inside the in-app WebView. Backgrounding stops the node and its loopback endpoint. External browsers require a separately supported remote/hosted endpoint. Recorded related Core work is [hosted mode #4381](https://github.com/freenet/freenet-core/issues/4381).
- Treat a native distribution link as a publisher pointer. Web/native handoffs require explicit identity authorization and fresh sessions under the host rules.
- Show publisher, installed publication, pending update, migration state, grants and retained data outside publisher-authored UI. Separate removing an app from deleting its data. Apply [forget/export policy in 1.5 Identity, keys and local protection](../1-freenet-mobile-appkit/05-identity.md) and report deletion failures.
- Route supported notification taps to a verified app and refresh state. Show [foreground message-alert scope in 1.1 Mobile feasibility and supported profiles](../1-freenet-mobile-appkit/01-feasibility.md#message-alerts). Keep private message content out of locked-device previews.
- Export diagnostics using the [host redaction rules in 1.3 Single-application host](../1-freenet-mobile-appkit/03-host.md#diagnostics). Include app/release identity, node role, last observation, pending outcomes, storage and budget failures.

## Acceptance

Valid invites reach the intended session, malformed or substituted references fail visibly, and handoffs preserve authority boundaries. Revocation invalidates privileged access. Removing an app keeps its private records. Data deletion is a separate, authorized decision, and failures are reported. Management and diagnostic screens pass keyboard, focus, large-text and screen-reader tests on real devices.
