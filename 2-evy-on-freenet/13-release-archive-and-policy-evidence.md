# 2.13 Release archive and policy evidence

## Repositories

| Repository | Role | Work in this plan |
| --- | --- | --- |
| [evy](https://github.com/EVY-Platform/evy) | Modified | Archive backend, exact evidence schemas and durable receipts |

## Purpose

Retain exact signed EVY UI documents, policies, archive receipts, publication confirmations, code deployment evidence and attribution snapshots. Payment-capable publication requires durable release and policy evidence.

Implement `api/src/modules/archive` with its `archive` schema in the shared backend database. Immutable objects remain in second-region object storage. Owner: EVY evidence lead. [2.14 Backend operations and recovery](14-backend-operations-and-recovery.md) supplies deployment, storage, key custody and recovery. [2.5 EVY authoring and publishing](05-developer.md) owns publication sequencing.

## Base policy publication and retention

Before the first payment-capable UI release, the publisher signs policy version 1 under [2.6 Payments](06-payments.md#financial-policy-identity), including publisher identity, application key, `archive_url`, `archive_key` and payment key-role certificate references. The archive stores its exact canonical signed bytes and returns a durable policy receipt. Independent retrieval verifies those bytes and digest.

The policy archive endpoint is in the publisher workspace for initial setup; signed policy bytes bind the endpoint/audience and trusted key. Readers and backend services verify publisher/application identity before using it. Attribution extends the same envelope at a higher version. Each acknowledged UI document retains its referenced policy bytes for the lifetime of purchases and ledger evidence.

## Receipt and confirmation schema

| Record | Signed content and domain |
| --- | --- |
| Policy receipt | `evy.policy-archive/1`: application key, policy version/digest, stored-byte length, archive object identity, signer/role and durable-save timestamp |
| UI receipt | `evy.ui-archive/1`: application UI key, `service: evy`, version, UI digest/length, policy version/digest, signer/role and object identity |
| Publication confirmation | `evy.ui-publication/1`: exact UI receipt identity, independent node ID, readback time, verified key/tuple/digest, evidence digest and publisher signature |
| Repository contribution deployment evidence | `evy.code-deployment/1`: application, production environment, component/target, source revision, artifact identity/digest, platform applicability, activation evidence/time, retained policy and publisher signature. Test and documentation acceptances also bind their reviewed kind/revision and release-support evidence digests |

Archive deployment evidence and its build/activation references through the same durable receipt workflow. [2.8 Attribution](08-attribution.md#deployment-evidence) owns qualification and [2.12 Listings and purchases](12-listings-and-purchases.md#evy-purchase-interface) binds actual runtime context. Keep referenced evidence for every affected purchase and allocation. Shared vectors cover canonical first-deployment records, normal release/source provenance and runtime-context digests. Acceptances retain their first qualifying deployment; successor releases inherit cumulative credits through their normal version history.

Archive test and documentation support evidence with the same first-release record. Its digests bind passing release-validation results or the published/operational documentation revision to the reviewed work, named capability and exact production artifact. Shared vectors verify these bindings and required evidence for each contribution kind.

Canonicalize each record with RFC 8785, encode Ed25519 signatures as padded base64 and 32-byte digests as base58. The archive recomputes digests from supplied bytes and validates the signer’s retained-policy role. Save exact records and bytes immutably; identical signed retries return the existing receipt. Confirmation verifies exact receipt/readback identity and binds publication time for later purchase admission. [2.5 EVY authoring and publishing](05-developer.md#publishing-the-application) owns submission and retries.

## Commerce evidence

Retain exact participant checkpoints, buyer authorization/handover proofs, scoped key certificates, authority generations, independent acceptance receipts and publisher-signed cutoff/recovery records under [2.6 Payments](06-payments.md#payment-signing-key-revocation) and [2.12 Listings and purchases](12-listings-and-purchases.md#bounded-participant-history). Store dispute summaries and protected provider-evidence objects with their signed digests. Separate access-controlled private dispute evidence from public contract records. Keep every referenced object through purchase, dispute and ledger retention obligations.

Archive fixtures verify payload/receipt hashes, delayed pre-cutoff records, quarantined affected evidence, complete bounded parent chains and dispute-evidence recovery. Keep original proof identities with gross allocations, fee reversals, holds and EVY loss entries; replacement records link back to their original digests.

## Archiving before publication

For every payment-capable or attributed release, `evyctl ui publish` archives each complete signed EVY application document before its PUT or UPDATE. The base EVY policy supplies HTTPS `archive_url` and `archive_key`. The attributed policy version may authorize `attribution_key` for archive receipts through an explicit role binding. Each receipt identifies its signing key and role. The archive identity is the EVY application UI contract key, fixed `evy` namespace, version and `ui_digest`: the 32-byte BLAKE3 hash of the exact complete signed bytes sent as contract state. The publisher saves those bytes and the receipt for retries.

| Step | Required behavior |
| --- | --- |
| 1. Submit | The publisher supplies the signed document and its UI contract identity. The local publisher CLI calls the archive API and journals its signed response. |
| 2. Check | The archive backend checks the publisher signature against the application UI contract's parameters, the fixed EVY namespace, version, document validation and size cap, then computes the digest itself. |
| 3. Save | Create a receipt signed with the retained policy’s archive-authorized key under `evy.ui-archive/1`, covering the UI contract key, service, version, digest and the UI document's exact policy version and digest. Save an immutable copy of the exact signed document bytes, receipt and archive manifest in the second-region S3-compatible bucket from [Operating the services in 2.14 Backend operations and recovery](14-backend-operations-and-recovery.md#operating-the-services), then commit the index and receipt in the shared database's archive schema. |
| 4. Acknowledge | Return the saved receipt after the bucket objects and database commit are durable. A repeated submission returns the same receipt. |
| Publication consumer | [2.5 EVY authoring and publishing](05-developer.md#publishing-the-application) verifies the receipt and owns Freenet submission/readback. |
| Confirmation API | Verify the publisher’s signed confirmation schema and receipt/readback identity. Save it immutably and mark the document published; identical retry returns the saved confirmation acknowledgement. |

An acknowledged archive entry is prepared for publication. UI acceptance and snapshots use entries with verified publisher publication confirmation. UI proposal acceptance records name the same version and digest. The attribution backend consumes that confirmation and creates an attribution snapshot from archived bytes after later versions replace the live UI document. Each snapshot names the EVY application key, version and digest and records units by feature capability, and the archive retains its signed attribution snapshot with the publication evidence.

Archive failure keeps publication pending until a valid durable receipt is available. Identical retries keep one archive entry; different signed documents retain separate digest identities. The immutable copies cover acknowledged documents and signed attribution snapshots within the database's recovery window. Recovery verifies and reindexes these copies before resuming attribution or payout calculations.

## Acceptance

- Archive payment-capable releases with their exact signed policies before attribution is enabled. Invalid policy, UI identity, signature, audience or digest rejects the request.
- A receipt follows durable object storage and database commit. An identical retry returns the same saved receipt.
- Interrupt receipt delivery and confirmation; retry from the publisher journal. Only confirmed documents supply published release evidence.
- Retain distinct digest identities at one version and resolve a historical purchase after the live UI advances.
- Restore the shared database before an acknowledged write, verify immutable bucket copies and rebuild every receipt, policy, confirmation, deployment-evidence and snapshot index in the archive schema. Reproduce purchases from old/new iOS and Android builds using retained runtime-context proofs.
