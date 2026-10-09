# 1.10 Backup and restore

## Repositories

| Repository | Role | Work in this plan |
| --- | --- | --- |
| [freenet-core](https://github.com/freenet/freenet-core) | Modified | Snapshot barrier, versioned codec and staged restore |
| [freenet-appkit](https://github.com/glesage/freenet-appkit) | Modified | Recovery adapters and iOS/Android fixtures |
| [river](https://github.com/freenet/river) | Used | Room/key recovery fixtures |

## Purpose

Define one versioned backup codec, consistent snapshot and staged restore for River and EVY on iOS and Android. [1.5 Identity, keys and local protection](05-identity.md) owns platform keys, lock and Forget. [3.1 Automated backup](../3-optional-extensions/01-backup.md) owns scheduling, providers and retention.

Owner: AppKit recovery lead. Complete this plan before River test delivery and EVY production release.

## Export and import

Alice saves River's keys and private records in one encrypted backup file. On a new iPhone or Android phone, she opens the file with her recovery code and gets her rooms and DMs back.

Use Core's `export` and `import` support for the passphrase-encrypted [FNSX file](https://github.com/freenet/freenet-core/blob/e7d0b06c9326f377d250bf8344baaac2ba2658c6/docs/secrets-at-rest.md). Test coverage against the room identities available through [`riverctl identity export`](https://github.com/freenet/river/blob/8cf54dd7799514851da7eab051e4cc43f797208d/cli/README.md), River's UI and `IdentityExport` ([river#136](https://github.com/freenet/river/issues/136)).

### Recovery code

Generate 32 random bytes and encode them as 52 uppercase RFC 4648 base32 characters, without padding. Display grouped characters and require re-entry before enabling backups. Decode case-insensitively after removing display spaces/hyphens; validate length and unused tail bits. The canonical KDF input is the original 32 decoded bytes.

### Optional passkey recovery

Core maintainers and the AppKit recovery lead agree the wrapping method and #5764 integration before enabling this option. It gives users a passkey-based way to recover the same backup master key. Admission requires the iOS and Android interoperability and trusted-context fixtures below.

Owner: AppKit recovery lead. Track [Core #5764](https://github.com/freenet/freenet-core/issues/5764), checked 2026-10-09, as optional interoperability work. Trusted recovery UI uses a dedicated top-level loopback context at `http://localhost:<recovery-port>`, RP ID `localhost`, separate from River’s `127.0.0.1` application context. Only the recovery coordinator opens it; validate origin, challenge, RP ID and current recovery generation.

Matching native iOS and Android interfaces expose `CreateRecoveryCredential` and `UnwrapRecoveryMasterKey` to that trusted context. PRF output wraps the same backup master key; the versioned header names the credential wrapping method and authenticated parameters. Recovery codes are the default recovery method. Enable the passkey method after shared iOS/Android fixtures prove PRF availability, restored synced credentials, cross-platform unwrap, changed recovery port and rejection of application-frame calls. Record API/provider versions and format/signature vectors before admitting the method.

### The backup file

Core maintainers approve the versioned FNSX application payload, sealing interface and executable-inclusive export/import scope under #4035 before feature PRs. A fresh installation needs the exact delegate artifacts as well as its records to restore supported predecessors. The authenticated manifest binds code, secrets and host records to one snapshot; the codec and supported-generation fixtures are release requirements.

```text
River backup file
├── Authenticated header: format version, KDF parameters, salt and nonce
└── One FNSX encrypted envelope
    ├── Canonical manifest: backup ID, snapshot generation, application and coverage
    ├── Core records: selected secrets, delegate Wasm and exact registrations
    └── Declared host records: matching identity, migration and pending-operation state
```

Extend Core's FNSX payload to seal the complete application snapshot captured by [Export](#export). The `application-backup/1` codec derives a 32-byte master key with Argon2id from the canonical recovery-code bytes and a 16-byte random setup salt: 64 MiB memory, 3 iterations, parallelism 1. The header records that versioned profile. For each export, generate a fresh 16-byte envelope salt and 24-byte nonce; derive a 32-byte envelope key with HKDF-SHA256(master key, envelope salt, info `freenet.application-backup/1`). Encrypt the complete payload once with XChaCha20-Poly1305. The header is authenticated associated data. Core and host records enter the same envelope before sealing, with one encryption layer. Decode only bounded header fields before authentication.

Manual export derives the master key from the recovery code. Automatic export uses that same master key from protected device storage. Core’s sealing interface takes the derived envelope key directly; its versioned adapter specifies this exact key derivation. Shared fixtures fix code bytes, setup salt, envelope salt, nonce, header and payload and require identical encrypted bytes across Rust, Swift and Kotlin. Each export uses fresh randomness outside deterministic fixtures. Accept only declared KDF profiles and bounded header lengths before authentication; test tampered parameters, unknown profiles and manual/automatic cross-restores on iOS and Android.

The codec header declares format `application-backup/1`, KDF profile ID, 16-byte setup salt, 16-byte envelope salt, 24-byte nonce and ciphertext length. Wire fields use fixed-width lengths and raw salt/nonce bytes; the exact encoded header is authenticated associated data. The payload uses canonical manifest bytes plus length-prefixed Core/host record sets. Shared codec vectors fix field ordering, integer endianness and header/payload bytes before Core implementation is admitted. The profile is an implementation requirement of this plan; acceptance proves its Core/FNSX adapter and iOS/Android interoperability.

Capture uses the lower of the installation profile’s measured snapshot budget and 256 MiB/10,000 secrets. The profile declares a numeric barrier deadline and recovery-chunk size before acceptance. The host recovery coordinator supplies bounded-chunk export/import authority for River and EVY. EVY’s delegate capability checks are defined in [2.11 EVY delegate and private records](../2-evy-on-freenet/11-delegate-and-private-records.md#trusted-recovery-and-migration-access).

The canonical manifest binds these fields to the authenticated payload:

| Field | Contents |
| --- | --- |
| `backup_id`, `snapshot_generation` | Unique export ID and the captured application generation |
| Format and execution policy | Backup format version, source store-policy version and SHA-256 policy digest |
| Application and release | Application format, full published identity and verified `application_content_ref`, as [1.4 Application bundles](04-bundles.md#release-references) defines |
| Identity and migration | Identity generation, migration checkpoint and supported component generations |
| Inventory | Declared current and supported predecessor delegate namespaces and host-record sets |
| Components and records | Exact delegate keys, code hashes, registration parameters, record-set identifiers, byte lengths and SHA-256 digests |
| Coverage | Included and excluded application data and supported restore generations |

Authenticate the whole envelope and verify every declared length, digest, namespace and component before staging. This binds the coverage report, host records and executable artifacts to the same secrets and snapshot.

Implement the executable backup export and import proposed in [#4035](https://github.com/freenet/freenet-core/issues/4035), open and unassigned as checked on 2026-10-07. Core exports each selected delegate's Wasm, code hash, full delegate key and exact registration parameters from the snapshot. `crates/mobile` exposes snapshot capture and sealing to the host. Store device-only credentials in host-owned device credential storage outside the export selection: session tokens, node keys, sync member/coordinator private credentials, OS grants and local backup keys. They stay with their installation. The coverage report lists these exclusions; restore creates or provisions replacements through each owning protocol.

### Export

Core maintainers approve the snapshot barrier and capture/cancellation interface before its feature PR. Capturing delegate and host records together preserves writes already acknowledged to Alice and keeps identity, drafts and pending signatures consistent. Export acceptance requires the approved implementation and interruption/concurrent-write fixtures on iOS and Android.

File a Core issue for the snapshot barrier and capture interface below. Core and `crates/mobile` expose capture and cancellation to Swift and Kotlin. Capture the complete [application data inventory in 1.5 Identity, keys and local protection](05-identity.md#application-data-inventory).

Alice runs the export with River open. `crates/mobile` uses the application's coordinator to capture one complete generation:

1. Validate River's declared current and supported predecessor namespaces and host records against the application's inventory.
2. Enter a barrier covering request admission, delegate writes, identity changes, migration, restore and Forget. Pause new mutations and finish or durably classify in-flight work for the application before capturing its complete generation.
3. Capture an immutable snapshot of the selected secrets, delegate code and exact registrations, declared host records, identity generation, migration checkpoint, drafts and exact pending signed operations. Record `snapshot_generation` and verify cross-record references. Persist the snapshot encrypted under the installation KEK before releasing the barrier.
4. Resume application work. Seal the captured bytes and manifest in the versioned FNSX envelope defined in [The backup file](#the-backup-file), authenticating every selected part. A capture or sealing failure reports an export error and retains the previous completed backup.
5. Open the iOS or Android save dialog through trusted host code, as Freenet Mail does through the browser shell ([mail#77](https://github.com/freenet/mail/issues/77), [mail#194](https://github.com/freenet/mail/pull/194)). Alice saves the file, for example to iCloud Drive or Google Drive. Reclaim the local snapshot after publication or cancellation under the application's cleanup coordinator.

Set byte and time limits for the barrier and staging snapshot. On timeout or storage exhaustion, abort capture, release paused work and report the failure. Process recovery reclaims incomplete snapshots before retrying export. The snapshot contains every write acknowledged before its barrier.

### Restore

1. Alice picks the file and types her recovery code. The host authenticates the full envelope and header, then verifies its canonical manifest, all record and component digests, application inventory, snapshot generation and cross-record references. A wrong code, altered manifest, missing record set or damaged file stops the restore before any restore writes.
2. The host checks that this River release can read the file. Core verifies each Wasm code hash and delegate registration against the authenticated snapshot and the store build's [execution policy in 1.4 Application bundles](04-bundles.md#execution-policy). The app checks its migration checkpoint, adapters and mobile runtime against every restored generation. An expanded execution policy requires matching iOS and Android store builds before restore proceeds. The host shows Alice what the file holds and asks her to confirm. These checks finish before any restore writes.
3. `crates/mobile` creates an encrypted staging store for River. Core installs and registers the bundled delegates there through the capability required under #4035, then restores their secrets under the recorded keys with `import_bundle`. The host writes the declared host records into the same staged generation.
4. River runs its supported delegate migrations in staging and verifies the resulting records. The host activates the complete generation through the [staged restore transaction](#staged-restore-transaction).
5. River checks each restored signing key against Alice's member entry in "Skate club", then fetches messages, members and bans. The host opens new sessions and shows Alice the coverage report.

A backup from a supported earlier River release supplies that release's chat delegate Wasm and exact parameters. Core registers it in staging and restores its secrets under the recorded key. River carries those secrets forward to the current chat delegate in staging, as [1.7 Upgrades and migration](07-migration.md#delegate-secret-export-and-import) describes. River test delivery and EVY production delivery require their supported restore paths to pass on iOS and Android.

### Staged restore transaction

Core maintainers approve isolated execution, store selection and durable generation activation before its feature PR. Restore updates code, secrets and host records as one generation, so a crash recovers a complete usable identity. River test delivery and EVY production release require the approved transaction and failure-injection fixtures on iOS and Android.

File a Core issue for isolated restore stores and a durable activation record that selects one application's complete data generation. Core and `crates/mobile` expose the transaction to Swift and Kotlin. Build on the executable-inclusive backup capability proposed in [#4035](https://github.com/freenet/freenet-core/issues/4035).

Before staging, verify the authenticated manifest, snapshot generation and migration checkpoint from [Export](#export). `crates/mobile` coordinates the application's delegate code, registrations, secrets and declared host records:

| Phase | Required behavior |
| --- | --- |
| Stage | Show the host's native restoring screen and pause the app's sessions. Keep the existing generation selected. Write into separate delegate and host-record stores protected by the node KEK through the iOS Keychain or Android Keystore. Direct Core's per-entry `import_bundle` writes into this generation. |
| Validate and migrate | Check cross-record references, resume the migration checkpoint, run policy-admitted restore adapters and verify successor readback. Preserve identity keys, drafts and exact pending signed operations. Staged delegates run only restore adapters. |
| Prepare activation | Flush the complete generation and validated manifest to durable storage. Close the application session, delegates and store handles. |
| Activate | Atomically switch the durable activation record to select the complete application generation. Core and host records resolve through that record. Open a fresh session and reject callbacks from the previous generation. |
| Recover | Read the activation record on startup before opening sessions. An interruption before the switch selects the existing generation; an interruption after the switch selects the complete restored generation. A staging failure keeps the existing generation selected and offers a retry. |
| Clean up | Reclaim superseded generations and abandoned staging files after activation or recovery selects a complete generation. |

Report local restore success after activation. Resume network writes, subscriptions and automatic wake-ups, then refresh network state.

On iOS and Android, inject write failures, full storage, migration failures and termination before and after activation.

## Acceptance

- On iOS and Android, River's backup file restores Alice's signing keys, room secrets and DMs onto a fresh installation.
- On iOS and Android, a fresh installation containing only the latest River release restores a backup from a supported earlier delegate build using the file's Wasm and exact parameters, then migrates its keys and records to the current delegate. Fixtures cover skipped releases, code or registration mismatches and unsupported generations; validation failures keep the phone's data intact.
- Host records River declares round-trip through the backup file. Device-local backup keys, sync member/coordinator private credentials, session tokens, node keys, folder-access grants and cleanup-control records stay with their owning installation.
- On iOS and Android, export while signing, saving drafts, cleaning pending operations, changing identity, migrating or updating application components. Every accepted backup restores one consistent snapshot, including all writes acknowledged before its barrier, matching keys and records, and a resumable migration checkpoint.
- On iOS and Android, alter the manifest or header, mix record sets from two backups, remove a part, substitute a namespace or code artifact, and change a length or digest. Authentication or validation rejects each case before restore writes.
- On iOS and Android, terminate capture and sealing, fill snapshot storage and exceed the barrier deadline. Application work resumes or recovers, the previous completed backup remains usable, and incomplete snapshots are reclaimed.
- On iOS and Android, restore over an existing identity with different signing keys, room secrets and host records. Inject failures during code installation, each secrets and host-record write, migration, validation and activation. After recovery, the app reads either the complete existing generation or the complete restored generation. Fixtures include full storage and process termination immediately before and after the activation switch.
- On iOS and Android, staged delegates produce network effects only after activation. A successful restore opens new sessions, rejects callbacks from superseded sessions and reclaims staging files after recovery.
- Tests cover wrong recovery codes, damaged or cut-off files, unknown format versions, oversized fields, interrupted imports, reinstall and full storage.
- A restore opens new sessions and passes application identity and session-generation checks. A copied backup file opens only with its recovery code.
- Require passing identity, backup and restore tests for River test delivery and EVY production release.
