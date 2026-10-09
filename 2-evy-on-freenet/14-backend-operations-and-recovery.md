# 2.14 Backend operations and recovery

## Repositories

| Repository | Role | Work in this plan |
| --- | --- | --- |
| [evy](https://github.com/EVY-Platform/evy) | Modified | Shared deployment, key custody, backup and recovery runbooks |

## Purpose

Deploy, protect, back up and recover EVY payment, archive, attribution and remuneration backend services. Each domain owner adds its own schema, reconciliation and setup evidence to these shared templates.

Owner: EVY operations lead. Provision base storage and archive custody before payment-capable publication. Complete the combined drill before live payments.

## Operating the services

The payment database and journal are installed by [2.6 Payments](06-payments.md#service-setup), and the archive database and immutable evidence by [2.13 Release archive and policy evidence](13-release-archive-and-policy-evidence.md), then contributor state by [2.8 Attribution](08-attribution.md#service-setup), before their operations begin. This plan provisions shared storage/key custody first; each domain plan installs its schema and journal before enabling its operations. Run the combined recovery drill after commerce, attribution and remuneration are installed. Configure [`docker-compose.prod.yml`](https://github.com/EVY-Platform/evy/blob/d0fb7e6475f1dfc5c74325e37d4e92aed88d84ed/docker-compose.prod.yml) with `postgres:16` and one database per service on a named volume. [pgBackRest](https://pgbackrest.org/) provides encrypted backups to an S3-compatible bucket in a second region.

- Archive the write-ahead log with PostgreSQL `archive_timeout = 60`.
- Take a daily full backup.
- Keep 30 days of point-in-time recovery data.
- Keep one monthly full backup for the retention period agreed before launch.

| Service | Backs up | Recovery point | Recovery time |
| --- | --- | --- | --- |
| Payment | Pilot enrollment quotas, seller admission authorizations, hosted purchase inventory, listing reservations and fencing numbers, completed-sale uniqueness records, Stripe operation journal, charge, refund and fee object IDs, confirmed cumulative refund totals, the webhook inbox, every signed payment record revision and the outbox to purchase contracts and remuneration | 1 minute | 2 hours, to restore checkout |
| Archive | Exact policy/UI bytes, acknowledged receipts, confirmations, recovery records and attribution snapshots; durable immutable copies plus rebuildable index | Every acknowledged evidence object | 24 hours |
| Attribution | Contributor keys, `ActorId`s and GitHub links, policy versions, proposals and reviews, code eligibility records, verified merge evidence, acceptances, challenges, the saved bytes of every UI version and the snapshots | 1 minute | 24 hours |
| Remuneration | Original allocations, refund-rounding rule versions, applied cumulative fee totals, balances, payouts, reversal links and the transfer outbox | 1 minute | 24 hours |

The release archive keeps immutable copies of referenced signed policies and acknowledged signed UI documents, their receipts, publication evidence and signed attribution snapshots in the second-region bucket, as [Archiving before publication in 2.13 Release archive and policy evidence](13-release-archive-and-policy-evidence.md#archiving-before-publication) requires. Archive objects have their own retention policy and remain available for every purchase and ledger entry that references them. These objects survive the database's recovery window and retain the evidence for purchases using earlier UI versions. Recovery verifies their signatures and digests and rebuilds their database index.

Recover other work lost inside the recovery point from Stripe, which [lists events for 30 days](https://docs.stripe.com/api/events/list), and from the signed records in purchase and UI proposal contracts.

The operator runs a restore drill before the first live payment, after each schema or key change and every 3 months. The first drill uses a Stripe test-mode sale of the skateboard.

| Step | Action | Check |
| --- | --- | --- |
| 1. Restore | Restore the backend databases to one chosen time in an isolated environment, with a read-only Stripe [restricted key](https://docs.stripe.com/keys) and Freenet writes turned off | pgBackRest `verify` passes and schema versions match |
| 2. Totals | Sum the ledgers | Totals match those recorded at the restore point |
| 3. Archive and purchase | Verify and reindex immutable UI archive objects newer than the database restore point. Recompute Bob's purchase from version 8's exact signed bytes and matching digest and snapshot after EVY has moved to application version 9 | The acknowledged archive entries are recovered, and Bob's allocation is Carol 24, Dan 36, reviewer 7, validator 3 |
| 4. Stripe | Apply Stripe events newer than the restore point through the webhook inbox. Reconcile outstanding listing reservations, fences and Stripe operations before write access resumes | Every charge, application fee, refund, transfer and payout matches one record; each listing has at most one completed sale |
| 5. Replay | Run every outbox twice | Each charge, allocation and payout appears once |
| 6. Freenet | Send the latest signed payment record for Bob's purchase again with the same bytes | The purchase contract accepts it or already holds it |
| 7. Record | Write down the recovery point and time reached | Both meet the targets |

Keep unmatched records on hold. Restore Stripe write access after the operator resolves each held record. A cloud key service holds each service signing key and signs on request; hosts receive signatures only.

| Key | Service | Used for | Rotation | If it leaks |
| --- | --- | --- | --- | --- |
| Payment service key | Payment | Payment records in purchase contracts | Yearly and after a leak, with a new certificate from the EVY publisher key, as [The payment record in 2.6 Payments](06-payments.md#the-payment-record) describes | Pause checkout and record signing, then certify a new key. The remuneration service credits only records that match the payment service's database |
| Archive service key | Archive | Policy/UI receipts | Yearly and after a leak, with publisher-signed role authority | Pause receipt issuance, rotate and reconcile every acknowledged receipt against immutable exact-byte storage and the signed recovery record |
| Attribution service key | Attribution | Snapshots | Yearly and after a leak. The EVY publisher signs a policy version with the new `attribution_key` | Pause new snapshots and payouts, rotate, preserve original snapshots and publish signed recovery/replacement records |
| Stripe restricted keys and webhook secret | Payment (charges, refunds), remuneration (transfers) | Stripe API calls with only the permissions each service uses, and webhook checks | [Roll the key](https://docs.stripe.com/keys#rolling-keys), which keeps the old one working for up to 7 days. [Roll the webhook secret](https://docs.stripe.com/webhooks), with up to 24 hours of overlap | Roll immediately with zero overlap |
| Backup key | All | pgBackRest encryption | After each operator change | Start a new pgBackRest repository under a new key, take a full backup and remove the old repository |

## Signing-key recovery

The EVY publisher signs an `evy.key-recovery/1` record: application and key role, compromised key ID, trust cutoff and its evidence, replacement key/certificate, retained-policy identities, affected original evidence digests, trust disposition and replacement-record references. Archive the exact signed record under [2.13 Release archive and policy evidence](13-release-archive-and-policy-evidence.md). Keep original bytes immutable.

| Evidence | Recovery rule |
| --- | --- |
| Verified evidence before the cutoff | Preserve it under its original policy/key identity and recorded trust decision |
| Suspected evidence in the affected interval | Hold new allocation/payout use while independently reconciling database, provider and publication evidence |
| Reconstructed attribution snapshot | Sign a new replacement identity linked to original digest and recovery record; preserve historical allocation links |
| Payment authority | Apply publisher-authorized rotation/revocation under [2.6 Payments](06-payments.md#payment-signing-key-revocation) before resuming production writes; reconcile uncertain charges and listing fences |

Completion requires immutable-original verification, invalid-cutoff/replacement rejection, restored policy/authority checks and a drill covering pending payments, refunds and payouts. A schema change uses versioned codecs and matching iOS and Android admission fixtures. Back up keys/journals with named custodians and test recovery after operator changes; retain backup repositories until declared evidence retention and recovery coverage are satisfied.

## Acceptance

- Every backend records its primary/backup operator, deployment commit, schema version, storage retention, key audience and recovery runbook.
- Before the first live payment and after schema/key changes, restore isolated services and evidence stores. Meet the declared recovery point/time targets.
- Reindex immutable evidence newer than database recovery, reconcile reservations and provider operations, then replay outboxes twice. One charge, allocation and payout remain.
- Signing-key compromise drills preserve original evidence and apply signed recovery records before new financial writes.
