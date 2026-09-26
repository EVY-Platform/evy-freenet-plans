# Discovery and catalogue extensions

Plan ID: 5.4. Optional provider-based discovery.

## 5.4 Optional provider-based discovery

Milestone 5 adds application search to the [EVY home](../2-evy-mobile-app/01-catalogue.md), Atlas provider integration and signed catalogue updates. Milestone 2 requires the installed River and Atlas applications through fixed website container IDs. This extension lets EVY query Atlas as a search provider in addition to opening its application UI.

Prerequisites: [multi-app authority, 2.2](../2-evy-mobile-app/02-sessions.md), [verified installation, 2.3](../2-evy-mobile-app/03-installation-and-updates.md), [permissions, 2.4](../2-evy-mobile-app/04-permissions.md), [shared-node budgets, 2.5](../2-evy-mobile-app/05-lifecycle.md), and [reference handling, 2.6](../2-evy-mobile-app/06-navigation.md). Atlas provider adoption also requires the [Atlas SDK/index fixtures, 1.8](../1-freenet-mobile-appkit/08-reference-apps.md) for the selected provider revision.

### Scope

Own the search-provider interface, provider selection, result presentation and catalogue-update policy. Installation, trust, grants and migration stay with their canonical foundation owners.

- Start with the installed catalogue and add replaceable providers. Show the selected provider, result source and query privacy behavior in settings. Bound query size, pages, result counts, time, retries and cellular bytes.
- Return display metadata, a full application container reference and an optional exact publication reference. Resolve and verify that content through 2.3 before opening it. Provider metadata supplies a search result, while the application publisher supplies release authority.
- Search for applications. River's room list and private content stay within River's own application protocol and permissions.
- Treat deep links and search results as proposed destinations. App references follow verified installation, and arbitrary contract references follow the inspection flow in 2.6.
- Authenticate catalogue updates under a configured catalogue authority. Stage changes, record the newest accepted version and detect conflicting or replayed versions. Preserve a usable catalogue when updates fail. Application installation and grants still use the application's verified identity and host consent.
- Keep trusted installed apps and cached catalogue results usable within their stated freshness and compatibility limits. Expose unavailable providers, stale observations and incomplete pages separately.

### Acceptance

- A provider can be replaced or unavailable while verified installed apps remain usable.
- Atlas fixtures return bounded, source-labeled results that resolve to the expected publisher, container and optional exact release.
- Substituted references, malformed records, invalid catalogue signatures, replayed versions and same-version conflicts fail visibly before activation.
- Opening a result preserves host authority, permission prompts and app/user/session isolation. Catalogue changes preserve pending work and installed app data.
- Provider queries, catalogue fetches and retries stay within per-provider allocations and the shared [1.10 upload/download and total cellular limits](../1-freenet-mobile-appkit/10-thin-peer.md), including reconnect and serving-peer loss.
- Users can inspect the selected provider and understand which query data it receives. Cached results identify their source and observation time.

Record provider and catalogue versions, trust configuration, workload limits and test results before enabling the extension.
