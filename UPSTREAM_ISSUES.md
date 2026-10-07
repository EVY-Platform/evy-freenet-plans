# Upstream issues

These changes in Freenet Core, freenet-stdlib, freenet-migrate and River support the plans. Mobile SDK code lives in Core's `crates/mobile`. Release checks for Core issues in progress are in [1.3 Single-application host](1-freenet-mobile-appkit/03-host.md#freenet-issues-being-worked-on-that-are-required).

Each issue names the plan it unblocks. We get issue approval before opening a feature pull request, following Core's [issue approval rule](https://github.com/freenet/freenet-core/pull/4311) and [prioritization process](https://github.com/freenet/freenet-core/discussions/4412).

## Filed

| Change | Issue | Needed by |
| --- | --- | --- |
| Request IDs on client API success and error replies. The client sets an ID on each request, and Core and stdlib preserve it through every reply path for the request types enabled for parallel execution. The SDK uses one submitted request per connection until this coverage passes conformance tests | [freenet-stdlib#106](https://github.com/freenet/freenet-stdlib/issues/106), [freenet-core#5724](https://github.com/freenet/freenet-core/issues/5724) | [1.2 Embedded node and mobile SDK](1-freenet-mobile-appkit/02-sdk.md#matching-replies-to-requests), [2.6 Payments](2-evy-on-freenet/06-payments.md#paying-on-a-phone) |
| Core backup includes delegate Wasm and exact registration parameters, then installs and registers them during restore. #4035 is open and unassigned as checked 2026-10-07; the mobile export and import surface must expose the capability | [freenet-core#4035](https://github.com/freenet/freenet-core/issues/4035) | [1.5 Identity, keys and local protection](1-freenet-mobile-appkit/05-identity.md#the-backup-file), [1.7 Upgrades and migration](1-freenet-mobile-appkit/07-migration.md#delegate-secret-export-and-import), [3.1 Automated backup](3-optional-extensions/01-backup.md#the-backup-file) |
| Agreement on the sync design that the EVY delegate's sync library follows | [freenet-core RFC #5587](https://github.com/freenet/freenet-core/issues/5587) | [3.2 Device sync](3-optional-extensions/02-sync.md#what-core-still-needs) |
| Delegates update contracts they do not yet hold | [freenet-core#5542](https://github.com/freenet/freenet-core/issues/5542) | [3.2 Device sync](3-optional-extensions/02-sync.md#what-core-still-needs) |
| Delegate subscriptions register hosting demand on a running node and restore subscriptions after restart | [freenet-core#4669](https://github.com/freenet/freenet-core/issues/4669) | [1.6 Application protocols, data and operations](1-freenet-mobile-appkit/06-data-and-operations.md#lost-network-state), [3.2 Device sync](3-optional-extensions/02-sync.md#what-core-still-needs) |
| A delegate GET tells a missing contract from a failed lookup | [freenet-stdlib#131](https://github.com/freenet/freenet-stdlib/issues/131) | [3.2 Device sync](3-optional-extensions/02-sync.md#what-core-still-needs) |
| River reclaims old chat delegate copies and unregisters old delegate keys after a migration completes | [river#586](https://github.com/freenet/river/issues/586) | [1.7 Upgrades and migration](1-freenet-mobile-appkit/07-migration.md#retiring-the-old-version) |
| Persistent DM blocking and leaving a DM | [river#461](https://github.com/freenet/river/issues/461) | The DM part of blocking in [1.9 Testing and release](1-freenet-mobile-appkit/09-testing-and-release.md#store-requirements) |

## Future Core migration work

| Proposal | Scope | Adoption |
| --- | --- | --- |
| [freenet-core RFC #5255](https://github.com/freenet/freenet-core/issues/5255) | Author-bound delegate provenance and Core-mediated secret transfer to a successor delegate | Evaluate when the provenance checks and secret-deposit path are implemented and tested. |

EVY uses application-driven `migrate_delegate_secrets` with its own export and import adapters, as [1.7 Upgrades and migration](1-freenet-mobile-appkit/07-migration.md#delegate-secret-export-and-import) specifies. Its release requirements are the compatible library release in [M1](#m1-release-freenet-migrate-on-the-freenet-stdlib-that-core-pins), the mobile SDK interface in [C13](#c13-expose-application-driven-delegate-migration-to-mobile-hosts) and the migration fixtures in [2.4 SDUI data and actions](2-evy-on-freenet/04-data-and-actions.md#updating-the-evy-delegate).

## Core retention and delivery research

Core work will address offline delivery after contract eviction. In milestone 1 (Freenet mobile AppKit) and milestone 2 (EVY on Freenet), reconnect tests retain contract state within the pinned Core build's hosting budget. Those milestones and [3.2 Device sync](3-optional-extensions/02-sync.md#traffic-and-lifecycle) will adopt Core's stronger retention and delivery guarantees when they ship. This includes keeping data available while all linked mobile nodes are stopped.

| Thread | Scope | Status checked 2026-10-07 |
| --- | --- | --- |
| [#5041 Bounded local contract pin](https://github.com/freenet/freenet-core/issues/5041) | A quota-bounded API for retaining selected contracts on the user's node through normal demand eviction | Open design proposal with an exploratory fork; awaiting approach approval |
| [#4651 Contract storage design](https://github.com/freenet/freenet-core/issues/4651) | Evaluates on-disk persistence and a targeted backstop for newly published contracts until a second replica exists | Open design question |
| [#4785 Persist hosting demand across restart](https://github.com/freenet/freenet-core/issues/4785) | Restores live subscriptions for contracts with prior client demand after a node restart | Open follow-up proposal |
| [#3465 PUT propagation reliability](https://github.com/freenet/freenet-core/issues/3465) | Tracks locally applied PUTs whose reported results or remote propagation are unreliable | Open; assigned to iduartgomez |
| [#3611 PUT forwarding acknowledgements and retries](https://github.com/freenet/freenet-core/pull/3611) | Adds hop-level forwarding acknowledgements and retries for in-flight PUT operations | Merged 2026-03-21 |
| [#5515 Repair dropped broadcast UPDATEs](https://github.com/freenet/freenet-core/pull/5515) | Adds resynchronization for rate-limited broadcasts; [#5527](https://github.com/freenet/freenet-core/issues/5527) tracks repair latency when a throttle window suppresses another request | Merged 2026-09-02; latency follow-up open |

Evaluate future Core releases for local retention, subscription recovery and in-flight retries. A successful client PUT confirms local persistence; network propagation continues asynchronously, as [#3626](https://github.com/freenet/freenet-core/pull/3626) specifies.

## To file

File the Core issues first. The River changes depend on them.

| # | Issue | Repository | Unblocks |
| --- | --- | --- | --- |
| C1 | [Resolve gateway hostnames in the join loop](#c1-resolve-gateway-hostnames-in-the-join-loop) | freenet-core | [1.2 Embedded node and mobile SDK](1-freenet-mobile-appkit/02-sdk.md#start-stop-and-reconnect) |
| C2 | [Accept local updates and subscriptions before the first join](#c2-accept-local-updates-and-subscriptions-before-the-first-join) | freenet-core | [1.2 Embedded node and mobile SDK](1-freenet-mobile-appkit/02-sdk.md#start-stop-and-reconnect), [1.6 Application protocols, data and operations](1-freenet-mobile-appkit/06-data-and-operations.md#sending-updates) |
| C3 | [Re-read the Wasm memory address after each guest call](#c3-re-read-the-wasm-memory-address-after-each-guest-call) | freenet-core | [1.2 Embedded node and mobile SDK](1-freenet-mobile-appkit/02-sdk.md#running-wasm) |
| C4 | [Keychain and Keystore backends for the node encryption key](#c4-keychain-and-keystore-backends-for-the-node-encryption-key) | freenet-core, under [#4137](https://github.com/freenet/freenet-core/issues/4137) | [1.2 Embedded node and mobile SDK](1-freenet-mobile-appkit/02-sdk.md#keys), [1.5 Identity, keys and local protection](1-freenet-mobile-appkit/05-identity.md#node-encryption-key) |
| C5 | [Let an embedder supply the `UserInputPrompter`](#c5-let-an-embedder-supply-the-userinputprompter) | freenet-core | [1.3 Single-application host](1-freenet-mobile-appkit/03-host.md#background-runs-and-delegate-prompts) |
| C6 | [Permission codes, a set call and a public API for app grants](#c6-permission-codes-a-set-call-and-a-public-api-for-app-grants) | freenet-core | [1.3 Single-application host](1-freenet-mobile-appkit/03-host.md#base-authorization-and-device-access) |
| C7 | [Lock and unlock on `SecretsStore`](#c7-lock-and-unlock-on-secretsstore) | freenet-core | [1.5 Identity, keys and local protection](1-freenet-mobile-appkit/05-identity.md#locking-and-unlocking) |
| C8 | [Thin-peer role and cellular budgets](#c8-thin-peer-role-and-cellular-budgets) | freenet-core | [1.8 Thin-peer role and cellular data budgets](1-freenet-mobile-appkit/08-thin-peer.md#upstream-work-and-carrier-evidence) |
| C9 | [Send client updates as deltas](#c9-send-client-updates-as-deltas) | freenet-core | [1.8 Thin-peer role and cellular data budgets](1-freenet-mobile-appkit/08-thin-peer.md#upstream-work-and-carrier-evidence) |
| C10 | [Stage and activate a complete app restore](#c10-stage-and-activate-a-complete-app-restore) | freenet-core | [1.2 Embedded node and mobile SDK](1-freenet-mobile-appkit/02-sdk.md#what-to-build), [1.5 Identity, keys and local protection](1-freenet-mobile-appkit/05-identity.md#staged-restore-transaction), [3.1 Automated backup](3-optional-extensions/01-backup.md#restoring-on-a-new-phone) |
| C11 | [Scope private-data operations on a shared node](#c11-scope-private-data-operations-on-a-shared-node) | freenet-core | [1.3 Single-application host](1-freenet-mobile-appkit/03-host.md#shared-node-and-key-scope), [1.5 Identity, keys and local protection](1-freenet-mobile-appkit/05-identity.md#app-specific-export-and-import), [3.1 Automated backup](3-optional-extensions/01-backup.md#the-backup-file) |
| C12 | [Prepare and replay signed website publications](#c12-prepare-and-replay-signed-website-publications) | freenet-core | [1.4 Application bundles](1-freenet-mobile-appkit/04-bundles.md#publishing-and-evidence) |
| C13 | [Expose application-driven delegate migration to mobile hosts](#c13-expose-application-driven-delegate-migration-to-mobile-hosts) | freenet-core | [1.2 Embedded node and mobile SDK](1-freenet-mobile-appkit/02-sdk.md#what-to-build), [1.7 Upgrades and migration](1-freenet-mobile-appkit/07-migration.md#delegate-secret-export-and-import), [2.4 SDUI data and actions](2-evy-on-freenet/04-data-and-actions.md#updating-the-evy-delegate) |
| S1 | [A public delegate call in the TypeScript client](#s1-a-public-delegate-call-in-the-typescript-client) | freenet-stdlib | [2.5 EVY Developer on Freenet](2-evy-on-freenet/05-developer.md#the-evy-developer-bundle) |
| M1 | [Release freenet-migrate on the freenet-stdlib that Core pins](#m1-release-freenet-migrate-on-the-freenet-stdlib-that-core-pins) | freenet-migrate | [2.4 SDUI data and actions](2-evy-on-freenet/04-data-and-actions.md#updating-the-evy-delegate) |
| R1 | [Ship `app_definition.json` in the release build](#r1-ship-app_definitionjson-in-the-release-build) | river | [1.4 Application bundles](1-freenet-mobile-appkit/04-bundles.md#the-archive-and-its-definition) |
| R2 | [Publish with the packaging CLI and River's own container Wasm](#r2-publish-with-the-packaging-cli-and-rivers-own-container-wasm) | river | [1.4 Application bundles](1-freenet-mobile-appkit/04-bundles.md#saved-copies-and-recovery) |
| R3 | [Use the common publication version allocator](#r3-use-the-common-publication-version-allocator) | river | [1.4 Application bundles](1-freenet-mobile-appkit/04-bundles.md#the-archive-and-its-definition) |
| R4 | [Save drafts and pending signed messages in the chat delegate](#r4-save-drafts-and-pending-signed-messages-in-the-chat-delegate) | river | [1.6 Application protocols, data and operations](1-freenet-mobile-appkit/06-data-and-operations.md#reads-and-local-data) |
| R5 | [Complete River's store-release requirements](#r5-complete-rivers-store-release-requirements) | river | [1.9 Testing and release](1-freenet-mobile-appkit/09-testing-and-release.md#store-requirements) |

```mermaid
flowchart LR
    R2[R2 packaging CLI and container Wasm] --- R3[R3 publication version allocator]
    R1[R1 app_definition.json] --> R2
    C12[C12 prepare and replay signed state] --> R2
    C12 --> R3
    C1[C1 gateway hostnames] --> C2[C2 updates before first join]
    M1[M1 compatible migration library] --> C13[C13 mobile migration interface]
```

### freenet-core

#### C1 Resolve gateway hostnames in the join loop

The node fetches the public [gateway index](https://github.com/freenet/web/blob/main/hugo-site/static/keys/gateways.toml) at startup. The index uses hostnames. To let Bob open River on the subway, Core must start the node with its local data and retry gateway DNS lookups when a network is available.

Move hostname resolution and retries into Core's join loop. The node starts offline and joins once a lookup succeeds.

Sources: [node.rs](https://github.com/freenet/freenet-core/blob/main/crates/core/src/node.rs) (`parse_socket_addr`), [#1119](https://github.com/freenet/freenet-core/pull/1119), [offline startup findings](https://github.com/glesage/freenet-appkit/blob/main/docs/findings.md#the-node-cannot-start-offline-in-network-mode) and [community mobile gateway findings](https://github.com/freenet/river/issues/319).

#### C2 Accept local updates and subscriptions before the first join

Before its first network handshake, the node must read local contracts, merge local updates and record subscriptions. Bob can then open his saved River rooms offline and save "Skate session Saturday?" to a room.

Core sends the saved updates and subscriptions when the node joins. Apply this to contracts the node already stores.

Sources: `ensure_peer_ready` in [error.rs](https://github.com/freenet/freenet-core/blob/main/crates/core/src/client_events/error.rs), its callers in [client_events.rs](https://github.com/freenet/freenet-core/blob/main/crates/core/src/client_events.rs), and [#2385](https://github.com/freenet/freenet-core/pull/2385).

Depends on C1.

#### C3 Re-read the Wasm memory address after each guest call

The mobile runtime needs smaller Wasm memory reservations. The iPhone test exhausted Core's 256 MiB reservations after 22 calls. The iOS build uses 2 executors and replaces each Store after 4 instances; the Android build uses Core's defaults. Test the memory-address fix on both platforms.

Core must read each instance's memory address again after every contract and delegate call returns. Each instance can then reserve only the memory it uses. Follow the host-function handling in [#3248](https://github.com/freenet/freenet-core/issues/3248) and [#3270](https://github.com/freenet/freenet-core/pull/3270).

Sources: [contract.rs](https://github.com/freenet/freenet-core/blob/main/crates/core/src/wasm_runtime/contract.rs), the 256 MiB default from [#3990](https://github.com/freenet/freenet-core/pull/3990), [the iPhone refused Core's Wasm memory reservations](https://github.com/glesage/freenet-appkit/blob/main/docs/findings.md#the-iphone-refused-cores-wasm-memory-reservations) and the [recommended fix](https://github.com/glesage/freenet-appkit/blob/main/docs/findings.md#recommendation-core-re-reads-the-memory-address-after-each-guest-call).

#### C4 Keychain and Keystore backends for the node encryption key

The iOS and Android builds need persistent, platform-protected storage for the node encryption key.

Add iOS Keychain and Android Keystore backends as `KekBackendKind` variants. Android must reject the keyring backend because its in-memory mock loses secrets on restart. File this as a sub-issue of [#4137](https://github.com/freenet/freenet-core/issues/4137), which specifies a hardware-backed tier.

Sources: [kek.rs](https://github.com/freenet/freenet-core/blob/main/crates/core/src/config/kek.rs), [#4140](https://github.com/freenet/freenet-core/issues/4140) and the per-version Android settings in [Node encryption key in 1.5 Identity, keys and local protection](1-freenet-mobile-appkit/05-identity.md#node-encryption-key).

#### C5 Let an embedder supply the `UserInputPrompter`

The iOS and Android host must show delegate prompts and Core's `Background` consent (`prompt_capability`) in trusted native screens.

Expose `UserInputPrompter` as a public interface that the embedder passes to the node. Route iOS and Android prompts through that interface.

Sources: [p2p_impl.rs](https://github.com/freenet/freenet-core/blob/main/crates/core/src/node/p2p_impl.rs), [user_input.rs](https://github.com/freenet/freenet-core/blob/main/crates/core/src/contract/user_input.rs), and [#5749](https://github.com/freenet/freenet-core/issues/5749) on prompts from runs nobody started.

#### C6 Permission codes, a set call and a public API for app grants

Core keys each grant by user scope, app and permission code. The phone host needs to store Bob's `notifications` answer from River's first run in this table.

Add a code for each app permission, starting with `notifications`. Expose grant creation, listing and revocation through a public Rust API for `crates/mobile`.

Sources: [delegate_capabilities.rs](https://github.com/freenet/freenet-core/blob/main/crates/core/src/contract/delegate_capabilities.rs), [permission_prompts.rs](https://github.com/freenet/freenet-core/blob/main/crates/core/src/server/client_api/permission_prompts.rs), [#5730](https://github.com/freenet/freenet-core/pull/5730), [#5744](https://github.com/freenet/freenet-core/pull/5744) and [#4014](https://github.com/freenet/freenet-core/issues/4014).

#### C7 Lock and unlock on `SecretsStore`

`SecretsStore` keeps its keys in memory for as long as the node runs. When Alice's phone locks, the host has to wipe the node encryption key and every derived key from memory, then load them again on unlock.

Add `lock` and `unlock` to `SecretsStore`. Test that locking wipes the zeroizing buffers, as requested in [#5599](https://github.com/freenet/freenet-core/issues/5599).

Sources: [store.rs](https://github.com/freenet/freenet-core/blob/main/crates/core/src/wasm_runtime/secrets_store/store.rs) and [Locking and unlocking in 1.5 Identity, keys and local protection](1-freenet-mobile-appkit/05-identity.md#locking-and-unlocking).

#### C8 Thin-peer role and cellular budgets

The phone test measured about 60 KiB/s each way on Wi-Fi while routing and hosting for other peers. A phone on cellular needs a thin-peer role and a total byte budget that Core enforces.

Add a thin-peer role that connects to serving full peers for the phone's own applications. Enforce per-day upload and download caps. The issue must define how a thin peer repays the full peers that serve it ([D136](https://github.com/freenet/freenet-core/discussions/136), [D137](https://github.com/freenet/freenet-core/discussions/137), [D893](https://github.com/freenet/freenet-core/discussions/893)).

Sources: [phones are full peers on the public network](https://github.com/glesage/freenet-appkit/blob/main/docs/findings.md#phones-are-full-peers-on-the-public-network), [D420](https://github.com/freenet/freenet-core/discussions/420) (the only maintainer statement on a limited node on a phone), and the cost issues [#5643](https://github.com/freenet/freenet-core/issues/5643), [#5707](https://github.com/freenet/freenet-core/issues/5707), [#4965](https://github.com/freenet/freenet-core/issues/4965), [#5157](https://github.com/freenet/freenet-core/issues/5157) and [#3336](https://github.com/freenet/freenet-core/issues/3336).

#### C9 Send client updates as deltas

A client UPDATE merges on the phone and then goes to the serving peer as the whole merged state. Each message Bob sends to "Skate club" costs the full room state on cellular.

Send the client's delta, computed against what the receiving peer holds. Use Core's broadcast delta handling.

Sources: [#4072](https://github.com/freenet/freenet-core/pull/4072) deferred the raw-delta wire format, `RequestUpdate` in [op_ctx_task.rs](https://github.com/freenet/freenet-core/blob/main/crates/core/src/operations/update/op_ctx_task.rs), and [#2427](https://github.com/freenet/freenet-core/pull/2427) on why deltas must use the receiver's summary.

#### C10 Stage and activate a complete app restore

Core and `crates/mobile` provide isolated restore stores and a durable activation record for one app's complete data generation. The restore transaction:

1. Stages delegate Wasm, exact registrations, secrets and declared host records.
2. Runs local migration adapters and verifies successor readback.
3. Selects the complete generation in one recoverable activation step.
4. Replaces sessions for consumers whose shared namespace changes.
5. Resumes network activity after activation.

Staged delegates run only the restore adapters. Other applications retain their data under the shared node key encryption key (KEK). Lost-KEK recovery creates one replacement KEK. Each affected application's previous encrypted generation stays in quarantine until that application's recovery completes.

The mobile SDK exposes the transaction to Swift and Kotlin, and startup recovery selects a complete generation before opening sessions. Tests on iOS and Android inject write failures, full storage, migration failures and termination before and after activation. This work follows the [staged restore transaction in 1.5 Identity, keys and local protection](1-freenet-mobile-appkit/05-identity.md#staged-restore-transaction) and uses the executable-inclusive backup capability proposed in [#4035](https://github.com/freenet/freenet-core/issues/4035).

#### C11 Scope private-data operations on a shared node

The host authorizes the application data that Core and `crates/mobile` can export, stage for import or delete. Exports include delegate Wasm and exact registration parameters. The selection covers:

- Exact current and supported predecessor delegate namespaces.
- Declared host-record sets.

Core checks this selection before reading, writing or deleting records. Ownership and grants control access to shared components. When an application releases its grant, the owning component and remaining consumers keep their data.

The shared node keeps one KEK across applications.

| Operation | Result |
| --- | --- |
| Application Forget | Removes selected private records, registrations and grants. |
| Whole-node reset | Closes all sessions, deletes the KEK and clears the shared store. |

The host reports which data each operation covers. iOS and Android tests export, restore and forget one application while a second keeps its records and working sessions. They also reject ownership substitution and verify whole-node reset. Follow the rules in [1.3 Single-application host](1-freenet-mobile-appkit/03-host.md#shared-node-and-key-scope) and [1.5 Identity, keys and local protection](1-freenet-mobile-appkit/05-identity.md#forget).

#### C12 Prepare and replay signed website publications

fdev exposes separate preparation and submission operations:

| Operation | Inputs and result |
| --- | --- |
| Prepare | Takes the release directory, explicit unsigned 32-bit version, publisher key and pinned container Wasm. Returns the exact archive and complete signed container state for local storage. |
| Submit | Sends the saved state with the same container Wasm and parameters. |

The packaging CLI saves those bytes durably before sending. After an uncertain result, it replays the same bytes.

The packaging CLI owns the per-container journal, version reservation and release-job serialization defined in [1.4 Application bundles](1-freenet-mobile-appkit/04-bundles.md#publishing-and-evidence). fdev encodes the archive and signatures and validates the supplied version and state. Fixtures cover local preparation, exact replay after termination and readback through a second node. Implement this in Core's fdev.

#### C13 Expose application-driven delegate migration to mobile hosts

Core's `crates/mobile` runs freenet-migrate's `migrate_delegate_secrets` in Rust and exposes it to Swift and Kotlin. The app supplies its predecessor registry, walk policy and export, import and verification adapters. The host authorizes the selected application and delegate namespaces before migration starts, using the ownership rules in C11.

The runner holds other calls to the successor until imported records pass readback verification. After an interruption, it retains the predecessor records and resumes on the next start. Retirement follows [1.7 Upgrades and migration](1-freenet-mobile-appkit/07-migration.md#retiring-the-old-version). Backup restore runs the same adapters inside the C10 staging transaction.

Fixtures on iOS and Android cover normal upgrades, skipped supported generations, interruption, failed imports, successor readback and isolation from another application's records. EVY fixtures preserve `root_seed`, derived public keys, addresses and pending signed operations. Implement this in the mobile SDK after M1.

### freenet-stdlib


#### S1 A public delegate call in the TypeScript client

EVY Developer runs in a browser and keeps the service publisher key in its own delegate. The page asks the delegate to sign each UI version. This requires public delegate calls in freenet-stdlib's TypeScript `FreenetWsApi`.

Add public calls for `RegisterDelegate` and `ApplicationMessages`. Return the delegate's outbound messages to the caller.

Sources: [websocket-interface.ts](https://github.com/freenet/freenet-stdlib/blob/main/typescript/src/websocket-interface.ts), which already imports the delegate request and response types.

### freenet-migrate

#### M1 Release freenet-migrate on the freenet-stdlib that Core pins

The pinned Core uses freenet-stdlib 0.12.1. EVY moves delegate records with freenet-migrate's `migrate_delegate_secrets`, which `crates/mobile` runs for the Swift and Kotlin SDK. Release a compatible freenet-migrate version so these components build on the same stdlib.

Build the selected Core, stdlib and freenet-migrate versions together in the mobile SDK. Run the migration fixtures on that exact dependency set before release. C13 exposes the runner to Swift and Kotlin.

Sources: [Cargo.toml](https://github.com/freenet/freenet-migrate/blob/main/freenet-migrate/Cargo.toml), [stdlib #136](https://github.com/freenet/freenet-stdlib/pull/136) and [stdlib #137](https://github.com/freenet/freenet-stdlib/pull/137).

### river

#### R1 Ship `app_definition.json` in the release build

The AppKit host and packaging CLI read River's components, protocols and permissions from `app_definition.json` in the release archive.

River's release build writes `app_definition.json` with its room contract, chat delegate and `notifications` permission. Use the format in [1.4 Application bundles](1-freenet-mobile-appkit/04-bundles.md#the-archive-and-its-definition).

#### R2 Publish with the packaging CLI and River's own container Wasm

River publishes through the packaging CLI with `--contract-wasm published-contract/web_container_contract.wasm`. Preparation and submission both use that pinned Wasm and River's existing publisher key, preserving the container key `raAqMhMG7KUpXBU2SxgCQ3Vh4PYjttxdSWd9ftV7RLv`. River's publisher copies the signing key into fdev's key file, `~/.config/freenet/website-keys/<name>.toml`, and backs it up with the publication journal and prepared signed states.

Sources: River's [Makefile.toml](https://github.com/freenet/river/blob/main/Makefile.toml), [river-publish.md](https://github.com/freenet/river/blob/main/.claude/rules/river-publish.md), [website.rs](https://github.com/freenet/freenet-core/blob/main/crates/fdev/src/website.rs) and [publish-readback.sh](https://github.com/freenet/river/blob/main/scripts/publish-readback.sh).

Depends on R1 and C12. File together with R3.

#### R3 Use the common publication version allocator

River release jobs use the packaging CLI's per-container journal and lock. Each new publication reserves a version higher than the journal's highest reservation and the verified network version, with Unix seconds as a starting floor. Retries retain the exact prepared signed state and its version. River's publish rules and CI route releases through this common publisher workspace.

The first release reconciles the existing container version before reservation. Recovery restores the journal and prepared states alongside the publisher key, then reconciles pending attempts before preparing another release. [1.4 Application bundles](1-freenet-mobile-appkit/04-bundles.md#publishing-and-evidence) defines the allocator and readback rules.

Depends on C12. File together with R2.

#### R4 Save drafts and pending signed messages in the chat delegate

River must retain Bob's unsent draft and pending signed messages across app restarts and background node stops.

Save the draft and signed message in the chat delegate's store with `GetVersionedRequest` and `CasStoreRequest`. Keep signing in the page. Run the store call alongside the send, because delegate calls queue behind contract merges ([river#512](https://github.com/freenet/river/issues/512)).

Sources: [river#345](https://github.com/freenet/river/issues/345) (CAS requests), Mail's per-device drafts delegate ([mail#56](https://github.com/freenet/mail/pull/56)) and [Sending updates in 1.6 Application protocols, data and operations](1-freenet-mobile-appkit/06-data-and-operations.md#sending-updates).

#### R5 Complete River's store-release requirements

File a River release issue for the following work from [1.9 Testing and release](1-freenet-mobile-appkit/09-testing-and-release.md#store-requirements). Each row needs an owner and completion evidence before the iOS and Android store submissions.

| Work | Completion evidence |
| --- | --- |
| Reporting | River's UI reports a message or member to a monitored River-team inbox. A test report reaches the inbox, and the team publishes its response deadline on the support page. |
| Room-wide blocking | A user can block a member and hide that member's room messages. The block survives restart and new messages. Combined room and DM tests use the DM blocking work tracked in [river#461](https://github.com/freenet/river/issues/461). |
| Default content filter | River's UI filters objectionable messages by default, with acceptance fixtures covering the release's filter behavior. |
| Terms before posting | River shows its terms and requires acceptance before the user's first post. Tests cover acceptance and reopening the app. |
| Support page and listings | A published support page gives contact details and the report-response deadline. The iOS and Android store listings link to it. |
| Child-safety materials | River publishes its child-safety standards and completes the Play Console declaration. The release checklist records the published URL and declaration. |

River's invite-only release uses its room-owner and deputy ban controls. Related design work includes room membership and delegated moderation in [river#371](https://github.com/freenet/river/issues/371), and a recent-actions admin panel in [river#492](https://github.com/freenet/river/issues/492). R5 tracks the store-release work above and links the existing DM issue for its blocking checks.
