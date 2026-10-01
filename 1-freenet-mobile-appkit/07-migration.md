# 1.7 Upgrades and migration

## Repositories

| Repository | Role | Work in this plan |
| --- | --- | --- |
| [river](https://github.com/freenet/river) | Modified | Reclaims old chat delegate copies and unregisters old delegate keys once a migration completes |
| [freenet-migrate](https://github.com/freenet/freenet-migrate) | Used | Registry build, contract and delegate migration, walk policies and pointer resolution |
| [freenet-core](https://github.com/freenet/freenet-core) | Used | Typed `Missing` probe answers ([#5729](https://github.com/freenet/freenet-core/pull/5729)) and `UnregisterDelegate` |

## Purpose

This plan sets the rules apps follow to carry their state and private records across upgrades. It owns component keys, predecessor registries, contract carry-forward, delegate secret migration and retiring old versions.

The [installation interface in 1.4 Application bundles](04-bundles.md#installing-a-copy) verifies a release and [1.3 Single-application host](03-host.md#activating-a-release) activates it. Each app runs its own migrations with freenet-migrate when the new release first starts, and runs them again on the next start if they fail. The latest freenet-migrate release is 0.7.0.

| App | Migration code | freenet-migrate pin |
| --- | --- | --- |
| River | [delegate_migration.rs](https://github.com/freenet/river/blob/main/ui/src/components/app/freenet_api/delegate_migration.rs) | 0.5 |
| Delta | [delegate_migration.rs](https://github.com/freenet/delta/blob/main/ui/src/freenet_api/delegate_migration.rs) | 0.6 |
| Harvest | [migrate.rs](https://github.com/freenet/harvest/blob/main/ui/src/migrate.rs) for contracts, [delegate_migrate.rs](https://github.com/freenet/harvest/blob/main/ui/src/delegate_migrate.rs) for the delegate | 0.6 |
| Atlas | The publisher's CLI, [main.rs](https://github.com/freenet/atlas/blob/main/cli/src/main.rs) and [migration.rs](https://github.com/freenet/atlas/blob/main/cli/src/migration.rs) | 0.6 |

The app keeps the old version's data until the new copy is proven complete, so a failed migration loses nothing. It then retires the old version as in [Retiring the old version](#retiring-the-old-version). While a migration runs, the app shows a migrating state, as River's room list does with `RoomListDisplay::Migrating` ([delta#52](https://github.com/freenet/delta/issues/52), [delta#53](https://github.com/freenet/delta/pull/53)). Data the publisher owns, such as the Atlas index, is migrated by the publisher's CLI before the release is published.

## Component identity and re-keying

A contract or delegate key derives from BLAKE3 over its code hash and exact parameter bytes. A change to those inputs creates a successor identity, while retained state stays under its original identity. Parameter encodings belong to the application and must have shared fixtures.

| River component | Identity inputs |
| --- | --- |
| Room contract | Code hash and `ChatRoomParametersV1 { owner: VerifyingKey }` |
| Chat delegate | Code hash and empty parameters, yielding BLAKE3 of the code hash |
| Website container | Code hash of the pinned container Wasm, which [1.4 Application bundles](04-bundles.md#the-archive-and-its-definition) passes on every publication, and the publisher's verifying-key parameters |

Sources: [River FREENET.md](https://github.com/freenet/river/blob/main/FREENET.md), [publication rules](https://github.com/freenet/river/blob/main/.claude/rules/river-publish.md), and the [whitepaper status](https://github.com/freenet/paper-1/blob/main/sections/07-status.tex). [Core upgrade issue #2776](https://github.com/freenet/freenet-core/issues/2776) is related protocol evidence. freenet-migrate provides the explicit application migration adapters. The dapp-builder skill's [upgrade and migration guide](https://github.com/freenet/freenet-agent-skills/blob/main/skills/dapp-builder/references/upgrade-and-migration.md) gives app authors the same rules.

### Predecessor registry

A new Wasm build gives a component a new key. When River ships a new room contract, Alice's "Skate club" room gets a new key, and its state stays under the old key. The predecessor registry lists every earlier version of a component. The app's new release uses it to work out the old keys and find that state.

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

Two kinds of entry need their own handling:

- In a row marked `irregular_key = true`, the key doesn't match BLAKE3 of the code hash. The app probes the recorded `delegate_key`. River's V1 chat delegate is the only such row.
- River's delegate registry has no V4 to V6 rows, because messages from those delegates don't deserialize in the current runtime ([river#204](https://github.com/freenet/river/issues/204)). Users whose data sits only under those keys rejoin their rooms by invite. Registry fixtures include this gap.

#### Walk policies

Each app names the policy its migration walk uses. Under the default policies, a predecessor that doesn't answer stops the walk.

| Policy | Part | What the walk does | Trade-off | Used by |
| --- | --- | --- | --- | --- |
| `NewestSnapshotWins` (default) | Delegate secrets | Takes the newest generation that answers and stops at the first one that stays silent | Protects against rollback. Generations behind a silent one stay stranded | None |
| `NewestSnapshotWinsContinuePastUnresponsive(RollbackRiskAck)` (0.7.0) | Delegate secrets | Walks past a silent generation | Gives up rollback protection | None |
| `UnionAllGenerations` | Delegate secrets | Merges every generation that answers | Can bring back secrets that were deleted by leaving them out. River limits this with ranked tombstones ([river#590](https://github.com/freenet/river/issues/590)) | River, Delta, Harvest |
| `NewestFirstWins` (default) | Contract state | Takes the newest real state and stops at an unknown newer generation, unless the app passes `RollbackRiskAck` to `continue_past_unknown` | Protects against rollback | River's room contract |
| `FoldAll` | Contract state | Merges every real generation | Can bring back data that was deleted by leaving it out | Atlas index, Harvest |

### Delegate secret export and import

Apps move delegate secrets with freenet-migrate's `migrate_delegate_secrets`, as River, Delta and Harvest do. It reads each old delegate through the app's own messages, writes through the new delegate's own handler, and marks each old key done. Core's own copy-forward of delegate secrets stays disabled ([#4908](https://github.com/freenet/freenet-core/pull/4908), [#5199](https://github.com/freenet/freenet-core/pull/5199)), so this app-side call is the only path.

For River the call moves the entries in the chat delegate's key index:

| Entry | What it holds for Alice | Defined in |
| --- | --- | --- |
| `room:<owner key>` | One room's state, her signing key (`self_sk`), her member records and her nickname. River rebuilds the room secrets from the room state with her key | `ROOM_KEY_PREFIX` in [ui/src/components/app/chat_delegate.rs](https://github.com/freenet/river/blob/main/ui/src/components/app/chat_delegate.rs), `RoomSlot` in [ui/src/room_data.rs](https://github.com/freenet/river/blob/main/ui/src/room_data.rs) |
| `rooms_meta` | Her current room, notification settings and room order | `ROOMS_META_KEY` in the same file, `RoomsMeta` in `room_data.rs` |
| `outbound_dms` | Her outbound DMs | `OUTBOUND_DMS_STORAGE_KEY` in [common/src/chat_delegate.rs](https://github.com/freenet/river/blob/main/common/src/chat_delegate.rs#L15) |

River re-keys its chat delegate roughly weekly. The chat delegate also holds entries outside the key index, and the migration doesn't move them:

- `signing_key:` entries. River stores Alice's signing key again from `room:<owner key>` at start, with `signing::migrate_signing_key` in [ui/src/signing.rs](https://github.com/freenet/river/blob/main/ui/src/signing.rs).
- `room_sub:`, `room_members:` and `room_secret:` caches. The new delegate fills them again after River sends `EnsureRoomSubscription` for each room Alice owns ([subscription.rs](https://github.com/freenet/river/blob/main/delegates/chat-delegate/src/subscription.rs)).

Secrets pass through the app in plain text during the move, so the app's privacy notes say so. Same-key backup and restore belongs to [1.5 Identity, keys and local protection](05-identity.md).

We track [#4909](https://github.com/freenet/freenet-core/issues/4909). When a predecessor holds a corrupt blob, the pair never seals, so each start copies again and brings back secrets the user deleted. Registry fixtures include a predecessor with a corrupt blob.

### Retiring the old version

River copies every room into each of its 27 delegate generations. A hosted node counts a user's secrets across every delegate that holds them, and one user's copies filled the 4 MiB per-user quota ([river#586](https://github.com/freenet/river/issues/586)). Each old delegate also stays registered, so it keeps getting `NodeStarted` runs and wake-ups ([#5747](https://github.com/freenet/freenet-core/pull/5747) review item S8).

Once a migration completes, the app retires each old delegate version in this order:

| Step | What the app does |
| --- | --- |
| 1. Prove | Confirms that the new delegate holds every entry the walk found. River's reclaim design is in [river#586](https://github.com/freenet/river/issues/586). |
| 2. Reclaim | Deletes the old copies through the old delegate's own delete message. |
| 3. Unregister | Sends `UnregisterDelegate` for the old key. Core drops the old key's record, and its wake-ups stop at the next fire. |

### Pointer records

A pointer record lets other apps find a component's current code hash after its key changes. It is a contract at a fixed address, signed by the publisher ([#5194](https://github.com/freenet/freenet-core/issues/5194), built in [freenet-migrate#9](https://github.com/freenet/freenet-migrate/pull/9)). River publishes `river.room-contract` and `river.chat-delegate` and re-signs them whenever either component changes key ([pointer-records.toml](https://github.com/freenet/river/blob/main/pointer-records.toml)). River's CI runs `check-pointer-freshness`. Its checks that no record vanishes and that versions only rise don't run in `--ci` mode ([river#677](https://github.com/freenet/river/issues/677)).

An app that uses River's chat delegate resolves `river.chat-delegate` with `resolve_app_pointer` and saves the returned floor, so an older record can't roll the key back. Only the `NeverPublished` outcome lets the app use a key built into its code ([freenet-migrate#33](https://github.com/freenet/freenet-migrate/issues/33)). A pointer only finds code ([river#695](https://github.com/freenet/river/issues/695)). Data under the old key still moves through the app's own migration.

## Acceptance

- Shared fixtures derive identical keys on all supported hosts, including empty parameters and recorded irregular keys. CI requires registry coverage for changed Wasm.
- River's room contract and chat delegate migrations run on iOS and Android and keep Alice's "Skate club" room and keys, including across skipped versions.
- A test migrates from a real old River chat delegate Wasm under Pulley on iOS and Android ([river#630](https://github.com/freenet/river/issues/630)).
- An interrupted or failed migration keeps the predecessor's data, and the next start runs it again. The app shows its migrating state while the migration runs.
- After a completed migration on iOS and Android, River has reclaimed the old copies, the old chat delegate key is unregistered, and the old key gets no further wake-ups.
- Drafts and signed messages waiting to be sent survive activation and migration.
