# 3.1 Product and contributor registration

## Repositories

| Repository | Role | Work in this plan |
| --- | --- | --- |
| [evy](https://github.com/EVY-Platform/evy) | Modified | `services/attribution`: product and contributor registration, PIN issuance, roles and mapping history; the repository integration verifies PINs in pull requests |
| `freenet-appkit` | Used | Publication references from 1.4 Application bundles |
| [freenet-core](https://github.com/freenet/freenet-core) | Used | Protected signing keys from 1.5 Identity, keys and local protection |

## Owned scope

The transactional attribution service owns product registration, economic authority, each product's commercial eligibility policy, contributor key lineage, role eligibility and ownership checks. It retains signed decisions and audit history. [3.2 Attribution workflow and allocation weights](02-attribution.md) owns accepted work and weights. [3.3 Artifact certification and publication evidence](03-certification.md) owns artifact certification. Repository integrations use the same service API.

## Prerequisites

Use protected signing keys and recovery from [1.5 Identity, keys and local protection](../1-freenet-mobile-appkit/05-identity.md), publication identities from [1.4 Application bundles](../1-freenet-mobile-appkit/04-bundles.md), and verified repository and publisher access. Registration establishes economic authority separately from host permissions and delegate namespaces.

## Product and identity records

| Identifier | Owned meaning |
| --- | --- |
| `ProductId` | Economic product mapped to authorized application containers |
| `ActorId` | Contributor signing-key lineage |
| `CapabilityId` | Credited domain behavior, such as `marketplace.fulfillment.agree` |

[1.4 Application bundles](../1-freenet-mobile-appkit/04-bundles.md) owns `PublicationRef`, the exact publication reference.

Verify product/repository ownership and publisher authority before approving a product-to-container mapping. Retain the signed mapping history. Publisher transfers follow [1.7 Upgrades and migration](../1-freenet-mobile-appkit/07-migration.md), with separate attribution approval of the successor mapping. Marketplace and River have separate products even when EVY hosts both.

Security permissions and credited capabilities use separate identifiers and schemas.

The product authority signs a versioned commercial eligibility policy for each product. This policy decides whether the product's certified content can take new paid operations.

## Roles and registration evidence

| Role | Responsibility | Eligibility |
| --- | --- | --- |
| Contributor | Submit signed proposals, evidence and contribution splits | Protected signing key and verified repository evidence |
| Reviewer | Sign acceptance or rejection against the evidence revision | Two accepted proposals in the product |
| Validator | Sign size estimates and settle size disagreements | Two accepted proposals and two accepted reviews in the product |
| Operator | Run the service and record signed product configuration | Named in that configuration |

Each product publishes a signed bootstrap list of reviewers and validators. Every assignment separates the proposal's contributors from its reviewers and validators. Role eligibility follows the actor's verified key history and remains product-scoped.

1. The contributor signs a proposal linking an exact pull request revision.
2. The service issues a one-time PIN bound to the proposal and signing key, valid for 24 hours.
3. The contributor puts the PIN in the pull request description. The repository integration verifies it, consumes it once and retains the repository response and verified revision in the audit history. Later description edits leave that recorded decision intact.
4. One contributor proves PR ownership. Co-contributors sign the proposed split with their own keys. A commit-only proposal carries its PIN in the commit message.

Record key rotation, role grants, suspension, false-evidence findings and signed reinstatement. Rotation requires an old-key signature naming the successor. Recovery uses 1.5 Identity, keys and local protection and must match the repository identity recorded at registration. A key without verified lineage starts with contributor eligibility.

## Acceptance

This plan requires product-scoped bootstrap, one-time ownership checks and co-contributor signatures. Tests reject self-review, substituted repositories, unauthorized publisher mappings, replayed PINs and unsupported recovery claims. Retain tested service revisions and results.
