# 3.4 Payments and checkout adapters

## Repositories

| Repository | Role | Work in this plan |
| --- | --- | --- |
| [evy](https://github.com/EVY-Platform/evy) | Modified | `services/payment`: Stripe Connect Checkout, webhook inbox, refunds, signed status record with its verifier crate, Freenet bridge peer and outbox |
| `freenet-appkit` | Modified | Host checkout adapter: authenticated request binding, native trusted confirmation, browser handoff and return reconciliation |
| `evy-marketplace` | Used | Order contract links the status verifier and the pilot exercises the whole flow |

## Owned scope

Payment is the canonical authority for Checkout, purchase and application-fee refunds, reconciled cash adjustments and signed payment status. [3.3 Artifact certification and publication evidence](03-certification.md) owns certified-content eligibility. [3.5 Usage evidence, remuneration and payouts](05-remuneration.md) owns allocation calculations and contributor payout execution.

## Prerequisites

Use:

- Certification and publication evidence from [3.3 Artifact certification and publication evidence](03-certification.md).
- The settlement interface from [3.5 Usage evidence, remuneration and payouts](05-remuneration.md#funding-and-settlement-policy).
- The trusted host from [1.3 Single-application host](../1-freenet-mobile-appkit/03-host.md).
- Protected keys from [1.5 Identity, keys and local protection](../1-freenet-mobile-appkit/05-identity.md).
- Operation IDs and journals from [1.6 Application protocols, data and operations](../1-freenet-mobile-appkit/06-data-and-operations.md).
- Authenticated multi-app sessions from [2.2 Multi-application sessions and authority](../2-evy-mobile-app/02-sessions.md).

Production use requires [3.7 Operating readiness](07-operations.md#acceptance), including processor and regional approval checks.

Custom web and native application code requests Checkout through an authorized service adapter. The first paid pilot uses Marketplace's custom web UI inside EVY's curated WebView host and a native checkout bridge. Optional SDUI invocation belongs to [4.7 SDUI commerce and attribution](../4-sdui/07-commerce.md).

## Trusted checkout handoff

1. Application code submits the product, order, product-scoped economic operation ID, agreed terms digest, authorized payer, seller beneficiary, currency and stable checkout request ID.
2. The host authenticates the caller from the installed application and active session. It checks the user's grant and binds the request to that app, user, session and exact content reference. Application-supplied identity fields remain claims until verified.
3. Native trusted UI shows the verified seller, amount, currency and fee terms for confirmation. The WebView can request this prompt through its scoped bridge. The host owns the confirmation and approved external-browser handoff.
4. The payment service independently verifies the signed terms, payer authority, seller account, target contract and commercial eligibility. It reserves one payment attempt and fixes the amount, fee and evidence bindings before creating Checkout.
5. The adapter opens only the service-returned, validated Stripe HTTPS Checkout URL in the system browser or approved browser session. A browser-only integration uses an authorized host path and popup or redirect compatible with Core's sandbox policy.
6. The return handler validates its correlation state and routes to the original application and order. It obtains signed status from the payment service, verifies it, and reconciles the order update.

The adapter persists the request ID, operation ID, payment/attempt IDs, order, terms digest and return correlation before leaving the app. It handles the embedded node being suspended or the app being terminated. On return, restore the authenticated session and resume the node under the host's lifecycle policy. Fetch signed service status even when Freenet synchronization is pending. A redirect or a success-looking URL supplies navigation evidence only.

The payment service's Freenet peer publishes signed order updates while the phone is backgrounded. The client can also submit the same signed status after reconnecting. Both paths merge as one payment revision. [1.3 Single-application host](../1-freenet-mobile-appkit/03-host.md), [2.2 Multi-application sessions and authority](../2-evy-mobile-app/02-sessions.md) and [2.5 Shared node, data and lifecycle](../2-evy-mobile-app/05-lifecycle.md) remain the security boundary. Payment credentials stay in the service's secrets store.

## Fixed checkout evidence

Record these bindings against the operation and agreed terms:

- The exact `application_content_ref` defined by [1.4 Application bundles](../1-freenet-mobile-appkit/04-bundles.md), naming a publication or certified native build.
- The signed contribution record, immutable attribution snapshot and retained source/publication or distribution evidence from [3.3 Artifact certification and publication evidence](03-certification.md#certification-records).
- The product's signed capability-allocation policy and the signed settlement policy owned by remuneration.
- The usage epoch assigned under remuneration's admission profile.

Verify product authority, content eligibility, included capabilities and required completion evidence before accepting a digest or contribution record. Persist the verified signed evidence alongside its IDs. These bindings remain fixed through application updates, different clients, publisher transfer and delayed fulfillment.

Commercial suspension governs new Checkout requests under the product policy. Record the authority and latest verified observation used for that decision. Existing attempts, refunds and settlement keep their recorded bindings.

Bind each attempt to one order and immutable terms digest. Keep the purchase's economic operation ID through payment attempts, fulfillment claims and refunds. Reserve requests durably and use stable Stripe idempotency keys. Serialize attempts for the same order so concurrent clients reuse its active attempt. Reconcile an uncertain attempt against both service and processor records before authorizing a replacement.

## Contributor fee

The contributor fee is 100 basis points of the agreed checkout amount, taken from the seller's proceeds. Show it in the signed terms before checkout. Compute it in currency minor units with round-half-up. Store the fee base, computed fee and policy version. A 70-dollar sale contributes 0.70 dollars.

Use Stripe Connect Checkout with a connected seller destination and `payment_intent_data.application_fee_amount`. Reconcile successful application-fee collection into a fee receipt. Stripe holds the money in its account balances. The destination-charge model charges processor costs to the payment service balance. Budget those costs separately so the contributor fund receives its promised amount.

[Stripe's destination-charge guide](https://docs.stripe.com/connect/destination-charges) describes the processor mechanism. Account, country, payment-method and distribution-policy checks are launch gates. The selected integration remains subject to processor and platform approval.

Send fee receipts and reconciled cash adjustments to remuneration through a durable outbox under the refund flow below. Each service commits and recovers its own transaction. Remuneration owns allocation arithmetic, reserves and contributor payout execution.

## Payment states

Preserve processor state and expose a versioned mapping based on the [PaymentIntent lifecycle](https://docs.stripe.com/payments/paymentintents/lifecycle).

| Payment status | Meaning |
| --- | --- |
| Pending | Checkout is open or the PaymentIntent requires a method or confirmation |
| Action required | Customer action such as `requires_action` authentication |
| Authorized | `requires_capture` when manual capture is enabled |
| Processing | Processor result remains pending |
| Accepted | `succeeded` for the bound terms |
| Failed | Failed attempt, retained for retry history |
| Canceled or expired | Canceled PaymentIntent or expired unpaid Checkout Session |

Payments can skip states. Track captured and refunded amounts, partial/full refunds, disputes and chargeback outcomes separately. Accepted payment and subsequent reversals remain in history. Manual-capture authorization permits only the order actions allowed by the agreed policy.

## Webhooks and reconciliation

Receive the Checkout, PaymentIntent, charge, refund, dispute and application-fee events used by supported payment methods. Follow [Stripe's webhook guidance](https://docs.stripe.com/webhooks).

1. Verify the raw-body signature and endpoint secret, durably store the event, then acknowledge it.
2. Deduplicate by Stripe account and event ID. Serialize processing per payment.
3. Retrieve relevant current processor objects to reconcile duplicate, delayed or reordered notifications.
4. Commit reconciled state, financial entries and outbound bridge messages in one transaction. Assign an increasing per-payment revision there.
5. Periodically reconcile open payments and missing events through the same update path.

## Refunds and fee returns

1. Payment authorizes and executes purchase refunds under the agreed order policy. It reconciles buyer refunds, chargebacks and destination-transfer recovery with the processor.
2. Remuneration consumes those reconciled facts and calculates allocation effects and any application-fee return, including unclaimed shares after the cutoff. It reserves the return and submits an authenticated instruction with a stable return ID, original payment/fee receipt, amount, beneficiary, policy and source adjustment revision.
3. Payment verifies that instruction against the original fee receipt, beneficiary and remaining returnable fee. It serializes execution per receipt and uses the processor's purchase/application-fee refund APIs with stable idempotency keys. Reconcile an uncertain operation before retrying or accepting a replacement calculation.
4. Payment publishes immutable reconciled cash adjustments through its durable outbox. Each names the adjustment ID, kind, original receipt, related return/refund ID, currency, amount, beneficiary and revision. Distinguish buyer purchase refunds, seller application-fee returns and destination-transfer recovery. Corrections append linked adjustments.
5. Remuneration consumes each adjustment once, records its allocation effects and releases or resolves the matching reservation. It owns contributor payout execution and post-payout recovery accounting under its bound policy.

The v1 unclaimed-fee beneficiary is the original seller whose proceeds bore the fee. Purchase refunds go to the buyer. Payment validates the seller's original account binding before returning an application fee. Use the explicit fee-return amount calculated by remuneration so earlier unclaimed returns and later purchase refunds reconcile against the same receipt. Total application-fee cash returns stay within the amount collected.

[3.5 Usage evidence, remuneration and payouts](05-remuneration.md#return-calculations-and-allocation-effects) owns the return arithmetic, overlap accounting and the [combined unclaimed-return/partial-refund/post-payout fixture in 3.5 Usage evidence, remuneration and payouts](05-remuneration.md#combined-return-and-refund-fixture). 3.7 Operating readiness replays this flow through the owning services.

## Signed payment status

The payment service signs a versioned record containing:

```text
schema_version
product_id, order_id, operation_id
payment_id, attempt_id, terms_digest
currency, amount_minor, contributor_fee_minor
payment_status, processor_status
captured_minor, refunded_minor, dispute_status
application_content_ref, contribution_record_id, attribution_snapshot_id
allocation_policy_id, settlement_policy_id, usage_epoch
revision, previous_record_digest
bridge_key_id, key_succession_chain, signature
```

Retain raw processor payloads, customer details and processor object IDs in private service records. Public Freenet records use opaque payment IDs. The public record still reveals its order, amount and content links under the [pilot privacy policy in 3.8 Paid application pilot and commercial acceptance](08-marketplace.md#pilot-privacy-and-disputes).

Embed the signed record in the order update. The order contract verifies its schema, signature, amount, currency and terms digest deterministically from that evidence. It uses the fixed bridge root key in its parameters. Every verification input needed by the contract travels in the update or its existing state.

| Location | Evidence |
| --- | --- |
| Order parameters | Fixed bridge root key, alongside the order's own parameters |
| Signed status record | Append-only key succession from the root to the signer, each successor authorized by its predecessor |
| Order state | Bounded records by payment ID and revision |

Parameters hash into contract identity, so rotating keys appear in the signed succession chain. Earlier records remain verifiable under their original signer. [3.7 Operating readiness](07-operations.md#signing-keys-and-access) owns rotation and compromise runbooks.

Merge identical revisions once. Retain different signed payloads at one revision as a conflict, keeping the two lowest digests. The [order profile in 3.8 Paid application pilot and commercial acceptance](08-marketplace.md#orders-canonical-terms-and-conflicts) retains at most 32 revision slots per payment. Use the highest unconflicted verified revision for display. Automated order actions require predecessor recovery across gaps and an authorized signed resolution naming conflicting digests and the replacement chain. Pause those actions for the affected payment while preserving the evidence.

An optional audit contract can mirror the records. The order validates against its embedded evidence. Marketplace applies its own fulfillment transitions after matching payment amount, currency and terms. Inventory and completion evidence remain separate domain facts.

## Bridge delivery and recovery

The payment service runs a Freenet peer and a durable outbound queue. Retry an order update with the same payment ID, revision and signed bytes. Retain target order bindings and all signed revisions for reconciliation and republication.

During a Freenet outage, processor collection and webhook accounting continue. The queue retains pending order updates. The app distinguishes service-confirmed payment from order synchronization. A client can fetch and verify the signed record, then submit the same order update when its node resumes.

[3.7 Operating readiness](07-operations.md#durable-queues-and-reconciliation) requires recoverable service state, signing evidence, queue cursors and tested processor reconciliation. A future transfer of payment authority into Freenet also needs authenticated processor-event and custody primitives, alongside the [migration gates in 3.5 Usage evidence, remuneration and payouts](05-remuneration.md#recovery-and-authority).

## Acceptance and evidence

This plan passes when:

- Custom web code completes Checkout through the authenticated native adapter on iOS and Android. A custom native fixture uses the same service interface.
- Forged callers, revoked grants, stale sessions, wrong orders and substituted return links fail. Trusted native UI confirms the exact terms.
- Concurrent clients receive one active attempt with the same fixed amount and evidence bindings.
- Backgrounding, termination and node suspension preserve request IDs. Return reconciliation uses signed status and resumes order delivery.
- Duplicate and reordered webhooks, refund retries and racing workers produce one reconciled financial result.
- Changed application content, publisher authority or allocation policy during checkout preserves the original attempt's bindings.
- Wrong-order payment proofs fail. Bridge-key rotation verifies through the root, and revision conflicts pause automated transitions.
- Refunds and disputes update both the order record and contributor funding, including after payout. The [combined return fixture in 3.5 Usage evidence, remuneration and payouts](05-remuneration.md#combined-return-and-refund-fixture) separates seller fee returns from buyer refunds and produces one cash adjustment per processor effect.

Retain processor test evidence, tested host/Core revisions and real-device results. Stripe documentation describes API behavior, while the service, adapter and signed-status protocol here are planned work. The [Harvest source map in 3.8 Paid application pilot and commercial acceptance](08-marketplace.md#harvest-design-references) records the separate source for embedded payment-proof design.
