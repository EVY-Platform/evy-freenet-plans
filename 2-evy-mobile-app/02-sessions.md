# Plan 2.2: Multi-application sessions and authority

## Purpose

Run several applications with separate authority and callbacks on one embedded thin node. River and Atlas each use an isolated WebView session with storage, grants and callbacks scoped to the app, user and session.

## Prerequisites

The released [single-app host in 1.3](../1-freenet-mobile-appkit/03-host.md) and verified caller admission on the pinned Core build. [Identity 1.5](../1-freenet-mobile-appkit/05-identity.md) supplies key and record protection. Mobile profiles inherit [1.10's thin-peer and cellular gate](../1-freenet-mobile-appkit/10-thin-peer.md).

## Multi-app sessions

Apply [1.3's session bindings and bridge rules](../1-freenet-mobile-appkit/03-host.md#who-controls-what) separately to each app. Bind its full container identity, verified content reference, user, installation and session generation through trusted host authority. Use the canonical [1.3 admission and permission evidence](../1-freenet-mobile-appkit/03-host.md#host-admission-and-permission-dependencies) to verify every supported access path.

- Keep cookies, web storage, caches, file access and native handles isolated by application and user, with their declared lifetime across reloads and restarts.
- Authenticate frames, WebView messages, native calls, loopback calls and alternate API paths before forwarding work.
- Route targeted replies and autonomous private events only to authorized sessions. Reject expired-session callbacks.
- Preserve the other applications' authorized work when one session closes. [Lifecycle 2.5](05-lifecycle.md) schedules their remaining demand.

## Delegate namespace policy

On a device node, Core partitions delegate secrets by the full delegate key. Two apps using identical delegate code and parameters therefore address the same store. A host-side app label alone supplies no storage separation.

Admit that combination only when the delegate has an audited multi-app protocol that authorizes the attested caller, separates private records and routes private results safely. Shared identity or records also require explicit user authorization under [2.4](04-permissions.md). Otherwise the host rejects the conflicting installation on its shared node. Multi-user protocols must verify the user authority they use for record selection. Payload-selected namespaces fail admission tests.

The [concrete delegate protocol in 1.6](../1-freenet-mobile-appkit/06-data-and-operations.md#delegate-requests-and-results) defines immediate-caller `MessageOrigin` handling, delegate-to-delegate calls and origin-free events. The host supplies verified user, installation and session bindings. [1.3](../1-freenet-mobile-appkit/03-host.md#who-controls-what) also records the hosted profile's shell-token binding that requires verification before use.

## Acceptance

- Run River and Atlas on one thin-peer node with separate WebViews. Cross-app reads, callbacks and secret access fail.
- Forged app identities, frames, bridge messages, loopback requests and expired sessions fail admission. Each required browser or native admission path passes on the pinned Core build before that profile ships.
- Identical delegate code and parameter references pass the explicit sharing policy or reject installation. Exercise app and user separation, caller-selected namespaces and unauthorized private events.
- Reload and termination preserve only authorized records. Closing or reopening one session preserves the other's authority and eligible demand.
- Resource-exhaustion and malicious-input tests contain failure to the affected app. Shared traffic passes 1.10's cellular budgets.

The combined product evidence belongs to [2.7](07-acceptance.md).
