# 2.7 EVY Marketplace

## Repositories

| Repository | Role | Work in this plan |
| --- | --- | --- |
| [evy](https://github.com/EVY-Platform/evy) | Modified | Marketplace's rows in the home document `freenet/ui/home.json`. Marketplace's flows published to the `marketplace` UI contract. Marketplace's lookups and photo contracts in `freenet/contracts/` and `evyctl lookups publish`. Items carry EVY's item schema and purchase references. SwiftUI and Compose readers derive availability from verified purchases |
| [freenet-appkit](https://github.com/glesage/freenet-appkit) | Used | Swift package and Kotlin library in the EVY app |

## Purpose

EVY's Marketplace lets people buy and sell locally ([EVY-Platform/evy](https://github.com/EVY-Platform/evy), [data models](https://github.com/EVY-Platform/evy/blob/dev/docs/services/marketplace/data.md)). This plan runs Marketplace on Freenet. Contracts in evy's `freenet/` workspace store its data. The `marketplace` UI contract stores its flows, and purchases use [2.6 Payments](06-payments.md). The evy repository defines Marketplace's schemas and behavior.

A new home version adds Marketplace's search and tabs and adds `marketplace` to `services`. The installed iOS and Android apps derive Marketplace's UI contract key from that entry, as [The home service in 2.2 EVY UI contracts and publishing](02-ui-contracts.md#the-home-service) describes.

## What is cloned

| Marketplace component | Storage or implementation |
| --- | --- |
| Items, `marketplace.items` ([item.schema.json](https://github.com/EVY-Platform/evy/blob/dev/services/marketplace/src/schema/item.schema.json)) | The items contract from [The purchase contract in 2.6 Payments](06-payments.md#the-purchase-contract), with service ID `marketplace` and EVY's item schema |
| Lookups: `selling_reasons`, `conditions`, `durations` and `areas` ([lookup.schema.json](https://github.com/EVY-Platform/evy/blob/dev/services/marketplace/src/schema/lookup.schema.json)) | One lookups contract, signed by the EVY publisher key from [2.1 Hello EVY world](01-hello-evy-world.md#the-evy-publisher-key) and seeded from [service_data.json](https://github.com/EVY-Platform/evy/blob/dev/scripts/fixtures/services/service_data.json). The EVY publisher updates it with `evyctl lookups publish --service marketplace <file>` |
| Item statuses, `marketplace.item_statuses` ([status.ts](https://github.com/EVY-Platform/evy/blob/dev/services/marketplace/src/status.ts)) | Both readers derive item availability from the verified states of its linked purchase contracts, using [Item availability](#item-availability) |
| Requests and replies between buyer and seller, `evy.messages` ([purchase.ts](https://github.com/EVY-Platform/evy/blob/dev/services/marketplace/src/purchase.ts)) | The shared message adapter projects signed messages from the common purchase contract in [2.6 Payments](06-payments.md#shared-purchase-interface) |
| Payment calls and `item_payment_intents` ([payments.ts](https://github.com/EVY-Platform/evy/blob/dev/services/marketplace/src/payments.ts)) | `services/payment` from 2.6 Payments |
| Pickup address, `evy.addresses` | The shared address adapter projects the private field of Alice's `accept` message after her EVY delegate seals it to the purchase participants and their reader decrypts it in the verified purchase context |
| Photos, `evy.files` named in `photo_ids` | The shared file adapter reads one immutable photo contract per content hash |
| "View Item" flow (page "Item details") and "Create item" flow (pages "Create listing", "Describe item", "Pickup and delivery" and "Payment options") ([service_sdui.json](https://github.com/EVY-Platform/evy/blob/dev/scripts/fixtures/services/service_sdui.json)) | The `marketplace` UI contract, published with `evyctl ui publish` ([Publishing a UI version in 2.2 EVY UI contracts and publishing](02-ui-contracts.md#publishing-a-ui-version)) |
| Item search, the "For you", "From you" and "Scheduled" tabs and the "Sell something" button on EVY's SDUI home page ([evy_sdui.json](https://github.com/EVY-Platform/evy/blob/dev/scripts/fixtures/evy/evy_sdui.json)) | The same rows in the `home` document. Search results and "Sell something" open Marketplace's "View Item" and "Create item" flows by flow UUID, and Marketplace's flows return to the home flow the same way |
| Checks on items and messages ([validation.ts](https://github.com/EVY-Platform/evy/blob/dev/services/marketplace/src/validation.ts), purchase.ts) | Checks in the items and purchase contracts ([Service rules in 2.4 SDUI data and actions](04-data-and-actions.md#service-rules)) |

The `resources` maps in the `marketplace` and `home` documents declare `marketplace.items` and the shared `evy.purchases`, `evy.messages`, `evy.addresses` and `evy.files` bindings from [Resource bindings in 2.4 SDUI data and actions](04-data-and-actions.md#resource-bindings). Both applications use the same implementations and source instances.

## Shared messages, addresses and files

| Resource | Interface in Home and Marketplace |
| --- | --- |
| `evy.purchases` | A purchase row retains its originating item and contract key. Either application opens the same purchase and observes the same status |
| `evy.messages` | Purchase messages retain their purchase key and parent ID. Actions sign with the actor's verified buyer or seller role and update that purchase |
| `evy.addresses` | Create item saves or edits Alice's address in the delegate's private address book and retains its `address_id` in her item. Acceptance reads that owner-held address and seals a copy for Alice's service encryption key and Bob's purchase-scoped encryption key, with the service, resource, purchase key and message ID bound as authenticated context. `Open` checks that context and exposes a received copy to a permitted recipient. Home and Marketplace use the same address adapter |
| `evy.files` | Photo selection, validation, immutable publication, local caching and fetch use one shared adapter in the iOS and Android readers. The owning item's signed `photo_ids` supplies the references and write permission |

These adapters are registered in [Shared EVY catalogue in 2.4 SDUI data and actions](04-data-and-actions.md#shared-evy-catalogue). Future EVY applications use the same versioned interfaces and declare their source bindings in their signed UI documents.

### Converting the existing flows

| Flow | Shared resource binding |
| --- | --- |
| Request pickup creates an initial `evy.messages` record | Create `evy.purchases` with the item reference and pickup request data. The adapter creates the signed purchase and its initial `pending` message and saves the returned purchase key for the flow |
| Accept, reject, cancel, pay and handover actions | Create messages with the selected `purchase_key` and parent message ID. Select messages within that purchase |
| Latest request or message selected by item and type | Select by purchase key and verified participant role. Buyer views show that user's scoped buyer purchases; seller views retain every request for their items. Public availability reads the bounded reference set separately |
| Home reads `marketplace.item_statuses` | Bind to the derived `status` on the verified item projection from [Item availability](#item-availability) |
| Create item creates or edits `evy.addresses`; acceptance finds `address_id` | Use the shared delegate-held address book before a purchase exists, then seal a copy into the selected purchase's acceptance message |

The converted `home` and `marketplace` documents ship together with their adapter bindings. The validator checks each action's payload against its operation schema, including purchase routing fields.

Each photo has an immutable contract. Its parameter is the JPEG's BLAKE3 hash; its state is the JPEG. The iOS and Android apps keep each photo below 1 MiB so peers can fetch it from a phone behind NAT ([#5643](https://github.com/freenet/freenet-core/issues/5643)). `photo_ids` holds the contract keys, and each phone caches the JPEG. Use [EVYFileRPC.swift](https://github.com/EVY-Platform/evy/blob/dev/ios/evy/Data/API/EVYFileRPC.swift) and [EVYFileCache.swift](https://github.com/EVY-Platform/evy/blob/dev/ios/evy/Data/EVYFileCache.swift) for the iOS file adapter and cache, with matching Android behavior. [seed-files](https://github.com/EVY-Platform/evy/tree/dev/scripts/fixtures/services/seed-files) supplies fixtures.

## Item availability

The SwiftUI and Compose readers load each candidate listing's `purchases` references and read their purchase contracts. They verify the supported purchase code, contract parameters and signed records, and check that the purchase names this listing's service, item ID and seller. Home search, item details and the seller and buyer tabs use the same derived availability.

The reader uses the first matching availability rule.

| Verified purchase evidence | Derived availability | Reader behavior |
| --- | --- | --- |
| Any linked purchase is `sold` | `sold` | Hide the listing from available-item search; show the completed sale and any partial refund amounts in participant views |
| Any linked purchase is `refunded` | `refunded` | Keep the listing closed and show the refund in participant views |
| Any linked purchase is `pickup_pending`, including a declined card awaiting retry | `pickup_pending` | Show the reservation and its purchase flow |
| Required linked purchase state is missing or unavailable | Unknown | Show "Availability unknown" and offer refresh; enable a new purchase request once availability resolves to `available` |
| All linked purchases resolve, and each is unaccepted or has a completed cancellation; an empty reference list also matches | `available` | Show the listing in available-item search and enable a purchase request |

The derived `status` is a reader value supplied to the UI rows and action guards. It updates when the listing's reference set or a linked purchase changes. Readers fetch the required state for search candidates and open listings, keep subscription handles while those views need them, and release the handles with the views. Offline views show the observation time of cached purchase state and refresh availability on reconnect.

Cleanup keeps the reference to every captured sale for the listing's lifetime, including a sale later partially or fully refunded. Seller edits preserve these references. Canceled purchases become eligible for reference cleanup after terminal cancellation is verified; where a PaymentIntent exists, its signed payment record must confirm `canceled`. The listing's 32-reference cap includes retained sale references. Alice uses a new listing ID when she lists an item for sale again after a refund.

## The skateboard sale

Alice sells her skateboard on her iPhone and Bob buys it on his Android phone.

| Step | Who | What they do | Message | Derived item availability |
| --- | --- | --- | --- | --- |
| 1 | Alice | Lists the skateboard in "Create item" for 70 dollars, with photos and Saturday pickup times | None | `available` |
| 2 | Bob | Finds it in search, opens "Item details" and taps "Request 10:00" for Saturday | `pending` | `available` |
| 3 | Alice | Taps "Accept" in "For you". Her message carries the pickup address sealed to Alice and Bob | `accept` | `pickup_pending` |
| 4 | Bob | At the pickup on Saturday, taps "Item received" and pays 70.00 dollars in Stripe's payment sheet | `transaction` | `pickup_pending` |
| 5 | Alice | Taps "Confirm" in "Item given". The payment service captures the payment | `transaction_completed` | `sold` |

Readers that receive the verified completed purchase hide the skateboard from available-item search, including while Alice's app is closed. Alice receives 69.30 dollars, as [Fees and seller accounts in 2.6 Payments](06-payments.md#fees-and-seller-accounts) shows.

## Acceptance

- On iOS and Android, Home and Marketplace read the same purchase, message and file instances through the shared bindings. Both expose the same decrypted pickup address to Alice and Bob. Substituting another service, purchase, message or recipient in the address context fails decryption or permission checks.
- On iOS and Android, Bob and Carol request the same item. Each buyer sees their own purchase and messages; Alice sees both requests. Acceptance and payment target the selected purchase. Home's derived availability agrees with Marketplace. Alice's address exists before either request, survives backup restore and delegate migration, and only each intended recipient decrypts their purchase's address copy.
- On iOS and Android, after the home version that adds `marketplace`, the home page shows item search, the three tabs and "Sell something", in the installed apps. A search result opens "View Item" and "Sell something" opens "Create item" from the `marketplace` UI contract.
- On iOS and Android, the skateboard sale passes with Alice on iOS and Bob on Android, then with the platforms swapped. Both phones show `available`, `pickup_pending` and `sold` at the same steps, and an independent peer reads the same item and purchase.
- On iOS and Android, terminate Alice's app after her `transaction_completed` message reaches the purchase contract and before capture finishes. The payment service completes capture, and Bob's reader and a third reader derive `sold` and hide the listing from available-item search. The item record keeps the same revision during capture.
- Shared SwiftUI and Compose fixtures cover multiple linked purchases, a declined card awaiting retry, cancellation, sale, refund and unavailable purchase state. A sold purchase takes precedence over an unresolved reference. An unresolved reference with no known reservation or completed sale shows "Availability unknown" and enables a new request after refresh resolves it as `available`.
- On iOS and Android, cleanup removes a terminally canceled purchase reference and retains a captured sale reference through seller edits and partial or full refunds. A partial refund keeps `sold` with its refunded amount; a full buyer refund shows `refunded`. Both readers keep the completed listing closed. A purchase with the wrong supported code, seller, service or item ID fails link validation.
- On iOS and Android, the skateboard's photos show on Bob's phone, read from their photo contracts.
- `evyctl ui publish` accepts Marketplace's two flows and the new home version against EVY's schemas, including every `navigate` between them.
- The items contract rejects an item not signed by its seller and a price of 0, following EVY's item schema. A photo contract rejects bytes that do not match its hash.
- Only Alice's and Bob's phones can read the pickup address.
