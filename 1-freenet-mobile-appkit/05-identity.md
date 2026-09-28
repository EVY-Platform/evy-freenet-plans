# 1.5 Identity, keys and local protection

## Repositories

| Repository | Role | Work in this plan |
| --- | --- | --- |
| [freenet-core](https://github.com/freenet/freenet-core) | Modified | `crates/mobile` gains protected key and record handling, typed lock states, explicit forget, the encrypted export and import package and the restore flow, built on the secrets-at-rest backends, delegate secret store and FNSX bundle; the mobile Keychain and Keystore backends land through 1.2 Embedded node and mobile SDK |
| [river](https://github.com/freenet/river) | Used | `riverctl identity export` and `import`, privacy model and chat delegate store as the application fixture |

## Purpose

This plan protects a defined application's keys and private records. Before public use with valuable identities, the application provides a tested encrypted export/import path that states exactly what it restores.

## Prerequisites

The selected [profiles in 1.1 Mobile feasibility and supported profiles](01-feasibility.md), [SDK platform-store integration in 1.2 Embedded node and mobile SDK](02-sdk.md) and [1.3 Single-application host](03-host.md).

This plan owns key protection, deletion, key-loss behavior and the minimum app-specific recovery package. [1.3 Single-application host](03-host.md#base-authorization-and-device-access) owns base authorization. [1.7 Upgrades and migration](07-migration.md) owns component upgrades and publisher transfer.

## Separate identities and authority

| Identity | Authority |
| --- | --- |
| Application | Full container identity verified under [1.4 Application bundles](04-bundles.md) |
| Publisher signer | Publisher-controlled signing key and tested publisher backup |
| Application user | Application identity controlled by an enrolled key and its recovery policy, bound to the host session |
| Device | Explicit authorization by the user or their recovery authority |
| Node transport | The node installation's network identity |
| Delegate | Full code-and-parameter key and its authorized private namespace |

The [1.3 Single-application host](03-host.md) binds user authority to each verified application session and handles sharing across web and native contexts. It keeps grants and publisher trust outside application-readable storage. Export excludes active session tokens. Import establishes fresh sessions through the trusted host.

## Protected keys and records

Wrap the node's key encryption key with iOS Keychain or Android Keystore protection through the selected SDK/Core backend. The source evidence in [secrets at rest](https://github.com/freenet/freenet-core/blob/main/docs/secrets-at-rest.md) describes systemd-credential, file and opt-in macOS/Windows keyring backends. Mobile backends and any hardware-signing adapter require implementation and device validation under [1.2 Embedded node and mobile SDK](02-sdk.md). Treat this source snapshot as plan evidence and check the pinned build's behavior at release.

Delegates sign inside Wasm, so their signing material enters Wasm memory. A platform-protected wrapping key protects stored material. Hardware-backed signing requires a compatible algorithm and a signing adapter. Record each key's algorithm, purpose, namespace, exportability and supported successor-authorization method. Authorized application calls receive scoped opaque handles where the host supplies key access.

Core owns the delegate secret store. Its device-node namespace follows the delegate key. [1.3 Single-application host](03-host.md#who-controls-what) owns base admission. Apply equivalent protection to host records that contain private payloads. An encrypted database backup requires the corresponding key to open it.

| Record | Protection and recovery coverage |
| --- | --- |
| User identity and authorized device records | Protected application identity records. Restore recoverable key material or use the declared recovery authority to authorize a supported successor |
| Delegate secrets | Core's encrypted store. Same-key recovery uses its encrypted FNSX bundle and import path |
| River private room messages | Encrypted room contract state under the [River privacy model](https://github.com/freenet/river/blob/main/README.md#privacy-model). Restore the room secret and locate an available state copy |
| River outbound DM plaintext | Chat delegate secret store, covered by that delegate's export |
| Application records the app declares | Protected host records. The application declares their export coverage and how it reconciles them after a restore |
| Room members and bans | Signed room contract state, refreshed against retained references |

Return typed locked-device and invalidated-key states. Preserve protected records and identity references while the user restores access. Explicit forget identifies and removes selected keys and private records, verifies deletion, and reports failures. Explain which network records, exported packages and other devices retain copies, and the effect on rooms the user owns or has joined.

## App-specific export and import

River's [CLI documentation](https://github.com/freenet/river/blob/main/cli/README.md) supplies an application fixture through `riverctl identity export` and `riverctl identity import`. This plan integrates and tests the selected application's supported path on mobile, with versioning, integrity checks and declared coverage.

Use an encrypted package protected by a customer-held recovery secret. For delegate-store backup, wrap Core's encrypted FNSX bundle and import it into the same full delegate identity. The source snapshot caps its plaintext at 256 MiB and describes export decrypting each secret while building the bundle. A hosted operator handling that export can see plaintext. State that exposure in the hosted profile. [1.7 Upgrades and migration](07-migration.md#delegate-secret-export-and-import) owns cross-key moves.

| Package content | Required detail |
| --- | --- |
| Format and cryptographic profile | Version, creation time and authenticated integrity metadata |
| Application and user identity | Full references, supported lineage and recovery authority |
| Recoverable keys and private records | Purpose, namespace and exact coverage of each entry |
| Record references | Original component code and parameters, retained data references and their availability assumptions |
| Protocols and declared application records | Concrete protocol versions and the application records the app declares, within declared coverage |
| Coverage report | Hardware-bound keys, omitted records, service-managed accounts and prerequisites for restoring each item |

Use a reviewed, versioned authenticated-encryption profile. Authenticate the complete metadata, derive separate keys for separate purposes, bound sizes before decoding and reject unsupported profiles. Keep the recovery secret and any plaintext equivalent separate from the package.

The app-specific restore flow:

1. Authenticate and decode the package within its limits. Check application identity, coverage and required component versions.
2. The trusted host verifies the destination and obtains the user's approval for it. Restore only authorized records. Stage imports and retain a usable copy until validation completes.
3. Read back and validate keys and records through the application's protocol. Import shared records only with the signatures their domain requires. Resume an interrupted import idempotently.
4. Establish fresh sessions, refresh shared state and hand the declared application records to the application's reconciliation step.
5. Report restored and uncovered records. State the package location and who retains it.

Setup includes reopening a sample package with the user's recovery secret. Recovery requires both that secret and an available package. Loss of the secret and every other authorized recovery path leaves the covered identity unrecoverable. State that consequence before the user relies on the identity. The package restores only its declared local material.

## Acceptance

- On iOS and Android, River's declared export/import restores its identity, covered room secrets and private records onto a fresh installation.
- Declared application records round-trip through the package with their declared coverage.
- Tests cover wrong secrets, corrupt/truncated packages, unsupported profiles, oversized fields, interrupted imports, reinstall and exhausted storage.
- Device lock and key invalidation produce typed access states. A hardware-bound key follows its declared successor path or appears as uncovered in the report.
- A restore obtains fresh sessions and passes host isolation tests. A copied package grants only the authority proven by its recovery path.
- Explicit forget verifies deletion and reports failures and retained external copies.
- The baseline passes before public release with valuable identities.
