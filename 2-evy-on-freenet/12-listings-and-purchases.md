# 2.12 Listings and purchases

## Repositories

| Repository | Role | Work in this plan |
| --- | --- | --- |
| [evy](https://github.com/EVY-Platform/evy) | Modified | Listing/purchase contracts, adapters and admission coordinator |

## Purpose

Define Marketplace listings, purchases, participant messages, admission and one-sale reservations. [2.6 Payments](06-payments.md) supplies Stripe integration, financial policy and payment evidence. [2.7 EVY Marketplace](07-marketplace.md) supplies production flows, moderation and pilot hosting.

Owner: EVY commerce lead. Agree contract and payment interfaces before implementing either service path.

## The purchase contract

EVY uses `evy.purchases` and `evy.messages` from [EVY resource catalogue in 2.4 SDUI data and actions](04-data-and-actions.md#evy-resource-catalogue). Each sale has one purchase contract. Home and Marketplace read one application purchase projection. Data fields named `service` identify the internal source feature; UI and policy identities identify EVY itself.

| Contract | Parameters | Holds | Writers |
| --- | --- | --- | --- |
| Items contract | The EVY publisher key and internal feature namespace, `marketplace`, laid out as for the guestbook in 2.4 SDUI data and actions | One entry per item: seller-signed fields and admission authorization, a service-signed listing decision with at most 32 live purchase references, and separate captured-sale evidence | Sellers write their own fields and authorize the certified payment service to admit purchases and decide reservations for that listing. That service writes the listing decision and retains captured-sale evidence for the listing's lifetime |
| Purchase contract | Seller key (32 bytes), buyer key (32 bytes) and purchase ID (16 UUID bytes), concatenated in that order | The purchase record below | Alice, Bob and the payment service |

- EVY application version 6 adds the Marketplace test item. Its complete UI document maps `marketplace.items` to the items contract ([Resources and contracts in 2.4 SDUI data and actions](04-data-and-actions.md#resources-and-contracts)), and Alice adds the skateboard with a `create` action.
- The seller key is Alice's EVY key for the originating feature. Bob's EVY delegate derives a buyer key with that feature and `scope = purchase:<purchase ID>`, so each purchase has its own key ([The EVY delegate in 2.11 EVY delegate and private records](11-delegate-and-private-records.md#the-evy-delegate)). The iOS and Android apps create purchase IDs as UUIDs, following EVY's message-ID generation ([EVY+Mutations.swift](https://github.com/EVY-Platform/evy/blob/d0fb7e6475f1dfc5c74325e37d4e92aed88d84ed/ios/evy/Core/EVY+Mutations.swift)).
- The shared purchase adapter PUTs the purchase contract, then submits its signed initial state through the admission operation below. Alice's app subscribes to her items, so it finds the purchase and subscribes to it. Home can resolve that same reference through its own binding to Marketplace items.
- Readers derive item availability from verified linked purchases, using [Item availability in 2.7 EVY Marketplace](07-marketplace.md#item-availability). The shared Marketplace fixture uses these rules. The payment service's purchase updates feed this derived status while either participant's app is closed.
- Each signature covers a domain prefix and the RFC 8785 JSON, as in [The hello contract in 2.1 Hello EVY world](01-hello-evy-world.md#the-hello-contract).

```jsonc
{
  "purchase": {                                          // what Bob buys
    "resource": "marketplace.items",                           // EVY resource ref of the item
    "fk": "4f1c6a0e-2b7d-4c1e-9a55-0d8e3f6b2a91",        // item ID, EVY's fk
    "application_key": "<full EVY UI contract key>",   // pinned EVY application identity
    "feature": "marketplace",                                  // internal source feature
    "ui_version": 6,                                      // retained complete EVY application document
    "ui_digest": "3b9e...",                              // exact signed UI state
    "policy_version": 1,                                 // accepted financial policy
    "policy_digest": "9a2f...",                          // exact signed policy
    "type": "pickup",                                    // EVY's transfer type
    "amount_cents": 7000,                                // 70.00 dollars, the item's price
    "currency": "AUD",                                   // the one currency EVY's Stripe code takes
    "fee_cents": 70,                                     // 1% contributor fee, rounded half up
    "signature": "pX3a...9Q=="                           // Bob's buyer key, signed under evy.purchase/1
  },
  "messages": [                                          // each written once, with id, parent_message_id,
                                                         // created_at, data and its author's signature
    { "value": "pending", "by": "buyer" },               // Bob asks to buy
    { "value": "accept", "by": "seller" },               // Alice agrees to the purchase above
    { "value": "transaction", "by": "buyer" },           // Bob pays. data.signature holds his payment request
    { "value": "transaction_completed", "by": "seller" } // Alice confirms the handover
  ],
  "payment": { "status": "succeeded", "...": "..." },    // the payment record, see The payment record
  "status": "sold"                                       // available, pickup_pending, sold or refunded
}
```

The initial purchase signature covers `evy.purchase/1`, the target contract key, a newline and canonical purchase fields, including seller, buyer, purchase ID, EVY application identity, originating feature/item and the UI and policy identities. Each message signs its purchase context. The contract checks each message's author and requires its parent message first. It computes `status` with EVY's purchase status machine ([purchase.ts](https://github.com/EVY-Platform/evy/blob/d0fb7e6475f1dfc5c74325e37d4e92aed88d84ed/services/marketplace/src/purchase.ts)), following [Service rules in 2.4 SDUI data and actions](04-data-and-actions.md#service-rules). The payment service handles purchase messages using EVY's payment orchestration ([payments.ts](https://github.com/EVY-Platform/evy/blob/d0fb7e6475f1dfc5c74325e37d4e92aed88d84ed/services/marketplace/src/payments.ts)).

| Message | Author | Status after it | The payment service |
| --- | --- | --- | --- |
| `pending` | Bob | `available` | Does nothing |
| `accept` | Alice | `pickup_pending` for this purchase | Requests the listing reservation; only its confirmed winner can pay |
| `reject` | Alice | `available` | Does nothing |
| `transaction` | Bob | `pickup_pending` | Creates the PaymentIntent when Bob's app calls `payment_intent` |
| `transaction_completed` | Alice | `sold`, once the payment record is `succeeded` | Captures the payment (`payment_capture`) |
| `transaction_rejected` | Alice | `available` | Cancels the PaymentIntent (`payment_cancel`) |
| `cancel` | Alice or Bob, before `sold` | `available` | Cancels the PaymentIntent if there is one |

Purchase status describes its participant-message history. Listing availability and checkout permission come from the service's signed reservation decision, so an accepted competing request can show "Another request is reserved" while retaining its acceptance.

Captured-payment evidence (`succeeded` or `refunded`) wins over a concurrent `cancel`, and a `cancel` wins over a concurrent `accept`, so every peer merges to the same status. A `failed` payment record reports a failed card attempt; an accepted purchase stays `pickup_pending` while Bob can retry. A `canceled` payment record or a valid purchase cancellation sets `available` again. A partial buyer refund retains the captured payment's `succeeded` status and the completed purchase's `sold` status. A full buyer refund sets both statuses to `refunded`, as in [Refunds in 2.6 Payments](06-payments.md#refunds). Each author writes at most 16 messages per purchase.

### EVY purchase interface

`purchase/1` and `purchase-messages/1` run in the shared iOS and Android reader layer. The signed UI bindings name the supported purchase code hash and source items binding. The adapters expose collections to existing EVY bindings and route actions by each row's retained source identity.

| Operation | Shared behavior |
| --- | --- |
| Discover | Follow the certified service's latest listing decision and its admitted live references plus retained sale evidence. Read each referenced instance and check its code hash, exact parameters, originating resource, item ID, seller and signed purchase. Home and Marketplace resolve the same instances |
| Create purchase | `create(evy.purchases, ...)` takes the source item reference, creates the purchase UUID, obtains the scoped buyer keys and derives the contract key with the common parameter codec. Signs the purchase and initial `pending` message and PUTs the valid initial state. The projected row's `id` is the contract key; it also exposes `purchase_id`, the originating resource and item ID |
| Admit purchase | Call `register_purchase` with the buyer-signed initial state, exact source context and pilot enrollment proof bound to the buyer key. The payment service verifies and hosts that state, checks seller authorization and admission limits, then returns a signed admission receipt and publishes its higher-revision listing decision. The receipt names the listing and purchase identities. Repeating the operation returns the saved receipt |
| Resume creation | Keep the creation and admission steps with the pending operation's source context. A retry reuses the same UUID, keys, parameters and signed bytes and completes the remaining step. Capacity or enrollment refusal retains the draft and shows the reason. The row stays "Sending" until the hosted purchase, admission receipt and listing decision agree under [Offline writes in 2.4 SDUI data and actions](04-data-and-actions.md#offline-writes) |
| Read purchase | Project `purchase`, participant parameters, derived `status` and the latest verified payment into one purchase row. Keep the signed originating UI and financial policy identities for [2.9 Remuneration and payouts](09-remuneration.md) |
| Read messages | Project each nested message into `evy.messages`, retaining its `purchase_key`, message ID, parent ID, author role, timestamp and data. Subscription updates refresh this purchase's messages |
| Write message | `create(evy.messages, ...)` names `purchase_key` and the message it answers. The adapter validates the permitted transition, resolves the buyer scope or seller feature key and asks the delegate to sign under the participant-message domain. It UPDATEs that purchase with the message delta. Messages are immutable once signed |
| Pay | A permitted `transaction` message for the currently reserved purchase triggers the payment request and native payment sheet from [Paying on a phone in 2.6 Payments](06-payments.md#paying-on-a-phone). The request retains the same purchase key and authorization message ID when Home and Marketplace display it |
| Update purchase view | Participant changes such as acceptance, cancellation and handover create messages through the message adapter. The contract computes purchase status and verifies payment-service records |

The purchase resource and item reference identify the originating EVY feature. Buyer signatures, payment authorization and seller onboarding preserve that feature context. Home opens the internal purchase route in its retained complete application document. The native reader supplies the verified application, feature and participant context before signing. Participant messages sign `evy.message/1 <base58 purchase contract key>`, a newline and the RFC 8785 canonical JSON of the other message fields. `SignOperation` from [The EVY delegate in 2.11 EVY delegate and private records](11-delegate-and-private-records.md#the-evy-delegate) selects the catalogue's purchase-creation, participant-message or admission-request schema, validates the target and actor, and saves the signed bytes with their replay context.

Collection fixtures cover seller item edits interleaved with service admission decisions, repeated creation and interrupted admission. Parameter and signing fixtures give the same purchase key and payloads in Rust, Swift, Kotlin and the payment service.

### Listing admission and one sale

The payment service is the trusted admission and reservation authority for each listing. The seller's signed listing authorization names the service key certificate, originating feature, items contract and immutable listing ID. Listing decisions sign that identity, a monotonic `revision`, live purchase references, reservation owner and fencing number under `evy.listing-decision/1`.

| Rule | Required behavior |
| --- | --- |
| Register listing | `register_listing` verifies the seller-signed item and service admission authorization, and saves the item and referenced photos in the operator hosting inventory. It commits listing decision revision 1 as `available`, with empty live references and no reservation or sale. Publication completes after that decision and hosting receipt verify, so the first buyer can request the item. Replays return the same receipt. |
| Admission | Verify the complete initial purchase, buyer signature, source listing and supported contract code, then save its bytes and host it before acknowledging. The pilot operator issues enrollment credentials; the service binds a credential to each buyer key and allows one live request per enrolled buyer per listing, with at most 32 live requests per listing. More scoped keys retain the same enrollment quota. A full listing shows "Requests full" and preserves the draft. |
| Merge | Seller fields and service decisions merge independently by their signed `(revision, hash)`. Each service decision contains the complete bounded live-reference set. Peers select the same higher tuple even at capacity; clients submit admission requests to the service. |
| Cleanup | A rejected or canceled request leaves the live set after its terminal state is verified. An associated PaymentIntent must be terminally canceled first. Captured-sale certificates merge separately as immutable service-signed evidence and remain through refunds and listing edits. They consume no live-request slots. The certificate proves permanent closure; the sale's latest verified payment revision supplies current refund totals. |
| Reservation | On a verified seller acceptance, serialize by `(originating feature, items contract, listing ID)` in Postgres. Reserve for one admitted purchase and issue a signed fencing number. Concurrent acceptances keep their messages but show "Another request is reserved". Payment authorization requires the current reservation. |
| Capture | A durable listing row and unique completed-sale key permit one successful sale for the listing. The worker records the intended Stripe operation and fencing number before dispatch. Every intent, capture and cancel uses the same listing coordinator and checks its fence. |
| Uncertain results | An in-flight capture or uncertain intent/cancel keeps the reservation fenced. Reconcile the saved Stripe operation before releasing or changing its owner. A confirmed capture permanently closes the listing; a refund keeps it closed. Release requires either a durable journal proving that no intent creation was dispatched, or reconciled terminal cancellation with absence of a captured charge. |
| Cancellation and expiry | The signed purchase and acceptance fix the pickup end time. The retained policy supplies `reservation_grace_seconds`; the service signs the resulting reservation deadline. User cancellation or deadline expiry enters the same serialized release path. A never-dispatched intent permits immediate release; a dispatched or uncertain operation keeps its fence until Stripe evidence confirms cancellation or capture. |
| Recovery | Restore the listing coordinator, operation journal and outbox together. Before resuming Stripe writes, reconcile outstanding operations and signed decision revisions with Stripe and hosted contracts. Retries reuse the saved operation identity and bytes. |

The shared item projection exposes `purchases` as the deduplicated union of the latest decision's live purchase keys and retained captured-sale keys. It retains their distinct live/sale roles and the decision identity for validation, discovery and restore.

The iOS and Android readers derive listing availability from the verified listing decision and captured-sale evidence. Pending references are requests; the authority's reservation determines whether checkout can start. A missing purchase limits that request's detail view while the service repairs its hosted copy. A missing or unverifiable listing decision shows "Availability unknown" and offers refresh.

## Acceptance

- On iOS and Android, registration and interrupted admission return one verified listing decision and hosting receipt. Quotas bind repeated scoped buyer keys to one enrollment.
- Shared fixtures verify purchase parameter bytes, participant roles, source listing and exact UI/policy identities. Home and Marketplace observe one purchase projection.
- Opposite-order decisions converge at 32 live requests. Captured-sale certificates survive cleanup, seller edits and refunds.
- Race two seller acceptances, intent/capture/cancel dispatch and database restore. One reservation fence permits one completed sale; uncertain provider results retain the fence.
- An intent with durable evidence of zero dispatch permits release. Every dispatched or uncertain intent waits for reconciled terminal cancellation or capture.
- Invalid parent messages, forged source/participant contexts, unsupported code and changed terms fail before admission. Merge-law fixtures cover listings and purchases.
