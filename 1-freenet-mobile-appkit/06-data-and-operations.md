# Plan 1.6: Application protocols, data and operations

## Purpose

Provide concrete application protocols over delegate access and keep reads, drafts and submitted updates usable through disconnection, restart and supported upgrades. Application code owns orchestration. River's web UI or a custom native control reads room state, asks the chat delegate to sign, and submits the prepared message through the authorized host/SDK interface.

This plan owns delegate request/result protocols and validation, durable operation identity, storage namespaces, observed outcomes, retry rules and retained-state repair for application-owned contracts. [EVY 2.5](../2-evy-mobile-app/05-lifecycle.md) adds shared-node scheduling and per-app budgets. Optional generic envelopes, schemas, declared actions, bounded steps, executors, bindings, form state and operation presentation belong to [SDUI 4.5](../4-sdui/05-actions.md) and [4.6](../4-sdui/06-data.md).

## Prerequisites

Delegate registration, messaging, request correlation and lifecycle in [SDK 1.2](02-sdk.md), [host authority 1.3](03-host.md) and [protection 1.5](05-identity.md). Mobile release tests use the required [thin-peer profile and cellular budgets in 1.10](10-thin-peer.md).

## Who does what

| Part | Responsibility |
| --- | --- |
| Application code | Coordinate requests, interpret domain results and update its own UI |
| Host | Admit callers, check grants and targets, route replies and enforce resource limits |
| SDK | Register delegates, transfer bytes and correlate client requests and callbacks |
| Delegate | Hold private records, apply caller policy, sign and prepare domain results |
| Contract | Validate shared state and merge updates through `ContractInterface` |

Shared helpers follow needs demonstrated by applications. Domain codecs, signing inputs and reconciliation rules stay with the application. Delegate secret upgrades use [migration 1.7](07-migration.md).

## Application orchestration

For River's send flow, application code obtains a [durable operation record](#operation-identity-and-journal), reads the room, calls the chat delegate, and passes its prepared result to the authorized submission path. The host validates the returned target and bytes before any effect. A read or subscription later supplies domain evidence of the outcome.

The selected release fixes concrete delegate code, parameter bytes and supported protocol versions for the session. Compatibility fixtures run against those selections. The [host](03-host.md) owns session activation and permission checks.

Time and randomness used in preparation come through testable application/host interfaces. Fixtures supply deterministic values. Resource references returned by a delegate pass host target and query limits before the application follows them.

## Delegate requests and results

The [Rust client API](https://github.com/freenet/freenet-stdlib/blob/main/rust/src/client_api.rs) and [delegate interface](https://github.com/freenet/freenet-stdlib/blob/main/rust/src/delegate_interface.rs) provide the plan evidence below. Confirm these details against the pinned SDK and Core versions, and recheck upstream issue status before release.

| API detail | Constraint |
| --- | --- |
| `DelegateRequest::ApplicationMessages` | Carries a delegate key, parameters and inbound messages |
| `ApplicationMessage` | Carries opaque payload bytes, `DelegateContext` and a processed flag |
| `DelegateContext::MAX_SIZE` | 409,600 bytes in the source snapshot |
| `DelegateInterface::process` | Receives an `Option<MessageOrigin>` and produces outbound messages |
| `MessageOrigin::WebApp(contract id)` | Attests the web application when Core has authenticated its session |
| `MessageOrigin::Delegate(key)` | Attests the immediate calling delegate and replaces the web-app origin for that call |
| `OutboundDelegateMsg` | Reaches a client as `HostResponse::DelegateResponse` |

Delegates can request contract get, put, update, subscribe and unsubscribe operations, call another delegate, and issue `RequestUserInput`. Each supported path needs end-to-end SDK fixtures.

Subscription-triggered execution and the startup behavior described in [#5730](https://github.com/freenet/freenet-core/pull/5730) can run with no origin or request ID. Handle those as autonomous delegate events under explicit policy. Deliver private results only to authorized subscribers through the [host admission and routing rules](03-host.md#host-admission-and-permission-dependencies).

Select the application's existing protocol through pinned, verified release metadata that identifies the delegate code, parameter bytes and supported codec/version. Use that protocol's request and response wire format.

| Adapter responsibility | Requirement |
| --- | --- |
| Protocol selection | Match the pinned release metadata to a supported concrete codec before sending a request |
| Correlation | Use the protocol's request IDs where supplied, with SDK/session correlation for the selected transport |
| Payload handling | Encode and validate the application's exact arguments, records and results |
| Error handling | Map the protocol's errors, including strings, into host/application error types |

Fixtures specify exact encodings, numeric ranges, canonical signing inputs, error mappings and ownership of transferred bytes. Bindings bound payload size and measure copying. Conflicting request-ID reuse, unknown handles, malformed results and expired-session completions fail validation. A request ID correlates one exchange. The [operation ID](#operation-identity-and-journal) identifies the durable user operation across exchanges and retries.

Delegate policy uses the runtime-attested `MessageOrigin`. Application/user/session fields copied into payload bytes remain unverified claims. The host owns its user and installation bindings. Where a delegate needs additional authority, the application protocol must supply evidence it can verify through the trusted admission path.

### River signing fixture

River's [chat delegate](https://github.com/freenet/river/blob/main/common/src/chat_delegate.rs) accepts `SignMessage` with a request ID, room key and serialized `MessageV1`. The room key is the owner's key. It returns `SignResponse` with the same request ID and a 64-byte signature, or an error string when the room's key is unavailable. Application code combines the message and signature into [AuthorizedMessageV1](https://github.com/freenet/river/blob/main/common/src/room_state/message.rs).

The integration fixture preserves those wire formats and exact signing bytes. The adapter maps the error string for its callers. Core's attested origin identifies the calling River container when session authentication succeeds.

## Limits and security

- Validate input sizes, source identities, signatures, result types, resource references and prepared bytes before an effect.
- Apply the [host's current grants](03-host.md#base-authorization-and-device-access) to every protected operation. The delegate applies its own policy as well.
- Keep private keys, platform objects and external networking behind authorized interfaces.
- Bound concurrent requests, response size, execution time and event frequency. Run expensive work away from the UI thread.
- On failure, end the affected request or session and preserve its [durable journal](#operation-identity-and-journal).

Core's source snapshot includes a 50 MiB contract-state limit and a Wasm wall-clock deadline. [SDK 1.2](02-sdk.md) owns runtime configuration, measured mobile limits and missing SDK APIs. [Host 1.3](03-host.md#host-admission-and-permission-dependencies) owns the Core admission, callback-isolation and permissions dependency table.

## Reads, views and freshness

The Rust client API is the plan evidence for these constraints. Verify them against the versions selected in 1.1, and recheck upstream issue status before release.

| API | Source-snapshot behavior |
| --- | --- |
| `Get { key, return_contract_code, subscribe }` | Returns `GetResponse { key, contract, state }` or a missing-instance result |
| `Subscribe { key, summary }` | Returns `SubscribeResponse`, then `UpdateNotification { key, update }` |
| Contract responses | Carry contract identity and data. The host records response arrival time |
| stdlib 0.12.0 `ContractRequest` | Correlation uses response variant and key. The [SDK](02-sdk.md) owns a safe correlation implementation |

Application codecs verify and project state for their screens. Code sets query bounds, allowed resource targets and cache age. A delegate-suggested shard or record reference passes host authorization and query limits before a fetch. Large searches use bounded index shards.

Keep cached values with their observation time, source reference and decoding version. The UI distinguishes loading, ready, stale, missing, error and permission-required outcomes using its own code. A recent response can contain locally cached state. Its arrival time measures when this host observed it, while a domain timestamp has only the meaning its signed protocol assigns.

Reference-count subscription demand by owning session and contract. Releasing one consumer preserves the others. The SDK supplies wire-level cancellation and unsubscribe behavior. On background shutdown, release demand under the supported lifecycle and reject late callbacks. EVY 2.5 schedules this demand across apps within 1.10's total traffic budget.

Evidence for SDK verification includes [TypeScript response matching #5048](https://github.com/freenet/freenet-core/issues/5048) and [delegate unsubscribe #5600](https://github.com/freenet/freenet-core/issues/5600). Use integration results from the selected client build as release evidence.

## Values and local storage

Concrete application codecs define byte, numeric, timestamp and missing-value behavior. Shared fixtures cover canonical records, signing inputs, numeric ranges and conversion errors. Test inputs supply deterministic time and randomness.

| Record | Owner and scope | Lifetime |
| --- | --- | --- |
| Route parameters and session values | Application/session | Route entry or session |
| Drafts, saved values and private records | Application delegate's protected store, under the [host authority policy](03-host.md#who-controls-what) and later [shared-node namespace policy](../2-evy-mobile-app/02-sessions.md#delegate-namespace-policy) | Until explicit authorized data deletion or forget |
| Pending operations | Protected host journal per user, full application identity and installation | Until the outcome and required evidence retention are complete |
| Cached projections | Host cache, partitioned by authority and keyed by contract identity, codec and delegate version | Until refresh or eviction |
| Owned contract-state inventory | Protected host storage scoped by app and user | Retain verified recoverable copies under the declared recovery policy |
| Grants and publisher trust | Trusted host storage | Under the [host's grant rules](03-host.md#base-authorization-and-device-access) |

The source snapshot describes delegate key-value operations `get_secret`, `set_secret`, `remove_secret` and prefix-based `list_secrets` in [native_api.rs](https://github.com/freenet/freenet-core/blob/main/crates/core/src/wasm_runtime/native_api.rs). [Identity](05-identity.md) owns encryption at rest and export coverage. [Migration](07-migration.md) owns moves to successor delegates.

A draft save is a delegate call. Batch edits and flush on pause, navigation and backgrounding. Mark a save durable only after storage acknowledges it. A later process kill preserves acknowledged data. Storage exhaustion produces a visible failure before the UI claims a durable save. Cache eviction preserves drafts, unresolved operations, the recovery inventory and their required artifacts. Removing an application from the host retains its private records until explicit authorized data deletion or forget.

### Owned contract-state inventory and repair

For application-owned contracts covered by the release's recovery policy, retain:

- The full contract identity, original code hash and retained artifact reference, and exact parameter bytes.
- Verified canonical state with its domain-required signatures, including deletion and conflict records.
- Concrete protocol versions, ownership evidence and original record and operation references.
- Readback provenance and repair progress, scoped to the application and user.

The host coordinates bounded repair through application-owned domain adapters and the SDK:

1. Refresh the referenced contract. Record local-cache observations separately from a separately exercised network retrieval. A missing-network-state result starts repair assessment. Timeouts retain an uncertain outcome.
2. Recheck current grants, ownership, code and parameter identity. The domain adapter validates retained signatures and state against that contract's validation and merge rules, including deletions and conflicts.
3. Journal the authorized repair under the operation rules below and submit the retained signed canonical state to the same contract identity. Preserve original record and operation identities, and retain the recoverable copy while repair is pending.
4. Read back and verify the accepted state and domain merge result before recording completion. Record network retrievability through a separate retrieval when reporting restored network availability.

Bound refreshes, submitted bytes and retries within the application's resource limits and 1.10's cellular budgets. Keep unresolved repairs and their verified copies available for resume. [Migration 1.7](07-migration.md) owns moves to changed component identities. [Recovery 5.2](../5-optional-extensions/02-recovery.md) adds broader automated backup and destinations.

## Submitting updates and pending operations

`Update { key, data }` sends state, delta or both. The contract's `update_state` merges into the receiving replica and returns `UpdateModification`. `UpdateResponse { key, summary }` describes the local node's merge. An application observes its domain result through subsequent state. A timeout can follow remote acceptance, as recorded in [#3465](https://github.com/freenet/freenet-core/issues/3465).

### Operation identity and journal

Allocate and persist an operation ID before delegate preparation or any other side effect. Application adapters make preparation and delegate state changes idempotent under that ID. Persist the exact prepared bytes before submission and before showing the operation as durably pending.

| Journal field | Purpose |
| --- | --- |
| `operation_id` | One user operation across retries, restarts, upgrades and recovery |
| User, container key and installation | Select the protected storage namespace |
| `originating_content_ref` | Preserve the exact web publication or native build from [bundles](04-bundles.md#publishing-and-evidence) |
| Application protocol and delegate reference | Identify the concrete codec, full delegate identity and selected protocol |
| Resource reference | Identify the target contract and original parameter encoding |
| `canonical_payload`, optional base summary | Retain the exact prepared submission and the state basis the domain requires |
| Created time, retry policy and status | Track scheduling and observed progress |
| Completion evidence | Retain the domain evidence that supports the recorded result |

A delegate request ID belongs to one [protocol exchange](#delegate-requests-and-results). SDK request correlation belongs to [1.2](02-sdk.md). Neither replaces the durable operation ID.

For paid operations, retain the funded content and contribution bindings with the evidence required by [remuneration](../3-attribution-remuneration-payment/05-remuneration.md). A newer release completing an older operation uses those original bindings. Canonical `publication_ref` and `application_content_ref` definitions remain in [1.4](04-bundles.md#publishing-and-evidence).

### Outcomes and retries

| State | Meaning |
| --- | --- |
| Queued | Durable work is waiting for validation, authority or connectivity |
| Rejected | Local validation failed before submission |
| Submitted | The recorded payload was sent and its outcome is being checked |
| Accepted | A local merge and a later `GetResponse` or `UpdateNotification` show the intended record under the application's rules |
| Superseded | Domain evidence shows a competing record won the merge |
| Unresolved | Available evidence is insufficient to determine the submitted outcome |

Accepted describes observed domain evidence, rather than global finality. The application defines how its protocol recognizes an operation and when evidence is sufficient. A missing record alone may reflect stale or unavailable state.

1. Refresh relevant state and recheck current host grants before queued work runs.
2. Ask application code or its delegate to reconcile uncertain outcomes before retrying.
3. A retry preserves the operation ID and exact submitted bytes. If repair changes the payload, create a linked successor operation and retain the earlier outcome/evidence.
4. Cancellation stops local cancellable work. Keep tracking submitted mutations until their outcome is known.
5. After restart, recovery or release activation, resume from the journal with fresh session authority and the original protocol/content bindings.

For River, an owner-signed configuration edit can lose to another valid edit under the room's merge rule, as described in [configuration.rs](https://github.com/freenet/river/blob/main/common/src/room_state/configuration.rs). Message reconciliation uses room state evidence such as [version.rs](https://github.com/freenet/river/blob/main/common/src/room_state/version.rs). If a ban rotates the room secret while an offline change is pending, preserve the draft and let the domain adapter decide whether repair needs a successor operation.

## Reference definitions

| Term owned here | Meaning |
| --- | --- |
| Application delegate protocol | The exact payload encoding and domain behavior agreed by an application and delegate |
| Protocol version | The concrete codec/version selected through pinned release metadata |
| Delegate request ID | One exchange within a session |
| `MessageOrigin` handling | Policy based on the runtime-attested immediate caller, including explicit handling of absent origin |
| Storage namespace | Host records scoped by user, full app identity and installation |
| Observation time | When this host received a state response |
| Operation ID | Durable identity for one user operation |
| Canonical payload | Exact prepared bytes retained for submission and retry |
| Operation outcome | Domain evidence recorded as accepted, superseded, rejected or unresolved |

SDK request correlation belongs to [1.2](02-sdk.md). Host session authority belongs to [1.3](03-host.md).

## Acceptance

### Protocol acceptance

- River's WebView sends a real `SignMessage` through the SDK and delegate, validates the 64-byte signature, constructs the authorized message and observes its domain result on iOS and Android. Byte-level fixtures preserve the existing request/response encoding, including request IDs and error strings.
- A small custom Swift/Kotlin integration fixture calls a concrete delegate protocol at the support level declared in 1.1.
- Fixtures cover malformed bytes, unsupported protocols, wrong signing inputs, missing keys, conflicting request IDs, oversized results, expired sessions and unauthorized targets.
- Forged payload identities fail caller-policy tests. Delegate-to-delegate calls and origin-free events receive only the authority their attested context supplies.
- Autonomous private results reach only authorized sessions. The two-app shared-node isolation case has a separate gate in [2.2](../2-evy-mobile-app/02-sessions.md#acceptance).
- Termination during preparation or submission passes the durable operation tests below.

### Data and operation acceptance

- River's read, draft, send and reconnect flows pass on both mobile platforms using its actual application code and delegate.
- Termination at each preparation, persistence, submit and readback boundary preserves acknowledged work and its original operation ID. Retry tests compare exact payload bytes.
- Timeout-after-acceptance and duplicate-response fixtures reconcile without repeating the domain effect. Changed-payload repair creates a successor operation.
- Concurrent edits, rotated room secrets, stale caches, codec errors and incompatible versions produce defined outcomes with repairable drafts where applicable.
- Permission revocation, device lock and expired sessions stop unauthorized effects while preserving the journal. Storage exhaustion reports failed durable saves.
- Two consumers within the single application share subscription demand correctly. Releasing one preserves the other's subscription.
- An owned-contract fixture loses its network copy, repairs from the retained signed state with the original code and parameters, and verifies readback while preserving record and operation identities.
- Repair fixtures cover invalid signatures, mismatched parameters, revoked authority, concurrent state, interrupted submission and budget exhaustion. A local-cache read retains local-only provenance.
- Upgrade and app-specific export/import fixtures preserve originating content references, pending IDs and completion evidence, including paid-operation bindings when enabled.

The later [EVY 2.7 acceptance gate](../2-evy-mobile-app/07-acceptance.md) tests cross-app subscription isolation and retained records under 2.5's scheduling policy, including app removal followed by a separate authorized data-deletion decision.
