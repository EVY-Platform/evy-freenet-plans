# 2.7 Multi-application acceptance

## Repositories

| Repository | Role | Work in this plan |
| --- | --- | --- |
| [evy](https://github.com/EVY-Platform/evy) | Modified | River-and-Atlas release suite, recorded builds and fixed catalogue configuration for iOS and Android |
| `freenet-appkit` | Used | Host, SDK and subscription cleanup under test |
| [river](https://github.com/freenet/river) | Used | Actual web UI in the concurrent two-app suite |
| [atlas](https://github.com/freenet/atlas) | Used | Actual web UI and the product flows from 1.8 Reference apps and compatibility fixtures in the concurrent two-app suite |
| [freenet-core](https://github.com/freenet/freenet-core) | Used | Pinned thin-role build for the cellular cap cases |

## Purpose

Own the River-and-Atlas release suite and product evidence on iOS and Android. Exercise each app's actual web UI in separate sessions on one embedded thin node.

## Prerequisites

- [1.9 Developer package and release acceptance](../1-freenet-mobile-appkit/09-release.md)
- Completed plans:
  - [2.1 EVY shell and curated catalogue](01-catalogue.md)
  - [2.2 Multi-application sessions and authority](02-sessions.md)
  - [2.3 Installation and updates](03-installation-and-updates.md)
  - [2.4 Identity, permissions and device access](04-permissions.md)
  - [2.5 Shared node, data and lifecycle](05-lifecycle.md)
  - [2.6 Navigation and application management](06-navigation.md)
- The [Atlas fixtures in 1.8 Reference apps and compatibility fixtures](../1-freenet-mobile-appkit/08-reference-apps.md#atlas-fixture-scope-and-acceptance)

The app-specific [Atlas product flows defined in 1.8 Reference apps and compatibility fixtures](../1-freenet-mobile-appkit/08-reference-apps.md#atlas-product-flows-for-the-later-27-multi-application-acceptance-gate) become a release gate here.

## Acceptance

- Run River and Atlas concurrently with separate sessions, grants, WebView stores and pending operations on one thin node. Exercise the [River reference flows in 1.8 Reference apps and compatibility fixtures](../1-freenet-mobile-appkit/08-reference-apps.md#river-acceptance-cases) alongside the [Atlas application flows in 1.8 Reference apps and compatibility fixtures](../1-freenet-mobile-appkit/08-reference-apps.md#atlas-product-flows-for-the-later-27-multi-application-acceptance-gate).
- Forge app IDs, session tokens and stale callbacks. Attempt cross-app access through loopback, bridges and web/native handoffs. Verify the authority failures defined in 2.2 Multi-application sessions and authority.
- Exercise two apps using identical delegate code and parameter bytes. Prove the host's namespace policy protects each app and user before enabling that configuration.
- Stage compatible archives and fail updates through missing content, invalid signatures, conflicting versions, interrupted activation and migrations. Keep each session on a consistent usable release and preserve the other app's work.
- Close, suspend or exhaust resources in one app while the other remains usable within its allocation. Verify released subscriptions cease consuming network budget under the SDK's tested cleanup strategy. Releasing one app's subscription preserves the other's eligible demand.
- Remove an app and verify that its private records remain under [retention rules in 1.6 Application protocols, data and operations](../1-freenet-mobile-appkit/06-data-and-operations.md#values-and-local-storage). Exercise a separate authorized data-deletion decision and report deletion failures under 1.5 Identity, keys and local protection.
- Terminate during pending submissions and recover by refresh and reconciliation. Preserve operation IDs, exact payloads and originating release references.
- Pass node-wide and per-app cellular tests, including [two-app continuous-publish cap cases in 1.10 Thin-peer role and cellular data budgets](../1-freenet-mobile-appkit/10-thin-peer.md#acceptance), serving-peer loss, foreground lifecycle and accounting checks. Per-app caps preserve the other app's eligible demand. A node-wide cap stops both streams within the shared reserve. Unsupported thin negotiation stays visible and preserves the configured role.
- Test inaccessible archives, offline caches, revoked permissions, invalid links, native/external handoffs and accessibility through both apps' actual UIs.

The release suite uses River's and Atlas's actual web UIs. Record both application builds for iOS and Android, container identities, devices, workloads and redacted results alongside the fixed catalogue configuration.
