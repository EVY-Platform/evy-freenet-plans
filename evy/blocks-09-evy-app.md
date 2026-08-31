# EVY App

**Parent plan:** [AppKit + EVY](README.md). **Depends on:** [Mobile Readers](blocks-06-appkit-mobile-readers.md), [Marketplace](blocks-08-marketplace.md). **Consumes, built separately:** [Freenet Mobile](../freenet-mobile/README.md), [Product attribution app](../attribution/README.md).

EVY App is the consumer-facing mobile and web product assembled from the reusable repositories: the trusted host shell, the AppKit readers, an app discovery and installation experience, and the home of the first-party Marketplace and Messages modules. It is a simple native entry point to Freenet applications — installed apps open from cached definitions and synchronize in the foreground — without making EVY a central app store or backend.

## 1. Responsibilities

EVY implements the [trusted host shell](blocks-06-appkit-mobile-readers.md#5-the-trusted-host-shell) and additionally owns:

- the installed app/release catalogue and navigation;
- permission grant storage and identity/account selection UI;
- AppKit extension installation policy;
- the Freenet Mobile lifecycle;
- local cache, drafts, pending operations, and diagnostics;
- deep-link and message handler selection;
- first-party Marketplace and Messages presentation;
- update, rollback, attribution, and conflict UX.

EVY does not own the AppKit, messaging, marketplace, or attribution protocols, and it verifies and displays attribution records without calculating earnings or mixing units across products.

## 2. Native architecture

```text
evy-app/
  shared/            product models and policies
  ios/               trusted shell, AppKit SwiftUI host, Freenet Mobile adapter
  android/           trusted shell, AppKit Compose host, Freenet Mobile adapter
  web/               trusted web shell, AppKit Web Reader host
  product-modules/   home, apps, messages, marketplace, settings
  migration/
```

Use SwiftUI and Jetpack Compose natively; the web shell uses TypeScript/React/Vite. Share protocol models and fixtures through released packages rather than a new EVY-specific cross-platform runtime.

## 3. Home and app contexts

The EVY home shows installed apps, recent conversations/trades, saved actions, and connection state. It does not download all remote app data to create a feed.

Each app runs inside a scoped host context:

```text
verified product/release
app instance
capability set
granted permissions
namespaced local storage
active contract subscriptions
registered message/deep-link handlers
```

Closing an app releases its transient subscriptions after a short grace period.

## 4. Discovery and installation

Support direct signed app/release references, Atlas search/browse metadata, QR/deep links, message links to compatible handlers, and first-party curated suggestions as optional signed lists.

Installation verifies the [release record](blocks-01-appkit-foundation.md#2-release-record): publisher policy, artifact hashes, compatibility, requested permissions, and extension dependencies. Discovery metadata is never treated as proof of authenticity.

## 5. Updates and rollback

The shell checks the signed release chain and shows publisher identity, new permissions or delegate changes, protocol compatibility, attribution policy and snapshot changes, and a warning on conflicting/equivocating releases.

Automatic updates are allowed only within user policy and a compatible, non-conflicting release lineage. Keep the previous verified release and compatible local definition for rollback. Contract state migration follows the application's signed upgrade plan; UI rollback cannot automatically reverse shared state.

## 6. Freenet Mobile integration

EVY starts [Freenet Mobile](../freenet-mobile/README.md) when foregrounded and demand exists, and follows its [lifecycle rules](../freenet-mobile/README.md#23-lifecycle) on backgrounding. The shell's own additions: it consolidates requests from open AppKit modules so duplicate contract subscriptions share one underlying request, and it stays useful offline for cached views and drafts while clearly marking stale shared state.

## 7. Messages and Marketplace

Messages displays a unified local index of the conversations the user participates in, built on the marketplace's messaging layer ([marketplace §6](blocks-08-marketplace.md#6-trade-messaging)) — or Freenet Mail, if adopted there. It routes structured payloads to Marketplace or another installed handler.

Marketplace is installed/bundled as an AppKit application/module. EVY may provide polished native extension components, but the underlying contracts and flows remain usable by other hosts.

## 8. Identity, permissions, and recovery

The shell provides fixed trusted permission screens and communicates with identity delegates, displaying app identity and requested resource scope. Users can inspect and revoke grants per app and app instance.

EVY includes clear recovery and export tools, but must not imply that private state moves across devices automatically: delegate-secret migration is unsolved upstream and is the top launch blocker ([README item 1](README.md)); a cross-device trust anchor is future work ([Freenet Mobile §4](../freenet-mobile/README.md#4-future-improvement-a-delegate-trust-anchor)).

## 9. Attribution UX

For each installed product release, show: product and publisher identity; release generation and artifact verification; capability catalogue and policy; activated proposals and accepted contribution summaries; accumulated contributor, reviewer, and validator units; evidence links and historical attribution; and conflict warnings.

Each product's units stay separate, and they display as the non-currency weights the [attribution app](../attribution/README.md#5-attribution-units) defines — never as ownership or earnings.

## 10. Migration from current EVY

The current EVY app is local-first but synchronizes through a central JSON-RPC/Postgres stack. Migration is explicit:

1. add AppKit/Freenet providers behind existing local data interfaces (the `LegacyEvyProvider` of [Data Bindings §9](blocks-04-appkit-data-bindings.md#9-implementations));
2. import current SDUI definitions through the [Builder's importer](blocks-07-app-builder.md#11-migration-from-evy);
3. export user-owned records and drafts into signed/new contract operations where valid;
4. migrate one domain at a time, beginning with read-only app definitions;
5. keep a time-limited legacy login/export path;
6. show users which data was migrated, skipped, or needs action;
7. avoid silent dual ownership of the same record in both systems.

## 11. Diagnostics

Provide a non-technical status screen:

```text
Connected peers
Active app/contracts
Last successful refresh
Pending local changes
Storage use
App/release verification
Permission grants
Recoverable errors
```

Allow exporting redacted diagnostics. Payloads, private contract keys, identity secrets, and decrypted messages are excluded by default.

## 12. Delivery

Testing: install/open/update/rollback flows with signed fixtures; permission spoofing and malicious app tests; foreground/background and force-termination tests; offline draft and pending-operation recovery; message handler routing between two installed apps; a Marketplace end-to-end flow; accessibility and onboarding tests with non-technical users; physical-device performance tests for Freenet Mobile and the native readers.

| Phase | Delivers | Done when |
| --- | --- | --- |
| 1. Trusted shell | Install/open/update, permissions, identity selection, diagnostics | Trusted prompts cannot be imitated by app content |
| 2. AppKit readers | Web, SwiftUI, and Compose application rendering | A user installs and uses an AppKit app without understanding contracts or delegates |
| 3. Freenet Mobile | Foreground contract/delegate access and local-first cache | Cached experiences open offline and refresh in foreground; no EVY-operated backend is required |
| 4. Discovery and links | Atlas browsing, direct references, handlers, verified metadata | Installation trusts only verified release records, never discovery metadata |
| 5. Messages and Marketplace | First-party modules from the released marketplace packages | Marketplace remains a reusable dependency, not a hidden EVY fork |
| 6. Release and attribution UX | Identity, policy, snapshot, units, history, conflicts, rollback | Every installed release shows verifiable identity, policy, and snapshot; units are never mixed across products |
| 7. Migration | Controlled import from the current central system | Users see exactly what was migrated, skipped, or needs action |
