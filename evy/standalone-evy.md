# EVY standalone on Freenet

EVY is a marketplace and messaging app with a web builder and an iOS client. Its screens are defined as data (JSON Schema SDUI) rather than hard-coded, so the same definitions drive both the React and SwiftUI renderers. This plan moves EVY's shared state onto Freenet.

## 1. Goals

- Ship one EVY product from the existing EVY repository.
- Preserve the existing machinery: the JSON Schema SDUI, generated models, web builder, React and SwiftUI renderers, action system, and local cache. The iOS app stays recognizably EVY, local-first behaviour included.
- Store marketplace and messaging state in EVY-owned contracts.
- Keep identity keys and private user state in delegates or protected local storage.
- Use Freenet Mobile for foreground network access from the iOS app.
- Keep releases and product-level attribution verifiable.

## 2. Architecture

### 2.1 EVY provider

Every EVY screen reads and writes data through three narrow interfaces:

```text
EvyDataProvider
  get(resource)
  list(resource, query)
  update(resource, operation)
  subscribe(resource)

EvyPrivateProvider
  request(operation)

EvyFileProvider
  put(blob)
  get(reference)
```

Implement `FreenetEvyProvider` as the only data adapter. It serves these interfaces by calling EVY contracts and delegates through the Freenet client API.

### 2.2 SDUI

Keep the existing EVY `flows`, `pages`, `rows`, actions, expressions, and JSON Schema definitions. Extend resource references only where EVY needs to address its own Freenet and local data:

```text
contract:evy.marketplace.listing
contract:evy.marketplace.index
contract:evy.messaging.conversation
delegate:evy.identity.current
local:evy.draft.listing
param:itemId
```

Publish a versioned app definition containing:

```text
release ID
SDUI schema version
minimum renderer version
SDUI artifact hash and reference
EVY contract and delegate versions
required EVY capabilities
previous release reference
maintainer signatures
```

Builder changes remain small mergeable operations such as `CreatePage`, `InsertRow`, `SetRowProperty`, and `SetAction`. Publishing produces one immutable release artifact and advances the app-definition contract to reference it. The builder publishes only EVY application definitions.

### 2.3 Contracts

Use separate contract families where state has different ownership, size, or merge rules. They still ship as one product.

```text
app-definition contract
store/profile contract
listing contract or bounded listing shard
discovery index contract
order/trade contract
conversation and inbox contracts
```

Contracts hold public or encrypted shared state and deterministic validation rules. They never hold private keys, plaintext private profile data, payment credentials, or local drafts.

The discovery index is EVY's search surface. It holds bounded hints that point at listings; a client verifies the listing itself before displaying it or acting on it. Do not put all searchable marketplace state in one unbounded global contract.

### 2.4 Delegates and local state

Delegates hold identity keys, signing, message encryption, private contact data, and scoped authorization. Drafts, unread markers, recent views, and pending operations stay in the existing local-first store unless they need shared synchronization.

EVY stores offline writes as intents. On reconnect it fetches the current contract state, rebuilds or revalidates each update, and shows a recoverable conflict if the contract rejects it.

### 2.5 Marketplace

Payment moves on external rails behind the [remuneration plan](../remuneration/README.md)'s adapter interface. Contracts may store signed payment-status references, but they must never treat a client's own claim as proof of payment.

The discovery index must ship with a moderation policy hook from the start; section 2.8 explains why it cannot be retrofitted. The build order for the marketplace is in section 3.

### 2.6 Messaging

Build only the messaging that marketplace and product flows require:

- questions attached to a listing;
- direct conversations between marketplace participants;
- offers and offer responses;
- order-status messages;
- normal text and encrypted attachments;
- local unread, retry, and delivery state.

Messaging is EVY-internal, not a generic library. Evaluate adopting [Freenet Mail](https://github.com/freenet/mail)'s message design before building new: end-to-end encrypted, signed messages delivered through inbox contracts. The design rules that hold regardless of implementation — sender timestamps are claims, delivery needs recipient-signed receipts, retention is bounded and never a promise of erasure, attachments are separately encrypted blobs, keys live in delegates — are collected in the [marketplace plan's messaging section](blocks-08-marketplace.md#6-trade-messaging).

### 2.7 Attribution

EVY registers in the [attribution app](../attribution/README.md) as one product: one `ProductId` and one shallow capability catalogue for the whole product. Internal repositories, contracts, SDUI components, and packages get no separate attribution identities. Each EVY release activates accepted proposals and signs one attribution snapshot, exactly as that plan defines; nothing attribution-specific is redefined here.

### 2.8 Moderation

On a permissionless network nobody can take content down, so moderation is a launch blocker for a consumer marketplace. EVY's control is what it operates itself: the discovery index decides what search surfaces, and the client decides what it renders.

Moderation policy (rules, scans, appeals, jurisdiction) is a separate plan. Two pieces cannot wait for it because neither can be retrofitted:

- The discovery index ships with a policy hook. Contracts cannot run content scans or gate publication, so whatever moderation runs later attaches at the index.
- Complaint tokens follow [Harvest](https://github.com/freenet/harvest)'s design: only a real trading partner can file one, and the reputation set is grow-only, meaning entries are added but never removed ([#5320](https://github.com/freenet/freenet-core/issues/5320)). A "clear my history" feature can never be added later, so this shape is fixed on day one. Harvest is a dormant prototype: adopt the design, not the code.

## 3. Implementation sequence

Two terms used below: a vertical slice is one feature built end to end, from data type to screen; fixtures are shared test files of recorded valid and invalid inputs that every platform replays.

| Phase | Build | Done when |
|---|---|---|
| 1. Listing vertical slice | Listing types and fixtures, minimal listing contract, provider `get`/`update`/`subscribe`, one listing screen | The flow runs against a local Freenet node |
| 2. App definition | Signed release types and fixtures, app-definition contract, immutable builder artifacts, publish commands | Both renderers load and verify the same published definition; unsupported releases fail with a clear error |
| 3. Marketplace | Store/profile and listing state, bounded discovery indexes, saved searches and drafts, signed order/trade transitions | A two-user trade completes end to end; concurrent edits and invalid transitions rejected in tests |
| 4. Messaging | Message and receipt types, crypto fixtures, conversation and inbox contracts, messaging delegate, marketplace questions and offers wired in | A two-user encrypted conversation completes; offline retry, duplicate delivery, and key rotation tested |
| 5. iOS | Freenet Mobile adapter, generated Swift types, app-definition verification, marketplace and messaging subscriptions | The listing slice runs on a device; backgrounding, force termination, and reconnect tested; CPU, memory, battery, and bandwidth measured |

## 4. Deferred decisions

Attribution units are not money. Fee splits, settlement, and contributor payouts are the [remuneration plan](../remuneration/README.md), reviewed and built separately.

Moderation policy (appeals, jurisdiction, and how scans and feedback tokens combine) is a separate plan; section 2.8 fixes the two pieces that cannot wait for it.

## 5. References

- [EVY repository](https://github.com/EVY-Platform/evy)
- [Freenet component overview](https://freenet.org/build/manual/components/overview/)
- [Building applications on Freenet](https://freenet.org/build/manual/tutorial/)
- [Freenet TypeScript SDK](https://freenet.org/build/manual/typescript-sdk/)
- [Freenet contract interface](https://freenet.org/build/manual/contract-interface/)
- [Freenet Mobile](../freenet-mobile/README.md)
