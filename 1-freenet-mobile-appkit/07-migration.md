# 1.7 Upgrades and migration

## Repositories

| Repository | Role | Work in this plan |
| --- | --- | --- |
| `freenet-appkit` | Modified | Component key derivation, predecessor registry checks, contract carry-forward, delegate export and import coordination and transfer statements |
| [freenet-migrate](https://github.com/freenet/freenet-migrate) | Used | `freenet-migrate-build`, probe drivers, carry-forward policies, delegate secret migration and pointer resolution |
| [river](https://github.com/freenet/river) | Used | Legacy contract and delegate registries, pointer records, delegate migration rules and FREENET.md as fixtures |
| [freenet-core](https://github.com/freenet/freenet-core) | Used | Upgrade issue #2776, pointer records #5194, FNSX interfaces #4035 and #4592, RFC #5255 and PR #5199 as evidence |
| [paper-1](https://github.com/freenet/paper-1) | Used | Status section on the upgrade protocol |

## Purpose

This plan carries application state, private records and publisher authority across supported upgrades. It owns component keys, predecessor registries, contract carry-forward, delegate secret migration and publisher transfer.

## Prerequisites

- Compatible SDK and `freenet-migrate` versions from [1.1 Mobile feasibility and supported profiles](01-feasibility.md) and [1.2 Embedded node and mobile SDK](02-sdk.md)
- [1.4 Application bundles](04-bundles.md)
- [1.5 Identity, keys and local protection](05-identity.md)
- [1.6 Application protocols, data and operations](06-data-and-operations.md)

Mobile upgrade tests run under the required [thin-peer and cellular gate in 1.10 Thin-peer role and cellular data budgets](10-thin-peer.md).

The [single-app installation interface in 1.3 Single-application host](03-host.md#single-app-installation-interface) supplies release activation and host database staging for milestone 1 (Freenet mobile AppKit). [2.3 Installation and updates](../2-evy-mobile-app/03-installation-and-updates.md) composes that shared interface per app. Application code supplies concrete codecs and migration adapters. Optional screen and reader compatibility belongs to [4.9 SDUI migration and conformance](../4-sdui/09-migration-and-conformance.md).

Source links below preserve this plan's implementation evidence. Release validation must confirm behavior and compatibility against pinned revisions, including the migration library's published and unreleased interfaces.

## Component identity and re-keying

A contract or delegate key derives from BLAKE3 over its code hash and exact parameter bytes. A change to those inputs creates a successor identity, while retained state stays under its original identity. Parameter encodings belong to the application and must have shared fixtures.

| River component | Identity inputs |
| --- | --- |
| Room contract | Code hash and `ChatRoomParametersV1 { owner: VerifyingKey }` |
| Chat delegate | Code hash and empty parameters, yielding BLAKE3 of the code hash |
| Website container | Container code hash and the publisher's verifying-key parameters |

Sources: [River FREENET.md](https://github.com/freenet/river/blob/main/FREENET.md), [publication rules](https://github.com/freenet/river/blob/main/.claude/rules/river-publish.md), and the [whitepaper status](https://github.com/freenet/paper-1/blob/main/sections/07-status.tex). [Core upgrade issue #2776](https://github.com/freenet/freenet-core/issues/2776) is related protocol evidence. AppKit uses explicit application migration adapters.

### Predecessor registry

Record original code hashes, exact parameter encodings, protocol versions and actual instance references. Require a predecessor entry in CI whenever supported component code changes. Preserve parameter bytes through migration.

River runs `freenet_migrate_build::codegen()` over these registries, as described in its [delegate migration rules](https://github.com/freenet/river/blob/main/.claude/rules/delegate-migration.md). The recorded build checks reject an empty generated table and changed Wasm without a registry entry.

| Registry | Recorded fields |
| --- | --- |
| [common/legacy_room_contracts.toml](https://github.com/freenet/river/blob/main/common/legacy_room_contracts.toml) | `version`, `description`, `date`, `code_hash`, oldest first |
| [legacy_delegates.toml](https://github.com/freenet/river/blob/main/legacy_delegates.toml) | `version`, `description`, `date`, `code_hash`, `delegate_key`, and `irregular_key = true` on V1 |

For an irregular row, probe its recorded `delegate_key`. For River V1 this recorded key is the usable identity. Registry fixtures also cover gaps such as River's V4-V6 delegate artifacts, whose deserialization failures limit the supported predecessor set. Probe the retained supported rows and report uncovered generations.

Resolve a verified code hash with the actual parameters and retain the resolver's minimum accepted version. Handle stale, unavailable, conflicting and withdrawn pointer results. A pointer locates code. An application adapter recovers data.

## Contract carry-forward

The [migration library](https://github.com/freenet/freenet-migrate) supplies these integration points in the source evidence:

| Interface | Responsibility |
| --- | --- |
| `freenet-migrate-build` | Generate lineage tables from the application's TOML registry |
| `predecessor_ids`, `ProbeDriver`, `migrate_contract` | Derive and probe predecessor IDs newest first under a `SelectionPolicy` |
| `CarryForward`, `policy_check` | Run `verify()` after `merge()` and test commutative, idempotent and order-invariant merges |
| `resolve_app_pointer` | Resolve the pointer contract described in [#5194](https://github.com/freenet/freenet-core/issues/5194) |

Application adapters implement probe I/O, domain codecs, validation and recovery policy. The host coordinates authorized reads, imports, publication and readback. Custom application code can link the library directly, as River does. SDK feasibility pins compatible adapters and dependencies.

| Policy | Domain use | Proof |
| --- | --- | --- |
| Newest generation | A snapshot such as current room state | Successor validation accepts the recovered state |
| Combined generations | Histories containing edits, deletions, bans and conflicts | `policy_check` passes against the real domain model |

Retain unresolved predecessor reads for retry. Validate recovered state under the successor's rules, publish through authorized operations, and read it back before recording success. Mixed-version participants follow the application's transition rules. Shared-state migration has its own journal, separate from host database staging and archive activation.

## Delegate secret export and import

The full delegate code-and-parameter identity is the secret-store boundary. A successor key starts its own namespace. The baseline upgrade path is an application-controlled export from the predecessor and import into the successor under explicit user approval.

`migrate_delegate_secrets` and `register_delegate_with_migration` use `PredecessorSecretsIo`, `SuccessorSecretsIo` and `MigrationAuthorization`, with a migrated marker to guard against resurrection. Application-owned adapters implement those interfaces. River's startup sweep of its registry is a concrete source fixture in [FREENET.md](https://github.com/freenet/river/blob/main/FREENET.md).

Every AppKit delegate that retains user material must support the authorized export/import path for its supported upgrades. Coverage includes keys, drafts and private records. River's [chat delegate](https://github.com/freenet/river/blob/main/delegates/chat-delegate/README.md) holds `rooms_data` with room and signing keys, private room secrets and outbound DM plaintext.

1. Verify the successor release, namespaces, supported protocols and migration coverage. Obtain the user's approval for that exact move.
2. Journal predecessor, successor, namespace, approving user and migration revision.
3. Export through the predecessor's application protocol. Validate records with the application's adapter.
4. Import into the authorized successor, read back and validate completeness.
5. Record completion before retiring the predecessor. Retain a recoverable copy until the verified result and retention policy permit deletion.

Plaintext secrets transit the application during this round trip. State that exposure in the application's privacy documentation. Resume interrupted imports idempotently and retain original encoding information so later releases can find earlier records.

| Interface or proposal | Boundary to verify |
| --- | --- |
| Same-key backup through Core's FNSX | [1.5 Identity, keys and local protection](05-identity.md) owns package limits, cryptography and recovery coverage. Restore to the same full delegate key |
| Delegate-specific CLI export/import | [#4035](https://github.com/freenet/freenet-core/issues/4035) records interface work to check in the selected Core build |
| Live import into the user's peer | [#4592](https://github.com/freenet/freenet-core/issues/4592) records the required import path |
| Core-mediated provenance, deposit and merge | [RFC #5255](https://github.com/freenet/freenet-core/issues/5255) proposes signed delegate containers and install-from-container behavior. Adoption requires separate authorization and import tests |
| Successor secret-store isolation | [PR #5199](https://github.com/freenet/freenet-core/pull/5199) and the stdlib 0.9.0 API change are regression evidence. Tests permit cross-key movement only through an explicitly approved migration path |

Protected operations in the first public application require this upgrade gate. Test malicious successors, copied parameters, caller-selected namespaces, replayed approvals, concurrent migrations and incomplete export coverage.

## Publisher continuity

Routine web updates retain container validator code and publisher parameters. Changing either creates a successor container. [1.4 Application bundles](04-bundles.md#publishing-and-evidence) owns the signed archive format and publication references.

The initial profile uses the stock website container and its single publisher verifying key. It accepts strictly higher versions and replaces the whole state. Publisher recovery therefore uses tested backups of that signing key. A validator with recovery-key parameters would be a separately reviewed successor identity.

| Container property | Transfer rule |
| --- | --- |
| Whole-state replacement | Every later predecessor publication carries its transfer statement |
| Strict version ordering | Verify the highest signed predecessor state the host has observed |
| Two signed digests at one version | Retain both as compromise evidence and suspend automatic transfer pending a signed resolution |

The AppKit transfer convention uses matching statements authenticated by both containers' normal signatures:

1. Publish and verify the successor container.
2. Publish a higher predecessor version with full predecessor and successor identities, a unique transfer ID and its purpose.
3. Publish the successor's acknowledgement of those exact fields. Bundle metadata carries each statement.
4. Verify and retain both snapshots. Obtain user approval before running the successor or moving private data and grants.
5. Journal the local migration, apply the delegate export/import rules, verify the result and retain recovery evidence. Expanded scopes require fresh host grants.

After same-version divergence, a higher signed predecessor version names the competing digests and selected successor. The host can then resume transfer verification. Keep references to the user's current container and data throughout the process. Compatibility and consent remain activation gates.

### River pointer fixture

River's source records use `river.room-contract` and `river.chat-delegate` under publisher anchor `river:v1:vk:9Ebskq4y7NvJpTQTrF1FAxU8g6bR4Rhe4TRikXba55EJ`. The publisher re-signs them on each component re-key, and CI checks freshness in [pointer-records.toml](https://github.com/freenet/river/blob/main/pointer-records.toml) and [FREENET.md](https://github.com/freenet/river/blob/main/FREENET.md). Rotating the author key moves the container and both pointer addresses. Test all three references together.

[Milestone 3 (Attribution, remuneration and payment)](../README.md#3-attribution-remuneration-and-payment) separately approves product-to-container mappings. Existing contribution and funded-operation evidence keeps its original content references through a transfer.

## Reference definitions

| Term owned here | Meaning |
| --- | --- |
| Component key | Code hash plus exact parameter bytes under the component key derivation |
| Predecessor entry | Recorded earlier identity, parameter encoding and supported protocol |
| Recovery policy | Application rules for carrying state across generations |
| Migration record | One approved move between component namespaces |
| Transfer statement | Publisher-authenticated offer to move to a successor container |

## Acceptance

- Shared fixtures derive identical keys on all supported hosts, including empty parameters and recorded irregular keys. CI requires registry coverage for changed Wasm.
- Contract migration covers skipped versions, late predecessors, deletions, conflicts, unavailable reads, mixed-version participants and interrupted readback.
- Delegate migration preserves covered secrets and drafts through termination at each step. Unauthorized successors, replayed consent and conflicting concurrent moves fail safely.
- Same-key FNSX restore and cross-key application migration pass separate tests. The pinned build preserves successor namespace isolation.
- Forged transfers, mismatched acknowledgements, competing successors, copied parameters and expanded permissions fail authorization tests.
- A restored publisher backup signs a valid update to the original container. A transfer fixture verifies the container and pointer changes together.
- Pending operations retain original IDs, exact bytes and content bindings through activation and migration. Real-device upgrade runs pass the thin-peer and cellular budgets in 1.10 Thin-peer role and cellular data budgets.
