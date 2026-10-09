# 2.11 EVY delegate and private records

## Repositories

| Repository | Role | Work in this plan |
| --- | --- | --- |
| [evy](https://github.com/EVY-Platform/evy) | Modified | Delegate, predecessor registry and authority fixtures |
| [freenet-appkit](https://github.com/glesage/freenet-appkit) | Used | Swift/Kotlin recovery and lifecycle interfaces |

## Purpose

Keep one EVY delegate per user installation. Define feature and purchase signing scopes, protected private records and exact pending operations for the iOS and Android readers.

Owner: EVY identity lead. The adapter interface is defined by [2.4 SDUI data and actions](04-data-and-actions.md).

## The EVY delegate

Distinct public keys reduce links between feature records and purchases. Define derivation inputs, signing scopes and recovery behavior in shared key vectors. Reader and contract fixtures verify those vectors and the context checks below.

The EVY delegate, alias `evy.delegate`, holds the user's EVY keys for every EVY feature on the phone. It lives in `freenet/delegates/evy/`. Its parameters are empty, so its key is a hash of its code. Both apps carry its Wasm and register it with the node on every start.

| Secret | What it holds |
| --- | --- |
| `root_seed` | 32 random bytes, made on first start from Core's random source for Wasm ([rand.rs](https://github.com/freenet/freenet-stdlib/blob/fca0848b78b12942f77422309bb07f76108940d6/rust/src/rand.rs)) |
| `addresses/<id>` | The user's private address-book record, with its UUID and revision. EVY views use this local store; a purchase carries its own sealed copy |
| `pending/<service>/<id>` | A signed operation with its adapter, target contract key, exact parameters, signing scope and operation ID, for replay with the same bytes; see [Offline writes in 2.4 SDUI data and actions](04-data-and-actions.md#offline-writes) |

| Rule | Implementation |
| --- | --- |
| Feature keys | HKDF-SHA256 over `root_seed` with info `evy/hello/signing` derives Alice's hello Ed25519 key; `evy/hello/encryption` derives her hello X25519 key. Each feature has distinct keys to prevent linking its records through a common public key. An optional `scope`, such as a record ID, uses info `evy/<service>/<scope>/signing`. Ordinary signing calls return public keys and signatures; authorized `Open` returns only requested decrypted fields |
| Secret storage | Core stores secrets in the encrypted delegate store from [1.5 Identity, keys and local protection](../1-freenet-mobile-appkit/05-identity.md#what-the-key-protects). The [app-specific backup in 1.10 Backup and restore](../1-freenet-mobile-appkit/10-backup-and-restore.md#export-and-import) includes `root_seed`, so restoring it restores the same keys |
| Authorized callers | The delegate accepts EVY's native calls over the [trusted path in 1.3 Single-application host](../1-freenet-mobile-appkit/03-host.md#trusted-calls). It rejects a web app or another delegate as `MessageOrigin` ([delegate_interface.rs](https://github.com/freenet/freenet-stdlib/blob/fca0848b78b12942f77422309bb07f76108940d6/rust/src/delegate_interface.rs)) |
| Private fields | The resource's `private` list names fields for selected readers. The reader sends them in `Seal`; the delegate encrypts them to the author and each X25519 key in `readers`, using HPKE ([RFC 9180](https://www.rfc-editor.org/rfc/rfc9180), X25519, HKDF-SHA256 and ChaCha20-Poly1305). The record stores ciphertext in `sealed`. `Open` decrypts fields sealed to the local user |

## Trusted recovery and migration access

| Operation | Caller and lifecycle state | Required checks |
| --- | --- | --- |
| `ExportRecords` | Host recovery/migration coordinator during an unlocked snapshot barrier | Current identity and session generation, inventory, exact source artifact and coordinator-only capability; output enters protected snapshot buffers |
| `ImportRecords` | Host coordinator during fenced first-start upgrade or isolated staging restore | Authenticated source inventory, permitted source/target pair and complete record validation; successor readback before activation |
| `DeleteRecords` | Host coordinator during verified predecessor retirement or confirmed Forget | Verified successor/checkpoint or cleanup journal, exact namespace and stale-generation fencing |

The trusted host creates an unforgeable lifecycle capability bound to operation, source/target identities, generation and expiry. Ordinary reader actions hold signing/decryption authority. Export includes `root_seed` and private records for trusted recovery only. Imported secrets stay under protected Core storage; release controlled plaintext buffers after sealing/migration. On iOS and Android, test ordinary UI calls attempting every recovery operation and recovery racing lock, Forget and session replacement.

Messages are JSON, with schemas in `freenet/common/`:

| Message | Reply | Used for |
| --- | --- | --- |
| `GetPublicKeys { service, scope? }` | `signing_key` and `encryption_key`, base58 | `author`, `readers` and `owns()` |
| `SignRecord { service, scope?, resource, context, record }` | The record with `author` and `signature`. The delegate also saves it as pending | Collection `create` and `update` |
| `SignOperation { service, scope?, resource, context, kind, payload }` | The signed operation in the catalogue's schema, saved with its replay context | Purchase creation, participant messages and admission requests |
| `ListPending {}` | Every pending record | Each start |
| `ClearPending { service, operation_id, evidence }` | Done | The adapter confirms its target state contains the signed operation, or receives a definitive refusal. Purchase creation confirms the hosted instance, signed admission receipt and listing decision |
| `ListAddresses {}`, `PutAddress { id, expected_revision, fields }` | Private rows, or the saved row with its next revision | Address-book reads, creation and edits from the trusted native reader. A conflicting revision keeps the draft for review |
| `Seal { service, scope?, resource, context, fields, readers }` | `sealed` | Private fields bound to the source record or purchase and message, before signing |
| `Open { service, scope?, resource, context, sealed }` | The fields, or `NotSealedForYou` | Drawing private fields in their verified source context |
| `ExportRecords {}`, `ImportRecords { records }`, `DeleteRecords {}` | Records, per-record results, done | [Updating the EVY delegate](#updating-the-evy-delegate) |

`context` carries the adapter version, operation ID, target contract key and exact parameters, plus the verified source item or purchase and actor role. For `SignOperation`, `kind` selects a supported catalogue operation. The handler checks parameter derivation, service and actor binding, required source signatures and the permitted signing domain.

| Operation | Result |
| --- | --- |
| Purchase creation | Signed initial purchase, `pending` message and admission request under one saved creation context |
| Message signing | Delta for that purchase |
| Transport and retry | Operation IDs distinguish pending work across resources; replies keep the target and scope |
| `ClearPending` | Evidence identifies the verified target state and adapter completion condition. Collection evidence includes record ID, revision and signed-record hash. Listing creation also requires the verified initial listing decision and operator hosting receipt from `register_listing` |

`ExportRecords` and `ImportRecords` include the address book with the root seed and pending operations. Backup, staged restore and delegate migration preserve those records. The address adapter keeps owner-editable rows separate from received purchase copies, so an address-book edit leaves the signed purchase's sealed copy intact.

## Updating the EVY delegate

A new EVY delegate build has a new key. The iOS and Android apps move Alice's records from the predecessor to the new delegate. EVY follows [1.7 Upgrades and migration](../1-freenet-mobile-appkit/07-migration.md#delegate-secret-export-and-import):

| Step | Who | What happens |
| --- | --- | --- |
| 1. Record | evy CI | `freenet/delegates/evy/legacy.toml` lists every earlier code hash. `freenet-migrate-build` generates the lineage, and CI fails when the Wasm changes without a new row ([Predecessor registry in 1.7 Upgrades and migration](../1-freenet-mobile-appkit/07-migration.md#predecessor-registry)) |
| 2. Move | The app, on the first start of the new build | Registers the new delegate and runs freenet-migrate's `migrate_delegate_secrets` with `NewestSnapshotWins`. It reads each old delegate with `ExportRecords` and writes through `ImportRecords`. The app waits for the move to finish before sending other messages to the new delegate. This preserves the existing `root_seed`. The app shows a native "Updating EVY" screen meanwhile |
| 3. Verify and retry | The app | Reads back the imported records and verifies the root seed, derived public keys, addresses and pending signed operations. A failed or interrupted move runs again on the next start; predecessor records stay until verification completes |
| 4. Retire | The app | Sends `DeleteRecords` to the old delegate, then unregisters its key ([Retiring the old version in 1.7 Upgrades and migration](../1-freenet-mobile-appkit/07-migration.md#retiring-the-old-version)) |

Release requires compatible libraries, a mobile SDK interface and passing migration fixtures.

| Requirement | Work and evidence |
| --- | --- |
| Compatible library versions | [Compatible migration library in 1.7 Upgrades and migration](../1-freenet-mobile-appkit/07-migration.md#compatible-migration-library) aligns freenet-migrate with Core's pinned stdlib. The selected dependency set builds together in the SDK. |
| Mobile SDK interface | [Mobile migration interface in 1.7 Upgrades and migration](../1-freenet-mobile-appkit/07-migration.md#mobile-migration-interface) exposes the Rust runner to Swift and Kotlin with EVY's export, import and verification adapters and host-authorized namespaces. |
| Migration fixtures | iOS and Android tests verify preserved identity, addresses and pending signed operations, retries after interruption or failed imports, skipped supported generations and rejection of records outside the EVY inventory. Successor readback completes before retirement. |

During backup restore, these adapters run in the staging store defined by [1.10 Backup and restore](../1-freenet-mobile-appkit/10-backup-and-restore.md#staged-restore-transaction). The staged current delegate receives the restored `root_seed` through `ImportRecords` before normal application messages. EVY opens its application session and submits pending records after the complete restored generation becomes active.

EVY will evaluate [Core RFC #5255](https://github.com/freenet/freenet-core/issues/5255) against the adoption checks in [Core-assisted migration in 1.7 Upgrades and migration](../1-freenet-mobile-appkit/07-migration.md#core-assisted-migration). This plan releases with application-driven migration.

## Acceptance

- On iOS and Android, initialize one root seed and preserve derived public keys, addresses and exact pending operation bytes through restart, backup and migration.
- Ordinary calls return signatures, public keys and authorized decrypted fields. Recovery calls pass the lifecycle authority checks defined in this plan.
- Reject web/delegate callers, stale sessions, substituted feature/purchase contexts and unauthorized export/import/delete calls.
- A private-field fixture opens for each declared recipient; a third device receives `NotSealedForYou`.
- On iOS and Android, interrupt upgrades and staged restores before and after import, readback and activation. Preserve predecessors until verification and retire them through [1.7 Upgrades and migration](../1-freenet-mobile-appkit/07-migration.md#retiring-the-old-version).
- CI requires registry coverage for changed delegate Wasm; shared fixtures cover skipped supported generations and inventory violations.
