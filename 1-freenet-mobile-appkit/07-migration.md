# 1.7 Upgrades and migration

## Repositories

| Repository | Role | Work in this plan |
| --- | --- | --- |
| [river](https://github.com/freenet/river) | Modified | Connect the existing migration adapter and journal to SDK coordination; verify completion and retire predecessor records |
| [freenet-migrate](https://github.com/freenet/freenet-migrate) | Modified | Compatible library release for contract and delegate migration |
| [freenet-core](https://github.com/freenet/freenet-core) | Modified | SDK migration coordination, native Rust runner, migration probes and delegate removal |

## Purpose

Carry application state and private records across upgrades. Define component keys, record supported predecessors, migrate contract state and delegate secrets, and retire predecessor versions after verification.

The [installation interface in 1.4 Application bundles](04-bundles.md#release-verification) verifies a release and [1.3 Single-application host](03-host.md#activating-a-release) activates it. One SDK lifecycle coordinator manages each installation's upgrade on iOS and Android. River supplies its existing application migration adapter and completeness journal; native EVY uses the shared Rust migration runner with EVY's record adapters. The coordinator resumes interrupted work from the selected driver's durable checkpoint. Release fixtures record the exact compatible library, Core and stdlib commits selected for the build.

| App | Migration code | freenet-migrate version |
| --- | --- | --- |
| River | [delegate_migration.rs](https://github.com/freenet/river/blob/78307756805f3e02399791dda142c86b83780b8f/ui/src/components/app/freenet_api/delegate_migration.rs), with the durable completeness journal | 0.7 |
| Delta | [delegate_migration.rs](https://github.com/freenet/delta/blob/6e8c96031642e03f9cdcbe1bea71059b03699b1d/ui/src/freenet_api/delegate_migration.rs) | 0.6 |
| Atlas | The publisher's CLI, [main.rs](https://github.com/freenet/atlas/blob/051e38033e81a4232341ffa4360af94232e7809b/cli/src/main.rs) and [migration.rs](https://github.com/freenet/atlas/blob/051e38033e81a4232341ffa4360af94232e7809b/cli/src/migration.rs) | 0.6 |

Keep predecessor data until successor readback proves the migration complete. It then retires the old version as in [Retiring the old version](#retiring-the-old-version). While a migration runs, the app shows a migrating state, as River's room list does with `RoomListDisplay::Migrating` ([River room-list source](https://github.com/freenet/river/blob/78307756805f3e02399791dda142c86b83780b8f/ui/src/components/room_list.rs)). Delta's [#52](https://github.com/freenet/delta/issues/52) and [#53](https://github.com/freenet/delta/pull/53) provide separate application migration examples. The publisher's CLI migrates publisher-owned data, such as the Atlas index, before publishing the release.

## Component identity and re-keying

A contract or delegate key derives from BLAKE3 over its code hash and exact parameter bytes. A change to those inputs creates a successor identity, while retained state stays under its original identity. Parameter encodings belong to the application and must have shared fixtures.

| River component | Identity inputs |
| --- | --- |
| Room contract | Code hash and `ChatRoomParametersV1 { owner: VerifyingKey }` |
| Chat delegate | Code hash and empty parameters, yielding BLAKE3 of the code hash |
| Website container | Code hash of the container Wasm, which [1.4 Application bundles](04-bundles.md#the-archive-and-its-definition) passes on every publication, and the publisher's verifying-key parameters |

Sources: [River FREENET.md](https://github.com/freenet/river/blob/78307756805f3e02399791dda142c86b83780b8f/FREENET.md), [publication rules](https://github.com/freenet/river/blob/78307756805f3e02399791dda142c86b83780b8f/.claude/rules/river-publish.md), and the [whitepaper status](https://github.com/freenet/paper-1/blob/bff15702759800a003ffbfce639fe859f57d966d/sections/07-status.tex). [Core upgrade issue #2776](https://github.com/freenet/freenet-core/issues/2776) is related protocol evidence. freenet-migrate provides the explicit application migration adapters. The dapp-builder skill's [upgrade and migration guide](https://github.com/freenet/freenet-agent-skills/blob/890ad1b20c03ee99dd0a0ae89ec3e3b17c19eac4/skills/dapp-builder/references/upgrade-and-migration.md) gives app authors the same rules.

### Predecessor registry

A new Wasm build gives a component a new key. When River ships a new room contract, Alice's "Skate club" room gets a new key, and its state stays under the old key. The predecessor registry lists earlier component versions. The new release derives their keys and locates their state.

River keeps one registry per component. Each is a TOML file, oldest version first. The current key comes from the Wasm in the bundle, so the registry lists only earlier versions.

| Registry | Component | Fields per entry |
| --- | --- | --- |
| [common/legacy_room_contracts.toml](https://github.com/freenet/river/blob/78307756805f3e02399791dda142c86b83780b8f/common/legacy_room_contracts.toml) | Room contract | `version`, `description`, `date`, `code_hash` |
| [legacy_delegates.toml](https://github.com/freenet/river/blob/78307756805f3e02399791dda142c86b83780b8f/legacy_delegates.toml) | Chat delegate | The same, plus `delegate_key` and `irregular_key` |

| Step | Who | Rule |
| --- | --- | --- |
| 1. Record | Developer | Add the old version to the registry before rebuilding the Wasm. River runs `cargo make add-migration` for the delegate and `cargo make add-room-contract-migration` for the room contract. |
| 2. Check | CI | Fail the build when a component's Wasm changes without a new entry, or when `freenet_migrate_build::codegen()` generates an empty table. River's [delegate migration rules](https://github.com/freenet/river/blob/78307756805f3e02399791dda142c86b83780b8f/.claude/rules/delegate-migration.md) run both checks. The empty-table check catches a misnamed TOML table, which freenet-migrate reads as an empty registry ([freenet-migrate#20](https://github.com/freenet/freenet-migrate/issues/20)). |
| 3. Probe | App | When the new release [first starts](#purpose), work out each old key from the entry's code hash and the room's exact parameter bytes, then probe newest first. For "Skate club" the parameters are `ChatRoomParametersV1 { owner }` with Alice's verifying key. Keep those bytes unchanged, because re-encoded parameters produce a different key. Core answers a probe of an unregistered delegate key with a typed `DelegateError::Missing` ([#5729](https://github.com/freenet/freenet-core/pull/5729)), so the app can tell "not registered" apart from "no answer". |
| 4. Carry forward | App | Move the state the probe finds into the new contract. freenet-migrate's `migrate_contract` runs steps 3 and 4, as Atlas's CLI does. The app's [walk policy](#walk-policies) decides whether the new contract gets the newest copy or all copies merged. Delegate secrets move as in [Delegate secret export and import](#delegate-secret-export-and-import). |

Handle these registry cases:

- For `irregular_key = true`, probe the recorded `delegate_key` in place of the BLAKE3-derived key. River's V1 chat delegate uses this entry.
- Users with data only in River delegate versions V4 to V6 rejoin their rooms by invite. The registry covers versions whose messages the current runtime can deserialize ([river#204](https://github.com/freenet/river/issues/204)). Include V4 to V6 recovery in the registry fixtures.

### Supported backup generations

The registry at River commit `78307756805f3e02399791dda142c86b83780b8f`, checked 14 October 2026, contains 30 delegate predecessors (V1–V3 and V7–V33) and 33 room predecessors (V1–V33). Generate candidate coverage directly from both TOML registries during the build; record their digests and fail if the compiled coverage disagrees. The release build declares tested source/target pairs, exact artifacts and backup format `application-backup/1` in its compiled inventory; admission requires passing iOS and Android readback evidence for each declared pair.

River room recovery for V4–V6 delegates uses a valid invite and is a separate recovery fixture. Report that coverage explicitly alongside automatic migration. Shared backup coverage lists current generation plus every admitted predecessor; skipped-version tests verify the declared pairs before public release.

### Walk policies

Declare walk policy for River's room contract and chat delegate. Live upgrades use the release's predecessor registry and declared policy. Backup restore uses the authenticated source set under [Restore source generations](#restore-source-generations). Atlas and Delta provide source and regression examples. The default policies stop at an unresponsive predecessor in the selected walk scope.

| Policy | Part | What the walk does | Trade-off | Used by |
| --- | --- | --- | --- | --- |
| `NewestSnapshotWins` (default) | Delegate secrets | Takes the newest generation that answers and stops at the first one that stays silent | Protects against rollback. Generations behind a silent one stay stranded | SDK policy fixture |
| `NewestSnapshotWinsContinuePastUnresponsive(RollbackRiskAck)` (0.7.0) | Delegate secrets | Walks past a silent generation | Gives up rollback protection | None |
| `UnionAllGenerations` | Delegate secrets | Merges every generation that answers | Can bring back secrets that were deleted by leaving them out. River limits this with ranked tombstones ([river#590](https://github.com/freenet/river/issues/590)) | River, Delta |
| `NewestFirstWins` (default) | Contract state | Takes the newest real state and stops at an unknown newer generation, unless the app passes `RollbackRiskAck` to `continue_past_unknown` | Protects against rollback | River's room contract |
| `FoldAll` | Contract state | Merges every real generation | Can bring back data that was deleted by leaving it out | Atlas index |

### Restore source generations

The SDK coordinator derives restore sources from the authenticated backup manifest and the build's tested source/target migration path. [1.10 Backup and restore](10-backup-and-restore.md#the-backup-file) defines the snapshot's exhaustive `source_generations` set and required record references.

| Route | Predecessor scope and failure rule |
| --- | --- |
| Live upgrade | Use the release's normal registry, walk policy and durable checkpoint. Apply its checks for unresponsive or unknown predecessors before declaring completion |
| Backup restore | Validate every declared source against the authenticated snapshot, inventory, exact artifact/parameter identities and supported migration path. Run the predecessor walk and completeness journal over that source set. A required missing, damaged or unresponsive source blocks activation and preserves the existing generation |

A version 1 snapshot restored by a version 4 build can omit data generations 2 and 3. Generations absent from the authenticated source set are outside this restore walk. The tested path may require intermediate transformation artifacts; admit and verify those artifacts independently through the execution policy.

Bind the restore checkpoint to the backup ID, snapshot generation, selected source set, target generation and driver route. Resume that same scope after interruption. Preserve deletions under the selected application's migration policy, verify successor keys and records, then activate the complete generation. Restore fixtures verify root seeds, addresses, drafts and exact pending signed operations on iOS and Android.

### Delegate secret export and import

Use freenet-migrate through the selected application route. River's existing adapter calls `migrate_delegate_secrets_journaled` and owns its completeness journal. Native EVY uses the shared Rust runner and EVY's export, import and verification adapters. Read through predecessor messages, write through successor handlers and mark a pair complete after verified readback. The SDK coordinator requires that completion before activation. Native SDK fixtures on iOS and Android exercise the [mobile migration interface](#mobile-migration-interface) against the [compatible migration library](#compatible-migration-library).

[Core-assisted migration](#core-assisted-migration) defines the adoption checks for the proposed Core-mediated secret transfer.

Before an upgrade or restore, check every current and predecessor artifact against the [execution policy in 1.4 Application bundles](04-bundles.md#execution-policy). A policy expansion ships in matching iOS and Android store builds. Serialize migration with the [export barrier in 1.10 Backup and restore](10-backup-and-restore.md#export): each snapshot contains one identity generation, its records and a resumable migration checkpoint.

On a fresh iOS or Android installation, the coordinator validates the backup's [restore source generations](#restore-source-generations) and tested source/target path before restore writes. Core installs and registers its Wasm and exact parameters from the authenticated backup in staging, as [1.10 Backup and restore](10-backup-and-restore.md#restore) requires under [#4035](https://github.com/freenet/freenet-core/issues/4035). The app migrates through the registered predecessor's messages and verifies successor readback in staging. The [staged restore transaction in 1.10 Backup and restore](10-backup-and-restore.md#staged-restore-transaction) then activates the restored generation. CI fixtures cover every supported backup generation, including skipped releases.

For River the call moves the entries in the chat delegate's key index:

| Entry | What it holds for Alice | Defined in |
| --- | --- | --- |
| `room:<owner key>` | One room's state, her signing key (`self_sk`), her member records and her nickname. River rebuilds the room secrets from the room state with her key | `ROOM_KEY_PREFIX` in [ui/src/components/app/chat_delegate.rs](https://github.com/freenet/river/blob/78307756805f3e02399791dda142c86b83780b8f/ui/src/components/app/chat_delegate.rs), `RoomSlot` in [ui/src/room_data.rs](https://github.com/freenet/river/blob/78307756805f3e02399791dda142c86b83780b8f/ui/src/room_data.rs) |
| `rooms_meta` | Her current room, notification settings and room order | `ROOMS_META_KEY` in the same file, `RoomsMeta` in `room_data.rs` |
| `outbound_dms` | Her outbound DMs | `OUTBOUND_DMS_STORAGE_KEY` in [common/src/chat_delegate.rs](https://github.com/freenet/river/blob/78307756805f3e02399791dda142c86b83780b8f/common/src/chat_delegate.rs#L15) |

Include the current delegate's `freenet_migrate::MIGRATION_JOURNAL_KEY`, per-record import markers, `::key_index` and River migration cadence/top-up/short-index metadata in the snapshot inventory. Their exact keys and roles come from the selected [migration adapter](https://github.com/freenet/river/blob/78307756805f3e02399791dda142c86b83780b8f/ui/src/components/app/freenet_api/delegate_migration.rs). Export journal/control records as recovery metadata; the selected driver validates their source/target/route before resuming. Apply the adapter's reserved-key filtering to predecessor user-record imports. Draft/pending indexes from [1.6 Application protocols, data and operations](06-data-and-operations.md#bobs-saved-draft) join this inventory. Test interrupted migration before/after each journal/import marker and exact successor readback, alongside separate V4–V6 invite recovery.

River re-keys its chat delegate roughly weekly. Rebuild entries outside the migration key index on startup:

- `signing_key:` entries. River stores Alice's signing key again from `room:<owner key>` at start, with `signing::migrate_signing_key` in [ui/src/signing.rs](https://github.com/freenet/river/blob/78307756805f3e02399791dda142c86b83780b8f/ui/src/signing.rs).
- `room_sub:`, `room_members:` and `room_secret:` caches. The new delegate fills them again after River sends `EnsureRoomSubscription` for each room Alice owns ([subscription.rs](https://github.com/freenet/river/blob/78307756805f3e02399791dda142c86b83780b8f/delegates/chat-delegate/src/subscription.rs)).

Disclose in the app's privacy notes that secrets pass through application code as plaintext during migration. Backup packaging and restore belong to [1.10 Backup and restore](10-backup-and-restore.md).

Include a predecessor with a corrupt blob in the registry fixtures ([#4909](https://github.com/freenet/freenet-core/issues/4909)). Verify that completion waits for a valid migration and that retries preserve the user's deletions.

### Compatible migration library

Library compatibility and the integrated runner are release requirements for supported upgrades and restores.

Selected integration route: a maintained compatibility adapter around freenet-migrate 0.7 at `d4ff8172a129b4f60bc98426f19cea762e7d8b07`, which declares freenet-stdlib 0.8.2. Core baseline `99612051c535ff7f18ce7c40857ecd236bbbdd46` uses stdlib 0.12.1. River baseline is `78307756805f3e02399791dda142c86b83780b8f`; browser/host interface source baseline is stdlib `7782c176a622efc3f284ce4710b4f184c4986405`.

The AppKit migration integration owner records an exact `migration-dependencies` release manifest: selected mobile Core commit/patch digest, both resolved stdlib package versions/checksums, migration library commit, River adapter commit, compatibility-adapter commit and Cargo.lock digest. The adapter converts key, parameter, request/reply and error types explicitly and preserves canonical wire bytes across both stdlib versions. Verify delegate probes, export/import, CAS/journal writes, unknown/missing/timeout replies and successor readback through River's route and native EVY's Rust runner on iOS and Android. This exact built dependency set and shared vectors are acceptance requirements. A later compatible library release replaces the adapter through the same dependency-manifest and fixture gate.

Sources: [Cargo.toml](https://github.com/freenet/freenet-migrate/blob/d4ff8172a129b4f60bc98426f19cea762e7d8b07/freenet-migrate/Cargo.toml), [stdlib #136](https://github.com/freenet/freenet-stdlib/pull/136) and [stdlib #137](https://github.com/freenet/freenet-stdlib/pull/137).

### Mobile migration interface

Implement one installation lifecycle coordinator in `crates/mobile`, exposed to Swift on iOS and Kotlin on Android. It selects the declared migration route, pauses ordinary work, manages staging and requires verified completion before activation. The host supplies application policy and trusted UI. Before migration, it checks the application and declared delegate namespaces under [Application data inventory in 1.5 Identity, keys and local protection](05-identity.md#application-data-inventory).

| Owner | Responsibility |
| --- | --- |
| SDK lifecycle coordinator | Authorize the route, source/target identities and current migration generation; serialize upgrade, export and restore; retain one active owner; require readback and the driver's durable completion checkpoint before activation |
| River application adapter | Run River's existing freenet-migrate adapter and completeness journal through an authorized migration session. Export, import and verify River records; report completion to the coordinator |
| Native Rust runner | Run freenet-migrate for native EVY through EVY's predecessor registry, walk policy and export/import/verification adapters. Expose progress, resume and verified completion through the SDK |
| Host | Present progress and recovery actions, supply policy decisions and activate the verified release/data generation through the coordinator |

Select one execution route per application migration generation. River's startup enters the coordinator's migration session and resumes its existing journal. Native EVY enters the Rust runner through the same coordinator. The coordinator's activation checkpoint references the selected driver's journal and verified source/target generation.

| Migration path | Permitted execution and activation |
| --- | --- |
| First start after a build upgrade | The coordinator starts the selected driver with ordinary work fenced. Supported-predecessor roles export verified records; the successor imports under the snapshot barrier. Commit the verified checkpoint before opening the fresh host session |
| Backup restore or isolated transform | The coordinator runs the selected route's policy-admitted adapters against encrypted staging. Backup restore scopes its walk and checkpoint to the authenticated source generations and tested path. Fence network effects, verify the complete generation and activate it atomically before normal calls |

Migration-only roles execute inside staging. A transform needed by a live upgrade creates a staging generation and uses the same activation transaction. Interruption retains the complete predecessor and resumes the selected driver's checkpoint.

Before execution, the host authorizes the exact current, supported predecessor and migration-only Wasm and parameter identities. The coordinator:

- Holds ordinary successor calls until the selected driver verifies imported records and commits its completion checkpoint.
- Keeps predecessor records after interruption and resumes the same route on the next start.
- Runs restore adapters inside the [staged restore transaction in 1.10 Backup and restore](10-backup-and-restore.md#staged-restore-transaction).
- Serializes migration with the [export barrier in 1.10 Backup and restore](10-backup-and-restore.md#export), so each snapshot captures one complete generation and a matching checkpoint.

After verification, the selected route performs [Retiring the old version](#retiring-the-old-version) under coordinator authorization.

iOS and Android fixtures cover normal upgrades, skipped supported generations, interruption, failed imports, successor readback and rejected records outside the inventory. Race startup, reconnect, export and restore: one route owns each migration generation, ordinary calls wait for verification and activation selects one complete generation. River fixtures preserve room identities, keys, drafts, exact pending signed messages and the completeness journal. Native EVY fixtures preserve its root seed, addresses, keys and pending operations.

### Core-assisted migration

Evaluate [Core RFC #5255](https://github.com/freenet/freenet-core/issues/5255) after Core implements and tests author-bound delegate provenance and Core-mediated secret transfer to a successor. Adoption tests verify provenance, secret deposit and preservation of application records. River uses [application-driven migration](#delegate-secret-export-and-import).

### Retiring the old version

Reclaim predecessor copies within the installation's measured storage budget and declared supported-predecessor retention in [1.11 Cellular data and resource budgets](11-cellular-data-and-resource-budgets.md#resource-budgets). Test River's 27 delegate generations as the workload ([river#586](https://github.com/freenet/river/issues/586)).

After migration completes, retire each predecessor delegate in this order:

| Step | What the app does |
| --- | --- |
| 1. Verify | Confirms through successor readback that the new delegate holds every entry the migration walk found. |
| 2. Reclaim | Deletes predecessor copies through the predecessor delegate's own delete message. |
| 3. Unregister | Sends `UnregisterDelegate` for the predecessor key to stop its `NodeStarted` runs and wake-ups ([#5747](https://github.com/freenet/freenet-core/pull/5747) review item S8). Core drops the key's record, and its wake-ups stop at the next fire. |

### Pointer records

Publisher tooling uses signed pointer records to locate update candidates and check publication freshness. River's `river.room-contract` and `river.chat-delegate` records identify its components ([pointer-records.toml](https://github.com/freenet/river/blob/78307756805f3e02399791dda142c86b83780b8f/pointer-records.toml)). CI checks retention and increasing versions ([river#677](https://github.com/freenet/river/issues/677)).

An installed mobile build runs exact identities admitted by [1.4 Application bundles](04-bundles.md#execution-policy). Runtime pointer lookup starts when a named River update-discovery flow needs it. That flow verifies publisher signature and version floor, records the candidate, checks build admission and migrates through declared adapters. Discovery never expands execution authority. [freenet-migrate#33](https://github.com/freenet/freenet-migrate/issues/33) and [river#695](https://github.com/freenet/river/issues/695) supply candidate-resolution evidence.

## Acceptance

- Shared fixtures derive identical keys on all supported hosts, including empty parameters and recorded irregular keys. CI requires registry coverage for changed Wasm.
- River's room contract and chat delegate migrations run on iOS and Android and keep Alice's "Skate club" room and keys, including across skipped versions.
- A test migrates from a real predecessor River chat delegate Wasm under Pulley on iOS and Android ([river#630](https://github.com/freenet/river/issues/630)).
- On iOS and Android, a fresh installation containing only the latest app restores each supported predecessor generation from a backup, registers its bundled Wasm and exact parameters, and migrates its secrets to the current delegate. A version 1 to version 4 fixture succeeds with data generations 2 and 3 absent from the authenticated source set. Missing declared records, unsupported paths and substituted source sets block activation and preserve existing data.
- On iOS and Android, the SDK coordinator retains the selected route and durable checkpoint across interruption. River resumes its existing adapter/journal; native EVY resumes the Rust runner with EVY adapters. Concurrent startup, reconnect and recovery requests preserve one migration owner and one complete activation generation. The app shows its migrating state until verification completes.
- After a completed migration on iOS and Android, River has reclaimed the old copies, the old chat delegate key is unregistered, and the old key gets no further wake-ups.
- Drafts and signed messages waiting to be sent survive activation and migration.
- On iOS and Android, export during migration captures one consistent generation and its checkpoint. Restore verifies the authenticated snapshot, runs only policy-admitted predecessor and migration adapters, and preserves identity keys and pending signed bytes. Test skipped versions and a predecessor whose Wasm comes only from the backup.
