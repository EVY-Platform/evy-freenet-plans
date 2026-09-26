# Plan 1.3: Single-application host

## Purpose

Run one defined application's code through authorized access to a Freenet node. Own the core host bridge, caller admission, basic session authority, base authorization, single-app installation interface and diagnostic redaction.

The first mobile route is River's web UI in a WebView served by the embedded node. Custom Swift/Kotlin applications use the [same SDK](02-sdk.md). [Sessions 2.2](../2-evy-mobile-app/02-sessions.md), [installation 2.3](../2-evy-mobile-app/03-installation-and-updates.md) and [permissions 2.4](../2-evy-mobile-app/04-permissions.md) compose these foundations for several applications. Optional reader integration belongs to [milestone 4](../README.md#4-optional-sdui).

## Prerequisites

Supported profiles and SDK [1.1](01-feasibility.md)-[1.2](02-sdk.md), bundle tooling [1.4](04-bundles.md), protection [1.5](05-identity.md) and operations [1.6](06-data-and-operations.md). All mobile profiles inherit the required [thin-peer and cellular gate in 1.10](10-thin-peer.md).

## Who controls what

| Part | Authority |
| --- | --- |
| Trusted host | Verify releases, create sessions, enforce grants, scope storage and route callbacks |
| Host-owned screens | Show installation, permission, identity and recovery decisions outside application-controlled content |
| Application code | Own screens and orchestration through the permitted host/SDK interfaces |
| Core | Enforce authenticated client access and attest the immediate caller to delegates |
| Delegate | Apply its policy to the attested caller and protect its secret namespace |

The host binds each session to the full application container identity, verified `application_content_ref`, user, installation ID and session generation. [Bundles](04-bundles.md#publishing-and-evidence) owns content references. The installation ID identifies one installed copy. Every new session gets a new generation. These local identifiers select host authority and callback routing. Copies supplied by application payloads are untrusted.

Before a protected request reaches Core, the host checks the current grant, target and session. It routes each response only to its authorized requester and discards expired-session callbacks. The [delegate protocol](06-data-and-operations.md#delegate-requests-and-results) defines `MessageOrigin` handling. Core's web-app attestation identifies a contract, while user, installation and session bindings require the trusted host path.

Core's device-node delegate secret store uses the full delegate key as its namespace. [Identity 1.5](05-identity.md#protected-keys-and-records) owns key and record protection. The later [2.2 namespace policy](../2-evy-mobile-app/02-sessions.md#delegate-namespace-policy) governs admission of several apps using the same delegate identity.

In the hosted source profile, the per-user secret context derives from a shell-minted token stored in browser local storage. Verify its binding and isolation against the selected Core build before relying on it.

## Browser and native hosts

| Profile | Application execution | Required boundary |
| --- | --- | --- |
| River mobile | River's web code in a WebView, with files served by embedded Core | Trusted shell/bridge admission, isolated web storage and bounded node access |
| Custom native | Installed Swift/Kotlin UI calling the SDK | Trusted in-process calls with session authority |
| Browser | Publisher web code inside Core's sandboxed frame | Core shell admission, storage and capability enforcement |

River's [UI package](https://github.com/freenet/river/blob/main/ui/Cargo.toml) and [bundle configuration](https://github.com/freenet/river/blob/main/ui/freenet.toml) are evidence for the WebView route. Pin and test the actual artifacts under 1.1.

The host must:

- Keep node credentials and privileged bridge methods in trusted code. Authenticate each caller, including loopback and alternate API paths.
- Bind frames, WebView messages and native calls to the verified session. Validate message source, navigation and target before forwarding requests.
- Scope cookies, web storage, caches, file access and native handles by application and user. Preserve the declared storage lifetime across reloads and restarts.
- Apply the node-only web sandbox policy to app code and loaded media. Route outside services, embedded pages and external links through approved adapters.
- Validate deep-link application identities, destinations and parameters before routing. External/native handoffs obtain explicit authority for keys or private data.
- When milestone 3 enables checkout, use the authenticated [payment adapter](../3-attribution-remuneration-payment/04-payment.md) for handoff and return reconciliation.

## Host admission and permission dependencies

This table owns host admission and permission evidence. The source snapshot records the gaps below. Links identify implementation or review evidence, and their current upstream status remains to be checked against the versions pinned in 1.1. [SDK 1.2](02-sdk.md) owns mobile API, runtime, key-store and subscription gaps.

| Requirement | Evidence | Release check |
| --- | --- | --- |
| Core-authenticated app admission | [Session admission #5264](https://github.com/freenet/freenet-core/issues/5264) | Bind verified app identity to the connection or trusted in-process caller. Reject caller-selected identities on every equivalent path |
| Private delegate response routing | Source snapshot describes locality-based delivery to local clients. [Admission #5264](https://github.com/freenet/freenet-core/issues/5264) covers the caller boundary | Targeted replies and autonomous private events reach only authorized sessions |
| Declared, revocable capabilities and per-app embedding | [Permissions #4014](https://github.com/freenet/freenet-core/issues/4014), [security discussion #5380](https://github.com/freenet/freenet-core/discussions/5380) | Enforce grants at the capability boundary, including page-initiated access |
| Fresh consent for expanded access | [Permissions implementation #4086](https://github.com/freenet/freenet-core/pull/4086), [review findings #4090](https://github.com/freenet/freenet-core/pull/4090) | A changed manifest prompts before any new access, and grants remain revocable |
| Durable, isolated web storage | [Storage #5165](https://github.com/freenet/freenet-core/issues/5165), [sandbox/storage #5254](https://github.com/freenet/freenet-core/issues/5254) | Reload and termination preserve only authorized records. The second-application case is the later 2.2/2.7 gate |
| Delegate prompts | Core's `RequestUserInput` interface, described in [delegate protocols](06-data-and-operations.md#delegate-requests-and-results) | Trusted prompts identify the requester and return only to the authorized request |

## Single-app installation interface

The single-app host implements verified installation and recoverable activation for milestone 1. [Bundles 1.4](04-bundles.md#installing-a-copy) owns content checks and [migration 1.7](07-migration.md) owns application migration. [Plan 2.3](../2-evy-mobile-app/03-installation-and-updates.md) owns the staged installation workflow composed across apps through this shared per-app interface.

| Interface responsibility | Milestone 1 requirement |
| --- | --- |
| Verify a candidate | Check the selected app's snapshot before execution, including host APIs, concrete protocols, setup, device adapters and data compatibility. Obtain consent for changed delegates, setup or access |
| Track release selection | Keep active content separate from the newest observed version/digest and observation time. Preserve the highest-observed version during local rollback |
| Stage and migrate | Stage checked files and host database changes with recoverable copies. Run application-owned migrations and verify readback |
| Activate | Activate checked files and compatible storage together at a session boundary. Create a fresh generation and retain pending work's originating content references |
| Retain and recover | Keep the working copy, one backup and artifacts required by pending operations within the storage budget. Preserve a usable copy and saved work on failure |

An older publication preserves the active copy and newest-observed record. Same-version divergence retains accepted bytes and both pieces of evidence, suspending automatic activation and transfer until a higher signed version resolves the conflict. Unsupported host APIs or protocols retain the compatible copy and report the unmet requirement. Deliberate local rollback passes current data compatibility checks. Component changes and publisher transfer follow 1.7 with required consent.

State subscriptions refresh live application data. Signed archives replace verified web releases. Component code or parameter changes can re-key contracts or delegates and require migration. Each session uses one consistent release and selected component/protocol versions.

Milestone 1 acceptance tests this interface for River. Milestone 2 adds per-app composition and tests that an update preserves another application's session.

## Saving work and reopening an app

[Data 1.6](06-data-and-operations.md) owns draft durability, subscriptions, journal states and retry safety. [SDK 1.2](02-sdk.md) owns node start/stop.

On app suspension, save acknowledged drafts and journal changes, release cancellable demand and invalidate the session. Reopening establishes fresh authority, shows retained state with its observation time, and reconciles pending operations. [EVY 2.5](../2-evy-mobile-app/05-lifecycle.md) adds scheduling across applications.

App-specific import/export follows [identity 1.5](05-identity.md). The host verifies the destination, reports uncovered records and imports shared records only with the signatures their domain requires. Network recovery depends on a surviving copy, including the [cold-state case #4642](https://github.com/freenet/freenet-core/issues/4642).

## Base authorization and device access

A grant records the full application identity, user, installed copy, permitted operation and target scope. Store grants and publisher trust decisions outside application-readable storage.

- Declare required and optional capabilities in bundle metadata. Prompt in trusted host UI when the user first needs an ungranted capability.
- Recheck grants before each protected operation and before queued work runs. Revocation stops further use immediately.
- Prompt before an update gains newly declared access. Changed delegates and setup require installation approval.
- Require explicit authorization when sharing identity or private records between WebViews and native contexts. [Plan 2.4](../2-evy-mobile-app/04-permissions.md) adds cross-app sharing and grant management.
- Return typed denial, unavailable, locked-device and expired-handle results. Bind selected files or photos to the requesting operation and session.

Camera, photos, files, notifications, clipboard, location, maps, contacts and outside services use only the adapters in the selected release profile. River's [notification integration](https://github.com/freenet/river/blob/main/ui/src/components/app/notifications.rs) is an application fixture. Notification taps validate the target and refresh application state before showing it. The foreground/background delivery promise belongs to [1.1](01-feasibility.md#scope-and-acceptance).

Startup execution is declared by the delegate's Wasm manifest, as described in [#5730](https://github.com/freenet/freenet-core/pull/5730). The mobile embedder may approve it as part of the trusted installation decision for that application. Browser hosts obtain the corresponding grant. Runtime work remains subject to the SDK lifecycle, current authority and budgets.

## Diagnostics

Expose per-app connection state, subscription demand, last observation time, pending-operation counts, storage use, verified release, grants and typed failures. [EVY 2.6](../2-evy-mobile-app/06-navigation.md) owns multi-app screens. [Release 1.9](09-release.md) owns the developer diagnostic package. Exported reports redact keys, message bodies, session tokens, private references and private records by default.

## Acceptance

- Open River's real web UI on iOS and Android and exercise join, read, send, deep links, reload, termination and reconnect. A native fixture proves the declared SDK support level.
- Forged app identities, frames, bridge messages, loopback requests and expired sessions fail admission. App code stays within its supported network and storage policy.
- Targeted delegate replies and autonomous private results reach only authorized sessions.
- The single-app installation interface passes interrupted activation, replayed content, same-version divergence, rollback, data changes, failed migration and cleanup with pending work.
- Trusted prompts, expanded permissions, immediate revocation, locked devices and web/native handoffs enforce base authorization. Queued work rechecks authority.
- Resource-exhaustion and malicious-input tests contain failure to the affected request or session. Measured traffic passes 1.10's cellular budgets.
- Each required browser or native admission path passes on the pinned Core build before that profile ships.

Cross-app admission, shared delegate namespaces, concurrent updates and grant UX pass the separate [2.7 gate](../2-evy-mobile-app/07-acceptance.md).
