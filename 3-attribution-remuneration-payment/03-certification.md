# 3.3 Artifact certification and publication evidence

## Repositories

| Repository | Role | Work in this plan |
| --- | --- | --- |
| [evy](https://github.com/EVY-Platform/evy) | Modified | `services/attribution`: contribution records, snapshots, publication observations, native artifact records, eligibility lookup and retention |
| `freenet-appkit` | Used | Exact envelope retention, local readback and independent-node fetch from the 1.4 Application bundles packaging CLI |

## Owned scope

The attribution service owns source-to-artifact mappings, contribution records, immutable snapshots, publication observations and commercial eligibility evidence. It certifies exact web archives, contract/delegate builds and native executables. Its [decision authority in 3.2 Attribution workflow and allocation weights](02-attribution.md#authority-and-later-extensions) is shared with registration and work acceptance.

## Prerequisites

Use accepted work from [3.2 Attribution workflow and allocation weights](02-attribution.md) and release tooling from [1.4 Application bundles](../1-freenet-mobile-appkit/04-bundles.md). 1.4 Application bundles owns `publication_ref` and the tagged `application_content_ref` format, plus building, signing, submission, exact-envelope retention and publication readback.

## Certification records

`ContributionRecordId` identifies an immutable signed certification of exact archive or native-build contents.

| Record | Owned binding |
| --- | --- |
| Contribution record | Product, authorized container, exact archive digest and hash profile, included acceptances, active capabilities and snapshot |
| Snapshot, `SnapshotId` | Immutable resolved actor and role weights for a certified artifact, capability scope and policy version |
| Publication observation | Verified publication reference, matching contribution record, observing node and retained publisher evidence |
| Native artifact record | Product, platform/build identity, exact build digest, accepted source evidence, capabilities, snapshot and distribution evidence |

[3.2 Attribution workflow and allocation weights](02-attribution.md#work-records) owns acceptance records that bind the exact source revision, contribution shares and policy. Reviewed artifacts, including web and native builds, can share a snapshot when the service verifies their source and capability mapping.

## Certification and paid eligibility

Attribution consumes bundle evidence in this commercial order:

1. Verify the accepted source revision, build inputs, source-to-artifact mapping and publisher authority against the exact archive stored by the publishing node.
2. Commit the immutable snapshot and separate signed contribution record in one transaction. Verified local readback and source evidence are sufficient for certification. Record paid eligibility as pending while independent publication evidence is outstanding.
3. Associate an independent-node observation with the exact publication reference and matching certified digest. Retain its signed publisher evidence, observing node and observation details, whether supplied with certification or later.
4. Enable paid use when certification, the matching independent observation and the product's commercial eligibility policy all pass.

The contribution record stays outside the archive it certifies. Sign every binding field with a specified, versioned encoding. Repeating an identical certification request returns the existing record. Changed bytes require matching certification and review of changed evidence. Retain source bytes or a verifiable source archive alongside repository references, dependency/build inputs and provenance. A repository URL alone is insufficient recovery evidence.

A publishing-node read proves local acceptance, while an independent-node read proves retrievability at that observation time. The same archive can appear at several container versions, each with its own verified publication observation. Ongoing availability follows the bundle retention and republishing rules.

Native builds use their own artifact certification and publisher/distribution evidence under a declared verification policy. A client-supplied digest becomes verified evidence only after those checks pass.

Each snapshot identifies capabilities present in the certified contents. Retain contribution history through capability removal and later restoration. The product's signed policy selects eligible records for new paid operations. Existing payments retain their original bindings through updates and publisher transfers.

## Service lookup and retention

For a verified publication or native artifact and capability, return:

- The signed contribution record and its publication or distribution evidence.
- Whether that capability exists in the certified contents.
- The immutable snapshot, resolved recipients and contribution-policy version.
- The product's current eligibility for new commercial operations.

Historical lookups return the original evidence and weights. [3.4 Payments and checkout adapters](04-payment.md#fixed-checkout-evidence) fixes the checkout bindings. [3.5 Usage evidence, remuneration and payouts](05-remuneration.md#verification-and-credit-accounting) verifies those bindings when allocating funds. Commercial suspension governs new operations while existing payments follow their recorded settlement policy.

Retain exact source and artifact bytes, mappings, snapshots, signatures and publication evidence for the configured support and transaction-evidence periods. [3.7 Operating readiness](07-operations.md#backups-and-exact-evidence) owns backups and restore drills. A drill must verify a historical payment after the live container advances and the publisher's primary archive becomes unavailable.

## Acceptance

This plan requires changed-byte rejection, idempotent certification and certification from verified local readback while paid eligibility awaits independent observation. A matching later observation can enable paid use under policy. A mismatched observation keeps it pending. Tests also reject absent capabilities and unverified native digests, preserve original weights after updates, publisher transfer and commercial suspension, and consume the bundle tooling's uncertain-publication recovery evidence.

These are planned service requirements. [1.4 Application bundles](../1-freenet-mobile-appkit/04-bundles.md) establishes the publication mechanism. Acceptance must retain tested revisions and results for the certification and service checks.
