# Plan 2.6: Navigation and application management

## Purpose

Own validated deep-link routing, app management and app-scoped diagnostics.

## Prerequisites

The shell in [2.1](01-catalogue.md) and canonical authority, installation and permission interfaces in [2.2](02-sessions.md), [2.3](03-installation-and-updates.md) and [2.4](04-permissions.md).

## Routes, handoffs and management

- Treat links as proposed routes or actions. Verify the destination app and arguments, then obtain required consent before private access. A River invite selects a room and asks the user to join. Arbitrary contract references open an inspection view.
- Keep local-node websites inside the in-app WebView. Backgrounding stops the node and its loopback endpoint. External browsers require a separately supported remote/hosted endpoint. Recorded related Core work is [hosted mode #4381](https://github.com/freenet/freenet-core/issues/4381).
- Treat a native distribution link as a publisher pointer. Web/native handoffs require explicit identity authorization and fresh sessions under the host rules.
- Show publisher, installed publication, pending update, migration state, grants and retained data outside publisher-authored UI. Separate removing an app from deleting its data. Apply [1.5's forget/export policy](../1-freenet-mobile-appkit/05-identity.md) and report deletion failures.
- Route supported notification taps to a verified app and refresh state. Show [1.1's foreground message-alert scope](../1-freenet-mobile-appkit/01-feasibility.md#scope-and-acceptance). Keep private message content out of locked-device previews.
- Export diagnostics using [host redaction rules](../1-freenet-mobile-appkit/03-host.md#diagnostics). Include app/release identity, node role, last observation, pending outcomes, storage and budget failures.

## Acceptance

Valid invites reach the intended session, malformed or substituted references fail visibly, and handoffs preserve authority boundaries. Revocation invalidates privileged access. Management and diagnostic screens pass keyboard, focus, large-text and screen-reader tests on real devices.

[Payments 3.4](../3-attribution-remuneration-payment/04-payment.md) owns the authenticated host checkout adapter, web-to-native handoff, return and reconciliation. It has a separate milestone 3 acceptance gate. Broader recovery in [5.2](../5-optional-extensions/02-recovery.md) and [device sync 5.3](../5-optional-extensions/03-sync-and-collaboration.md) are optional. Restart durability, base identity protection and supported migrations remain required foundation behavior.
