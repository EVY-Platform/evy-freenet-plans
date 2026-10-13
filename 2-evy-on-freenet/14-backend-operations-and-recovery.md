# 2.14 Backend operations and recovery

## Repositories

| Repository | Role | Work in this plan |
| --- | --- | --- |
| [evy](https://github.com/EVY-Platform/evy) | Modified | Shared deployment, key custody, backup and recovery runbooks |

## Purpose

Deploy, protect, back up and recover one EVY backend application for milestone 2 (EVY on Freenet). Payment, archive, attribution and remuneration are modules with separate schemas in one PostgreSQL database. Each domain owner supplies its interfaces, durable jobs, signing roles, reconciliation and setup evidence.

Owner: EVY operations lead. Provision base storage and archive custody before payment-capable publication. Complete the combined drill before live payments.

## Operating the services

Use the existing `api/` Bun application as the backend foundation. Reuse its server/bootstrap, database tooling, payment procedures and Stripe webhook handler. Add payment, archive, attribution and remuneration modules under `api/src/modules/` with module-owned PostgreSQL schemas named `payment`, `archive`, `attribution` and `remuneration`. Adapt the existing Marketplace orchestration through the payment module. Domain interfaces and signed protocol roles retain their defined names.

Update [`docker-compose.prod.yml`](https://github.com/EVY-Platform/evy/blob/d0fb7e6475f1dfc5c74325e37d4e92aed88d84ed/docker-compose.prod.yml) to deploy one backend application with one `postgres:16` database on a named volume and one shared backend Freenet node. Modules share a node adapter that keeps demand, replies and component permissions bound to their domain. Keep immutable archive objects in second-region object storage and private signing keys in the cloud key service. [pgBackRest](https://pgbackrest.org/) provides encrypted database backups to a second-region S3-compatible bucket.

| Boundary | Required behavior |
| --- | --- |
| Domain code and data | Each module owns its schema and writes through explicit interfaces. Use a database transaction for related local changes when the owning workflow requires it |
| Durable work | Retain module-owned operation journals, webhook inboxes, outboxes and retryable jobs. Persist work before calling Stripe, publishing to Freenet or acknowledging an external effect |
| Signing and credentials | Keep distinct certified signing roles, request audiences and restricted provider credentials. Authorize each signing request for its domain; the key service holds private keys |
| Runtime | One application release and shared failure/security boundary. Bound worker concurrency, queue sizes and retries per module; expose per-module health and pause controls |
| Enablement | Install shared storage and key custody first. Enable each module after its schema, credentials, dependencies and recovery gate pass |

[2.6 Payments](06-payments.md#service-setup) installs the payment schema and journals; [2.13 Release archive and policy evidence](13-release-archive-and-policy-evidence.md) installs the archive schema and immutable evidence; [2.8 Attribution](08-attribution.md#service-setup) installs contributor state; [2.9 Remuneration and payouts](09-remuneration.md) installs the ledger and payout jobs. Run the combined recovery drill before enabling live financial operations. Reuse sources: [API bootstrap](/Users/glesage/Desktop/Repos/evy/api/src/index.ts:18), [API build and database commands](/Users/glesage/Desktop/Repos/evy/api/package.json:8).

- Archive the write-ahead log with PostgreSQL `archive_timeout = 60`.
- Take a daily full backup.
- Keep 30 days of point-in-time recovery data.
- Keep one monthly full backup for the retention period agreed before launch.

| Module | Backs up | Recovery point | Recovery time |
| --- | --- | --- | --- |
| Payment | Pilot enrollment quotas, seller admission authorizations, hosted purchase inventory, listing reservations and fencing numbers, completed-sale uniqueness records, Stripe operation journal, charge, refund, fee and dispute object IDs, provider dispute evidence and balance movements, authority acceptance journal and receipt sequences, certified participant checkpoints and admission results, confirmed cumulative refund totals, the webhook inbox, every signed payment record revision and the outbox to purchase contracts and remuneration | 1 minute | 2 hours, to restore checkout |
| Archive | Exact policy/UI bytes, acknowledged receipts, confirmations, recovery records and attribution snapshots; durable immutable copies plus rebuildable index | Every acknowledged evidence object | 24 hours |
| Attribution | Contributor keys, `ActorId`s and GitHub links, policy versions, proposals and reviews, repository contribution eligibility/merge records, cumulative deployment-qualified acceptances, first-deployment and normal release/source evidence, test/documentation release-support evidence, challenges, exact UI bytes and base snapshots | 1 minute | 24 hours |
| Remuneration | Original allocations with runtime-context digests, eligible acceptance IDs and proof references, refund-rounding rule versions, applied cumulative fee totals, balances, dispute holds, EVY chargeback-loss entries, payouts, reversal links and the transfer outbox | 1 minute | 24 hours |

The release archive keeps immutable copies of referenced signed policies and acknowledged signed UI documents, their receipts, publication evidence, deployment/build/activation evidence and signed attribution snapshots in the second-region bucket, as [Archiving before publication in 2.13 Release archive and policy evidence](13-release-archive-and-policy-evidence.md#archiving-before-publication) requires. Archive objects have their own retention policy and remain available for every purchase and ledger entry that references them. These objects survive the database's recovery window and retain the evidence for purchases using earlier UI versions. Recovery verifies their signatures and digests and rebuilds their database index.

Recover other work lost inside the recovery point from Stripe, which [lists events for 30 days](https://docs.stripe.com/api/events/list), and from the signed records in purchase and UI proposal contracts.

## Restore drill

The operator runs a restore drill before the first live payment, after each schema or key change and every 3 months. The first drill uses a Stripe test-mode sale of the skateboard.

| Phase | Action | Passing evidence |
| --- | --- | --- |
| 1. Read-only restore | Restore every schema and queue to one chosen time in an isolated deployment. Use a read-only Stripe restricted key for the matching source mode/account; keep provider dispatch and Freenet writes paused | pgBackRest `verify` passes, schema versions match and restored ledger totals match the restore point |
| 2. Evidence and reconciliation | Reindex immutable archive objects newer than the restore point. Recover exact UI/policy/snapshot/runtime-context proofs. Read provider events/objects and every page of charges, fees, refunds, disputes and transfers; reconcile reservations, authority receipts and operation IDs | Bob's original version 8 allocation is Carol 24, Dan 36, reviewer 7, validator 3. Every provider effect maps to one journal record; uncertain/unmatched records remain held |
| 3. Controlled test writes | For the test-mode drill, replace the read-only key with a restricted write key for the same allowlisted Stripe test account and test connected accounts. Enable an isolated Freenet network with test publisher/role keys and explicit gateways. Verify account/mode/network identity before dispatch | The allowlist contains only the drill's purchase, refund, dispute and payout operation IDs. Live-mode restored records stay fenced in read-only reconciliation |
| 4. Replay twice | Record baseline provider object IDs/counts and balances, then dispatch each allowlisted journal/outbox entry twice with its original operation ID and signed bytes. Reconcile each outcome between passes; exercise interrupted capture/refund/payout and dispute holds | One intended charge, allocation and transfer per journal identity. Existing operations create zero additional effects; a seeded undispatched operation creates exactly one. Fee reversals, dispute holds and EVY losses match provider evidence |
| 5. Contract readback | Replay saved payment, checkpoint and dispute envelopes on the isolated network and verify them through a second node | Exact bytes are accepted or already present; historical authority/cutoff proofs verify and the listing stays closed after capture |
| 6. Record and close | Record source point, recovery time, account/mode, test record allowlist, credential transitions, baseline/final provider counts and reconciliation results. Revoke test write credentials and stop isolated writers | Every module meets its recovery targets and the drill evidence is retained |

A production restore uses phases 1 and 2 with live read-only credentials. Validate controlled replay in a separate test-mode fixture dataset and isolated network. The operations lead restores production write credentials only after every production operation, reservation, authority and provider effect is reconciled or explicitly held, and signs the allowlist of records permitted to resume. Workers retain all other holds. A cloud key service holds each domain signing key and signs authorized requests; the backend receives signatures. Resume each module after its required database, provider and archive reconciliation passes; prioritize checkout dependencies within the payment recovery target.

## Backup-key rotation

| Event | Required disposition |
| --- | --- |
| Routine operator change | Create a new pgBackRest repository under a new key, take and verify a full backup and direct subsequent WAL/backups there. Retain each previous repository and its protected recovery credentials for its complete 30-day point-in-time window, monthly retention obligations and referenced recovery/evidence coverage |
| Retirement | Record repository creation/last-write times, restore coverage, monthly expiry, named recovery custodians and deletion eligibility. Verify the replacement's recovery coverage and complete an old-key restore before deleting a repository and its credentials after all obligations expire |
| Suspected key exposure | Isolate the affected repository, revoke its write/access credentials and create a replacement under a new key. Restore and re-encrypt required retained generations into protected storage, verify their coverage and immutable evidence digests, then retire exposed copies under a signed incident disposition. Encryption-key exposure prompts an incident review of previously accessible data |

Test routine rotation just before and after the 30-day recovery boundary and a monthly retention boundary. Restore a pre-rotation point and a retained monthly full backup using their recorded credentials; verify post-rotation WAL coverage and blocked early deletion. The compromise drill records custody, re-encrypted coverage, access revocation and final disposition.

| Key | Service | Used for | Rotation | If it leaks |
| --- | --- | --- | --- | --- |
| Payment service key | Payment | Scoped payment, checkpoint and dispute records in purchase contracts | Yearly and after a leak, with a new certificate from the EVY publisher key, as [The payment record in 2.6 Payments](06-payments.md#the-payment-record) describes | Pause checkout and record signing, then publish the authority cutoff and certify a new key. The remuneration module credits only records verified through the payment module's reconciliation interface |
| Payment acceptance key | Payment authority | Independent receipts over verified payloads and monotonic acceptance sequences | Publisher-certified replacement with preserved journal and cutoff coverage | Pause new receipts, reconcile the acceptance journal and publish a publisher-signed recovery disposition |
| Archive service key | Archive | Policy/UI receipts | Yearly and after a leak, with publisher-signed role authority | Pause receipt issuance, rotate and reconcile every acknowledged receipt against immutable exact-byte storage and the signed recovery record |
| Attribution service key | Attribution | Snapshots | Yearly and after a leak. The EVY publisher signs a policy version with the new `attribution_key` | Pause new snapshots and payouts, rotate, preserve original snapshots and publish signed recovery/replacement records |
| Stripe restricted keys and webhook secret | Payment (charges, refunds), remuneration (transfers) | Stripe API calls with only the permissions each service uses, and webhook checks | [Roll the key](https://docs.stripe.com/keys#rolling-keys), which keeps the old one working for up to 7 days. [Roll the webhook secret](https://docs.stripe.com/webhooks), with up to 24 hours of overlap | Roll immediately with zero overlap |
| Backup key | All | pgBackRest encryption | After each operator change | Follow [Backup-key rotation](#backup-key-rotation); retain repositories and recovery credentials through their declared coverage/retention |

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

- The shared backend records its primary/backup operator, deployment commit and schema versions. Each module records retention, signing audience, queue limits, health and recovery evidence.
- Before the first live payment and after schema/key changes, restore the shared database and immutable evidence into an isolated deployment. Meet the declared module recovery point/time targets.
- Duplicate jobs, concurrent workers and a module pause preserve one charge, allocation and payout. Exhaust a module queue and restart the backend: bounded workers and durable recovery preserve the declared domain outcomes. Disabled modules retain their work until their enablement gates pass.
- The read-only and controlled-write phases in [Restore drill](#restore-drill) pass with recorded account/mode/network allowlists and expected provider effect counts. Production resumption follows reconciled per-record authority.
- The routine and compromise fixtures in [Backup-key rotation](#backup-key-rotation) preserve point-in-time, monthly and evidence coverage through retirement.
- Signing-key compromise drills preserve original evidence and apply signed recovery records before new financial writes.
