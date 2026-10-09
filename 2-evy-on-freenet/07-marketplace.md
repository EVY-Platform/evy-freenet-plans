# 2.7 EVY Marketplace

## Repositories

| Repository | Role | Work in this plan |
| --- | --- | --- |
| [evy](https://github.com/EVY-Platform/evy) | Modified | Home search rows and Marketplace flows in the complete application document `freenet/ui/evy.json`, published to `ui.evy`. Marketplace's lookups and photo contracts in `freenet/contracts/` and `evyctl lookups publish`. Items carry EVY's item schema and purchase references. SwiftUI and Compose readers derive availability from certified listing decisions and retained sale evidence |
| [freenet-appkit](https://github.com/glesage/freenet-appkit) | Used | Swift package and Kotlin library in the EVY app |

## Purpose

Marketplace is a feature inside the EVY application. Its listing, purchase and photo contracts store data; its Home search, View Item and Create item flows are part of the complete signed EVY UI document. Purchases use [2.6 Payments](06-payments.md).

Publish EVY application version 7 containing Marketplace flows, internal routes and resource bindings under [2.2 EVY UI contracts and publishing](02-ui-contracts.md#application-routes-and-compatible-updates). Matching iOS and Android readers activate that complete document and navigate within it.

## What is cloned

| Marketplace component | Storage or implementation |
| --- | --- |
| Items, `marketplace.items` ([item.schema.json](https://github.com/EVY-Platform/evy/blob/d0fb7e6475f1dfc5c74325e37d4e92aed88d84ed/services/marketplace/src/schema/item.schema.json)) | The items contract from [The purchase contract in 2.12 Listings and purchases](12-listings-and-purchases.md#the-purchase-contract), with service ID `marketplace` and EVY's item schema |
| Lookups: `selling_reasons`, `conditions`, `durations` and `areas` ([lookup.schema.json](https://github.com/EVY-Platform/evy/blob/d0fb7e6475f1dfc5c74325e37d4e92aed88d84ed/services/marketplace/src/schema/lookup.schema.json)) | One lookups contract, signed by the EVY publisher key from [2.1 Hello EVY world](01-hello-evy-world.md#the-evy-publisher-key) and seeded from [service_data.json](https://github.com/EVY-Platform/evy/blob/d0fb7e6475f1dfc5c74325e37d4e92aed88d84ed/scripts/fixtures/services/service_data.json). The EVY publisher updates it with `evyctl lookups publish --service marketplace <file>` |
| Item statuses, `marketplace.item_statuses` ([status.ts](https://github.com/EVY-Platform/evy/blob/d0fb7e6475f1dfc5c74325e37d4e92aed88d84ed/services/marketplace/src/status.ts)) | Both readers derive item availability from the verified listing decision, reservation and retained sale evidence, using [Item availability](#item-availability) |
| Requests and replies between buyer and seller, `evy.messages` ([purchase.ts](https://github.com/EVY-Platform/evy/blob/d0fb7e6475f1dfc5c74325e37d4e92aed88d84ed/services/marketplace/src/purchase.ts)) | The shared message adapter projects signed messages from the common purchase contract in [2.12 Listings and purchases](12-listings-and-purchases.md#evy-purchase-interface) |
| Payment calls and `item_payment_intents` ([payments.ts](https://github.com/EVY-Platform/evy/blob/d0fb7e6475f1dfc5c74325e37d4e92aed88d84ed/services/marketplace/src/payments.ts)) | `services/payment` from 2.6 Payments |
| Pickup address, `evy.addresses` | The shared address adapter projects the private field of Alice's `accept` message after her EVY delegate seals it to the purchase participants and their reader decrypts it in the verified purchase context |
| Photos, `evy.files` named in `photo_ids` | The shared file adapter reads one immutable photo contract per content hash |
| "View Item" flow (page "Item details") and "Create item" flow (pages "Create listing", "Describe item", "Pickup and delivery" and "Payment options") ([service_sdui.json](https://github.com/EVY-Platform/evy/blob/d0fb7e6475f1dfc5c74325e37d4e92aed88d84ed/scripts/fixtures/services/service_sdui.json)) | The complete EVY UI document, published with `evyctl ui publish` ([Publishing a UI version in 2.2 EVY UI contracts and publishing](02-ui-contracts.md#publishing-a-ui-version)) |
| Item search, the "For you", "From you" and "Scheduled" tabs and the "Sell something" button on EVY's SDUI home page ([evy_sdui.json](https://github.com/EVY-Platform/evy/blob/d0fb7e6475f1dfc5c74325e37d4e92aed88d84ed/scripts/fixtures/evy/evy_sdui.json)) | Home rows inside the complete EVY document. Search results and "Sell something" open Marketplace's "View Item" and "Create item" flows by the internal application routes `marketplace.view-item` and `marketplace.create-item`; Marketplace returns through `entry` |
| Checks on items and messages ([validation.ts](https://github.com/EVY-Platform/evy/blob/d0fb7e6475f1dfc5c74325e37d4e92aed88d84ed/services/marketplace/src/validation.ts), purchase.ts) | Checks in the items and purchase contracts ([Service rules in 2.4 SDUI data and actions](04-data-and-actions.md#service-rules)) |

The complete application document's `resources` map declares `marketplace.items` and the shared `evy.purchases`, `evy.messages`, `evy.addresses` and `evy.files` bindings from [Resource bindings in 2.4 SDUI data and actions](04-data-and-actions.md#resource-bindings). Home and Marketplace views use the same EVY data-store projections and source instances.

## Shared messages, addresses and files

| Resource | Interface in Home and Marketplace |
| --- | --- |
| `evy.purchases` | A purchase row retains its originating item and contract key. Either view opens the selected purchase and observes the same status |
| `evy.messages` | Purchase messages retain their purchase key and parent ID. Actions sign with the actor's verified buyer or seller role and update that purchase |
| `evy.addresses` | Create item saves or edits Alice's address in the delegate's private address book and retains its `address_id` in her item. Acceptance reads that owner-held address and seals a copy for Alice's feature encryption key and Bob's purchase-scoped encryption key, with the service, resource, purchase key and message ID bound as authenticated context. `Open` checks that context and exposes a received copy to a permitted recipient. Home and Marketplace use the same address adapter |
| `evy.files` | Photo selection, validation, immutable publication, local caching and fetch use one shared adapter in the iOS and Android readers. The owning item's signed `photo_ids` supplies the references and write permission |

These adapters are registered in [EVY resource catalogue in 2.4 SDUI data and actions](04-data-and-actions.md#evy-resource-catalogue). EVY features declare their supported bindings in the complete signed application document.

### Converting the existing flows

| Flow | Shared resource binding |
| --- | --- |
| Request pickup creates an initial `evy.messages` record | Create `evy.purchases` with the item reference and pickup request data. The adapter creates the signed purchase and its initial `pending` message and saves the returned purchase key for the flow |
| Accept, reject, cancel, pay and handover actions | Create messages with the selected `purchase_key` and parent message ID. Select messages within that purchase |
| Latest request or message selected by item and type | Select by purchase key and verified participant role. Buyer views show that user's scoped buyer purchases; seller views retain every request for their items. Public availability follows the certified listing decision and retained sale evidence |
| Home reads `marketplace.item_statuses` | Bind to the derived `status` on the verified item projection from [Item availability](#item-availability) |
| Create item creates or edits `evy.addresses`; acceptance finds `address_id` | Use the shared delegate-held address book before a purchase exists, then seal a copy into the selected purchase's acceptance message |

The converted Home and Marketplace flows use stable internal application routes and compatible adapter bindings under [Application routes and compatible updates in 2.2 EVY UI contracts and publishing](02-ui-contracts.md#application-routes-and-compatible-updates). The validator checks each action's payload, route arguments and purchase context against all supported document generations.

Each photo has an immutable contract. Its parameter is the JPEG's BLAKE3 hash; its state is the JPEG. The iOS and Android apps keep each photo below 1 MiB so peers can fetch it from a phone behind NAT ([#5643](https://github.com/freenet/freenet-core/issues/5643)). `photo_ids` holds the contract keys, and each phone caches the JPEG. Use [EVYFileRPC.swift](https://github.com/EVY-Platform/evy/blob/d0fb7e6475f1dfc5c74325e37d4e92aed88d84ed/ios/evy/Data/API/EVYFileRPC.swift) and [EVYFileCache.swift](https://github.com/EVY-Platform/evy/blob/d0fb7e6475f1dfc5c74325e37d4e92aed88d84ed/ios/evy/Data/EVYFileCache.swift) for the iOS file adapter and cache, with matching Android behavior. [seed-files](https://github.com/EVY-Platform/evy/tree/d0fb7e6475f1dfc5c74325e37d4e92aed88d84ed/scripts/fixtures/services/seed-files) supplies fixtures.

## Item availability

The SwiftUI and Compose readers verify each listing's seller-authorized service decision and retained captured-sale evidence under [Listing admission and one sale in 2.12 Listings and purchases](12-listings-and-purchases.md#listing-admission-and-one-sale). They fetch admitted purchase states for request details and verify code, parameters, service, item and participant signatures. Home search, item details and participant tabs use the same authority-backed availability.

The reader uses the first matching availability rule. A capture certificate permanently closes its listing. Refund display uses that sale's highest verified payment `(revision, payment_hash)`; earlier capture/payment records remain evidence.

| Verified purchase evidence | Derived availability | Reader behavior |
| --- | --- | --- |
| A capture certificate exists and its latest verified payment revision has a partial or zero buyer refund | `sold` | Hide the listing from available-item search; show the completed sale and any partial refund amounts in participant views |
| A capture certificate exists and its latest verified payment revision has a full buyer refund | `refunded` | Keep the listing closed and show the refund in participant views |
| A capture certificate exists while payment details are unavailable | `sold` | Keep the listing closed and show "Payment details refreshing"; update the refund display when its latest payment revision verifies |
| The current signed listing decision reserves one purchase, including a declined card awaiting retry | `pickup_pending` | Show the reservation and its purchase flow |
| The listing decision is missing or unverifiable | Unknown | Show "Availability unknown" and offer refresh; enable requests once the authority verifies availability |
| The current signed decision has no reservation or captured sale | `available` | Show the listing in search. Enable a request within admission capacity; otherwise show "Requests full". A missing pending purchase affects its detail view while the service repairs it |

The derived `status` is a reader value supplied to the UI rows and action guards. It updates when the signed listing decision or captured-payment evidence changes. EVY's application data layer fetches and subscribes to the required state for search candidates and open listings. Views observe its projections. The layer keeps a bounded contract set and refreshes it through the connection lifecycle. Offline views show the observation time of cached purchase state and refresh availability on reconnect.

The service removes live requests after verified terminal rejection or cancellation, following the reservation fence rules. Captured-sale evidence remains separate for the listing's lifetime, including after refunds and seller edits. Alice uses a new listing ID to sell an item again after a refund.

### Pilot hosting

The EVY operator owns a durable hosting inventory for admitted purchases, listing decisions and referenced photos. `register_listing` and `register_purchase` perform the required inventory steps. Before admission or an item-publication acknowledgement, its full peer verifies the exact contract code, parameters and bytes and saves a recovery copy in operator storage. The payment service keeps admitted purchases subscribed from request through completion and the declared dispute/retention period. The operator keeps photos available for the listing and its retained sale evidence.

The inventory records the owning listing, contract identity, digest and retention deadline. A worker verifies availability through a second node, repairs missing hosted copies with saved bytes and alerts the operator on failure. Capacity refusal retains the user's draft and reports the limit before acknowledgement. Set storage quotas and retention periods before the pilot; recovery replays the inventory. Core's own hosting budgets still apply, so the operator supplies this application-level recovery responsibility.

## Moderation and seller admission

Owner: Marketplace product owner. Before pilot launch, name a primary and backup moderator, publish support contact/response time and approve seller/buyer terms. Product definitions in this section feed release checks in [2.10 Testing and release](10-testing-and-release.md#store-requirements).

| Record | Signed schema and authority |
| --- | --- |
| Seller lookup | Publisher-signed `marketplace.sellers/1`: application/feature, monotonic revision, policy identity, map keyed by seller public key, enrollment ID, Stripe association verification, admitted/suspended status and effective time. One active entry per verified seller. |
| Report | `marketplace.report/1`: UUID, scoped reporter key, target kind (`item`, `photo`, `purchase-message`), source contract key, target ID/digest, reason (`prohibited`, `scam`, `offensive`, `other`), creation time and signature. Optional private supporting details are sealed to the moderator. |
| Moderator authority | Publisher-signed `marketplace.moderator/1`: moderator key, application/feature, allowed report/removal/seller-suspension roles, validity interval and authority generation. |
| Removal | `marketplace.removal/1`: target contract/ID/digest, immutable target identity, authority reference, revision, reason and moderator signature. A valid tombstone suppresses visible content across readers. |

The reports contract has a 512 KiB state cap and retains at most 1,000 ranked report IDs. Its versioned merge keeps the higher signed revision/hash per ID and the highest immutable `(created_at, id)` ranks; moderation tombstones keep ranked slots. The operator archives report/decision evidence before compaction and enforces bounded pilot admission. Shared merge fixtures cover same-rank reports, replay and archived resolutions. Public reports disclose target and reason; the report screen explains that scope.

Seller admission verifies the seller key through a signed backend challenge and the resulting Stripe connected account association in [2.6 Payments](06-payments.md#fees-and-seller-accounts). The payment backend enforces the current admitted seller lookup at listing registration and new purchase admission. Search and reader actions use the verified latest lookup; offline views label its observation time. Suspension removes new-listing/request authority and preserves existing purchases, payment/refund reconciliation and retained sale evidence.

| User-written flow | Required actions and filtering |
| --- | --- |
| Listing details, description and photos | Report selected content; Block verified seller key; hide tombstoned or blocked content in Home search and Marketplace views |
| Purchase requests and participant messages | Report selected message; Block its verified author/purchase scope. Suppress later content from that key while retaining transaction status, receipts and dispute access |
| Production guestbook, if retained | Named moderator, Report/Block and authenticated tombstones under its owning feature policy |

Block lists are encrypted host records in the global inventory, with observed signing scopes and source context. The reader discloses the chosen scope; purchase-scoped keys bind only the selected purchase. Moderation and user blocking preserve transaction evidence needed for payments, refunds and support. A removal tombstone suppresses display; immutable network/evidence bytes remain under their declared retention.

Terms acceptance records identify actor scope, role, document digest, version and time before listing/request submission. The service verifies terms and seller admission along with the signed source/purchase context. The support page states report response time, a 14-day buyer dispute window after pickup and a 7-day moderation decision window. Moderator refund access is a separately assigned backend role.

```text
evyctl lookups publish --service marketplace sellers.json
evyctl record list marketplace.reports --status open
evyctl report resolve marketplace.reports <report-id> --decision remove --reason scam
evyctl record remove marketplace.items <item-id> --authority marketplace-moderator
evyctl seller suspend marketplace <seller-key> --reason scam
```

Each command validates its role, saves exact signed bytes, submits idempotently and records independent readback. Seller suspension publishes a higher lookup revision. Report resolution/removal retain target evidence and the signed decision in operator storage; a receipt follows durable retention. Readers verify authority and apply tombstones before rendering. Fixtures cover forged moderator keys, stale lookup/revocation, blocked messages in both views, restored block/consent records and receipt/status access after blocking.

## The skateboard sale

Alice sells her skateboard on her iPhone and Bob buys it on his Android phone.

| Step | Who | What they do | Message | Derived item availability |
| --- | --- | --- | --- | --- |
| 1 | Alice | Lists the skateboard in "Create item" for 70 dollars, with photos and Saturday pickup times | None | `available` |
| 2 | Bob | Finds it in search, opens "Item details" and taps "Request 10:00" for Saturday | `pending` | `available` |
| 3 | Alice | Taps "Accept" in "For you". Her message carries the sealed pickup address; the payment service confirms Bob's listing reservation | `accept` and reservation receipt | `pickup_pending` |
| 4 | Bob | At the pickup on Saturday, taps "Item received" and pays 70.00 dollars in Stripe's payment sheet | `transaction` | `pickup_pending` |
| 5 | Alice | Taps "Confirm" in "Item given". The payment service captures the payment | `transaction_completed` | `sold` |

Readers that receive the verified completed purchase hide the skateboard from available-item search, including while Alice's app is closed. Alice receives 69.30 dollars, as [Fees and seller accounts in 2.6 Payments](06-payments.md#fees-and-seller-accounts) shows.

## Pilot enrollment

The Sydney/AUD pilot uses the signed seller lookup above and one operator-issued buyer enrollment per verified participant. Enrollment ID, quota scope and credential expiry are defined with [2.12 Listings and purchases](12-listings-and-purchases.md#listing-admission-and-one-sale). Repeated purchase-scoped buyer keys share enrollment quotas. Set hosting storage, repair alarms, live-request limits and listing/dispute retention before the pilot. Record named product and operations owners with exact policy/lookup versions.

## Acceptance

- Deliver an immutable capture certificate, its original zero-refund payment and a higher full-refund revision in either order. Both readers keep the listing closed and show `refunded`; a partial latest refund shows `sold` with its amount.

- Turn off both participant phones after the operator acknowledges a listing with photos and an admitted unpaid purchase. A fresh reader fetches the item, photos and request from the operator-backed network copies. Evict one copy, restore it from inventory and verify exact bytes through a second node. Capacity refusal preserves the draft.

- On iOS and Android, Home and Marketplace read the same purchase, message and file instances through the shared bindings. Both expose the same decrypted pickup address to Alice and Bob. Substituting another service, purchase, message or recipient in the address context fails decryption or permission checks.
- On iOS and Android, Bob and Carol request the same item. Each buyer sees their own purchase and messages; Alice sees both requests. Acceptance and payment target the selected purchase. Home's derived availability agrees with Marketplace. Alice's address exists before either request, survives backup restore and delegate migration, and only each intended recipient decrypts their purchase's address copy.
- On iOS and Android, after the EVY application version that adds Marketplace, the home page shows item search, the three tabs and "Sell something", in the installed apps. A search result opens "View Item" and "Sell something" opens "Create item" within the complete EVY UI document.
- On iOS and Android, the skateboard sale passes with Alice on iOS and Bob on Android, then with the platforms swapped. Both phones show `available`, `pickup_pending` and `sold` at the same steps, and an independent peer reads the same item and purchase.
- On iOS and Android, terminate Alice's app after her `transaction_completed` message reaches the purchase contract and before capture finishes. The payment service completes capture, and Bob's reader and a third reader derive `sold` and hide the listing from available-item search. The item record keeps the same revision during capture.
- Shared SwiftUI and Compose fixtures cover multiple linked purchases, a declined card awaiting retry, cancellation, sale, refund and unavailable purchase state. Retained captured-sale evidence keeps the listing closed when purchase or payment details are missing, including alongside a stale available decision. A missing pending purchase affects that request's details while the verified listing decision still governs admission. A missing listing decision shows "Availability unknown" until it verifies.
- On iOS and Android, cleanup removes a terminally canceled purchase reference and retains separate captured-sale evidence through seller edits and partial or full refunds. A partial refund keeps `sold` with its refunded amount; a full buyer refund shows `refunded`. Both readers keep the completed listing closed. A purchase with the wrong supported code, seller, service or item ID fails admission validation.
- On iOS and Android, the skateboard's photos show on Bob's phone, read from their photo contracts.
- `evyctl ui publish` accepts the complete EVY document containing Home and Marketplace flows, with valid internal routes and resource bindings.
- The items contract rejects an item not signed by its seller and a price of 0, following EVY's item schema. A photo contract rejects bytes that do not match its hash.
- Only Alice's and Bob's phones can read the pickup address.
