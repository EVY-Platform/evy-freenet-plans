# 3.8 Paid application pilot and commercial acceptance

## Repositories

| Repository | Role | Work in this plan |
| --- | --- | --- |
| `evy-marketplace` | Created | Admission, continuation, store, listing and order contracts, domain delegates, cryptographic profile, custom web UI and fixtures |
| [evy](https://github.com/EVY-Platform/evy) | Modified | Catalogue entry and pilot wiring in the iOS and Android apps; the attribution, payment and remuneration services serve the pilot |
| `freenet-appkit` | Used | Bundles, host authority, checkout adapter, journals and migration from milestone 1 (Freenet mobile AppKit) and milestone 3 (Attribution, remuneration and payment) |
| [harvest](https://github.com/freenet/harvest) | Used | Design references listed at the end of this plan |
| [freenet-core](https://github.com/freenet/freenet-core) | Used | Hosting and eviction #4642 and local pin #5041 as retention references |

## Owned scope

Marketplace proves one commercial flow through a certified application release: listing, agreed pickup, checkout, fulfillment evidence, contributor allocation, payout and refunds. This plan owns the pilot, fulfillment protocol, bounded storage profiles, product release approvals and supporting Harvest source references.

The first UI is custom web application code hosted in EVY's isolated WebView session. It calls concrete Marketplace contracts and delegates through AppKit, then uses the authorized native checkout bridge. Developers can also write custom native clients against those protocols. Optional [4.7 SDUI commerce and attribution](../4-sdui/07-commerce.md) uses the same domain evidence, with reader conformance in milestone 4 (SDUI).

## Prerequisites

Use the curated River and Atlas host from [2.1 EVY shell and curated catalogue](../2-evy-mobile-app/01-catalogue.md) and authenticated multi-app sessions from [2.2 Multi-application sessions and authority](../2-evy-mobile-app/02-sessions.md) in milestone 2 (EVY mobile app). The foundation supplies:

- [1.3 Single-application host](../1-freenet-mobile-appkit/03-host.md)
- [1.4 Application bundles](../1-freenet-mobile-appkit/04-bundles.md)
- [1.5 Identity, keys and local protection](../1-freenet-mobile-appkit/05-identity.md)
- [1.6 Application protocols, data and operations](../1-freenet-mobile-appkit/06-data-and-operations.md)
- [1.7 Upgrades and migration](../1-freenet-mobile-appkit/07-migration.md)

The mobile run requires [1.10 Thin-peer role and cellular data budgets](../1-freenet-mobile-appkit/10-thin-peer.md).

Commercial acceptance requires:

- [3.1 Product and contributor registration](01-registration.md)
- [3.2 Attribution workflow and allocation weights](02-attribution.md)
- [3.3 Artifact certification and publication evidence](03-certification.md)
- [3.4 Payments and checkout adapters](04-payment.md)
- [3.5 Usage evidence, remuneration and payouts](05-remuneration.md)
- [3.6 Contribution and release workspace](06-developer.md)
- [3.7 Operating readiness](07-operations.md)

Service work and application fixtures can proceed in parallel against these interfaces.

## Product release approval

Select one supported region/currency and a small set of onboarded sellers. The pilot uses fixed-price pickup at an agreed place and time, manual seller agreement, cancellation/refund handling and participant-signed completion. A curated seller list limits product scope while public contract inputs still require adversarial validation.

Name the people holding these roles in the release record. Both roles approve the pilot and each expansion before its flows are enabled.

| Approving role | Required decision |
| --- | --- |
| Marketplace product owner | Enabled modes, participant terms, privacy disclosures, baseline moderation, dispute handling and passing product fixtures |
| Financial operations lead | Supported regions/processors and actual accounts, costs, refund and reserve rules, regional/distribution policy, abuse-response capacity, recovery readiness and passing operational fixtures |

Pilot tests reject unsupported bargaining, rescheduling, delivery, shipping and automatic acceptance before signing a commitment or opening checkout. Expansion approval names each added mode, its policy versions and passing [mode-specific tests](#expansion-acceptance). Neighborhood search and wider moderation tools also require product and operations approval. Optional reputation and provider-based discovery follow [5.1 Peer reputation](../5-optional-extensions/01-reputation.md) and [5.4 Discovery and catalogue extensions](../5-optional-extensions/04-discovery.md).

## Pilot sequence

Alice lists a skateboard for 70 dollars. Bob proposes Saturday pickup. Both sign the complete agreed terms, then Bob checks out. They each confirm the handover. The services verify the domain evidence, allocate the collected contributor fee and pay eligible contributors under the fixed policy.

| Step | Required result |
| --- | --- |
| Certified release | Attribution verifies the custom web archive and its source/publication evidence |
| Listing | Seller signs a bounded listing revision with price, currency, quantity and coarse area |
| Agreed pickup | Bob's signed request and both participants' agreement bind the exact listing and terms |
| Checkout | Native trusted confirmation and payment service checks bind one attempt to those terms |
| Payment evidence | The order verifies embedded signed status and matches amount, currency and terms |
| Fulfillment | Both participants sign completion evidence for the agreed handover |
| Allocation | Remuneration validates the policy's capabilities and completion evidence against the original payment |
| Payout | The service reserves and pays funded balances, preserving receipt lineage |
| Refund | The processor, order status, fee adjustments and contributor ledger reconcile under their recorded policies |

## Application and authority boundaries

Marketplace code owns forms, navigation and concrete request orchestration. Its delegates decode domain records, prepare canonical updates and sign/encrypt through protected storage. Contracts validate shared state. The foundation interfaces listed in [prerequisites](#prerequisites) own delegate access, durable operations, host authority and identity.

Package the custom web build and required domain artifacts through [1.4 Application bundles](../1-freenet-mobile-appkit/04-bundles.md). Publish from the [repository/CLI/CI workflow in 3.6 Contribution and release workspace](06-developer.md#repository-and-clici-workflow). A native build uses its separate certified artifact and distribution policy. Financial capabilities describe domain behavior, such as `marketplace.fulfillment.agree` and `marketplace.order.complete`.

| Owner | Authoritative result |
| --- | --- |
| Marketplace contracts and authorized participants | Listing, agreed terms, fulfillment and dispute evidence |
| Attribution service | [3.2 Attribution workflow and allocation weights](02-attribution.md), [3.3 Artifact certification and publication evidence](03-certification.md) |
| [3.4 Payments and checkout adapters](04-payment.md) | Checkout, fee terms, processor reconciliation and signed payment status |
| [3.5 Usage evidence, remuneration and payouts](05-remuneration.md) | Usage record format, allocation, balances and payouts |

## Record identity

Each domain record carries its schema version, application identity, logical request ID, author, recipient, order and listing reference, terms revision and causal predecessor.

1. Derive its record ID from a domain-separated canonical encoding of every unsigned field, excluding the record ID and signature.
2. Sign the complete content together with that derived ID.
3. After encryption and envelope signing, derive the storage entry digest from the complete final envelope bytes.
4. Recompute each identity at the boundary where it applies.

Changing a price, destination, schedule or other signed term creates a new record identity. A counterproposal references its predecessor. A retry preserves the logical operation ID and original signed/encrypted bytes. Keep logical request/order identity distinct from a content-derived record ID. Participant journals retain observed conflicting variants within their disclosed evidence limits.

## Orders, canonical terms and conflicts

An agreed order binds buyer, seller, originating request, exact listing revision, quantity, amount, currency, pickup terms, charges, verified seller beneficiary, contributor-fee terms, terms revision and payment authority. Compute its digest from the complete canonical terms. All agreement signatures and Checkout requests cover that digest. Changed terms require a new signed revision and renewed agreement.

The buyer verifies that the seller's acceptance answers the buyer's own request. Create each order as a separate contract instance with a `Put` for the initial proposal. Preserve the original contract parameters and actual instance reference through retries and migration.

Keep signed events and derive status from verified evidence. Incompatible concurrent events produce `Conflicted`. Resolving an economic commitment requires the affected parties' signed agreement or evidence from the authority defined for that payment operation.

| Order profile rule | Bound |
| --- | --- |
| Authorized writers | Buyer, seller and payment bridge, with fixed bridge root key in parameters |
| Record size | 4 KiB including signed envelope |
| Records per writer/event kind | 16, with lowest-digest selection beyond the limit |
| Payment revisions | 32 revision slots per payment, keeping the highest revision numbers |
| Disputes | 4 records per participant, with lowest-digest selection beyond the limit |
| Variants per slot | Two lowest digests retained as conflict evidence |

Full-state and delta merges apply deterministic selection over the combined valid set. Fix and test the finite event-kind schema, maximum payment attempts per order and maximum encoded succession evidence before pilot launch so total state is bounded. [3.4 Payments and checkout adapters](04-payment.md#signed-payment-status) owns revision-conflict and predecessor-recovery rules. Participant journals and service archives retain evidence that falls outside network bounds.

Progress runs through proposed, agreed, payment pending, paid, fulfillment pending and completed states. Decline, conflict, cancellation and dispute are explicit outcomes. Processor refunds and chargebacks append financial evidence even after completion. Payment idempotency applies to each bound payment operation. [Listing rules](#listings-and-storage-profiles) govern competing inventory commitments.

## Public first contact and bounded transport

Each listing advertises a seller-signed current request generation. Verify that signature and its seller/endpoint/encryption-key binding before sending. Public first contact uses a bounded admission contract. After admission, the seller grants a continuation page.

Both contracts merge by deterministic set union followed by selection. These constants form the proposed v1 wire profile:

| Contract | Record limit | Capacity | Selection |
| --- | --- | --- | --- |
| Public admission | 4 KiB including signed envelope and padded ciphertext | 64 records | Keep the lowest full content digests |
| Granted continuation | 4 KiB per record | 16 slots per participant | Keep the two lowest storage digests per slot |

Selection bounds storage and makes replicas converge. A sender can grind digests or flood admission and displace an honest request. Show `Awaiting seller receipt`, `Request absent from current set` or `Admission saturated` according to observed evidence. The host retains the original signed request and retries within budgets. Delivery requires a signed seller receipt. A seller can open a new generation, which remains subject to the same saturation risk.

A signed continuation grant binds application, page identity, generation, permitted participant writer, order, request ID, slot range, schema version and maximum record size. Each delta includes its grant and the operations using it. Reject a delta in full when its grant is absent. The sender re-offers the complete delta with the grant attached.

Two distinct valid records in one slot prove that its writer signed competing records. Mark the slot `Conflicted` and block the affected domain transition. Conflict witnesses pass the same writer, grant and signature checks as ordinary records. Additional observed variants can remain in bounded participant journals.

When a page fills, both participants sign its successor-page reference and agreed checkpoint. Recovery and dispute access rely on retained network copies and recovery-covered participant journals. A new generation or page preserves the referenced evidence and authorization chain.

Full-state and delta validation use identical encoding, signature, grant, digest and size rules. Define empty bootstrap state explicitly. Contract expiry requires explicit time evidence or signed participant action. Local retry deadlines and appointment times have their own meanings.

## Encryption, receipts and recovery

Use a reviewed, versioned cryptographic profile. Authenticate routing/context fields with the ciphertext, derive direction-specific keys and independently sign domain records. Keep signing and encryption keys in delegates or platform-protected stores. State ciphertext retention, compromised-key behavior and forward-secrecy expectations in that profile.

Apply limits before expensive parsing, key derivation or decryption. Encrypt allowed attachments separately and address them by ciphertext digest. Encrypt names, previews and sensitive metadata. Enforce count, byte, decode, CPU and download limits in the trusted host, including during malformed-record floods. Cache deterministic refusals to avoid repeated expensive work.

A signed admission receipt means the recipient verified and persisted a record locally. It records delivery rather than agreement, payment, dispatch or handover. Commit the processed-operation marker and resulting local state atomically. Retrying a processed record returns its saved result. Each side effect uses a stable operation ID under [1.6 Application protocols, data and operations](../1-freenet-mobile-appkit/06-data-and-operations.md).

Sender queues survive restart and uncertain submission. Re-fetch state, obtain delegate reconciliation and republish eligible pending records within budgets, including a bounded previous-generation window. A local deadline stops retries. Participant schedules describe agreed appointments. Contract expiry follows the evidence rules in [bounded transport](#public-first-contact-and-bounded-transport).

Confirm protected persistence of private order evidence before checkout. [1.5 Identity, keys and local protection](../1-freenet-mobile-appkit/05-identity.md) owns recovery coverage, explicit device enrollment and local deletion. Warn before forgetting an active order whose keys or evidence support fulfillment or a claim. Report failed deletion and the continued existence of network copies, exports or recipient-held data. Optional [5.3 Device sync and authoring collaboration](../5-optional-extensions/03-sync-and-collaboration.md) and [5.2 Extended customer backup and recovery](../5-optional-extensions/02-recovery.md) have separate gates.

Filter blocked keys in the domain delegate before presentation and acknowledgement. Apply the [public metadata disclosures](#pilot-privacy-and-disputes) before collecting data.

## Listings and storage profiles

The pilot uses bounded signed store/listing records. Wider search and fulfillment fields follow the [expansion gate](#product-release-approval).

| Contract | Writer | Record limit | Capacity | Selection |
| --- | --- | --- | --- | --- |
| Store | Seller | 4 KiB per record | One profile plus 256 listing references | Highest signed version per slot, retaining two lowest digests for a same-version conflict |
| Listing | Seller | 4 KiB per revision | 16 revision slots | Highest signed versions, retaining two lowest digests for a same-version conflict |

Test maximum canonical state size from the codec, including conflict witnesses. Seller-only authority controls admission, while deterministic selection preserves merge convergence.

A listing revision includes seller, stable listing reference, complete terms digest, status, title, description, category, media references, price/currency, availability, quantity, coarse location, fulfillment modes and claimed author times. Later delivery terms add service area and fees. Shipping adds supported destinations and services.

Each revision has an immutable content digest. Accepted orders bind the exact revision and agreed terms. Availability and quantity remain seller claims subject to concurrent commitments. A listing-level view references observed accepted orders and flags competing commitments with freshness information. A partition can hide another order, so the seller signs any inventory resolution.

Sellers republish their stores and listings within foreground budgets. Index operators republish their shards. Show cold-state loss as stale or unavailable data. Archive retention follows [1.4 Application bundles](../1-freenet-mobile-appkit/04-bundles.md), and domain repair follows [1.6 Application protocols, data and operations](../1-freenet-mobile-appkit/06-data-and-operations.md). The [hosting, placement and eviction issue #4642](https://github.com/freenet/freenet-core/issues/4642) and [bounded local pin issue #5041](https://github.com/freenet/freenet-core/issues/5041) are upstream design references. Validate the selected Core revision's actual retention behavior before relying on it.

## Pilot privacy and disputes

| Public or observable | Protected |
| --- | --- |
| Store profile, coarse area, listing terms and references | Precise pickup place and private logistics |
| Participant public keys, order links and public signed evidence | Participant private keys and recovery material |
| Request timing, ciphertext sizes and routing metadata | Encrypted request content and private evidence attachments |
| Payment amount, status and public content/contribution references | Processor objects, account details and legal identity in financial services |

Use pseudonymous application keys. Explain public links before collecting data. Encryption protects content while public metadata can still connect a buyer, seller and order. [Transport](#public-first-contact-and-bounded-transport) owns endpoint verification, and [evidence recovery](#encryption-receipts-and-recovery) owns protected persistence, retention and local deletion.

Before checkout, the seller supplies a signed claim statement bound to seller, authorized buyer, order ID, complete immutable terms digest, amount, currency, dispute target, schema and unique nonce. The buyer verifies and saves it in protected storage. A dispute filing verifies the statement, authorized claimant, target, nonce and payment evidence for the same order.

A filing records an allegation with authenticated evidence. Corrections and signed resolutions append alongside it. Publish which statement fields become public, who handles disputes, the evidence and response deadlines, and how refund requests reach the [refund authority in 3.4 Payments and checkout adapters](04-payment.md#refunds-and-fee-returns). Retain the [order bounds](#orders-canonical-terms-and-conflicts). The pilot uses a named manual review and appeals process with privacy, fraud, illegal-content and jurisdictional handling.

Every release applies baseline controls for listing spam and peer exposure. Apply seller-authorized listing writes, bounded listing/request profiles, blocked-sender filtering and a reporting path to manual review. Store reasons and policy versions with moderation decisions. Explain which participant keys, order links and claims become public before submission, and that public contracts remain reachable through other clients. Indexes control their results, and hosts control local display or catalogue removal. Broader discovery and fulfillment add coverage for new content, participants and jurisdictions.

## Checkout, lifecycle and upgrades

Use the [trusted checkout handoff in 3.4 Payments and checkout adapters](04-payment.md#trusted-checkout-handoff) for authenticated WebView requests, native trusted confirmation, browser return and signed-status reconciliation. A backgrounded or terminated phone resumes the original attempt and session reconciliation. Show service-confirmed payment separately from an order update awaiting Freenet delivery.

Subscribe to viewed listings, active orders and request generations. Restore subscriptions after reconnect. Keep app-scoped drafts, protected evidence and original pending-operation bytes. Show stale, pending, conflicted and unavailable states based on observed evidence. During foreground use, devices submit authorized state repairs within their cellular budgets. Serving full peers host the network copies.

Application updates retain the payment's fixed content, contribution snapshot and policies. Domain upgrades follow [migration and evidence retention](#migration-and-evidence-retention).

## Migration and evidence retention

Contract code changes create new instance identities. Preserve predecessor code hashes, original parameter encodings and actual instance references under [1.7 Upgrades and migration](../1-freenet-mobile-appkit/07-migration.md). Select recovery per contract. Snapshot records select the newest compatible generation. Signed event histories require merge, deletion-marker and conflict tests.

Validate recovered state, publish it and verify readback before changing indexes or pointers or recording success. Track local bundle installation, shared-contract migration and delegate-secret transfer separately. Check protocol compatibility before adopting domain artifacts. Tests include sellers offline across versions, mixed-version participants, full continuation pages and private-key migration.

## Later fulfillment and product scope

Enable each mode only after both roles approve it under [product release approval](#product-release-approval). Custom application code calls the approved operations directly. An optional SDUI adapter can map them under milestone 4 (SDUI).

| Operation | Domain meaning | Product scope |
| --- | --- | --- |
| `makeOffer`, `acceptOffer` | Propose and accept complete price/quantity terms | Pilot uses fixed-price agreement. Bargaining is later |
| `proposeFulfillment` | Propose pickup, delivery or shipping terms for an exact listing/order | Pickup in pilot. Delivery/shipping later |
| `respondFulfillment` | Accept, decline or counter the exact proposal digest | Accept/decline in pilot. General counterproposals later |
| `proposeReschedule` | Reference the current agreement and propose replacement scheduling terms | Later |
| `cancelRequest`, `cancelOrder` | Withdraw under the request/order rules | Pilot needs safe cancellation and refund handling |
| `recordDispatch` | Attach dispatch evidence and encrypted shipping reference | Later |
| `confirmFulfillment` | Sign handover or delivery confirmation | Pickup handover in pilot |
| `raiseDisputeReference` | Attach bounded evidence to the exact order and terms | Pilot with manual review |
| `closeOrder` | Close under the order's completion or resolution rules | Pilot |

Pickup proposes time windows and an encrypted meeting place. Delivery adds a service window, delivery fee and encrypted recipient details. Shipping adds a service choice, charge and encrypted destination. Seller response and participant completion are distinct signed events. Saving a listing stays local until the buyer submits a request.

A later seller policy may authorize its delegate to accept offers matching fixed listing terms while the seller is away. [Harvest's instant-checkout PR #159](https://github.com/freenet/harvest/pull/159) is the source reference. The [automatic-acceptance tests](#expansion-acceptance) gate activation.

Neighborhood indexes provide bounded results by region, category and freshness policy. Atlas is a possible provider under [5.4 Discovery and catalogue extensions](../5-optional-extensions/04-discovery.md). Every result points to signed listing state that the delegate verifies on opening. Users choose providers and their published moderation policies. Discovery adoption has its own release gate.

Optional classifiers flag content for review after measured phone cost and language coverage tests. Human appeals remain part of the policy. Optional proofs from [5.1 Peer reputation](../5-optional-extensions/01-reputation.md) use Marketplace's validated positive-event receipts and purpose-bound thresholds. Validated positive activity, authenticated allegations and financial results remain separate facts. [Seller-standing sources](#seller-standing-and-later-reputation) inform later policy decisions.

## Acceptance

This plan passes when one certified custom web release completes the [pilot sequence](#pilot-sequence) on iOS and Android through EVY's native checkout adapter, with traceable evidence for allocation, payout and refund reconciliation. Retain both release-role approvals, tested source/Core/SDK revisions, device results and the approved processor environment. Pin and inspect the relevant [Harvest source revisions](#harvest-design-references) when applying those designs. Protocol rules here are planned implementation requirements.

### Commercial and domain fixtures

- Source acceptance, exact-byte certification and independent-node publication observation through repository/CLI/CI.
- Fixed-price listing, public first contact, manual pickup agreement and both participants' signed completion evidence. Requests for unapproved modes fail before commitment or checkout.
- Forged callers, revoked permissions, terminated sessions, seller endpoint substitution, wrong buyers, counterparty substitution, incomplete signed terms, replayed claims and payment proofs for another order.
- Duplicate Checkout, webhook, domain and usage events, racing workers, processor uncertainty and return without signed payment evidence.
- App termination, backgrounded node, outages and update/publisher transfer between checkout and fulfillment.
- Altered terms, concurrent commitments, premature disputes, partial/full refunds, failed fulfillment, chargebacks and the [combined unclaimed-return/partial-refund/post-payout fixture in 3.5 Usage evidence, remuneration and payouts](05-remuneration.md#combined-return-and-refund-fixture).
- Listing spam, blocked senders, peer-exposure disclosures, reports, manual moderation decisions and appeals under the pilot policy.
- Protected evidence recovery, encrypted logistics and attachments, declared public links, reported deletion failures, exhausted storage and loss of every retained copy.
- Mixed-version participants and a seller returning after several versions, preserving signed history and secret access.

### Transport and cryptographic fixtures

- Property tests prove associativity, commutativity, idempotence, batch invariance and maximum encoded state size for admission, continuation, store and listing contracts. Order tests verify deterministic full-state/delta selection and every record/byte bound, including encoded succession evidence.
- Full-state and delta fixtures cover empty bootstrap, grants arriving out of order, copied grants, page/generation substitution, wrong writers, full continuation pages and same-slot conflicts.
- Digest grinding and flooding tests demonstrate bounded resource use and accurate delivery/saturation status.
- Independent known-answer vectors cover key agreement, direction-specific derivation, authenticated encryption and signatures. Reflected ciphertext and incomplete signature coverage fail.
- Crash fixtures cover persistence before acknowledgement, pending retries and uncertain submission. Reorder asynchronous replies and verify correlation at the consumer.

Run the [restore drill in 3.7 Operating readiness](07-operations.md#restore-drills) against the pilot's historical transaction. Retain the cryptographic profile, canonical codec fixtures and measured bounds. Unresolved transport capacity or recovery behavior blocks the product flow that depends on it. Broader fulfillment, discovery and optional SDUI have separate acceptance gates in their owning plans.

### Expansion acceptance

Each expansion repeats the pilot's transport, storage, baseline moderation and privacy tests, then adds its mode-specific cases. Record both role approvals with the enabled mode, policy versions and test evidence.

| Added mode | Required acceptance before activation |
| --- | --- |
| Bargaining and counterproposals | Each offer binds complete price, quantity and terms to its predecessor. Participants sign the selected revision. Stale acceptance and competing offers cannot authorize checkout for different terms |
| Rescheduling | Both participants approve replacement pickup/delivery terms. Pending work stays bound to its agreed revision. Tests resolve an existing payment before any changed economic terms start a replacement checkout |
| Delivery | Bind service area, service window, delivery fee and encrypted recipient details to the agreement. Test completion evidence, failed delivery, privacy and refund handling |
| Shipping | Bind supported destination, service and charge to the agreement. Verify signed dispatch and completion evidence with encrypted destination/tracking details. Test lost, delayed and disputed shipments and their refund outcomes |
| Automatic acceptance | Verify seller authorization, exact matching listing terms and policy version. Test revocation, concurrent requests, inventory conflicts and complete buyer/request binding while the seller is offline |

## Harvest design references

Marketplace uses its own application code and contracts. Harvest's repository, design documents, issues and pull requests inform the decisions below. An issue describes a proposal or reported finding, and a pull request records a change and its discussion. Implementation acceptance must pin and inspect the relevant revision. Current upstream status and Marketplace conformance require tested evidence.

### Sources and roadmap use

| Topic | Harvest source | Marketplace use |
| --- | --- | --- |
| Application structure | [Repository](https://github.com/freenet/harvest), with Rust domain/contracts/delegate code and a Dioxus web UI | [Application boundaries](#application-and-authority-boundaries) use custom web code, concrete domain protocols and an authorized native checkout bridge |
| Purchase flow | [Buy-flow PR #24](https://github.com/freenet/harvest/pull/24) | [Order rules](#orders-canonical-terms-and-conflicts) bind accepted terms to the buyer's own request. [Record identity](#record-identity) covers complete canonical terms |
| Private communication | [Messaging PR #23](https://github.com/freenet/harvest/pull/23) | [Bounded first contact and continuation](#public-first-contact-and-bounded-transport), with [encrypted participant-held evidence](#encryption-receipts-and-recovery) |
| Payment proof placement | [Bitcoin integration status document](https://github.com/freenet/harvest/blob/main/docs/bitcoin-integration-status.md) | [Signed payment status in 3.4 Payments and checkout adapters](04-payment.md#signed-payment-status) embeds proof in the order, with a fixed bridge root key in parameters and succession evidence in records |
| Seller accountability | [Standing proposal #8](https://github.com/freenet/harvest/issues/8) | [Signed pre-payment claims and dispute evidence](#pilot-privacy-and-disputes), plus later reputation policy |
| Automatic acceptance | [Instant-checkout PR #159](https://github.com/freenet/harvest/pull/159) | [Later seller-authorized acceptance](#later-fulfillment-and-product-scope) of requests matching fixed terms |
| Migration | [Migration design](https://github.com/freenet/harvest/blob/main/docs/design/migratability.md) | [Evidence retention](#migration-and-evidence-retention) across contract changes, with application-specific recovery tests |
| Design context | [Design index](https://github.com/freenet/harvest/blob/main/docs/design/README.md) | Review payment-proof, timestamp and privacy constraints during product scoping |

Harvest's payment design uses Bitcoin verification through a bridge. Marketplace's payment design in [3.4 Payments and checkout adapters](04-payment.md) uses processor Checkout and service-signed, order-bound status. The integration-status document discusses embedding payment proof and moving trusted-bridge information out of store parameters into signed order evidence. Marketplace's root-key and succession-chain protocol is a separate proposed design.

### Seller standing and later reputation

Harvest's standing proposal connects complaints to payment evidence. The pilot's [dispute policy](#pilot-privacy-and-disputes) owns bounded disputes and named manual review. [5.1 Peer reputation](../5-optional-extensions/01-reputation.md) owns optional private proofs of positive activity. Broader standing requires its own scope and acceptance decision.

| Source | Design relevance |
| --- | --- |
| [Bonded sellers and pre-signed claims #8](https://github.com/freenet/harvest/issues/8) | Proposed donation-backed standing, public order commitments, payment-backed complaints and refunds restoring standing. Includes exposure limits, buyer extortion, identity-level accounting and Bitcoin verification |
| [Incentive mechanism design](https://github.com/freenet/harvest/blob/main/docs/design/incentive-mechanism.md) | Identity replacement, exit scams, false complaints, penalty multipliers and privacy costs of publishing orders |
| [Gaming feedback #3](https://github.com/freenet/harvest/issues/3) | Category-only feedback as a response to misleading text in negative categories |
| [Feedback signature coverage #22](https://github.com/freenet/harvest/issues/22) | Coverage of text and categories, competing variants and suppressed complaints |
| [Purchase-flow security findings, PR #21](https://github.com/freenet/harvest/pull/21) | Payment verification, Ghostkey identity checks and feedback-token authorization |
| [Buyer-seller messaging, PR #23](https://github.com/freenet/harvest/pull/23) | Durable encrypted messages retaining the buyer's seller-signed claim |
