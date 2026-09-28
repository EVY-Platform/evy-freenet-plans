# 3.5 Usage evidence, remuneration and payouts

## Repositories

| Repository | Role | Work in this plan |
| --- | --- | --- |
| [evy](https://github.com/EVY-Platform/evy) | Modified | `services/remuneration`: usage contract, bridge and cursors, admission checks, ledger, settlement policy, financial onboarding, payouts, the authenticated recovery endpoint and a fixture completion-evidence producer |
| [freenet-core](https://github.com/freenet/freenet-core) | Modified | `crates/mobile` operation journal gains producer-journal recovery |
| `freenet-appkit` | Modified | Host service adapter for signed usage claims |

## Owned scope

Remuneration's transactional service is the canonical authority for usage decisions, allocation and fee-return calculations, balances, payout reservations and contributor payout execution. [3.2 Attribution workflow and allocation weights](02-attribution.md#contribution-weights) identifies recipients and weights. [3.4 Payments and checkout adapters](04-payment.md#refunds-and-fee-returns) executes purchase/application-fee refunds and supplies immutable reconciled cash adjustments.

## Prerequisites

Use:

- Contributor key lineage from [3.1 Product and contributor registration](01-registration.md#roles-and-registration-evidence).
- Attribution snapshots from [3.3 Artifact certification and publication evidence](03-certification.md#certification-records).
- Fixed payment evidence from [3.4 Payments and checkout adapters](04-payment.md#fixed-checkout-evidence).
- Operation IDs and journals from [1.6 Application protocols, data and operations](../1-freenet-mobile-appkit/06-data-and-operations.md).
- Protected identities from [1.5 Identity, keys and local protection](../1-freenet-mobile-appkit/05-identity.md).

Capability evidence describes domain outcomes independently of UI technology. The service applies the same attester, certified-content, funding and policy checks to custom web and native clients. Optional SDUI evidence integration belongs to [4.7 SDUI commerce and attribution](../4-sdui/07-commerce.md).

Attribution units measure accepted work. Usage credits record verified paid usage and its allocation within one payment. Payable balances express funded allocations in a named currency. Usage outside a paid operation remains analytics.

## Usage flow

1. Application code obtains domain evidence for the completion condition fixed at checkout. Its authorized delegate or protected signer signs the usage claim.
2. The application journals the original claim bytes and submits them to the designated Freenet usage contract.
3. The contract validates admission. A bridge subscribes, delivers retained events to remuneration and saves its delivery cursor. Claims awaiting service acknowledgement can also use producer-journal recovery below.
4. Remuneration verifies payment funding, completion and original attribution bindings, then commits one allocation decision.
5. The bridge acknowledges processing after commit and periodically scans for missed events.

Funding evidence proves a real payment. Domain evidence proves qualifying capability use. A claim stays pending until both pass. An order's validated fulfillment transition is one such domain outcome. Tests use a fixture completion-evidence producer that signs such an outcome. Rendering a screen supplies no completion evidence.

## Usage record and admission

```text
schema_version
usage_event_id
product_id
application_content_ref
contribution_record_id
capability_id
operation_id
payment_id
event_kind
evidence_reference_or_digest
producer_key
signature
embedded_payment_record
```

Derive `usage_event_id` from the product, capability, product-scoped operation ID and event kind using a canonical, domain-separated encoding. Preserve it and the exact signed bytes through retries. Use the payment's original content reference and contribution record, with the reference types owned by [1.4 Application bundles](../1-freenet-mobile-appkit/04-bundles.md). Keep private customer content and legal identity in authorized stores.

The contract requires a bridge-signed payment record bound to the same payment, product, operation/order and epoch. Verify it against the bridge root key in the usage contract parameters. Also check schema, producer signature, scope and size. A device signature alone is insufficient admission evidence. The service then verifies the producer against the authorized attesters in the payment's fixed policy and checks the claimed capability against its certified contribution record.

| Rule | Value |
| --- | --- |
| Record size | 4 KiB including the embedded payment record and signature |
| Records per epoch instance | 4,096 |
| Selection | Keep the lowest full content digests |
| Variants per event ID | Retain two by lowest digest as explicit conflict evidence |
| Instance parameters | Product, epoch number and bridge root key |

A usage epoch is a separate contract instance. Remuneration assigns the epoch for checkout, and payment records its ID in the [fixed checkout evidence in 3.4 Payments and checkout adapters](04-payment.md#fixed-checkout-evidence) and the signed record. On saturation, open a successor for new payments and record the boundary. Delayed claims remain bound to their payment's epoch.

Merge as an idempotent set with deterministic selection over the combined set. Lowest-digest selection can permanently exclude a valid claim. Preserve original claims in producer journals until the service acknowledges them, then retain evidence for the policy's recovery period. Report eviction, saturation and pending delivery accurately. Repeated bridge notifications or invented event IDs for the same payment and capability resolve to one allocation.

### Producer-journal recovery

Expose an authenticated recovery endpoint through the authorized host service adapter. A producer can submit directly when a claim lacks a service acknowledgement, including when the contract has never retained it. Authenticate the producer against the attester policy bound at checkout.

- Accept one original signed claim of at most 4 KiB per request, including its embedded payment record. Carry its original contract/epoch reference and retain the same event, operation and payment IDs.
- Apply versioned per-producer and per-product request/byte quotas, concurrency limits and bounded supporting-evidence fetches. Return explicit retry or rejection status within the published cutoff.
- Run the same schema, signature, payment-root, product, operation, epoch, size, attester, certification, funding and domain-completion checks used by the contract/bridge path. Contract set membership is delivery evidence, while these checks establish claim validity.
- Commit the original bytes and a durable receipt before acknowledging service admission. Both routes use the same inbox and allocation uniqueness constraints. Conflicting bytes under one event ID enter the same conflict process.
- Apply the payment's original epoch and claim cutoff. The service records the first durable receipt time for either route. On-time receipts can finish processing or be replayed after the cutoff. A new receipt after the cutoff gets the policy's late-claim outcome. Producer timestamps alone cannot establish timely receipt.

Archive directly received evidence with its origin and signed service receipt. A later contract notification resolves to the existing claim and decision. Retain separate pending states for service processing and optional network republication.

## Verification and credit accounting

1. Read the original event from the bridge or authenticated recovery inbox and apply the common admission and completion-evidence checks.
2. Ask attribution to verify the original content-to-contribution mapping, publication or native distribution evidence and included capability.
3. Require the response to name the contribution record, snapshot and policy version fixed at checkout. Record a rejection reason for any mismatch.
4. Verify the collected contributor fee against payment's reconciled receipts and adjustments.
5. Commit the payment/event IDs, evidence decision, snapshot, policy and credit entries in one database transaction. Enforce the payment's funding cap across all allocations.
6. Acknowledge after commit and retry with the same event ID after uncertainty.

Enforce uniqueness on event IDs, processor fee receipts and payment-capability-recipient allocations. Racing workers produce one result. Retain pending, credited, rejected and conflicted states with reasons. After commercial suspension, process existing payments under their original settlement policy and claim cutoff.

Each payment funds its own qualifying usage. Fabricated activity can recover at most that payment's contributor fee through remuneration. Payment's operating budget separately covers processor costs, fraud losses and subsidies.

## Funding and settlement policy

This plan defines the signed settlement policy, the product's signed capability-allocation policy and the usage epoch. Checkout records their IDs as `settlement_policy_id`, `allocation_policy_id` and `usage_epoch_id` in the [fixed checkout evidence in 3.4 Payments and checkout adapters](04-payment.md#fixed-checkout-evidence).

Track each currency in integer minor units. Reserve each payment's available contributor fee once. Split it among qualifying capabilities using the weights fixed at checkout, then among their contributors, reviewers and validators using the bound snapshot. Total allocations remain within the collected fee after reversals. [3.4 Payments and checkout adapters](04-payment.md#contributor-fee) owns the fee rate, payer and collection rules.

Use deterministic remainder allocation with stable recipient ordering. Record receipts, credit entries, policy, arithmetic and remaining balance per payment. Keep pending capability shares reserved against their originating payment. Shares with on-time unresolved claims stay reserved until the evidence decision. After the bound claim cutoff and those decisions, remuneration calculates the unclaimed return and reserves it for execution by payment. Empty or missing recipient weights keep shares pending until resolved or included in that return. The beneficiary follows the [fee-payer rule in 3.4 Payments and checkout adapters](04-payment.md#refunds-and-fee-returns).

Require a signed, versioned settlement policy with:

| Fields | Purpose |
| --- | --- |
| Capability weights, attribution snapshot and role shares | Resolve each recipient's allocation |
| Authorized attesters and completion-evidence rules | Establish which domain outcomes qualify |
| Payout schedule and currency-specific minimums | Establish when funds can be paid |
| Claim cutoff and unclaimed-fee return rules | Establish timely service receipt and the remaining shares to return to the original fee payer |
| Payout delay, reversal reserve and recovery rules | Cover settlement uncertainty and subsequent reversals |

The product's signed capability-allocation policy supplies capability eligibility and evidence requirements. The settlement policy binds that policy and the required financial terms consistently. The operator approves every required value before launch. Checkout requires complete signed policies, and each payment keeps them through delayed fulfillment and later policy changes.

### Return calculations and allocation effects

Calculate the cumulative refunded proportion of the original contributor fee with round-half-up, capped at the original fee. Split that target over the original funded and pending shares under the settlement policy's deterministic rounding rule. Cumulative reversals must only increase, stay within each original share and sum to the target. Record the cumulative amount reversed in each share and apply only the increase.

A share already returned as unclaimed covers its corresponding portion of a later refund target. Request only the additional fee cash return. If a purchase refund arrives first, the later unclaimed return covers the share's remaining amount. Track this overlap per original share so return order preserves the same result and total fee returns stay within the collected fee.

Serialize calculations per fee receipt, including pending return reservations.

1. Calculate the application-fee return from payment's reconciled facts, including unclaimed shares after the cutoff, and reserve it.
2. Send an authenticated fee-return instruction to payment under the [refund flow in 3.4 Payments and checkout adapters](04-payment.md#refunds-and-fee-returns). Each instruction carries a stable return ID, the original payment/fee receipt, amount, beneficiary, policy and source adjustment revision. Reconcile an in-flight instruction before replacing it.
3. Record calculated allocation effects as pending until their required cash adjustments reconcile. Payment alone publishes those cash adjustments.
4. Consume each adjustment once by its immutable ID, release or resolve the matching reservation, link the resulting allocation entries and preserve the original credits.

Contributor payout execution and post-payout recovery accounting follow the bound policy.

### Combined return and refund fixture

Use a 10,000-minor-unit purchase with a 100-unit contributor fee. The fixed policy assigns 60 units to a completed capability and 40 to an unclaimed capability. Run after the payout delay with approved reserve coverage for the 30-unit post-payout reversal.

1. Remuneration pays the 60 funded units to contributors. At the cutoff it reserves and requests the 40-unit unclaimed return. Payment returns those 40 units to the original seller and publishes the cash adjustment.
2. Payment then refunds 5,000 purchase units to the buyer and reconciles the associated destination-transfer recovery.
3. Remuneration calculates a 50-unit cumulative fee-refund target. Of that, 20 belongs to the unclaimed share already returned. It requests the remaining 30-unit fee return through payment and records the pending 30-unit contributor allocation reversal.
4. Payment returns 30 more fee units to the seller and publishes its adjustment. Remuneration consumes it once and applies the policy's post-payout reserve/recovery rules. Preserve the original 60-unit payout and link the 30-unit recovery obligation.

Assert 70 total fee units returned to the seller, 5,000 purchase units refunded to the buyer and 30 net contributor units. Replay duplicate/reordered inputs and timeouts during each handoff. Also run the refund before the unclaimed return. Both orders preserve these totals, one cash effect per operation and the original receipt lineage.

## Payout reservations and reversals

The service atomically reserves fee receipts and payable balances before creating a payout request. Uniqueness constraints prevent a second settlement from reusing those funds. Payout batches may combine balances while retaining each payment's allocation lineage.

Release payable funds only after processor settlement and the policy's payout delay, retaining the required reversal reserve. Use stable payout IDs and processor idempotency keys. After a timeout, reconcile the existing processor operation before retrying. Persist pending, processing, paid, failed and reversed outcomes. Release a reservation only after the processor confirms failure or cancellation.

Before a first payout, the contributor completes financial onboarding through protected service interfaces. Accepted units and funded balances remain separate while onboarding is pending. Keep legal identity, payout endpoints, tax records and processor credentials in protected service storage. A contributor views credits, payable funds and payout history through authorized service interfaces. Record currency conversion separately when selected.

Recovery or payout-destination changes require verified authority under [1.5 Identity, keys and local protection](../1-freenet-mobile-appkit/05-identity.md) and the lineage checks in [3.1 Product and contributor registration](01-registration.md#roles-and-registration-evidence). Freeze payout-identity changes while key recovery is unresolved. Payout-account and balance recovery require the financial service's authorization. A 1.5 Identity, keys and local protection export package never restores them.

Payment publishes the reconciled cash adjustment for a refund or chargeback, including after contributor payout. Remuneration consumes it once and records the allocation effects under the calculation rules above. Apply the signed reserve and recovery policy to unsettled funds or future allocations. Record recovery obligations and recoveries separately from the original payout. Preserve receipt and settlement linkage through every adjustment.

## Recovery and authority

The service signs auditable statements of credits and settlements. Its ledger owns contributor allocations, balances and payouts. Payment owns purchase and application-fee cash adjustments. Freenet records and authenticated recovery receipts supply the usage evidence trail.

During an outage, applications preserve signed claims and show queued processing. Recovery resumes from durable cursors and deduplicates events. Credit and payout displays include their last confirmed service update.

## Acceptance and evidence

This plan passes when:

- Custom web, custom native and two-device fixtures produce equivalent domain evidence for one operation.
- Admission rejects missing or invalid payment records, wrong epochs, substituted operations and invalid producer signatures. Merge tests prove convergence and encoded size bounds.
- Racing workers, new event IDs and repeated notifications produce one funded allocation per payment/capability/recipient.
- Unrelated capabilities, unauthorized attesters and incomplete domain outcomes fail eligibility.
- Checkout requires complete signed policies. A checkout whose policy IDs lack a complete signed settlement or capability-allocation policy fails.
- Application updates, publisher transfers, key recovery and policy changes preserve the checkout's original evidence and weights.
- Allocations, reserves, deterministic remainders and unclaimed returns reconcile per payment and currency, including missing weights and on-time claims still awaiting a decision. Cumulative refund-share rounding stays monotone, capped and conserved.
- Timeout retries create one payout. Duplicate, partial and post-payout reversals retain receipt lineage and respect the recovery policy.
- A valid claim that is never retained by a saturated contract reaches the service through authenticated journal recovery and receives one allocation. A later bridge delivery returns that decision. Wrong epochs, altered evidence, unauthorized producers and late first receipts receive the same rejection or cutoff treatment on both paths.
- Recovery endpoint tests enforce request, byte, concurrency and evidence-fetch bounds. Service outages, full epochs, evicted events and late evidence have explicit outcomes under the published retention and cutoff rules.
- The combined return and refund fixture reconciles unclaimed shares, partial refunds and post-payout recovery through duplicates and reordered inputs.

These are proposed protocol and service requirements. Acceptance records must include actual contract, database, processor and outage test results.
