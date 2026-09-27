# 4.7 SDUI commerce and attribution

Let optional SDUI flows use the released checkout, certification and usage-evidence interfaces.

Prerequisites:

- [3.3 Artifact certification and publication evidence](../3-attribution-remuneration-payment/03-certification.md)
- [3.4 Payments and checkout adapters](../3-attribution-remuneration-payment/04-payment.md)
- [3.5 Usage evidence, remuneration and payouts](../3-attribution-remuneration-payment/05-remuneration.md)
- [3.6 Contribution and release workspace](../3-attribution-remuneration-payment/06-developer.md)
- [4.2 SDUI bundles and publication](02-bundles.md)
- [4.5 SDUI actions and delegate protocols](05-actions.md)
- [4.6 SDUI data and operation presentation](06-data.md)

Paid-flow acceptance uses [3.8 Paid application pilot and commercial acceptance](../3-attribution-remuneration-payment/08-marketplace.md).

## Repositories

| Repository | Role | Work in this plan |
| --- | --- | --- |
| `freenet-sdui` | Modified | Checkout service step, domain-evidence action and payment status presentation |
| [evy](https://github.com/EVY-Platform/evy) | Modified | `services/attribution` gains the checkpoint-evidence path and checkpoint author registration |
| `evy-marketplace` | Modified | SDUI screens and action definitions for the pilot order flow |
| `freenet-appkit` | Used | Checkout adapter and usage-evidence interface from 3.4 Payments and checkout adapters and 3.5 Usage evidence, remuneration and payouts |
| `freenet-app-builder` | Used | Signed checkpoints as the visual-authoring evidence input |

## Ownership

| Owner | Behavior used by SDUI |
| --- | --- |
| [3.2 Attribution workflow and allocation weights](../3-attribution-remuneration-payment/02-attribution.md) and [3.3 Artifact certification and publication evidence](../3-attribution-remuneration-payment/03-certification.md) | Accepted work, contribution weights, artifact certification, publication/distribution evidence and eligibility |
| [3.4 Payments and checkout adapters](../3-attribution-remuneration-payment/04-payment.md) | Terms, checkout attempts, processor interaction, fee receipts and signed payment status |
| [3.5 Usage evidence, remuneration and payouts](../3-attribution-remuneration-payment/05-remuneration.md) | Completion-evidence verification, funded allocations, balances, reversals and payouts |
| [3.6 Contribution and release workspace](../3-attribution-remuneration-payment/06-developer.md) | Contribution review, release history, service status and earnings workflows |
| SDUI integration | Typed action bindings, reviewed SDUI artifact inputs and presentation of authoritative results |

Applications adopt this plan when they add SDUI to a commercial flow. The base commercial services apply their existing policies to web, native and SDUI callers.

## Checkout binding

Expose the released host checkout adapter as a versioned service step under [4.5 SDUI actions and delegate protocols](05-actions.md). Bind typed order references, agreed terms and the durable operation handle to the request. The adapter supplies the authenticated application/session context and verified content reference required by the payment service.

The host opens the approved checkout destination through its browser or native handoff. [Reader identity bindings in 4.4 SDUI identity and permissions](04-identity.md) enforce the same session and capability checks as other protected steps. Keep processor credentials in the payment service.

Verify the service-signed payment record and display its status using the [canonical status names and mapping in 3.4 Payments and checkout adapters](../3-attribution-remuneration-payment/04-payment.md). Separately show whether the verified order state contains that revision. An accepted payment can still be awaiting order synchronization.

A return link selects the order and starts reconciliation. Domain actions follow the order's verified evidence and policy, including its manual-capture rules. Show captured/refunded amounts and disputes from their authoritative fields.

Pending operations retain the original content, contribution-record, snapshot and policy bindings fixed at checkout. A reader, bundle or delegate update resumes that operation through the foundation and payment adapters. The new screen displays its existing bindings.

## Domain evidence

A declared action can name a qualifying capability and the domain completion condition exposed by the released evidence adapter. Delegates or approved application adapters interpret and verify the relevant domain records. The host records and submits the claim through the existing evidence interface.

Completion evidence must identify the same order, operation, payment and certified content used by the base service checks. Render events and button taps are presentation events. Remuneration eligibility comes from verified domain outcomes under the product's bound policy.

Use the service-defined event identity and durable delivery rules. Bindings expose pending, credited, rejected or conflicted processing results with their last confirmed update. The owning services handle duplicate claims, allocation limits, settlement and reversals.

## SDUI artifact integration

Accept either evidence path, or both when a release combines repository and visually authored content:

| Authoring path | Reviewed source and build evidence |
| --- | --- |
| Repository-authored SDUI | Exact reviewed repository revisions, accepted contribution references, and pinned build inputs and tool versions under the existing repository-evidence rules |
| Visual authoring | Exact signed [checkpoint defined in 4.8 EVY Developer visual authoring](08-developer.md#durable-checkpoint-protocol), project identity, membership epoch and roster digest, author-operation evidence, accepted contribution references, and pinned exporter version and inputs |

Repository-authored SDUI uses CLI packaging and certification independently of [4.8 EVY Developer visual authoring](08-developer.md). The checkpoint path uses 4.8 EVY Developer visual authoring when selected.

Both paths map their reviewed inputs to:

- Exact screen, action, view and delegate-schema digests.
- Reader build and schema package versions.
- Contract/delegate artifacts and any custom web build included in the archive.
- Capability IDs present in the reviewed contents.

Keep reviewed source evidence, prepared archive, contribution record and publication observation as separate records. The [certification owner in 3.3 Artifact certification and publication evidence](../3-attribution-remuneration-payment/03-certification.md) certifies exact retained archive bytes and verifies publication evidence. A dedicated native build follows its native-artifact policy. The service decides how reviewed SDUI and native artifacts share contribution weights.

Changed source or checkpoint content creates a new evidence revision and requires renewed review. Changed artifact bytes require matching certification of their reviewed source-to-artifact mapping. Browser publication readback and independent-node observation retain their base meanings. Payment eligibility follows the commercial service decision.

## Optional checkpoint evidence checks

This plan adds the checkpoint-evidence path to the attribution service for projects that select visual authoring. The service owns these checks and their signed decisions. The editor submits evidence and displays the result.

- Register a checkpoint author by verifying a signed request, the author's project membership and control of the signing key. Bind the verified author key to the contributor's `ActorId` lineage and retain the registration evidence.
- Verify the project identity, membership epoch, owner-signed roster and roster digest against the exact signed checkpoint. Verify included author-operation signatures, causal references and the operation frontier against that checkpoint and the membership authority for each operation.
- Bind contributor claims and co-contributor signatures to that exact evidence revision. Record the verified checkpoint and roster digests with the acceptance and source-to-artifact mapping. Apply the existing product-scoped review, role-separation and challenge rules through [3.2 Attribution workflow and allocation weights](../3-attribution-remuneration-payment/02-attribution.md).
- Require renewed review when checkpoint content changes. Preserve the signed evidence behind earlier accepted revisions.

At author registration, the attribution service approves and records a versioned contributor recovery profile with its recovery authority and required proofs. Use the [identity interfaces in 1.5 Identity, keys and local protection](../1-freenet-mobile-appkit/05-identity.md) for protected key recovery. The attribution service verifies a successor against the registered profile and retains signed contributor lineage. A repository-linked profile uses the repository identity recorded at registration. A checkpoint-author profile names the authorized recovery authority and project/identity evidence it accepts. Project membership establishes project access. Contributor-history transfer requires the registered recovery proof. Freeze payout-identity changes while recovery is unresolved. An identity lacking verified lineage starts with contributor eligibility.

## Acceptance

- The selected paid pilot completes the same order through SDUI, custom web and native controls with equivalent terms, verified completion evidence and service results.
- Checkout cancellation, spoofed return links, repeated taps and an uncertain handoff pass the base payment safety tests through the reader adapter.
- Manual-capture fixtures display canonical `Authorized` status and permit only policy-approved order actions. Canceled and expired unpaid checkout fixtures use the canonical `Canceled or expired` result.
- A verified `Accepted` payment awaiting order synchronization displays both states. Observing the matching signed revision updates the synchronization result while preserving the payment evidence.
- Updating the reader, definitions or delegate during checkout preserves the original payment/content/contribution/policy bindings.
- Repeated renders, replayed notifications and duplicate evidence submissions produce the same funded allocation result as the base service fixtures.
- Hand-authored SDUI in a repository completes CLI packaging, publication and certification from reviewed revisions and pinned build inputs while visual-authoring tools and checkpoint services are absent.
- Checkpoint certification verifies registered author lineage, project identity, epoch, roster signatures/digest and included operation signatures against the exact checkpoint. Substituted checkpoints, unauthorized authors and invalid successor lineage fail.
- Changed checkpoint content requires a new evidence revision and renewed review. Recovery fixtures accept the registered profile's authorized proof and freeze payout-identity changes for unresolved or unauthorized claims.
- Certification detects changed screens, actions, schemas, reader builds and domain artifacts against the reviewed mapping for both evidence paths.
- Offline and service-outage screens distinguish saved work, signed payment state, order synchronization and pending usage-evidence verification. Refund and reversal results remain visible after reader updates.
