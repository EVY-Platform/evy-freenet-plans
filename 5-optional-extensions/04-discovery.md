# 5.4 Discovery and catalogue extensions

This plan adds optional application search to the [EVY home in 2.1 EVY shell and curated catalogue](../2-evy-mobile-app/01-catalogue.md), Atlas provider integration, signed catalogue updates and Marketplace listing search.

## Repositories

| Repository | Role | Work in this plan |
| --- | --- | --- |
| [evy](https://github.com/EVY-Platform/evy) | Modified | Search provider interface, provider settings, result presentation and signed catalogue updates in the iOS and Android apps |
| [atlas](https://github.com/freenet/atlas) | Used | Search provider under the fixtures in 1.8 Reference apps and compatibility fixtures |
| `freenet-appkit` | Used | Verified installation and reference inspection from 2.3 Installation and updates and 2.6 Navigation and application management |
| `evy-marketplace` | Modified | Listing search through user-chosen regional and category index providers |

## Optional provider-based discovery

Milestone 2 (EVY mobile app) requires the installed River and Atlas applications through fixed website container IDs. This plan lets EVY query Atlas as a search provider in addition to opening its application UI.

Prerequisites:

- [2.2 Multi-application sessions and authority](../2-evy-mobile-app/02-sessions.md).
- [2.3 Installation and updates](../2-evy-mobile-app/03-installation-and-updates.md).
- [2.4 Identity, permissions and device access](../2-evy-mobile-app/04-permissions.md).
- [2.5 Shared node, data and lifecycle](../2-evy-mobile-app/05-lifecycle.md).
- [2.6 Navigation and application management](../2-evy-mobile-app/06-navigation.md).

Atlas provider adoption also requires [1.8 Reference apps and compatibility fixtures](../1-freenet-mobile-appkit/08-reference-apps.md) for the selected provider revision.

### Scope

Own the search-provider interface, provider selection, result presentation and catalogue-update policy. Installation, trust, grants and migration stay with their canonical foundation owners.

- Start with the installed catalogue and add replaceable providers. Show the selected provider, result source and query privacy behavior in settings. Bound query size, pages, result counts, time, retries and cellular bytes.
- Return display metadata, a full application container reference and an optional exact publication reference. Resolve and verify that content through 2.3 Installation and updates before opening it. Provider metadata supplies a search result, while the application publisher supplies release authority.
- Search for applications. River's room list and private content stay within River's own application protocol and permissions.
- Treat deep links and search results as proposed destinations. App references follow verified installation, and arbitrary contract references follow the inspection flow in 2.6 Navigation and application management.
- Authenticate catalogue updates under a configured catalogue authority. Stage changes, record the newest accepted version and detect conflicting or replayed versions. Preserve a usable catalogue when updates fail. Application installation and grants still use the application's verified identity and host consent.
- Keep trusted installed apps and cached catalogue results usable within their stated freshness and compatibility limits. Expose unavailable providers, stale observations and incomplete pages separately.

### Marketplace listing search

Marketplace from [3.8 Paid application pilot and commercial acceptance](../3-attribution-remuneration-payment/08-marketplace.md) uses the same provider model to search listings.

- Regional and category indexes return bounded results under a freshness policy. Atlas is a possible provider.
- Every result points to signed listing state. The Marketplace delegate verifies that state when the user opens the result.
- Users choose providers and see each provider's published moderation policy.
- Enabling listing search follows the [product release approval in 3.8 Paid application pilot and commercial acceptance](../3-attribution-remuneration-payment/08-marketplace.md#product-release-approval).

### Acceptance

- A provider can be replaced or unavailable while verified installed apps remain usable.
- Atlas fixtures return bounded, source-labeled results that resolve to the expected publisher, container and optional exact release.
- Substituted references, malformed records, invalid catalogue signatures, replayed versions and same-version conflicts fail visibly before activation.
- Marketplace listing results open only after the delegate verifies their signed listing state.
- Opening a result preserves host authority, permission prompts and app/user/session isolation. Catalogue changes preserve pending work and installed app data.
- Provider queries, catalogue fetches and retries stay within per-provider allocations and the shared [upload/download and total cellular limits in 1.10 Thin-peer role and cellular data budgets](../1-freenet-mobile-appkit/10-thin-peer.md), including reconnect and serving-peer loss.
- Users can inspect the selected provider and understand which query data it receives. Cached results identify their source and observation time.

Record provider and catalogue versions, trust configuration, workload limits and test results before enabling the extension.
