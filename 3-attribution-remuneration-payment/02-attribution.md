# 3.2 Attribution workflow and allocation weights

## Owned scope

The attribution service owns proposal, review, estimate, challenge, resolution and acceptance operations. It resolves exact contribution weights. Repository checks and the [Developer workspace](06-developer.md) display its authoritative status. [3.3](03-certification.md) commits immutable snapshots and certifies exact artifacts.

Milestone 3 uses repository evidence and custom web or native application code with concrete domain protocols. Application publishing can use attribution independently. The contributor-funded [Marketplace pilot](08-marketplace.md) requires it.

## Prerequisites

Complete [3.1 registration](01-registration.md), including product authority, verified actor lineage and product-scoped role eligibility.

## Work records

| Identifier | Owned meaning |
| --- | --- |
| `ProposalId` | Submitted work and its evidence revisions |
| `AcceptanceId` | Accepted exact source/evidence revision, size, contribution shares and policy version |

## Review and acceptance workflow

| Stage | Required evidence or decision |
| --- | --- |
| Submit | Problem, outcome, capabilities, proposed size, contributor split and exact repository evidence |
| Size and shares | Size in `1, 2, 3, 5, 8, 13, 21`. Capability shares total 10,000 basis points, as do contributor shares within each capability |
| Review | Eligible reviewer's signature against the evidence revision. Rejection closes the proposal. Further work starts a linked successor |
| Validate size | Eligible validator's signed estimate. Agreement accepts the size. A second validator selects between the two estimates on disagreement |
| Accept | Complete evidence, review, size, allocation and resolved challenges, bound to the evidence revision and policy version |

Changed source content creates a new evidence revision and requires review. An attributed change reaches acceptance before merge. The repository integration gates that merge on addressed review feedback, signed sizing and resolved challenges. Artifact provenance identifies unattributed work separately from accepted contributions.

## Challenges

A contributor can challenge omitted authorship, proportions, size, evidence or delivery before certification. A challenge blocks acceptance and certification until the challenger and every affected contributor named when it opened sign a resolution. An omitted-author claimant participates in that resolution.

A size resolution selects between the disputed estimates. Show overdue challenges and responsible contributors. Withdrawal closes the proposal while preserving its evidence. After certification, accepted units remain in audit history. [Payment](04-payment.md#refunds-and-fee-returns) owns cash adjustments and [remuneration](05-remuneration.md#return-calculations-and-allocation-effects) owns their allocation effects.

## Contribution weights

Store exact scaled or rational weights. [Remuneration](05-remuneration.md#funding-and-settlement-policy) owns currency rounding.

Only contributor, reviewer and validator work earns attribution units. An accepted proposal assigns 85% of its size to contributors, 10% to reviewer weights and 5% to validator weights. The accepted reviewer earns the review weight. Split validator weight equally among validators whose signed estimates determined the accepted size. Product-wide pools sum these earned weights by actor lineage and role. [Snapshots](03-certification.md#certification-records) resolve explicit recipients and weights.

For a size-8 proposal with Carol doing five eighths of the work and Dave three eighths:

| Recipient | Units |
| --- | ---: |
| Carol | 4.25 |
| Dave | 2.55 |
| Reviewer pool | 0.8 |
| Validator pool | 0.4 |
| Total | 8 |

If ten capabilities share that proposal equally across Marketplace and River, each receives one tenth of those weights. Shares conserve the accepted size across products. Units measure accepted work. [Remuneration](05-remuneration.md) converts eligible paid usage into funded allocations.

## Authority and later extensions

The transactional attribution service is the canonical authority for acceptance and [certification](03-certification.md). It owns uniqueness checks, signed decisions and audit history. Freenet publication remains under publisher authority. Transferring attribution decisions into Freenet requires exclusive decision primitives or an agreed consensus mechanism for uniqueness, PIN consumption and blocking challenges. Preserve IDs, signatures, snapshots and audit lineage through any transfer, coordinated with the [remuneration migration gates](05-remuneration.md#recovery-and-authority).

[Plan 4.7](../4-sdui/07-commerce.md) adds optional SDUI artifact and signed authoring-checkpoint mappings to these interfaces. [Plan 4.8](../4-sdui/08-developer.md) owns the visual tools.

## Acceptance

Plan 3.2 requires changed-evidence review, signed size tiebreaks, blocked unresolved challenges and reproducible snapshot weights. Tests conserve size across products, validate every share total and reproduce the example above. Retain tested service revisions and results.
