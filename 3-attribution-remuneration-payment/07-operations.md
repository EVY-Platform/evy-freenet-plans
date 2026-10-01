# 3.7 Operating readiness

## Repositories

| Repository | Role | Work in this plan |
| --- | --- | --- |
| [evy](https://github.com/EVY-Platform/evy) | Modified | `docker-compose.prod.yml` gets a named Postgres volume and pgBackRest archiving, plus a restore drill script, key runbooks and backup alerts for `services/attribution`, `services/payment` and `services/remuneration` |
| `evy-marketplace` | Used | The drill checks Alice's and Bob's order contract after it republishes the signed payment record |

## Purpose

This plan makes the three EVY services from [3.1 Contributor registration and attribution](01-attribution.md), [3.2 Release certification](02-certification.md), [3.4 Payments and checkout](04-payment.md) and [3.5 Remuneration and payouts](05-remuneration.md) ready to hold real money. It owns the one list of launch approvals, the recovery targets, the backups, the restore drill and custody of the service keys.

In the first real sale, Alice sells her skateboard for 70 dollars, Bob pays through Stripe and the 0.70-dollar contributor fee reaches the contributors. After a database loss, the operator restores that sale with no second charge and no second payout.

## Launch approvals

The operator records each approval in the evy repository with the approver, the date and a link to the evidence. Live payments start only when every row is approved.

| Approval | Approver | Evidence |
| --- | --- | --- |
| Operators | Service operator | A named primary and backup operator for each service |
| Stripe account and country | Financial operations lead | Stripe Connect approval for one country and currency, and a test onboarding of a seller like Alice and a contributor like Carol |
| App store payment rules | Financial operations lead | A physical-goods sale paid outside in-app purchase on iOS and Android, under the Apple and Google rules cited in 3.4 Payments and checkout |
| Money rules | Financial operations lead | The signed product policy from 3.1 Contributor registration and attribution, who pays Stripe's fees from 3.4 Payments and checkout, and the negative balance after a refund after payout from 3.5 Remuneration and payouts |
| Retention | Financial operations lead | How long each record kind in [What each service backs up](#what-each-service-backs-up) is kept |
| Recovery | Service operator | A passing [restore drill](#restore-drills) that meets the targets below |
| Keys | Service operator | A named holder for each key in [Service keys](#service-keys) |

## Recovery targets

The recovery point is the most recent work a restore may lose. The recovery time runs from the loss to the service taking requests again.

| Service | Recovery point | Recovery time | Why |
| --- | --- | --- | --- |
| Payment | 1 minute | 2 hours | Bob cannot pay while it is down |
| Remuneration | 1 minute | 24 hours | Payouts run on the product policy's schedule and can wait a day |
| Attribution | 1 minute | 24 hours | Reviews and certification can wait a day |

Work lost inside the recovery point comes back from Stripe, which [lists events for up to 30 days](https://docs.stripe.com/api/events/list), and from the saved signed bytes.

## What each service backs up

Today the evy [`docker-compose.prod.yml`](https://github.com/EVY-Platform/evy/blob/dev/docker-compose.prod.yml) runs `postgres:16` with no named volume and no backup, so all data lives on one host. This plan gives each service its own database on a named volume. [pgBackRest](https://pgbackrest.org/) archives the write-ahead log, with PostgreSQL `archive_timeout = 60`, takes a daily full backup and writes both, encrypted, to an S3-compatible bucket in a second region. The bucket keeps 30 days of point-in-time restore and one monthly full backup for the approved retention period.

| Service | Records | Defined in |
| --- | --- | --- |
| Attribution | Products, contributor keys, Carol's "Invite member" proposal with its review and size, product policy versions, contribution records, snapshots, and the saved archive bytes of each certified version | 3.1 Contributor registration and attribution, 3.2 Release certification |
| Payment | Stripe object IDs for Bob's payment, the webhook inbox, every signed payment record revision and the outbox to the order contract | 3.4 Payments and checkout |
| Remuneration | Allocations of the 0.70-dollar fee, balances, payouts and reversals | 3.5 Remuneration and payouts |

The website container keeps only its latest version, so the saved archive bytes are the only copy of the version Bob bought from.

## Restore drills

The operator runs a drill before the first live payment, after each schema or key change and every 3 months. The first drill uses a Stripe test-mode sale of the skateboard. Later drills use the real sale.

| Step | Action | Check |
| --- | --- | --- |
| 1. Restore | Restore all three databases to a chosen time in an isolated environment. The services use a Stripe [restricted key](https://docs.stripe.com/keys) with read access only, and Freenet publishing is off | pgBackRest `verify` passes and schema versions match |
| 2. Totals | Sum the ledgers | Totals per currency match the totals recorded at the restore point |
| 3. Sale | Recompute the sale from saved bytes after the website container has moved to a newer version | The contribution record, the 0.70-dollar fee and each contributor's allocation match the originals |
| 4. Stripe | Apply Stripe events newer than the restore point through the webhook inbox | Every payment, application fee, transfer and payout in Stripe matches one service record |
| 5. Replay | Run every outbox twice | No second charge, allocation or payout |
| 6. Freenet | Republish the latest signed payment record for Bob's order with the same bytes | The order contract accepts it or already holds it |
| 7. Record | Write down the achieved recovery point and time | Both meet the targets above |

Any record without a match stays on hold. Stripe write access stays off until the operator has decided each held record.

## Service keys

Each service signing key lives in a cloud key service that signs on request, so no host sees the private key. The payment service calls Stripe with a [restricted key](https://docs.stripe.com/keys) that holds only the permissions it uses, as Stripe recommends for new integrations. The publisher key belongs to the product publisher and has its tested backup under [1.4 Application bundles](../1-freenet-mobile-appkit/04-bundles.md#saved-copies-and-recovery). Carol's contributor key stays on her laptop, as 3.1 Contributor registration and attribution sets.

| Key | Service | Signs | Rotation | If it leaks |
| --- | --- | --- | --- | --- |
| Certification key | Attribution | Contribution records and snapshots | Yearly and after each leak | Pause certification, rotate, re-check records signed since the leak |
| Payment root key | Payment | Certificates for payment signing keys | Kept for the life of each order, because its accepted terms name it | Pause checkout, name a new root key in new terms, review payment records in open orders |
| Payment signing key | Payment | Signed payment records in the order contract | Yearly and after each leak, by a new certificate from the root key | Pause checkout and record signing, certify a new signing key, review records signed since the leak |
| Backup key | All | pgBackRest encryption | After each operator change | Start a new pgBackRest repository under a new key, take a full backup, then remove the old repository |
| Stripe restricted key and webhook secret | Payment | Stripe API calls and webhook checks | [Roll the restricted key in Stripe](https://docs.stripe.com/keys#rolling-keys), which keeps the old key working for up to 7 days. [Roll the webhook secret](https://docs.stripe.com/webhooks), which keeps the old secret valid for up to 24 hours | Roll at once with no overlap |

For any leak the operator records the decision before resuming the service.

## Acceptance

- Every service database restores within its recovery point and recovery time in a drill.
- The drill reproduces the skateboard sale's contribution record, 0.70-dollar fee and allocation from saved bytes after the website container has moved to a newer version.
- Replaying outboxes after a restore creates no second Stripe charge, allocation or payout.
- A refund after contributor payout, as 3.5 Remuneration and payouts sets it, survives a restore and a replay with the same result.
- A leaked-key drill pauses payment record signing and resumes under a new signing key that the order contract accepts through the root key.
- Every launch approval has an approver, a date and evidence before the first live payment.
