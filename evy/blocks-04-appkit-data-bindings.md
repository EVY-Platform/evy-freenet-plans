# AppKit Data Bindings

**Parent plan:** [AppKit + EVY](README.md). **Consumes, built separately:** [Freenet Mobile](../freenet-mobile/README.md) for the mobile provider.

Data bindings connect SDUI and actions to their data: Freenet contracts (shared state), delegates (private state), local drafts, navigation parameters, and message context. They replace EVY's assumption that every resource behaves like a central database table with one predictable read/write/subscribe interface, explicit data boundaries, and cached-first mobile rendering.

## 1. Reference grammar

References are structured values, with a readable text form:

```text
contract:marketplace.listings
contract:conversation.current
agent:identity.profile
local:draft.listing.title
param:itemId
message:payload.offer
```

The release record maps logical names such as `marketplace.listings` to actual contract or delegate references, so SDUI does not embed environment-specific addresses. The [runtime](blocks-03-appkit-runtime.md#1-scopes-and-values) adds a `session:` scope of its own and defines resolution behaviour.

## 2. Provider interfaces

Define narrow interfaces:

```text
ValueProvider
  read(reference, options) -> ValueState
  observe(reference, options) -> Stream<ValueState>

MutationProvider
  update(reference, operation, idempotency_key) -> OperationResult

AgentProvider
  request(reference, message, idempotency_key) -> AgentResult

BlobProvider
  put(bytes, metadata) -> ContentRef
  get(ContentRef) -> ByteStream
```

`ValueState` is one of `loading`, `ready`, `stale`, `missing`, `error`, or `permission_required`, and may include last-updated metadata. The runtime does not infer these states from null values.

## 3. Contract provider and declared views

The contract provider maps to Freenet `GET`, `SUBSCRIBE`, and `UPDATE` operations. It knows the contract schema/codec and returns decoded values only after verification.

It supports declared views, not arbitrary client-side database queries — Freenet contracts are not SQL tables. A domain contract may expose:

```text
all current state
one entity by stable ID
one summary/index shard
one application-defined projection
```

If an app needs search, sorting, or filtering beyond a small local collection, it must declare an index contract or a domain-specific query mechanism.

## 4. Delegate provider

Delegates expose message APIs, not readable memory. A binding to `agent:identity.profile` is implemented as a request such as `GetPublicProfile`, while signing uses `SignPayload` and returns only the signature.

The provider forwards caller identity and required permission information so the delegate can enforce its own policy. AppKit never treats delegates as general key-value stores.

## 5. Local state and parameters

Use an encrypted local database for drafts, preferences, cached derived values, unread markers, and operation queues. Local records are namespaced by product and app instance (`AppInstanceId`, [Foundation §1](blocks-01-appkit-foundation.md#1-identity-model)) to prevent accidental cross-app access.

Parameters are immutable for the current route entry; navigation creates a new parameter scope. Message context is immutable input to a handler unless an action writes elsewhere.

## 6. Cached-first reads

Readers render verified cached data immediately, marked stale when necessary, then refresh from Freenet. A subscription updates the cache and notifies only bindings whose selected value changed.

Use selectors carefully: the provider may decode one contract state once and derive several small local views, but must cap state size and computation. Large contract state should be sharded at the domain layer.

## 7. Offline updates

An update record contains:

```text
operation_id
app/product identity
contract reference
base summary/version if required
canonical operation bytes
created time
retry policy
status
```

The local store writes it before presenting optimistic success. On reconnect, the provider refreshes the contract, submits the operation, and records accepted, rejected, superseded, or unresolved status — the same fetch-then-revalidate rule [Freenet Mobile applies to its own pending operations](../freenet-mobile/README.md#23-lifecycle).

Do not use last-write-wins universally. Merge and validation belong to each contract. The UI receives enough structured information to let the user repair rejected work.

## 8. Attachments

Large bytes are content-addressed and referenced by metadata. The provider:

1. validates size and type policy;
2. encrypts when required by the application protocol;
3. stores/uploads the blob through the configured mechanism;
4. returns a verified content reference;
5. lets the contract/message contain only the reference and integrity metadata.

AppKit defines the interface but does not require one global file-storage contract.

## 9. Implementations

- `BrowserFreenetProvider`: TypeScript and `@freenetorg/freenet-stdlib`, connecting to the local peer. Two tracked upstream gaps sit on this exact path — UPDATE cannot be addressed by instance id ([#4978](https://github.com/freenet/freenet-core/issues/4978)) and the published npm SDK still ships FIFO request matching ([#5048](https://github.com/freenet/freenet-core/issues/5048)); see [README item 11](README.md).
- `MobileFreenetProvider`: Swift/Kotlin wrapper around [Freenet Mobile](../freenet-mobile/README.md);
- `MemoryProvider`: deterministic conformance tests and builder preview;
- `LegacyEvyProvider`: temporary adapter over the current central EVY backend, used only during the [migration](blocks-09-evy-app.md#10-migration-from-current-evy).

## 10. Security and limits

- release-record capabilities limit which logical bindings may resolve;
- the trusted shell grants app access to instances, contracts, and delegates ([Runtime §7](blocks-03-appkit-runtime.md#7-security));
- providers validate type, codec, maximum bytes, and update size;
- local storage is encrypted and namespaced;
- logs contain reference categories and operation IDs, not private payloads;
- subscriptions are reference-counted and stopped on navigation or app background.

## 11. Delivery

| Phase | Delivers | Done when |
| --- | --- | --- |
| 1. Reference grammar | Typed contract, agent, local, parameter, and message references | Unbounded query assumptions are rejected at validation, not discovered at runtime |
| 2. Provider interfaces | Read, observe, update, invoke, cache, and status contracts | Provider errors are structured identically on all platforms |
| 3. Browser provider | Official TypeScript SDK to the local Freenet peer | Conformance fixtures pass against a real local peer |
| 4. Mobile provider | Freenet Mobile plus native local store | A mobile app renders cached state before network synchronization |
| 5. Offline and reconciliation | Pending operations and explicit conflicts | Offline updates survive force termination and reconcile visibly |
| 6. Fixtures and limits | Portable tests and bounded query/payload behaviour | The same SDUI definition works with browser, mobile, memory, and migration providers; no app reaches an undeclared contract or another app's local namespace |

References:

- [Freenet TypeScript SDK](https://freenet.org/build/manual/typescript-sdk/)
- [Freenet contracts](https://freenet.org/build/manual/components/contracts/)
- [Freenet delegates](https://freenet.org/build/manual/components/delegates/)
