# 3.3 Marketplace pickup protocol

## Repositories

| Repository | Role | Work in this plan |
| --- | --- | --- |
| [evy-marketplace](https://github.com/EVY-Platform/evy-marketplace) | Created | Marketplace contracts, delegate and UI |
| [evy](https://github.com/EVY-Platform/evy) | Modified | iOS and Android catalogue entry |
| [freenet-appkit](https://github.com/glesage/freenet-appkit) | Used | Packaging CLI and WebView host |
| [freenet-core](https://github.com/freenet/freenet-core) | Used | Sessions, subscriptions and merge checks |
| [freenet-migrate](https://github.com/freenet/freenet-migrate) | Used | Delegate migration |
| [freenet-scaffold](https://github.com/freenet/freenet-scaffold) | Used | Contract merge model |
| [harvest](https://github.com/freenet/harvest) | Used | Marketplace design references |

## Purpose

This plan builds Marketplace, an app where Alice sells a skateboard to Bob for pickup. Alice lists it for 70 dollars. Bob asks to pick it up on Saturday, they agree a time and place, and on Saturday they both sign the handover. This plan moves no money. [3.4 Payments and checkout](04-payment.md) adds payment records and a paid state to the same order.

Marketplace is a web app in its own release bundle, packaged with the [packaging CLI in 1.4 Application bundles](../1-freenet-mobile-appkit/04-bundles.md#publishing-and-evidence). EVY's internal test builds for iOS and Android list it in their release configuration. It runs beside River and Atlas in its own session, as [2.1 EVY shell and curated catalogue](../2-evy-mobile-app/01-catalogue.md) and [2.2 Two apps on one node](../2-evy-mobile-app/02-shared-node.md) describe, on the phone's thin peer from [1.8 Thin-peer role and cellular data budgets](../1-freenet-mobile-appkit/08-thin-peer.md). Its `app_definition.json` declares `marketplace.fulfillment.agree` and `marketplace.order.complete` in the `capabilities` list from [3.2 Release certification](02-certification.md).

## Contracts and the delegate

| Component | Key parameters | Writers | Holds |
| --- | --- | --- | --- |
| Store contract | Alice's store verifying key | Alice | Her store profile and her signed listings, such as the skateboard |
| Mailbox contract | Alice's store verifying key | Anyone | Sealed first-contact messages to Alice, one mailbox per store |
| Order contract | Alice's store key, Bob's order key and the order ID | Alice and Bob | Every signed record of one order, from Bob's request to the handover |
| Marketplace delegate | Empty | None | Alice's store keys, Bob's per-order keys, drafts, signed records waiting to be sent and the list of open orders |

Bob's delegate makes a fresh signing key for each order, so his orders share no key. Marketplace lists these four components in its `app_definition.json`, as River does in [1.4 Application bundles](../1-freenet-mobile-appkit/04-bundles.md#the-archive-and-its-definition).

## The skateboard sale

```mermaid
sequenceDiagram
    participant Alice as Alice's Marketplace
    participant Store as Alice's store
    participant Mailbox as Alice's mailbox
    participant Order as Order contract
    participant Bob as Bob's Marketplace
    Alice->>Store: Update with the skateboard listing, 70 dollars, pickup only
    Bob->>Store: Get the listing
    Bob->>Order: Put with his signed request for Saturday 10:00 to 16:00
    Bob->>Mailbox: Get, and wait for the state or NotFound
    Bob->>Mailbox: Update with a sealed pointer to the order
    Mailbox-->>Alice: Notification when she opens Marketplace
    Alice->>Order: Subscribe, then propose Saturday 10:00 and the place
    Bob->>Order: Accept Alice's terms
    Note over Alice,Bob: Agreed
    Alice->>Order: Handover signature on Saturday
    Bob->>Order: Handover signature on Saturday
    Note over Alice,Bob: Completed
```

First contact follows Harvest. Bob's delegate seals the pointer with Harvest's mailbox encryption, which uses X25519 with Bob's ephemeral key, AES-256-GCM with a key per direction, and every envelope field as associated data ([messaging-privacy.md](https://github.com/freenet/harvest/blob/main/docs/messaging-privacy.md)). The pointer carries a 16-byte nonce, the time of Bob's request and Bob's order key. It carries no text. Harvest shows buyer text to a seller only with a per-conversation Ghost Key voucher, as its answer to spam in an open-write mailbox ([buyer Ghost Key](https://github.com/freenet/harvest/blob/main/docs/messaging-privacy.md#a-buyer-who-writes-shows-that-seller-a-ghost-key)).

IDs follow Harvest's instant checkout ([payment.rs](https://github.com/freenet/harvest/blob/main/common/src/payment.rs)). The request ID is BLAKE3 of Bob's ephemeral routing key and the nonce. The order ID is a hash of the request ID and the request time. Alice's delegate derives the order contract key from the order ID and the two keys, and refuses a pointer whose order contract doesn't match.

Bob's request waits in the mailbox until Alice opens Marketplace, and she answers it herself. Harvest's always-open stores show how her delegate could accept requests that match a listing's fixed terms while she is away. Harvest's delegate wakes every 300 seconds, writes a heartbeat to a presence contract and watches payment addresses with delegated watch keys ([harvest#177](https://github.com/freenet/harvest/pull/177), [harvest#178](https://github.com/freenet/harvest/pull/178), [harvest#179](https://github.com/freenet/harvest/pull/179)). Harvest sells at a fixed price with Buy now only. Core's wake-ups ([#5747](https://github.com/freenet/freenet-core/pull/5747)) set these limits for such a delegate:

- Its manifest declares at most 4 wake-ups, each firing every 60 seconds to 7 days.
- Each fire needs the app's `Background` grant.
- A run makes at most 300 contract operations a minute, and at most 60 writes a minute to one contract.
- A run cannot message another delegate.
- Wake-ups need a stdlib 0.12 manifest. freenet-migrate builds on stdlib 0.8, so Harvest writes its manifest section by hand ([node_glue.rs](https://github.com/freenet/harvest/blob/main/delegates/harvest-delegate/src/node_glue.rs)). On iOS and Android they fire only while the node runs, as [background runs in 1.3 Single-application host](../1-freenet-mobile-appkit/03-host.md#background-runs-and-delegate-prompts) describes.

Anyone can read Alice's store and listings, the mailbox's message count, padded sizes, arrival times and routing keys, and each order contract's parameters, record kinds, amount and currency. Only Alice and Bob can read the mailbox messages and the `private` part of each order record.

## Order records

Every record in the order contract carries its author's signature, because mailbox encryption proves no authorship ([messaging-privacy.md](https://github.com/freenet/harvest/blob/main/docs/messaging-privacy.md)). Private terms are encrypted under a key that Alice and Bob both derive from the mailbox conversation. Alice's proposal for the skateboard:

```jsonc
{
  "kind": "propose",                             // propose, accept, decline, cancel or handover
  "order_id": "9f2c...",                         // hash of the request ID and the request time
  "author": "alice-store-key",                   // a writer named in the contract parameters
  "seq": 2,                                      // Alice's 2nd record in this order, at most 16
  "listing": "skateboard, revision 3",           // exact listing revision in Alice's store
  "quantity": 1,
  "amount_minor": 7000,                          // 70.00 dollars
  "currency": "AUD",
  "private": {                                   // encrypted, only Alice and Bob read it
    "pickup_start": "2026-10-03T10:00:00+10:00", // Saturday
    "pickup_end": "2026-10-03T10:30:00+10:00",
    "place": "Brunswick skate park, north entrance"
  },
  "terms_digest": "41ab...",                     // BLAKE3 over every term above, signed by accept and handover
  "signature": "..."                             // Alice's Ed25519 signature over the whole record
}
```

| Record | Who writes it | Effect |
| --- | --- | --- |
| `propose` | Alice or Bob | Sets new terms with their own digest. The author agrees to those terms |
| `accept` | The other party | Signs the digest of the latest proposal. The order is agreed once Alice and Bob have both signed one digest |
| `decline` | Alice | Ends the order before agreement |
| `cancel` | Alice or Bob | Ends the order before handover |
| `handover` | Alice and Bob, one each | Signs the agreed digest at pickup. The order is completed once both exist |

The contract keeps every valid record and each delegate derives the state from them. Both handover records win over any cancel. A cancel wins over a concurrent accept. Two different records with the same author and `seq` make the order conflicted, and the app then offers only cancel. Alice's delegate counts agreed orders against the listing's quantity and refuses to propose or accept past it. Freenet's maintainers describe the same pattern, fixed precedence over signed records, for late writes after a revoke ([D643](https://github.com/freenet/freenet-core/discussions/643), [D2927](https://github.com/freenet/freenet-core/discussions/2927)). freenet-scaffold's `ComposableState`, which River's room state uses, is a model for this merge state.

Harvest derives its order ID from the request, so two versions of one order can share an ID ([harvest#189](https://github.com/freenet/harvest/issues/189), open). In this plan, `accept` and `handover` sign one `terms_digest`. A later proposal therefore cannot replace the terms Bob accepted, and a second record under one author and `seq` makes the order conflicted.

The contracts check signatures, writers, `seq` and digests. They never read the host clock, which Core deprecates for contracts ([#5470](https://github.com/freenet/freenet-core/pull/5470), [#5465](https://github.com/freenet/freenet-core/issues/5465)).

## Bounds

| Contract | Record size | Capacity | Past the limit |
| --- | --- | --- | --- |
| Store | 4 KiB | One profile and 256 listings | The contract rejects the update. Each listing keeps its highest signed revision, and the lower digest wins at an equal revision |
| Mailbox | Padded to 1, 4, 16 or 64 KiB | 512 messages and 4 MiB, as in Harvest | Count caps per size class (512, 128, 64 and 24) evict by Harvest's ranking, which keeps the merge associative ([mailbox.rs](https://github.com/freenet/harvest/blob/main/common/src/mailbox.rs), [harvest#82](https://github.com/freenet/harvest/pull/82)) |
| Order | 4 KiB | 16 records per writer, numbered by `seq` | The contract rejects a record past `seq` 16. For a repeated `seq` it keeps the two lowest digests |

## Sending, lost state and upgrades

- The delegate keeps Bob's draft request and its signed bytes. If the app stops before Core answers, Marketplace resends the same bytes, as in [1.6 Application protocols, data and operations](../1-freenet-mobile-appkit/06-data-and-operations.md#sending-updates). A send is draft, sent or rejected.
- Before Bob's first update to Alice's mailbox, his app reads the mailbox and waits for the state or `NotFound`, as [sending updates in 1.6 Application protocols, data and operations](../1-freenet-mobile-appkit/06-data-and-operations.md#sending-updates) requires. It reads the mailbox again after 20 seconds and resends the same sealed pointer if the pointer is missing, as Harvest does ([harvest#126](https://github.com/freenet/harvest/pull/126)). It keeps resending until Alice's first record appears in the order.
- Alice's delegate subscribes to her store and mailbox, and each delegate subscribes to its open orders. These subscriptions take network interest ([#5615](https://github.com/freenet/freenet-core/pull/5615)) and come back after a restart ([#5728](https://github.com/freenet/freenet-core/pull/5728)), and the app PUTs its node's copy back when the network loses one, as [lost network state in 1.6 Application protocols, data and operations](../1-freenet-mobile-appkit/06-data-and-operations.md#lost-network-state) describes. Hosting demand from delegate subscriptions is tracked in [#4669](https://github.com/freenet/freenet-core/issues/4669).
- Core allows 256 subscriptions per delegate and drops the least recently notified one past that ([#5623](https://github.com/freenet/freenet-core/pull/5623)). Alice's store and mailbox take two, which leaves 254 for her open orders. An order is open until it is completed or cancelled. At 254 open orders, Alice's delegate leaves new requests in the mailbox unanswered, and her app shows "254 open orders: finish or cancel one to take new requests". Bob's request then waits, as it does while Alice is away. A finished order gets no more updates, so Core drops its subscription first.
- Each contract and the delegate has a [predecessor registry in 1.7 Upgrades and migration](../1-freenet-mobile-appkit/07-migration.md#predecessor-registry). When a new version first starts, Marketplace migrates Alice's store, her mailbox and each open order with freenet-migrate's `ProbeDriver`, and runs `migrate_delegate_secrets` for its delegate. It retries on the next start, as Harvest does ([migrate.rs](https://github.com/freenet/harvest/blob/main/ui/src/migrate.rs), [delegate_migrate.rs](https://github.com/freenet/harvest/blob/main/ui/src/delegate_migrate.rs)). Marketplace's web code gets every reply in one browser `WebApi` handler, and `migrate_contract` needs replies matched to requests, as in [matching replies to requests in 1.2 Embedded node and mobile SDK](../1-freenet-mobile-appkit/02-sdk.md#matching-replies-to-requests). Order parameter bytes stay unchanged, so the app can derive each old order key.
- Before Alice [forgets Marketplace](../1-freenet-mobile-appkit/05-identity.md#forget), the app lists her open orders and warns that forgetting deletes the keys that sign their handover.

## Acceptance

- On iOS and Android, in EVY, Alice lists the skateboard for 70 dollars, Bob requests Saturday pickup while Alice's phone is off, Alice finds the request when she opens Marketplace and proposes 10:00 and the place, Bob accepts, and both sign the handover. Both apps show the order completed, and an independent peer reads the same order state.
- On iOS and Android, Alice cancels one open order and Bob cancels another, and neither app then offers accept. A concurrent cancel and accept merge to cancelled on every replica. Alice's delegate refuses a second agreed order for the sold skateboard.
- Seeded property tests in `cargo test` and an `fdev verify-merge` sweep prove associativity, commutativity and idempotence for the store, mailbox and order contracts, and cover every bound in the table. The sweep runs before each contract change merges, as in [Harvest's merge laws](https://github.com/freenet/harvest/tree/main/tests/merge-laws). The fixtures include Core's idempotency check from [sending updates in 1.6 Application protocols, data and operations](../1-freenet-mobile-appkit/06-data-and-operations.md#sending-updates).
- ID fixtures match Harvest's derivation, and Alice's delegate refuses a pointer whose order parameters don't derive from Bob's sealed request. Known-answer vectors cover the mailbox encryption, and a changed envelope field, a reflected ciphertext or a replayed nonce fails.
- The order contract rejects a bad signature, a writer not in its parameters, a record past `seq` 16 and an accept for an older digest. A repeated `seq` marks the order conflicted.
- Killing the app on iOS and Android while drafting, signing and sending keeps Bob's draft and signed bytes, and a resend leaves one copy of the record.
- On iOS and Android, Bob's first request to a mailbox his node does not hold reaches Alice's mailbox.
- In an isolated test network, an order that loses its network copy is PUT back from Alice's node and an independent peer reads it.
- On iOS and Android, a new version with new order contract code carries an open order forward. A failed migration keeps the old data and runs again on the next start.
- Forgetting Marketplace with an open order shows the warning first.
- On iOS and Android, with 254 open orders, Alice's delegate leaves Bob's new request unanswered and her app shows the limit. After she completes one order, the delegate answers the request.
