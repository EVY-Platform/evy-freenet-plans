# Plan 2.7: Multi-application acceptance

## Purpose

Own the River-and-Atlas release suite and product evidence on iOS and Android. Exercise each app's actual web UI in separate sessions on one embedded thin node.

## Prerequisites

[Milestone 1 acceptance](../1-freenet-mobile-appkit/09-release.md), completed plans [2.1](01-catalogue.md), [2.2](02-sessions.md), [2.3](03-installation-and-updates.md), [2.4](04-permissions.md), [2.5](05-lifecycle.md) and [2.6](06-navigation.md), and the [Atlas compatibility fixtures](../1-freenet-mobile-appkit/08-reference-apps.md#atlas-fixture-scope-and-acceptance). The app-specific [Atlas product flows defined in 1.8](../1-freenet-mobile-appkit/08-reference-apps.md#atlas-product-flows-for-the-later-27-gate) become a release gate here.

## Acceptance

- Run River and Atlas concurrently with separate sessions, grants, WebView stores and pending operations on one thin node. Exercise the [River reference flows](../1-freenet-mobile-appkit/08-reference-apps.md#river-acceptance-cases) alongside the [Atlas application flows](../1-freenet-mobile-appkit/08-reference-apps.md#atlas-product-flows-for-the-later-27-gate).
- Forge app IDs, session tokens and stale callbacks. Attempt cross-app access through loopback, bridges and web/native handoffs. Verify the authority failures defined in 2.2.
- Exercise two apps using identical delegate code and parameter bytes. Prove the host's namespace policy protects each app and user before enabling that configuration.
- Stage compatible archives and fail updates through missing content, invalid signatures, conflicting versions, interrupted activation and migrations. Keep each session on a consistent usable release and preserve the other app's work.
- Close, suspend or exhaust resources in one app while the other remains usable within its allocation. Verify released subscriptions cease consuming network budget under the SDK's tested cleanup strategy. Releasing one app's subscription preserves the other's eligible demand.
- Remove an app and verify that its private records remain under [1.6's retention rules](../1-freenet-mobile-appkit/06-data-and-operations.md#values-and-local-storage). Exercise a separate authorized data-deletion decision and report deletion failures under 1.5.
- Terminate during pending submissions and recover by refresh and reconciliation. Preserve operation IDs, exact payloads and originating release references.
- Pass node-wide and per-app cellular tests, including [1.10's two-app continuous-publish cap cases](../1-freenet-mobile-appkit/10-thin-peer.md#acceptance), serving-peer loss, foreground lifecycle and accounting checks. Per-app caps preserve the other app's eligible demand. A node-wide cap stops both streams within the shared reserve. Unsupported thin negotiation stays visible and preserves the configured role.
- Test inaccessible archives, offline caches, revoked permissions, invalid links, native/external handoffs and accessibility through both apps' actual UIs.

The release suite uses River's and Atlas's actual web UIs. Record both application builds for iOS and Android, container identities, devices, workloads and redacted results alongside the fixed catalogue configuration.
