# 3.7 Operating readiness

## Repositories

| Repository | Role | Work in this plan |
| --- | --- | --- |
| [evy](https://github.com/EVY-Platform/evy) | Modified | Backups, inbox and outbox reconciliation, restore drill tooling, key rotation and runbooks across `services/attribution`, `services/payment` and `services/remuneration` |
| `evy-marketplace` | Used | Historical pilot transaction replayed in restore drills |

## Owned scope

Financial service backups, restore drills, durable queues, reconciliation, audit retention and signing-key operations are mandatory for milestone 3 (Attribution, remuneration and payment). Optional customer backup extensions belong to [5.2 Extended customer backup and recovery](../5-optional-extensions/02-recovery.md).

## Prerequisites

Use the service records and invariants defined by:

- [3.1 Product and contributor registration](01-registration.md)
- [3.2 Attribution workflow and allocation weights](02-attribution.md)
- [3.3 Artifact certification and publication evidence](03-certification.md)
- [3.4 Payments and checkout adapters](04-payment.md)
- [3.5 Usage evidence, remuneration and payouts](05-remuneration.md)

[1.6 Application protocols, data and operations](../1-freenet-mobile-appkit/06-data-and-operations.md) owns application operation IDs and producer journals. Operators must establish recovery before the [3.8 Paid application pilot and commercial acceptance](08-marketplace.md) handles live money. Service development can proceed against test environments while these gates are completed.

## Launch decisions

| Responsibility | Required owner and launch evidence |
| --- | --- |
| Service operations | Named primary and backup operators, access controls, incident contact and escalation path |
| Processor and region support | Verified seller and contributor onboarding, supported countries/currencies/methods, account capabilities and processor approval |
| Mobile distribution | Review of payment handoff and supported product categories against applicable platform and regional policy |
| Financial policy | Approved settlement values, processor-cost budget, reserves, payout schedule and refund/recovery responsibilities |
| Recovery | Numeric recovery point and recovery time targets for each service, backup cadence and a passing restore drill |
| Privacy and retention | Data inventory, access roles, retention periods, deletion handling and audit access |
| Service capacity | Queue, storage and contract bounds with measured alert thresholds and an overload response |

Record each decision's approver, date, environment and evidence. Set numerical targets before launch and measure drills against them. Supported-region and processor checks are release gates, with approval recorded for the actual operating model.

## Durable queues and reconciliation

Each service commits its authoritative state and outbound work in one local transaction. Use inbox/outbox delivery with stable event IDs, durable cursors and acknowledgements after commit. Delivery is at least once, so consumers enforce their own uniqueness constraints.

| Path | Recovery evidence |
| --- | --- |
| Repository to attribution | Verified source revision, original signed requests, ownership evidence and authoritative decision |
| Payment webhook inbox | Original raw payload, signature-verification result, processor account/event ID and processing state |
| Payment to order contract | Target order, original signed status bytes, payment ID and revision |
| Remuneration to payment | Authenticated fee-return instruction, original receipt, calculation basis, beneficiary and reserved amount |
| Payment to processor | Purchase/application-fee refund and destination-transfer references, stable request IDs and reconciled cash effects |
| Payment to remuneration | Immutable fee receipt/cash-adjustment IDs, kinds, revisions and acknowledgement |
| Usage contract or producer journal to remuneration | Original contract/epoch and event bytes, bridge cursor or authenticated recovery receipt, and committed decision |
| Remuneration to processor | Contributor payout references, reservations and reconciled outcomes |

After a timeout, reconcile the existing operation before creating a replacement. Bound retry rates and queue growth, quarantine invalid messages with reasons and retain the exact evidence for review. Alert on oldest pending work, repeated rejection, revision conflicts, unreconciled processor balances and low reserve coverage.

Run scheduled reconciliation across processor objects, fee receipts, signed payment revisions, usage decisions and payout reservations. Follow the [refund flow in 3.4 Payments and checkout adapters](04-payment.md#refunds-and-fee-returns) for purchase/application-fee cash execution and [3.5 Usage evidence, remuneration and payouts](05-remuneration.md) for calculations, allocation effects and contributor payouts. Operational recovery uses those same service authorities. Freenet delivery can resume separately from processor accounting. Status screens distinguish a service-confirmed result from pending network publication.

## Backups and exact evidence

Back up transactional databases with the uniqueness constraints and reservation state needed to replay safely. Keep encrypted, access-controlled copies in an independent failure domain. Verify backup integrity and restore compatibility after schema changes.

Retain:

- Product mappings, contributor key lineage, role decisions, proposal evidence and signed resolutions.
- Exact reviewed source archives, source-to-build mappings, build inputs, certified artifact bytes, snapshots and contribution records.
- Signed publication envelopes, publication observations, native distribution evidence and historical verification policies.
- Payment terms, original checkout bindings, signed status revisions, key succession chains and processor inbox/outbox records.
- Usage events, authenticated producer-recovery receipts and receipt times, completion evidence, allocation decisions, fee-return instructions, immutable cash adjustments, balances, reservations and payout lineage.
- Queue cursors, acknowledged boundaries, schema/codec versions and the configuration required to reproduce validation.

Apply each record's legal, support and transaction-evidence retention period. A hash verifies bytes that are available. Restore coverage includes the bytes and verification context needed for historical transactions, even after the live container advances or a repository/archive disappears.

Back up signing and encryption material under a separate controlled recovery procedure. Test who can decrypt the backups and how access is revoked. Protect processor credentials and legal identity records separately from public audit exports. A backup containing encrypted data needs the corresponding key recovery path.

## Restore drills

Run a drill before live money, after material storage/key changes and on the operator's published schedule.

1. Restore into an isolated environment with outbound payments and publication paused.
2. Verify backup integrity, schema versions, actor lineage, signing chains, constraints and ledger totals by currency.
3. Verify a historical paid operation from exact source/artifact bytes through certification, payment terms, completion evidence and allocation. Use a fixture whose live publication has advanced and whose primary archive is unavailable.
4. Reconcile restored processor references against current processor objects before enabling any financial side effect. Recover events committed after the backup from durable evidence and processor history.
5. Replay inboxes and outboxes from retained cursors. Duplicate events, competing workers and restored reservations must produce the same financial result.
6. Republish retained Freenet records with their original IDs, revisions and signed bytes. Verify order and usage synchronization separately.
7. Record achieved recovery point/time, evidence gaps, operator decisions and approvals to resume.

A missing receipt, uncertain payout or conflicting signed revision remains held for reconciliation. Restore completion requires a recorded decision for every unresolved financial item and a safe operating state.

## Signing keys and access

Separate publisher, attribution, payment bridge and remuneration statement keys. Scope production access by service and role. Record key IDs, algorithms, custody, rotation authority and recovery coverage.

Payment order parameters keep the fixed bridge root key. Normal rotation appends predecessor-signed succession records, and new status records carry the chain required by [3.4 Payments and checkout adapters](04-payment.md#signed-payment-status). Retain verification keys and historical signatures for the evidence period. Test rotations against order and usage record size bounds before deployment.

A compromise or loss of the active signer needs a separate incident decision. Pause affected signing and new operations, preserve evidence, identify which attestations require review and use only the recovery authority the protocol can verify. A normal successor signature alone supplies no independent proof that a compromised predecessor was trustworthy. Publish the supported compromise response before launch, including any new-contract or customer action it requires.

Rotate processor credentials and webhook secrets with a tested overlap and verification procedure. Audit administrative access, payout-destination changes, recovery decisions and policy approvals. Use protected secrets storage and redacted diagnostics.

## Audit and failure runbooks

Keep append-only audit events for policy changes, role changes, certifications, funding adjustments, reconciliation and manual resolutions. Each event identifies its actor, reason, related immutable IDs and signed evidence. Preserve service statements and export enough evidence to reproduce a decision without exposing customer payloads or processor secrets.

| Incident | Required response |
| --- | --- |
| Processor timeout or outage | Preserve attempt/reservation, show uncertainty and reconcile before retrying |
| Freenet outage or cold-state loss | Queue status delivery, retain service accounting and republish verified evidence within budgets |
| Duplicate or reordered input | Replay through the canonical idempotent processing path |
| Capacity or admission saturation | Preserve producer journals and use remuneration's bounded authenticated recovery path within the original epoch and claim cutoff |
| Signed revision conflict | Hold affected automated actions, retain witnesses and require authorized resolution |
| Refund or chargeback after payout | Reconcile payment's cash adjustments, then apply remuneration's allocation and reserve/recovery rules once per adjustment |
| Database or queue loss | Restore in isolation, reconcile external effects and resume after approval |
| Signing-key incident | Pause affected operations and execute the supported rotation/compromise procedure |
| Identity or payout recovery | Verify lineage and financial authority before changing destinations or releasing held funds |

## Acceptance

This plan passes when:

- Operators approve the region, processor, distribution and financial policy checklist for the actual pilot.
- Every financial store, queue and required evidence archive has a tested backup and named owner.
- Restore drills meet the approved recovery targets and reproduce historical certification and allocation from exact bytes.
- Replay after restoration, outage or worker races preserves one checkout attempt, allocation and payout result.
- Key rotation preserves historical verification within wire limits, and the compromise runbook has an exercised response.
- The [combined return and refund fixture in 3.5 Usage evidence, remuneration and payouts](05-remuneration.md#combined-return-and-refund-fixture) survives queue replay and restore, preserving seller returns, buyer refunds and contributor recovery separately.
- A claim never retained in its usage contract reaches remuneration through the authenticated recovery path. Restore preserves its timely receipt and deduplicates later contract delivery.
- Audit exports preserve lineage while excluding protected customer data and secrets.

Acceptance records include drill and processor evidence. Financial recovery readiness is part of the commercial release, while broader consumer recovery and device synchronization follow their own milestone 5 (Optional extensions) plans.
