# 1.7 Upgrades and migration

## Repositories

| Repository | Role | Work in this plan |
| --- | --- | --- |
| [river](https://github.com/freenet/river) | Modified | Delegate cleanup after migration |
| [freenet-migrate](https://github.com/freenet/freenet-migrate) | Modified | Compatible library release for contract and delegate migration |
| [freenet-core](https://github.com/freenet/freenet-core) | Modified | Migration probes, delegate removal and the mobile migration interface |

## Purpose

Carry application state and private records across upgrades. Define component keys, record supported predecessors, migrate contract state and delegate secrets, and retire predecessor versions after verification.

The [installation interface in 1.4 Application bundles](04-bundles.md#release-verification) verifies a release and [1.3 Single-application host](03-host.md#activating-a-release) activates it. Each app runs its own migrations with freenet-migrate when the new release first starts, and runs them again on the next start if they fail. Release fixtures record the exact compatible library, Core and stdlib commits selected for the build.

| App | Migration code | freenet-migrate pin |
| --- | --- | --- |
| River | [delegate_migration.rs](https://github.com/freenet/river/blob/8cf54dd7799514851da7eab051e4cc43f797208d/ui/src/components/app/freenet_api/delegate_migration.rs) | 0.5 |
| Delta | [delegate_migration.rs](https://github.com/freenet/delta/blob/6e8c96031642e03f9cdcbe1bea71059b03699b1d/ui/src/freenet_api/delegate_migration.rs) | 0.6 |
| Harvest | [migrate.rs](https://github.com/freenet/harvest/blob/9eb4a04ed30e75c478df0b89f38f68044bbd947c/ui/src/migrate.rs) for contracts, [delegate_migrate.rs](https://github.com/freenet/harvest/blob/9eb4a04ed30e75c478df0b89f38f68044bbd947c/ui/src/delegate_migrate.rs) for the delegate | 0.6 |
| Atlas | The publisher's CLI, [main.rs](https://github.com/freenet/atlas/blob/051e38033e81a4232341ffa4360af94232e7809b/cli/src/main.rs) and [migration.rs](https://github.com/freenet/atlas/blob/051e38033e81a4232341ffa4360af94232e7809b/cli/src/migration.rs) | 0.6 |

Keep predecessor data until successor readback proves the migration complete. It then retires the old version as in [Retiring the old version](#retiring-the-old-version). While a migration runs, the app shows a migrating state, as River's room list does with `RoomListDisplay::Migrating` ([River room-list source](https://github.com/freenet/river/blob/8cf54dd7799514851da7eab051e4cc43f797208d/ui/src/components/room_list.rs)). Delta’s [#52](https://github.com/freenet/delta/issues/52) and [#53](https://github.com/freenet/delta/pull/53) provide separate application migration examples. The publisher's CLI migrates publisher-owned data, such as the Atlas index, before publishing the release.

## Component identity and re-keying

A contract or delegate key derives from BLAKE3 over its code hash and exact parameter bytes. A change to those inputs creates a successor identity, while retained state stays under its original identity. Parameter encodings belong to the application and must have shared fixtures.

| River component | Identity inputs |
| --- | --- |
| Room contract | Code hash and `ChatRoomParametersV1 { owner: VerifyingKey }` |
| Chat delegate | Code hash and empty parameters, yielding BLAKE3 of the code hash |
| Website container | Code hash of the pinned container Wasm, which [1.4 Application bundles](04-bundles.md#the-archive-and-its-definition) passes on every publication, and the publisher's verifying-key parameters |

Sources: [River FREENET.md](https://github.com/freenet/river/blob/8cf54dd7799514851da7eab051e4cc43f797208d/FREENET.md), [publication rules](https://github.com/freenet/river/blob/8cf54dd7799514851da7eab051e4cc43f797208d/.claude/rules/river-publish.md), and the [whitepaper status](https://github.com/freenet/paper-1/blob/bff15702759800a003ffbfce639fe859f57d966d/sections/07-status.tex). [Core upgrade issue #2776](https://github.com/freenet/freenet-core/issues/2776) is related protocol evidence. freenet-migrate provides the explicit application migration adapters. The dapp-builder skill's [upgrade and migration guide](https://github.com/freenet/freenet-agent-skills/blob/890ad1b20c03ee99dd0a0ae89ec3e3b17c19eac4/skills/dapp-builder/references/upgrade-and-migration.md) gives app authors the same rules.

### Predecessor registry

A new Wasm build gives a component a new key. When River ships a new room contract, Alice's "Skate club" room gets a new key, and its state stays under the old key. The predecessor registry lists earlier component versions. The new release derives their keys and locates their state.

River keeps one registry per component. Each is a TOML file, oldest version first. The current key comes from the Wasm in the bundle, so the registry lists only earlier versions.

| Registry | Component | Fields per entry |
| --- | --- | --- |
| [common/legacy_room_contracts.toml](https://github.com/freenet/river/blob/8cf54dd7799514851da7eab051e4cc43f797208d/common/legacy_room_contracts.toml) | Room contract | `version`, `description`, `date`, `code_hash` |
| [legacy_delegates.toml](https://github.com/freenet/river/blob/8cf54dd7799514851da7eab051e4cc43f797208d/legacy_delegates.toml) | Chat delegate | The same, plus `delegate_key` and `irregular_key` |

| Step | Who | Rule |
| --- | --- | --- |
| 1. Record | Developer | Add the old version to the registry before rebuilding the Wasm. River runs `cargo make add-migration` for the delegate and `cargo make add-room-contract-migration` for the room contract. |
| 2. Check | CI | Fail the build when a component's Wasm changes without a new entry, or when `freenet_migrate_build::codegen()` generates an empty table. River's [delegate migration rules](https://github.com/freenet/river/blob/8cf54dd7799514851da7eab051e4cc43f797208d/.claude/rules/delegate-migration.md) run both checks. The empty-table check catches a misnamed TOML table, which freenet-migrate reads as an empty registry ([freenet-migrate#20](https://github.com/freenet/freenet-migrate/issues/20)). |
| 3. Probe | App | When the new release [first starts](#purpose), work out each old key from the entry's code hash and the room's exact parameter bytes, then probe newest first. For "Skate club" the parameters are `ChatRoomParametersV1 { owner }` with Alice's verifying key. Keep those bytes unchanged, because re-encoded parameters produce a different key. Core answers a probe of an unregistered delegate key with a typed `DelegateError::Missing` ([#5729](https://github.com/freenet/freenet-core/pull/5729)), so the app can tell "not registered" apart from "no answer". |
| 4. Carry forward | App | Move the state the probe finds into the new contract. freenet-migrate's `migrate_contract` runs steps 3 and 4, as Atlas's CLI does. Harvest runs the same steps through freenet-migrate's `ProbeDriver`. The app's [walk policy](#walk-policies) decides whether the new contract gets the newest copy or all copies merged. Delegate secrets move as in [Delegate secret export and import](#delegate-secret-export-and-import). |

Handle these registry cases:

- For `irregular_key = true`, probe the recorded `delegate_key` in place of the BLAKE3-derived key. River's V1 chat delegate uses this entry.
- Users with data only in River delegate versions V4 to V6 rejoin their rooms by invite. The registry covers versions whose messages the current runtime can deserialize ([river#204](https://github.com/freenet/river/issues/204)). Include V4 to V6 recovery in the registry fixtures.

### Supported backup generations

The pinned River registry checked on 2026-10-09 lists chat delegates V1–V3 and V7–V31, and room contracts V1–V32. These are candidate automatic-migration fixtures. The release build declares tested source/target pairs, exact artifacts and backup format `application-backup/1` in its compiled inventory; admission requires passing iOS and Android readback evidence for each declared pair. EVY starts with delegate generation 1 and adds each tested predecessor pair when its code changes.

River room recovery for V4–V6 delegates uses a valid invite and is a separate recovery fixture. Report that coverage explicitly alongside automatic migration. Shared backup coverage lists current generation plus every admitted predecessor; skipped-version tests verify the declared pairs before public release.

### Walk policies

Declare walk policy for River room/chat components and the EVY delegate. Atlas, Delta and Harvest remain source/regression examples. The default policies stop at an unresponsive predecessor.

| Policy | Part | What the walk does | Trade-off | Used by |
| --- | --- | --- | --- | --- |
| `NewestSnapshotWins` (default) | Delegate secrets | Takes the newest generation that answers and stops at the first one that stays silent | Protects against rollback. Generations behind a silent one stay stranded | EVY |
| `NewestSnapshotWinsContinuePastUnresponsive(RollbackRiskAck)` (0.7.0) | Delegate secrets | Walks past a silent generation | Gives up rollback protection | None |
| `UnionAllGenerations` | Delegate secrets | Merges every generation that answers | Can bring back secrets that were deleted by leaving them out. River limits this with ranked tombstones ([river#590](https://github.com/freenet/river/issues/590)) | River, Delta, Harvest |
| `NewestFirstWins` (default) | Contract state | Takes the newest real state and stops at an unknown newer generation, unless the app passes `RollbackRiskAck` to `continue_past_unknown` | Protects against rollback | River's room contract |
| `FoldAll` | Contract state | Merges every real generation | Can bring back data that was deleted by leaving it out | Atlas index, Harvest |

### Delegate secret export and import

Move delegate secrets with freenet-migrate's `migrate_delegate_secrets`, as River, Delta and Harvest do. Read through each predecessor's messages and write through the successor's handler. Mark the pair complete after verification. EVY uses its `ExportRecords` and `ImportRecords` adapters through the [mobile migration interface](#mobile-migration-interface). The SDK builds against the [compatible migration library](#compatible-migration-library).

[Core-assisted migration](#core-assisted-migration) defines the adoption checks for the proposed Core-mediated secret transfer.

Before an upgrade or restore, check every current and predecessor artifact against the [execution policy in 1.4 Application bundles](04-bundles.md#execution-policy). A policy expansion ships in matching iOS and Android store builds. Serialize migration with the [export barrier in 1.10 Backup and restore](10-backup-and-restore.md#export): each snapshot contains one identity generation, its records and a resumable migration checkpoint.

On a fresh iOS or Android installation, the app validates support for the backup's predecessor generation before restore writes. Core installs and registers its Wasm and exact parameters from the authenticated backup in staging, as [1.10 Backup and restore](10-backup-and-restore.md#restore) requires under [#4035](https://github.com/freenet/freenet-core/issues/4035). The app migrates through the registered predecessor's messages and verifies successor readback in staging. The [staged restore transaction in 1.10 Backup and restore](10-backup-and-restore.md#staged-restore-transaction) then activates the restored generation. CI fixtures cover every supported backup generation, including skipped releases.

For River the call moves the entries in the chat delegate's key index:

| Entry | What it holds for Alice | Defined in |
| --- | --- | --- |
| `room:<owner key>` | One room's state, her signing key (`self_sk`), her member records and her nickname. River rebuilds the room secrets from the room state with her key | `ROOM_KEY_PREFIX` in [ui/src/components/app/chat_delegate.rs](https://github.com/freenet/river/blob/8cf54dd7799514851da7eab051e4cc43f797208d/ui/src/components/app/chat_delegate.rs), `RoomSlot` in [ui/src/room_data.rs](https://github.com/freenet/river/blob/8cf54dd7799514851da7eab051e4cc43f797208d/ui/src/room_data.rs) |
| `rooms_meta` | Her current room, notification settings and room order | `ROOMS_META_KEY` in the same file, `RoomsMeta` in `room_data.rs` |
| `outbound_dms` | Her outbound DMs | `OUTBOUND_DMS_STORAGE_KEY` in [common/src/chat_delegate.rs](https://github.com/freenet/river/blob/8cf54dd7799514851da7eab051e4cc43f797208d/common/src/chat_delegate.rs#L15) |

River re-keys its chat delegate roughly weekly. Rebuild entries outside the migration key index on startup:

- `signing_key:` entries. River stores Alice's signing key again from `room:<owner key>` at start, with `signing::migrate_signing_key` in [ui/src/signing.rs](https://github.com/freenet/river/blob/8cf54dd7799514851da7eab051e4cc43f797208d/ui/src/signing.rs).
- `room_sub:`, `room_members:` and `room_secret:` caches. The new delegate fills them again after River sends `EnsureRoomSubscription` for each room Alice owns ([subscription.rs](https://github.com/freenet/river/blob/8cf54dd7799514851da7eab051e4cc43f797208d/delegates/chat-delegate/src/subscription.rs)).

Disclose in the app's privacy notes that secrets pass through application code as plaintext during migration. Backup packaging and restore belong to [1.5 Identity, keys and local protection](05-identity.md).

Include a predecessor with a corrupt blob in the registry fixtures ([#4909](https://github.com/freenet/freenet-core/issues/4909)). Verify that completion waits for a valid migration and that retries preserve the user's deletions.

### Compatible migration library

Freenet migration-library maintainers agree the compatible release; Core maintainers approve its mobile integration. A tested dependency set lets the mobile runner read predecessor messages and preserve identity keys. Library compatibility and the integrated runner are release requirements for supported upgrades and restores.

File a freenet-migrate issue to release a version compatible with Core's pinned freenet-stdlib, 0.12.1. Build the selected Core, stdlib and freenet-migrate versions together in the mobile SDK and run migration fixtures on that exact dependency set before release. This library release precedes the mobile migration interface below.

Sources: [Cargo.toml](https://github.com/freenet/freenet-migrate/blob/74aed27eaec8a4347b47fa2665ea511d2fd14175/freenet-migrate/Cargo.toml), [stdlib #136](https://github.com/freenet/freenet-stdlib/pull/136) and [stdlib #137](https://github.com/freenet/freenet-stdlib/pull/137).

### Mobile migration interface

Core maintainers approve the mobile runner, namespace authorization and lifecycle fencing before its feature PR. The interface lets iOS and Android run the same migration adapters and verify successor records before opening a session.

File a Core issue for `crates/mobile` to run freenet-migrate's `migrate_delegate_secrets` in Rust and expose it to Swift and Kotlin. The app supplies its predecessor registry, walk policy and export, import and verification adapters. Before migration, the host checks the owning application and its declared delegate namespaces under [Application data inventory in 1.5 Identity, keys and local protection](05-identity.md#application-data-inventory).

| Migration path | Permitted execution and activation |
| --- | --- |
| First start after a build upgrade | Supported-predecessor roles read/export verified records; the current successor imports under the snapshot barrier with ordinary work fenced. Commit its verified checkpoint before opening the fresh host session. |
| Backup restore or isolated transform | Predecessor/current artifacts and migration-only adapters execute in encrypted staging, with network effects fenced. Activate the complete verified generation atomically before normal calls. |

Migration-only roles execute inside staging. A transform needed by a live upgrade creates a staging generation and uses the same activation transaction. Interruption retains the complete predecessor and resumes its checkpoint.

Before execution, the host authorizes the exact current, supported predecessor and migration-only Wasm and parameter identities.

The runner:

- Holds other calls to the successor until imported records pass readback verification.
- Keeps predecessor records after interruption and resumes migration on the next start.
- Runs backup restore adapters inside the [staged restore transaction in 1.10 Backup and restore](10-backup-and-restore.md#staged-restore-transaction).
- Serializes migration with the [export barrier in 1.10 Backup and restore](10-backup-and-restore.md#export), so each snapshot captures one complete migration generation.

After verification, the app follows [Retiring the old version](#retiring-the-old-version).

iOS and Android fixtures cover normal upgrades, skipped supported generations, interruption, failed imports, successor readback and rejection of records outside the application inventory. [2.11 EVY delegate and private records](../2-evy-on-freenet/11-delegate-and-private-records.md#updating-the-evy-delegate) supplies EVY fixtures preserving `root_seed`, derived public keys, addresses and exact pending signed operations.

### Core-assisted migration

Core maintainers decide author-bound provenance and successor transfer under #5255. Adoption is a separate gate: it requires an implemented protocol and the provenance, secret-transfer and record-preservation fixtures below. Supported releases use the application-driven migration path defined in this plan.

Evaluate [Core RFC #5255](https://github.com/freenet/freenet-core/issues/5255) after Core implements and tests author-bound delegate provenance and Core-mediated secret transfer to a successor. Adoption tests verify provenance, secret deposit and preservation of application records. EVY uses [application-driven migration](#delegate-secret-export-and-import).

### Retiring the old version

Reclaim predecessor copies within the installation’s measured storage budget and declared supported-predecessor retention in [1.11 Cellular data and resource budgets](11-cellular-data-and-resource-budgets.md#resource-budgets). Test River's 27 delegate generations as the workload ([river#586](https://github.com/freenet/river/issues/586)).

After migration completes, retire each predecessor delegate in this order:

| Step | What the app does |
| --- | --- |
| 1. Verify | Confirms through successor readback that the new delegate holds every entry the migration walk found. |
| 2. Reclaim | Deletes predecessor copies through the predecessor delegate's own delete message. |
| 3. Unregister | Sends `UnregisterDelegate` for the predecessor key to stop its `NodeStarted` runs and wake-ups ([#5747](https://github.com/freenet/freenet-core/pull/5747) review item S8). Core drops the key's record, and its wake-ups stop at the next fire. |

### Pointer records

Publisher tooling uses signed pointer records to locate update candidates and check publication freshness. River’s `river.room-contract` and `river.chat-delegate` records identify its components ([pointer-records.toml](https://github.com/freenet/river/blob/8cf54dd7799514851da7eab051e4cc43f797208d/pointer-records.toml)). CI checks retention and increasing versions ([river#677](https://github.com/freenet/river/issues/677)).

An installed mobile build runs exact identities admitted by [1.4 Application bundles](04-bundles.md#execution-policy). Runtime pointer lookup starts when a named River or EVY update-discovery flow needs it. That flow verifies publisher signature and version floor, records the candidate, checks build admission and migrates through declared adapters. Discovery never expands execution authority. [freenet-migrate#33](https://github.com/freenet/freenet-migrate/issues/33) and [river#695](https://github.com/freenet/river/issues/695) supply candidate-resolution evidence.

## Acceptance

- Shared fixtures derive identical keys on all supported hosts, including empty parameters and recorded irregular keys. CI requires registry coverage for changed Wasm.
- River's room contract and chat delegate migrations run on iOS and Android and keep Alice's "Skate club" room and keys, including across skipped versions.
- A test migrates from a real predecessor River chat delegate Wasm under Pulley on iOS and Android ([river#630](https://github.com/freenet/river/issues/630)).
- On iOS and Android, a fresh installation containing only the latest app restores each supported predecessor generation from a backup, registers its bundled Wasm and exact parameters, and migrates its secrets to the current delegate.
- An interrupted or failed migration keeps the predecessor's data, and the next start runs it again. The app shows its migrating state while the migration runs.
- After a completed migration on iOS and Android, River has reclaimed the old copies, the old chat delegate key is unregistered, and the old key gets no further wake-ups.
- Drafts and signed messages waiting to be sent survive activation and migration.
- On iOS and Android, export during migration captures one consistent generation and its checkpoint. Restore verifies the authenticated snapshot, runs only policy-admitted predecessor and migration adapters, and preserves identity keys and pending signed bytes. Test skipped versions and a predecessor whose Wasm comes only from the backup.
