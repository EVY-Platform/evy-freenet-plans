# Application data and actions

This plan owns AppKit's declared actions, data views, delegate convention and operation lifecycle. [Hosts](hosts.md) install applications and check permissions, [SDUI](sdui.md) defines screens, and [Bundles](bundles.md) define the signed archive that carries the definitions.

Bob's Make offer button invokes a declared action with his draft amount. The host saves the operation ID, reads the listing and sends the record and typed arguments to the application's delegate. The delegate checks the terms and prepares the signed offer. The host saves the exact prepared bytes, checks submission permission and submits them through the SDK. A subsequent read or subscription supplies evidence of the result.

Each target has its own SDK path, listed in the [SDK paths table](../freenet-mobile/README.md#0-feasibility-and-existing-evidence). Custom applications can implement their own orchestration through their target's SDK and the same domain protocols.

| Section | What Freenet provides today | What AppKit proposes |
| --- | --- | --- |
| [1](#1-who-does-what) | Per-target SDKs, Core's contract and delegate runtimes, delegate secret namespaces | The action executor, the host broker and the application delegate convention |
| [2](#2-declared-actions) | Application code that calls the client API directly | Versioned action definitions with bounded steps, run by installed readers |
| [3](#3-delegate-requests-and-results) | `ApplicationMessages` with opaque payload bytes and a runtime-attested `MessageOrigin` | A typed request and result protocol inside the payload, with fixtures and correlation |
| [4](#4-reads-views-and-freshness) | `Get`, `Subscribe`, `GetResponse` and `UpdateNotification` keyed by contract, with no timestamps | Logical resources, declared views, value states and host-recorded freshness |
| [5](#5-values-and-local-storage) | Opaque state bytes in Core and the browser storage gates | A shared value model, storage namespaces and cache keys |
| [6](#6-submitting-updates-and-pending-operations) | `Update`, total merge in `update_state` and an `UpdateResponse` summary from the local node | Operation IDs, a durable journal and the lifecycle from Queued to Accepted or Superseded |
| [7](#7-device-and-service-adapters) | The contract sandbox policy and delegate user prompts | Content-addressed blobs, scoped device handles and approved service adapters |
| [8](#8-limits-and-security) | Core's Wasm state, context and deadline limits | Host limits for actions, views, subscriptions and storage, plus session authority |
| [9](#9-application-migrations) | `freenet-migrate` carry-forward, pointer resolution and delegate export and import | Host-coordinated migration with application-owned adapters and per-domain policies |

## 1. Who does what

### What Freenet provides today

### What AppKit proposes

| Part | Runs in | Responsibility |
| --- | --- | --- |
| Freenet SDK | TypeScript SDK, browser Wasm or native library, by target | Encode Freenet requests, decode responses and carry subscription events |
| SDUI action executor | Installed reader | Evaluate bounded action steps and deliver typed results to controls |
| Host | Trusted browser shell or native application | Sessions, permissions, storage, operation journals and device/service adapters |
| Application delegate | Core's delegate runtime | Domain decoding, projections, update preparation and private operations |
| Contract validator | Freenet Core | Validate and merge shared state |
| Custom application | Browser or native application | Its own presentation and orchestration through the shared SDK |

Core owns delegate secret namespaces. Host databases hold drafts, caches and pending operations. [Identity and recovery](../identity/README.md) specifies protected key storage, enrollment and migration. Freenet library bindings expose communication primitives. AppKit defines the application conventions above them.

```mermaid
flowchart LR
    UI["SDUI reader or custom application"] --> H["Host checks access and coordinates operations"]
    H --> S["SDK for the target"]
    S --> F["Freenet Core"]
    F --> D["Application delegates"]
    F --> C["Contract validation"]
    H --> L["Scoped local storage"]
    H --> A["Device and service adapters"]
    D -->|"Typed results through Core and SDK"| H
    H -->|"Views and operation results"| UI
```

| Consumer | Integration |
| --- | --- |
| Web SDUI reader | Rust-backed browser SDK with JS/TS bindings, hosted by Core's shell |
| JavaScript/TypeScript application | Existing TypeScript SDK |
| Rust browser application | Rust stdlib linked into its browser Wasm build |
| Native reader and custom application | The same native SDK and Swift/Kotlin bindings, with independent app enrollment |
| Memory preview | Deterministic host adapters using the same declarative executor and typed delegate fixtures |

## 2. Declared actions

### What Freenet provides today

### What AppKit proposes

Implement versioned action definitions, view schemas and a typed delegate request/result convention. These are proposed AppKit interfaces. Prove them with Atlas before adopting them across products.

| Interface | Purpose |
| --- | --- |
| Invoke action | Accept a declared action name, typed arguments and a stable operation ID |
| Read or observe | Fetch a declared contract or retain bounded subscription demand |
| Call delegate | Pass typed arguments and bounded record bytes to a fully identified delegate |
| Delegate result | Return a typed projection, prepared operation bytes, or a defined error |
| Submit | Submit prepared bytes to a declared target after permission and payload checks |
| Local operation | Read or write app-scoped drafts, caches and journals |
| Device/service operation | Invoke an approved adapter and receive a scoped handle or typed result |
| Cancel or close | Stop cancellable work, release host-side demand and invalidate the session |

Action definitions reference named resources, declared input/output schemas and supported step versions. Allow bounded sequences and conditional branches. Cap steps, input sizes, expression depth and concurrent requests. A new action assembled from supported steps can arrive in a bundle. A new executor primitive requires a reader update.

Validate action arguments, delegate results and outgoing view data before use. Read definitions and schemas from one verified archive snapshot. Record the exact delegate code, parameters and protocol selected for the session. Hosts adopt updates after the [installation checks](hosts.md#6-installing-and-updating-applications).

| Operation family | Returns |
| --- | --- |
| Contract get and observe | Verified snapshot, subscription events and the host-recorded response time |
| Contract update | Merged locally, observed, superseded or unresolved operation result |
| Delegate request | Typed result the delegate returns after its own policy check, or an opaque handle |
| Local read/write/observe | App/user-scoped records and transaction outcome |
| Blob put/get | Verified content reference or bounded byte stream |
| Device operation | File/media handles or typed denial/unavailable result |
| External operation | On the browser target, a popup or redirect, or a service response through a delegate or contract. Core's Content Security Policy blocks every other cross-origin request. On native, an approved adapter response |
| Time/randomness | Host-supplied values with deterministic substitutes in tests |

## 3. Delegate requests and results

### What Freenet provides today

### What AppKit proposes

The host performs reads and submits updates through the SDK. Delegates receive the supplied records and return results through Core's delegate messaging API. Implement application adapters for domain codecs, canonical signing inputs and view projections. Validate source identities and signatures required by each domain. A delegate's proposed update still passes host authorization and contract validation.

Specify deterministic encoding, typed errors, request correlation and ownership of transferred bytes for the delegate convention and each language binding. Bound large payloads and measure copying across bindings. Reject conflicting request-ID reuse, unknown handles and completions from expired sessions. Delegate requests and results carry their protocol version. Fixtures define their exact encodings.

The host assigns the container identity, verified content reference, user, installation and session generation. It protects these fields from changes by application content. The content reference is the publication reference for a downloaded definition or the certified native artifact reference selected under the [bundle plan](bundles.md).

Core attaches only the originating app's contract id, or another delegate's key, to a delegate message. Delegate policy keys on that id alone. User, installation and session generation are host bookkeeping that the host enforces before a request reaches Core. A delegate treats copies of those fields inside message bytes as unverified data.

## 4. Reads, views and freshness

### What Freenet provides today

### What AppKit proposes

Definitions bind logical resources such as `marketplace.listings` and `identity.profile` to declared contracts and delegates. Views such as `listingDetails` declare input and output types. The host performs bounded queries and the domain delegate interprets the returned records. Large search uses bounded region/category index shards. A delegate may return a proposed shard reference, which the host checks against declared resource and query limits before fetching it.

Value states are `loading`, `ready`, `stale`, `missing`, `error` and `permission_required`. `ready` means a verified snapshot received through the selected provider. Permission prompts belong to the host.

Core's get response and update notification carry the key, contract and state. Freshness is therefore the host-recorded time it received the response, or a publisher timestamp the application encodes in contract state and declares in its view schema. A view declares a maximum age. `stale` means the recorded time exceeds that age, so the reader shows the value with its observation time and the host refreshes it.

The host reference-counts underlying subscriptions. Releasing a view releases its demand. Other active views retain their subscriptions. A client subscription to Core ends with the client connection: stdlib 0.10 has Put, Update, Get and Subscribe, and Core lists Unsubscribe as upcoming. When that request ships, the host's reference count decides when to send it. Background shutdown follows the SDK lifecycle and invalidates late callbacks.

## 5. Values and local storage

### What Freenet provides today

### What AppKit proposes

Shared values distinguish null, missing, booleans, integers, decimals, strings, byte references, timestamps, durations, lists and objects. Define numeric ranges, decimal encoding, comparisons and missing-value behavior in shared fixtures. Money remains an application domain object with explicit currency and integer minor units or an equally precise declared representation.

Storage namespaces include user, app identity, installation and schema version. Permission grants live in host-only storage. Route parameters are immutable for a route entry. Session values expire with the session. Drafts survive according to the declared flow policy.

Render cached projections with stale metadata, refresh their backing state and notify only changed views. Cache keys include contract identity and the definition, delegate and schema versions. Encrypt sensitive local data using platform-backed keys. Recovery coverage is explicit in the identity plan.

## 6. Submitting updates and pending operations

### What Freenet provides today

### What AppKit proposes

Allocate and persist the operation ID before delegate preparation or other side effects. Correlate preparation retries with that ID and make any delegate state changes idempotent. Save exact prepared bytes before submission and before showing the operation as locally pending:

```text
operation_id, app_ref, originating_content_ref, action_protocol, delegate_reference
resource_reference, canonical_payload, base_summary_if_required
created_time, retry_policy, status, completion_evidence
```

```mermaid
stateDiagram-v2
    [*] --> Queued
    Queued --> Rejected: local validation fails
    Queued --> Submitted: refresh, revalidate and submit
    Submitted --> Accepted: merged locally, then observed in a GET or update notification
    Submitted --> Superseded: a read shows the contract's merge chose a competing record
    Submitted --> Unresolved: response unavailable
    Unresolved --> Accepted: reconciliation observes the record
    Unresolved --> Superseded: reconciliation observes a competing record
```

Merge is total. An update merges into whichever replica receives it, and the client's update response carries only the key and a summary from its own node. Accepted therefore means merged locally and later observed in a GET or update notification. Superseded is the normal outcome when Bob and another buyer submit conflicting offers: the Marketplace contract's merge rule resolves them, and a later read shows which record won. Rejected covers local validation failures before submission, such as an amount below the listing's minimum.

Retrying the same action preserves its operation ID and exact encoded payload. Repair that changes the payload creates a successor operation. The host refreshes state and asks the domain delegate to reconcile the operation before retrying. The host rechecks permissions before queued operations execute.

Example: Alice lowers her skateboard price offline. Her laptop withdraws the listing. On reconnect, the host refreshes the listing, obtains the delegate's conflict result and preserves the draft for repair.

Cancellation stops local cancellable work. A submitted mutation remains tracked until its outcome is known. After navigation or backgrounding, an uncertain submission stays unresolved until a read or notification shows the record or a competing one. Core transport correlation and the durable application operation queue have separate responsibilities.

## 7. Device and service adapters

### What Freenet provides today

### What AppKit proposes

Validate attachment size and media policy before staging. Encrypt bytes when the application requires confidentiality. Store content-addressed bytes, authenticate metadata and return a verified reference. Publish the reference only after required upload evidence exists. Product policy defines availability repair.

File and photo pickers return scoped handles. Granted operations, the session and its lifetime bound application access. Preview, image loading and external URL actions follow broker policy, including implicit network requests.

Applications may declare completion evidence for the [remuneration plan](../remuneration/README.md). The adapter forwards that evidence with the operation's stable ID and the bindings the payment fixed at checkout, which the host retains and remuneration verifies. A newer application version submitting evidence for an older operation uses the original bindings.

Checkout actions request payment sessions through the approved service adapter. On the browser target the host opens the checkout URL in a popup or redirect, the only paths that escape Core's Content Security Policy. Native hosts open the system browser or an in-app browser session. On return, the host refreshes payment state from the service and the order contract. [Payments](../payment/README.md) owns payment status and terms binding.

## 8. Limits and security

### What Freenet provides today

### What AppKit proposes

Installed readers execute declarative steps under host limits. The browser SDK runs as Wasm and the mobile SDK runs as native code. Core executes contract and delegate Wasm under its own limits. Keep platform networking, native objects and private keys behind their owning SDK and host interfaces.

Enforce limits for memory, input/output sizes, subscriptions, storage, action steps, view complexity and event frequency. Schedule bounded work away from the UI thread. Cancel overdue sequences and enforce delegate execution limits through Core. A failure ends the affected operation or session while preserving its durable journal.

Every protected operation uses host-assigned session authority and current grants. Delegates apply their own policy to approved calls. Treat definitions and delegate results as untrusted input. Validate returned targets and prepared bytes before any side effect. Resource-limit tests cover both declarative evaluation and Core execution.

## 9. Application migrations

### What Freenet provides today

### What AppKit proposes

Use `freenet-migrate` and its build-time predecessor registry for contract and delegate upgrades. Record original code hashes, parameter encodings and actual instance references. Add a build check that requires a predecessor entry when component code changes.

The host coordinates migration reads, approved imports, publication and readback through the SDK. Application-owned delegate adapters supply codecs, validation and domain recovery rules, using `freenet-migrate` where its interfaces fit. The Atlas feasibility work must prove this adapter boundary. Custom applications can also use the library from their own compiled domain code.

Select a recovery policy for each domain. Use the library's newest-generation policy for snapshot state. Combining state from several generations requires tests that prove the application's merge and deletion rules support it. Preserve unresolved predecessor reads for retry. Validate recovered state with the successor's rules. Publish it through authorized host operations, then read it back before recording success.

Keep shared-state recovery separate from host database migration and bundle installation. Mixed-version clients must obey the domain's transition rules. Delegate migration is application-controlled, per the [identity plan](../identity/README.md#4-delegate-upgrades): the predecessor delegate answers an export request and the successor imports through the application. Plaintext secrets transit the application during that round trip. Every AppKit delegate implements export and import. A delegate without them strands its secrets on re-key. Use the existing resolver for successor pointers. Retain its minimum accepted version and handle stale, unavailable, conflicting and withdrawn results.

Fixtures cover several skipped versions, late predecessor responses, deletions, conflicting records, interrupted readback and mixed-version participants. Test the selected policy against the domain's actual state model. Reference: [freenet-migrate](https://github.com/freenet/freenet-migrate).

## 10. Reference recap

## 11. Acceptance

Use the [feasibility stage](../freenet-mobile/README.md#0-feasibility-and-existing-evidence) to measure SDK bindings separately from declarative/delegate orchestration. Run real delegate integration tests alongside deterministic previews. Verify a new compatible SDUI definition works without application-specific code compiled into the reader. Equivalent domain behavior across targets comes from shared protocol fixtures rather than from an identical SDK implementation.

Test request correlation, instance-ID updates and subscription repair through the [mobile SDK acceptance cases](../freenet-mobile/README.md#8-acceptance-cases). Acceptance covers canonical records, signing inputs, typed errors, schema mismatches, codec errors, stale caches, duplicate responses, request isolation and late completions. Run property tests for domain conversions and reconciliation. Formatting fixtures supply identical locale, time zone and current time.

Force termination, lock, permission revocation and network change must preserve recoverable drafts and operation identity. Reject cross-app access, forged caller IDs, malformed delegate results, undeclared targets and excessive action work. SDUI and custom native interfaces complete equivalent fixture actions through their target's SDK and the same domain protocols.
