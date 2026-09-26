# 3.6 Contribution and release workspace

## Owned scope

EVY Developer connects repository work to contribution review, certified releases and earnings. Developers write custom web or native application code in their chosen tools and use concrete application protocols.

The first commercial run uses the [Marketplace pickup pilot](08-marketplace.md#pilot-sequence). Optional extensions cover [visual authoring in 4.8](../4-sdui/08-developer.md), [authoring collaboration in 5.3](../5-optional-extensions/03-sync-and-collaboration.md) and [SDUI commerce in 4.7](../4-sdui/07-commerce.md).

## Prerequisites

Use release tooling from [1.4](../1-freenet-mobile-appkit/04-bundles.md), identity and protected signing from [1.5](../1-freenet-mobile-appkit/05-identity.md), and the service interfaces owned by [registration](01-registration.md), [attribution](02-attribution.md), [certification](03-certification.md), [payment](04-payment.md) and [remuneration](05-remuneration.md). Production acceptance also requires [3.7 financial operations readiness](07-operations.md#acceptance). The mobile pilot uses [2.2 authenticated multi-app sessions](../2-evy-mobile-app/02-sessions.md) and the required [1.10 thin-peer profile](../1-freenet-mobile-appkit/10-thin-peer.md).

Use TypeScript, React and Vite for the Developer web application, with Bun for development and tests. Connect the workspace, repository integration and CLI/CI clients through versioned service interfaces.

| Surface | Required work |
| --- | --- |
| Product setup | Register repository ownership, authorized publishers and application identities |
| Contribution review | Submit exact source evidence, show review assignments, estimates, contributor signatures and challenges |
| Release history | Show source revision, build evidence, artifact digest, publication reference and certification status as separate records |
| Commercial eligibility | Show the service decision, missing evidence and the last confirmed observation |
| Earnings | Show accepted weights, pending evidence, funded credits, payable balances, reversals and payout history |
| Financial onboarding | Use protected remuneration interfaces for identity and payout details |

## Repository and CLI/CI workflow

1. Register the product, repository and publisher through [registration](01-registration.md).
2. Submit signed proposals from the workspace or repository integration. Bind every review and size decision to the exact evidence revision.
3. Show the service's merge checks in the repository. A changed revision reruns the required checks.
4. Build application code in the project's own toolchain. CLI/CI submits source provenance and exact artifacts through [bundle tooling](../1-freenet-mobile-appkit/04-bundles.md).
5. Request certification and publication verification through attribution's release sequence. Display pending, verified, conflicted and failed results with the evidence needed to resolve them.
6. Use the services' confirmed records to show commercial eligibility and earnings.

The workspace keeps request IDs and submitted bytes through interrupted requests under [1.6 operation IDs and journals](../1-freenet-mobile-appkit/06-data-and-operations.md). Reconcile an uncertain service or publication result before retrying. CLI/CI credentials have separate scopes for repository access, certification requests and publisher signing. Keep publisher keys and service secrets in their protected stores.

## Release and earnings screens

Show a build artifact, contribution record and observed publication as distinct records. Link each to its owning service and retained evidence. Show whether a publication observation came from the publishing node or an independent node. The release screen consumes the eligibility decision defined by attribution.

Display contribution units separately from money. Each financial amount includes its currency, state and last confirmed service update. Show pending payout onboarding, unresolved recovery, held funds and reversals explicitly. Allocation previews use attribution's resolved weights and remuneration's policy, with a preview label until the owning service confirms the result.

Repository drafts and pending workspace requests survive service outages. A queued request stays pending until the service confirms it. A user can continue editing application code while financial services recover.

## Authority and owned interfaces

| Authority | Owns |
| --- | --- |
| Publisher signer | Container publication authorization |
| Attribution service | [Registration and roles](01-registration.md), [accepted evidence and weights](02-attribution.md), [snapshots and artifact certification](03-certification.md) |
| [Payment](04-payment.md) | Checkout, contributor-fee rules, processor reconciliation and signed payment status |
| [Remuneration](05-remuneration.md) | Usage records, allocations, reservations, balances and payouts |
| EVY Developer | Workflow screens, repository/CLI/CI integration and requests to those authorities |
| [Financial operations](07-operations.md) | Service backups, queue recovery, audit retention, key rotation and operating readiness |

Version requests and responses. Authenticate each actor and product scope, retain idempotency IDs, and show service validation errors next to the relevant evidence. The workspace displays canonical service results. UI caches and repository check summaries remain derived views.

## Acceptance

Plan 3.6 is complete when a developer can:

- Register a repository-backed product and submit a signed contribution through the workspace and CLI/CI.
- Complete review, size validation and challenge resolution against exact source evidence.
- Build a custom application in its own tools, certify its exact artifact and verify publication.
- Open release history and trace its artifact to accepted work and publisher evidence.
- See a pilot operation become a funded allocation, then a payout and a reconciled refund.
- Recover interrupted requests with the same IDs and source bytes.

Run browser tests for review, release and earnings screens, plus service integration tests for CLI/CI. Cover stale status, invalid authority, changed source, failed publication, missing payout details, pending identity recovery, service outages and reversals. Test accessibility and redact logs and diagnostics. A custom native fixture exercises the same service interfaces under its own certified-build policy.

## Governance

Adoption under Freenet Developer remains a proposal requiring agreement on governance, operations and stored-data responsibility. Keep the versioned interfaces compatible through any ownership transfer.
