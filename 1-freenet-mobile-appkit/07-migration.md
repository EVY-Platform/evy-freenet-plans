# 1.7 Upgrades and migration

## Repositories

| Repository | Role | Work in this plan |
| --- | --- | --- |
| [freenet-migrate](https://github.com/freenet/freenet-migrate) | Used | Registry build, contract and delegate migration and pointer resolution |
| [freenet-core](https://github.com/freenet/freenet-core) | Used | Upgrade issue [#2776](https://github.com/freenet/freenet-core/issues/2776) and pointer records [#5194](https://github.com/freenet/freenet-core/issues/5194) as evidence |

## Purpose

This plan sets the rules apps follow to carry their state and private records across upgrades. It owns component keys, predecessor registries, contract carry-forward and delegate secret migration.

The [installation interface in 1.4 Application bundles](04-bundles.md#installing-a-copy) verifies a release and [1.3 Single-application host](03-host.md#activating-a-release) activates it. Each app runs its own migrations with freenet-migrate when the new release first starts, and runs them again on the next start if they fail, as [River](https://github.com/freenet/river/blob/main/ui/src/components/app/freenet_api/delegate_migration.rs), [Delta](https://github.com/freenet/delta/blob/main/ui/src/freenet_api/delegate_migration.rs) and [Harvest](https://github.com/freenet/harvest/blob/main/ui/src/migrate.rs) do. The old version's data is never deleted, so a failed migration loses nothing. Data the publisher owns, such as the Atlas index, is migrated by the [publisher's CLI](https://github.com/freenet/atlas/blob/main/cli/src/main.rs) before the release is published.

## Component identity and re-keying

A contract or delegate key derives from BLAKE3 over its code hash and exact parameter bytes. A change to those inputs creates a successor identity, while retained state stays under its original identity. Parameter encodings belong to the application and must have shared fixtures.

| River component | Identity inputs |
| --- | --- |
| Room contract | Code hash and `ChatRoomParametersV1 { owner: VerifyingKey }` |
| Chat delegate | Code hash and empty parameters, yielding BLAKE3 of the code hash |
| Website container | Container code hash and the publisher's verifying-key parameters |

Sources: [River FREENET.md](https://github.com/freenet/river/blob/main/FREENET.md), [publication rules](https://github.com/freenet/river/blob/main/.claude/rules/river-publish.md), and the [whitepaper status](https://github.com/freenet/paper-1/blob/main/sections/07-status.tex). [Core upgrade issue #2776](https://github.com/freenet/freenet-core/issues/2776) is related protocol evidence. freenet-migrate provides the explicit application migration adapters.

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
| 2. Check | CI | Fail the build when a component's Wasm changes without a new entry, or when `freenet_migrate_build::codegen()` generates an empty table. River's [delegate migration rules](https://github.com/freenet/river/blob/main/.claude/rules/delegate-migration.md) run both checks. |
| 3. Probe | App | When the new release [first starts](#purpose), work out each old key from the entry's code hash and the room's exact parameter bytes, then probe newest first. For "Skate club" the parameters are `ChatRoomParametersV1 { owner }` with Alice's verifying key. Keep those bytes unchanged, because re-encoded parameters produce a different key. |
| 4. Carry forward | App | Move the state the probe finds into the new contract. freenet-migrate's `migrate_contract` runs steps 3 and 4, as Harvest and Atlas do. The app's merge rules decide whether the new contract gets the newest copy or all copies merged. Delegate secrets move as in [Delegate secret export and import](#delegate-secret-export-and-import). |

Two kinds of entry need their own handling:

- In a row marked `irregular_key = true`, the key doesn't match BLAKE3 of the code hash. The app probes the recorded `delegate_key`. River's V1 chat delegate is the only such row.
- River's delegate registry has no V4 to V6 rows, because messages from those delegates no longer deserialize in the current runtime ([river#204](https://github.com/freenet/river/issues/204)). Users whose data sits only under those keys rejoin their rooms by invite. Registry fixtures include this gap. The probe skips any version that fails to deserialize and moves on to the next one.

### Delegate secret export and import

Apps move delegate secrets with freenet-migrate's `migrate_delegate_secrets`, as River and Delta do. It reads each old delegate through the app's own messages, writes through the new delegate's own handler, and marks each old key done. The old delegate's data stays in place. For River this moves the [chat delegate's](https://github.com/freenet/river/blob/main/delegates/chat-delegate/README.md) per-room `room:<owner key>` entries, which hold Alice's room and signing keys and private room secrets, `rooms_meta`, which holds her room order and notification settings, and `outbound_dms`, which holds her outbound DMs.

Secrets pass through the app in plain text during the move, so the app's privacy notes say so. Same-key backup and restore belongs to [1.5 Identity, keys and local protection](05-identity.md).

### Pointer records

A pointer record lets other apps find a component's current code hash after its key changes. It is a contract at a fixed address, signed by the publisher ([#5194](https://github.com/freenet/freenet-core/issues/5194)). River publishes `river.room-contract` and `river.chat-delegate`, re-signs them whenever either component changes key, and checks in CI that they are current ([pointer-records.toml](https://github.com/freenet/river/blob/main/pointer-records.toml)).

An app that uses River's chat delegate resolves `river.chat-delegate` with `resolve_app_pointer` and saves the returned floor, so an older record can't roll the key back. Only the `NeverPublished` outcome lets the app use a key built into its code. A pointer only finds code. Data under the old key still moves through the app's own migration.

## Acceptance

- Shared fixtures derive identical keys on all supported hosts, including empty parameters and recorded irregular keys. CI requires registry coverage for changed Wasm.
- River's room contract and chat delegate migrations run on iOS and Android and keep Alice's "Skate club" room and keys, including across skipped versions.
- An interrupted or failed migration keeps the predecessor's data, and the next start runs it again.
- Drafts and signed messages waiting to be sent survive activation and migration.
