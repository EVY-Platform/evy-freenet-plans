# 3.6 Contribution and release workspace

## Repositories

| Repository | Role | Work in this plan |
| --- | --- | --- |
| [evy](https://github.com/EVY-Platform/evy) | Modified | `web/` Developer workspace, repository integration and merge checks, CLI and CI clients with scoped credentials |
| `freenet-appkit` | Used | Bundle tooling that CLI and CI drive for artifacts and publication |

## Owned scope

EVY Developer connects repository work to contribution review, certified releases and earnings. Developers write custom web or native application code in their chosen tools and use concrete application protocols.

Optional visual authoring belongs to [4.8 EVY Developer visual authoring](../4-sdui/08-developer.md).

## Prerequisites

Use release tooling from [1.4 Application bundles](../1-freenet-mobile-appkit/04-bundles.md), identity and protected signing from [1.5 Identity, keys and local protection](../1-freenet-mobile-appkit/05-identity.md), and the service interfaces owned by:

- [3.1 Product and contributor registration](01-registration.md)
- [3.2 Attribution workflow and allocation weights](02-attribution.md)
- [3.3 Artifact certification and publication evidence](03-certification.md)
- [3.4 Payments and checkout adapters](04-payment.md)
- [3.5 Usage evidence, remuneration and payouts](05-remuneration.md)

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

1. Register the product, repository and publisher through [3.1 Product and contributor registration](01-registration.md).
2. Submit signed proposals from the workspace or repository integration. Bind every review and size decision to the exact evidence revision.
3. Show the service's merge checks in the repository. A changed revision reruns the required checks.
4. Build application code in the project's own toolchain. CLI/CI submits source provenance and exact artifacts through the [bundle tooling in 1.4 Application bundles](../1-freenet-mobile-appkit/04-bundles.md).
5. Request certification and publication verification through attribution's release sequence. Display pending, verified, conflicted and failed results with the evidence needed to resolve them.
6. Use the services' confirmed records to show commercial eligibility and earnings.

The workspace keeps request IDs and submitted bytes through interrupted requests under [1.6 Application protocols, data and operations](../1-freenet-mobile-appkit/06-data-and-operations.md). Reconcile an uncertain service or publication result before retrying. CLI/CI credentials have separate scopes for repository access, certification requests and publisher signing. Keep publisher keys and service secrets in their protected stores.

## Release and earnings screens

Show a build artifact, contribution record and observed publication as distinct records. Link each to its owning service and retained evidence. Show whether a publication observation came from the publishing node or an independent node. The release screen consumes the eligibility decision defined by attribution.

Display contribution units separately from money. Each financial amount includes its currency, state and last confirmed service update. Show pending payout onboarding, unresolved recovery, held funds and reversals explicitly. Allocation previews use attribution's resolved weights and remuneration's policy, with a preview label until the owning service confirms the result.

Repository drafts and pending workspace requests survive service outages. A queued request stays pending until the service confirms it. A user can continue editing application code while financial services recover.

## Authority and owned interfaces

| Authority | Owns |
| --- | --- |
| Publisher signer | Container publication authorization |
| Attribution service | [3.1 Product and contributor registration](01-registration.md), [3.2 Attribution workflow and allocation weights](02-attribution.md), [3.3 Artifact certification and publication evidence](03-certification.md) |
| [3.4 Payments and checkout adapters](04-payment.md) | Checkout, contributor-fee rules, processor reconciliation and signed payment status |
| [3.5 Usage evidence, remuneration and payouts](05-remuneration.md) | Usage records, allocations, reservations, balances and payouts |
| EVY Developer | Workflow screens, repository/CLI/CI integration and requests to those authorities |

Version requests and responses. Authenticate each actor and product scope, retain idempotency IDs, and show service validation errors next to the relevant evidence. The workspace displays canonical service results. UI caches and repository check summaries remain derived views.

## Acceptance

This plan is complete when a developer can:

- Register a repository-backed product and submit a signed contribution through the workspace and CLI/CI.
- Complete review, size validation and challenge resolution against exact source evidence.
- Build a custom application in its own tools, certify its exact artifact and verify publication.
- Open release history and trace its artifact to accepted work and publisher evidence.
- Run a fixture paid operation in the test environments of [3.4 Payments and checkout adapters](04-payment.md) and [3.5 Usage evidence, remuneration and payouts](05-remuneration.md), with the fixture order contract and the fixture completion-evidence producer from those plans. See it become a funded allocation, then a payout and a reconciled refund.
- Recover interrupted requests with the same IDs and source bytes.

Run browser tests for review, release and earnings screens, plus service integration tests for CLI/CI. Cover stale status, invalid authority, changed source, failed publication, missing payout details, pending identity recovery, service outages and reversals. Test accessibility and redact logs and diagnostics. A custom native fixture exercises the same service interfaces under its own certified-build policy.

## Governance

Adoption under Freenet Developer remains a proposal requiring agreement on governance, operations and stored-data responsibility. Keep the versioned interfaces compatible through any ownership transfer.
