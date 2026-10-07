# 1.7 Upgrades and migration

## Repositories

| Repository | Role | Work in this plan |
| --- | --- | --- |
| [river](https://github.com/freenet/river) | Modified | Delegate cleanup after migration |
| [freenet-migrate](https://github.com/freenet/freenet-migrate) | Used | Contract and delegate migration |
| [freenet-core](https://github.com/freenet/freenet-core) | Modified | Migration probes, delegate removal and the mobile migration interface |

## Purpose

Carry application state and private records across upgrades. Define component keys, record supported predecessors, migrate contract state and delegate secrets, and retire predecessor versions after verification.

The [installation interface in 1.4 Application bundles](04-bundles.md#installing-a-copy) verifies a release and [1.3 Single-application host](03-host.md#activating-a-release) activates it. Each app runs its own migrations with freenet-migrate when the new release first starts, and runs them again on the next start if they fail. The latest freenet-migrate release is 0.7.0.

| App | Migration code | freenet-migrate pin |
| --- | --- | --- |
| River | [delegate_migration.rs](https://github.com/freenet/river/blob/main/ui/src/components/app/freenet_api/delegate_migration.rs) | 0.5 |
| Delta | [delegate_migration.rs](https://github.com/freenet/delta/blob/main/ui/src/freenet_api/delegate_migration.rs) | 0.6 |
| Harvest | [migrate.rs](https://github.com/freenet/harvest/blob/main/ui/src/migrate.rs) for contracts, [delegate_migrate.rs](https://github.com/freenet/harvest/blob/main/ui/src/delegate_migrate.rs) for the delegate | 0.6 |
| Atlas | The publisher's CLI, [main.rs](https://github.com/freenet/atlas/blob/main/cli/src/main.rs) and [migration.rs](https://github.com/freenet/atlas/blob/main/cli/src/migration.rs) | 0.6 |

Keep predecessor data until successor readback proves the migration complete. It then retires the old version as in [Retiring the old version](#retiring-the-old-version). While a migration runs, the app shows a migrating state, as River's room list does with `RoomListDisplay::Migrating` ([delta#52](https://github.com/freenet/delta/issues/52), [delta#53](https://github.com/freenet/delta/pull/53)). The publisher's CLI migrates publisher-owned data, such as the Atlas index, before publishing the release.

## Component identity and re-keying

A contract or delegate key derives from BLAKE3 over its code hash and exact parameter bytes. A change to those inputs creates a successor identity, while retained state stays under its original identity. Parameter encodings belong to the application and must have shared fixtures.

| River component | Identity inputs |
| --- | --- |
| Room contract | Code hash and `ChatRoomParametersV1 { owner: VerifyingKey }` |
| Chat delegate | Code hash and empty parameters, yielding BLAKE3 of the code hash |
| Website container | Code hash of the pinned container Wasm, which [1.4 Application bundles](04-bundles.md#the-archive-and-its-definition) passes on every publication, and the publisher's verifying-key parameters |

Sources: [River FREENET.md](https://github.com/freenet/river/blob/main/FREENET.md), [publication rules](https://github.com/freenet/river/blob/main/.claude/rules/river-publish.md), and the [whitepaper status](https://github.com/freenet/paper-1/blob/main/sections/07-status.tex). [Core upgrade issue #2776](https://github.com/freenet/freenet-core/issues/2776) is related protocol evidence. freenet-migrate provides the explicit application migration adapters. The dapp-builder skill's [upgrade and migration guide](https://github.com/freenet/freenet-agent-skills/blob/main/skills/dapp-builder/references/upgrade-and-migration.md) gives app authors the same rules.

### Predecessor registry

A new Wasm build gives a component a new key. When River ships a new room contract, Alice's "Skate club" room gets a new key, and its state stays under the old key. The predecessor registry lists earlier component versions. The new release derives their keys and locates their state.

River keeps one registry per component. Each is a TOML file, oldest version first. The current key comes from the Wasm in the bundle, so the registry lists only earlier versions.

| Registry | Component | Fields per entry |
| --- | --- | --- |
| [common/legacy_room_contracts.toml](https://github.com/freenet/river/blob/main/common/legacy_room_contracts.toml) | Room contract | `version`, `description`, `date`, `code_hash` |
| [legacy_delegates.toml](https://github.com/freenet/river/blob/main/legacy_delegates.toml) | Chat delegate | The same, plus `delegate_key` and `irregular_key` |

| Step | Who | Rule |
| --- | --- | --- |
| 1. Record | Developer | Add the old version to the registry before rebuilding the Wasm. River runs `cargo make add-migration` for the delegate and `cargo make add-room-contract-migration` for the room contract. |
| 2. Check | CI | Fail the build when a component's Wasm changes without a new entry, or when `freenet_migrate_build::codegen()` generates an empty table. River's [delegate migration rules](https://github.com/freenet/river/blob/main/.claude/rules/delegate-migration.md) run both checks. The empty-table check catches a misnamed TOML table, which freenet-migrate reads as an empty registry ([freenet-migrate#20](https://github.com/freenet/freenet-migrate/issues/20)). |
| 3. Probe | App | When the new release [first starts](#purpose), work out each old key from the entry's code hash and the room's exact parameter bytes, then probe newest first. For "Skate club" the parameters are `ChatRoomParametersV1 { owner }` with Alice's verifying key. Keep those bytes unchanged, because re-encoded parameters produce a different key. Core answers a probe of an unregistered delegate key with a typed `DelegateError::Missing` ([#5729](https://github.com/freenet/freenet-core/pull/5729)), so the app can tell "not registered" apart from "no answer". |
| 4. Carry forward | App | Move the state the probe finds into the new contract. freenet-migrate's `migrate_contract` runs steps 3 and 4, as Atlas's CLI does. Harvest runs the same steps through freenet-migrate's `ProbeDriver`. The app's [walk policy](#walk-policies) decides whether the new contract gets the newest copy or all copies merged. Delegate secrets move as in [Delegate secret export and import](#delegate-secret-export-and-import). |

Handle these registry cases:

- For `irregular_key = true`, probe the recorded `delegate_key` in place of the BLAKE3-derived key. River's V1 chat delegate uses this entry.
- Users with data only in River delegate versions V4 to V6 rejoin their rooms by invite. The registry covers versions whose messages the current runtime can deserialize ([river#204](https://github.com/freenet/river/issues/204)). Include V4 to V6 recovery in the registry fixtures.

#### Walk policies

Declare each app's migration walk policy. The default policies stop at an unresponsive predecessor.

| Policy | Part | What the walk does | Trade-off | Used by |
| --- | --- | --- | --- | --- |
| `NewestSnapshotWins` (default) | Delegate secrets | Takes the newest generation that answers and stops at the first one that stays silent | Protects against rollback. Generations behind a silent one stay stranded | EVY |
| `NewestSnapshotWinsContinuePastUnresponsive(RollbackRiskAck)` (0.7.0) | Delegate secrets | Walks past a silent generation | Gives up rollback protection | None |
| `UnionAllGenerations` | Delegate secrets | Merges every generation that answers | Can bring back secrets that were deleted by leaving them out. River limits this with ranked tombstones ([river#590](https://github.com/freenet/river/issues/590)) | River, Delta, Harvest |
| `NewestFirstWins` (default) | Contract state | Takes the newest real state and stops at an unknown newer generation, unless the app passes `RollbackRiskAck` to `continue_past_unknown` | Protects against rollback | River's room contract |
| `FoldAll` | Contract state | Merges every real generation | Can bring back data that was deleted by leaving it out | Atlas index, Harvest |

### Delegate secret export and import

Move delegate secrets with freenet-migrate's `migrate_delegate_secrets`, as River, Delta and Harvest do. Read through each predecessor's messages and write through the successor's handler. Mark the pair complete after verification. EVY uses its `ExportRecords` and `ImportRecords` adapters through the proposed Swift and Kotlin interface in [C13 in Upstream issues](../UPSTREAM_ISSUES.md#c13-expose-application-driven-delegate-migration-to-mobile-hosts). The SDK builds against the compatible Core, stdlib and freenet-migrate dependency set required by [M1 in Upstream issues](../UPSTREAM_ISSUES.md#m1-release-freenet-migrate-on-the-freenet-stdlib-that-core-pins).

Core-assisted migration is a future improvement tracked under [RFC #5255 in Upstream issues](../UPSTREAM_ISSUES.md#future-core-migration-work). Adoption will include tests for delegate provenance, secret transfer and preservation of the app's records.

For a backup restore on a fresh iOS or Android installation, Core first installs and registers the predecessor Wasm and exact parameters from the authenticated backup in a staging store, as [1.5 Identity, keys and local protection](05-identity.md#restore) requires under [#4035](https://github.com/freenet/freenet-core/issues/4035). The app validates support for that generation before restore writes, then runs the migration through the registered predecessor's own messages in staging. Successor readback completes before the [staged restore transaction in 1.5 Identity, keys and local protection](05-identity.md#staged-restore-transaction) activates the restored generation. CI fixtures cover every generation the release supports for backup restore, including skipped releases.

For River the call moves the entries in the chat delegate's key index:

| Entry | What it holds for Alice | Defined in |
| --- | --- | --- |
| `room:<owner key>` | One room's state, her signing key (`self_sk`), her member records and her nickname. River rebuilds the room secrets from the room state with her key | `ROOM_KEY_PREFIX` in [ui/src/components/app/chat_delegate.rs](https://github.com/freenet/river/blob/main/ui/src/components/app/chat_delegate.rs), `RoomSlot` in [ui/src/room_data.rs](https://github.com/freenet/river/blob/main/ui/src/room_data.rs) |
| `rooms_meta` | Her current room, notification settings and room order | `ROOMS_META_KEY` in the same file, `RoomsMeta` in `room_data.rs` |
| `outbound_dms` | Her outbound DMs | `OUTBOUND_DMS_STORAGE_KEY` in [common/src/chat_delegate.rs](https://github.com/freenet/river/blob/main/common/src/chat_delegate.rs#L15) |

River re-keys its chat delegate roughly weekly. Rebuild entries outside the migration key index on startup:

- `signing_key:` entries. River stores Alice's signing key again from `room:<owner key>` at start, with `signing::migrate_signing_key` in [ui/src/signing.rs](https://github.com/freenet/river/blob/main/ui/src/signing.rs).
- `room_sub:`, `room_members:` and `room_secret:` caches. The new delegate fills them again after River sends `EnsureRoomSubscription` for each room Alice owns ([subscription.rs](https://github.com/freenet/river/blob/main/delegates/chat-delegate/src/subscription.rs)).

Disclose in the app's privacy notes that secrets pass through application code as plaintext during migration. Backup packaging and restore belong to [1.5 Identity, keys and local protection](05-identity.md).

Include a predecessor with a corrupt blob in the registry fixtures ([#4909](https://github.com/freenet/freenet-core/issues/4909)). Verify that completion waits for a valid migration and that retries preserve the user's deletions.

### Retiring the old version

Reclaim predecessor copies to stay within the hosted node's 4 MiB per-user quota. Test River's 27 delegate generations as the workload ([river#586](https://github.com/freenet/river/issues/586)). Unregister each retired delegate to stop its `NodeStarted` runs and wake-ups ([#5747](https://github.com/freenet/freenet-core/pull/5747) review item S8).

Once a migration completes, the app retires each old delegate version in this order:

| Step | What the app does |
| --- | --- |
| 1. Prove | Confirms that the new delegate holds every entry the walk found. River's reclaim design is in [river#586](https://github.com/freenet/river/issues/586). |
| 2. Reclaim | Deletes the old copies through the old delegate's own delete message. |
| 3. Unregister | Sends `UnregisterDelegate` for the old key. Core drops the old key's record, and its wake-ups stop at the next fire. |

### Pointer records

A pointer record lets other apps find a component's current code hash after its key changes. It is a contract at a fixed address, signed by the publisher ([#5194](https://github.com/freenet/freenet-core/issues/5194), built in [freenet-migrate#9](https://github.com/freenet/freenet-migrate/pull/9)). River publishes `river.room-contract` and `river.chat-delegate` and re-signs them whenever either component changes key ([pointer-records.toml](https://github.com/freenet/river/blob/main/pointer-records.toml)). Run `check-pointer-freshness` in CI and enforce both record retention and increasing versions in `--ci` mode ([river#677](https://github.com/freenet/river/issues/677)).

Resolve `river.chat-delegate` with `resolve_app_pointer` and save the returned version floor to reject rollback. Only the `NeverPublished` outcome lets the app use a key built into its code ([freenet-migrate#33](https://github.com/freenet/freenet-migrate/issues/33)). Use the pointer to find code ([river#695](https://github.com/freenet/river/issues/695)). Migrate data under the predecessor key through the app's own adapters.

## Acceptance

- Shared fixtures derive identical keys on all supported hosts, including empty parameters and recorded irregular keys. CI requires registry coverage for changed Wasm.
- River's room contract and chat delegate migrations run on iOS and Android and keep Alice's "Skate club" room and keys, including across skipped versions.
- A test migrates from a real predecessor River chat delegate Wasm under Pulley on iOS and Android ([river#630](https://github.com/freenet/river/issues/630)).
- On iOS and Android, a fresh installation containing only the latest app restores each supported predecessor generation from a backup, registers its bundled Wasm and exact parameters, and migrates its secrets to the current delegate.
- An interrupted or failed migration keeps the predecessor's data, and the next start runs it again. The app shows its migrating state while the migration runs.
- After a completed migration on iOS and Android, River has reclaimed the old copies, the old chat delegate key is unregistered, and the old key gets no further wake-ups.
- Drafts and signed messages waiting to be sent survive activation and migration.
