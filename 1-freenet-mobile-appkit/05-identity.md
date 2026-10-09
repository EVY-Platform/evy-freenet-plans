# 1.5 Identity, keys and local protection

## Repositories

| Repository | Role | Work in this plan |
| --- | --- | --- |
| [freenet-core](https://github.com/freenet/freenet-core) | Modified | Key protection, backup and restore |
| [river](https://github.com/freenet/river) | Used | Identity export fixture |

## Purpose

Encrypt an app's keys and private data on iOS and Android, and let the user back them up, restore them and delete them. River is the first app:

- River encrypts Alice's identity key, her "Skate club" room secret and the DMs she sent on her phone. The iOS Keychain or Android Keystore protects the key that unlocks them.
- Alice exports them to an encrypted backup file. She opens it with her confirmed recovery code.
- On a new iPhone or Android phone, she imports the file. The app lists what it restored and what the file left out.
- Alice can delete her private records. The app verifies deletion and reports the result.

The app goes to public users only after backup and restore pass the tests in [Acceptance](#acceptance).

## Application and key identities

| Key | What it is | Who controls it |
| --- | --- | --- |
| Application | River's website container key. Core computes it from the container code and the publisher's verifying key | Nobody holds it. Anyone can recompute it |
| Publisher | The key that signs each River bundle release | The River publisher |
| User | Alice's signing key for "Skate club". River makes one per room and stores it in its chat delegate | Alice |
| Delegate | River's chat delegate key, a hash of its code. Its secret store holds Alice's signing keys and the DMs she sent | Nobody holds it. Anyone can recompute it |
| Node network key | The key Alice's node uses to connect to other peers. Core creates it on first run and saves it as `transport_keypair` in its secrets directory | Alice's node |
| Node encryption key | The key that encrypts every delegate's secret store. Core calls it the KEK and keeps it in a systemd credential, a file, or the macOS or Windows keyring | Alice's node |

## What this plan adds

| Change | Why | How |
| --- | --- | --- |
| [Keep the node encryption key in the iOS Keychain or Android Keystore](#node-encryption-key) | Protect the key separately from the encrypted secrets | [1.2 Embedded node and mobile SDK](02-sdk.md#keys) packages and tests the backends and platform settings defined in this plan |
| [Lock the key when the phone locks](#locking-and-unlocking) | Protect Alice's encrypted data while the phone is locked | Core wipes the key from memory when the phone locks and reads it again on unlock. Delegate calls in between return `Locked`. A missing key returns `KeyLost` |
| [One encrypted backup file in 1.10 Backup and restore](10-backup-and-restore.md#export-and-import) | Recover all of Alice's rooms and DMs from one file | Core's encrypted delegate backup (FNSX) uses a recovery code the app generates for Alice as its passphrase. One file holds the keys for all her rooms and her DMs |
| [New sessions after a restore in 1.10 Backup and restore](10-backup-and-restore.md#export-and-import) | Bind each session to the receiving installation | Export leaves out session tokens. Import opens new sessions through [1.3 Single-application host](03-host.md) |
| [Forget](#forget) | Remove the application identity and local data | Stop the application, clear its store and host records, delete its encryption and backup keys, and verify cleanup |

## Protected keys and records

### Node encryption key

Core maintainers approve the persistent iOS Keychain and Android Keystore backends under #4137 before their feature PR. Keeping the installation key in platform-protected storage supports private records across restarts and gives lock, key-loss and deletion checks a defined backend. Both platform backends and their device fixtures are release requirements.

Add persistent iOS Keychain and Android Keystore backends to Core's closed `KekBackendKind` enum. File a Core sub-issue of [#4137](https://github.com/freenet/freenet-core/issues/4137) for these backends and Android's rejection of keyring's in-memory mock backend. Use [kek.rs](https://github.com/freenet/freenet-core/blob/e7d0b06c9326f377d250bf8344baaac2ba2658c6/crates/core/src/config/kek.rs) and [#4140](https://github.com/freenet/freenet-core/issues/4140) as implementation references.

On first start, `crates/mobile` creates one encryption key for the node installation and stores it with the backend defined in this plan. Each River or EVY installation has its own node encryption key. EVY's feature records are held by one EVY delegate, following [Application node and key scope in 1.3 Single-application host](03-host.md#application-node-and-key-scope):

| Platform | Where the key lives | Key setting |
| --- | --- | --- |
| iOS | A Keychain item | `kSecAttrAccessibleWhenUnlockedThisDeviceOnly` |
| Android 9 to 11 | A file in the app's storage, encrypted with an Android Keystore AES key | [`setUnlockedDeviceRequired(true)`](https://developer.android.com/reference/android/security/keystore/KeyGenParameterSpec.Builder#setUnlockedDeviceRequired(boolean)) |
| Android 12 to 14 | The same file and Keystore key | Omit the unlocked-device setting to preserve the key when the user removes the lock screen and to allow creation without a lock screen |
| Android 15 and later | The same file and Keystore key | `setUnlockedDeviceRequired(true)` |

- `setUnlockedDeviceRequired` needs Android 9 (API 28), which sets the Android floor in [supported profiles in 1.1 Mobile feasibility and supported profiles](01-feasibility.md#supported-profiles).
- On iOS, Android 9 to 11 and Android 15 and later, the node can read the key only while the phone is unlocked. On Android 12 to 14, the Keystore key also works while the phone is locked. [Locking and unlocking](#locking-and-unlocking) wipes the key from memory on every version.
- [Keys in 1.2 Embedded node and mobile SDK](02-sdk.md#keys) tests each row with and without a lock screen.
- Core records the backend in `secrets_dir/kek_backend` and loads the key only from that backend. The host reports a missing key as `KeyLost`.
- `crates/mobile` sets the umask to `0o077` before it starts any thread, as Core's `freenet` binary does ([#4219](https://github.com/freenet/freenet-core/pull/4219)).
- Keep the key on its owning phone. Exclude the encrypted storage from iCloud and Google device backups. Use app-specific export for recovery because the encrypted files require their installation's key.
- Alice moves her data to a new phone with the backup file from [Export and import in 1.10 Backup and restore](10-backup-and-restore.md#export-and-import).

### What the key protects

Core derives a separate key for each delegate from the node encryption key. The host derives one more key the same way for its own private records. `crates/mobile` turns off Core's secret snapshots ([Storage in 1.2 Embedded node and mobile SDK](02-sdk.md#storage)), so the phone keeps only each secret's current value.

| Record | Where it lives | Protected by | After a restore |
| --- | --- | --- | --- |
| Alice's signing key, room secrets and membership proof for "Skate club" | River's chat delegate store, under `room:<owner key>` | The chat delegate's derived key | Back from the backup file |
| DMs Alice sent | River's chat delegate store | The chat delegate's derived key | Back from the backup file |
| Records the app declares | Host records | The host's derived key | Back from the backup file |
| "Skate club" messages, members and bans | Room contract state on the network | The [room secret](https://github.com/freenet/river/blob/8cf54dd7799514851da7eab051e4cc43f797208d/README.md#privacy-model) and member signatures | The app fetches them from the network |

### Locking and unlocking

Core maintainers approve the `SecretsStore` lock/unlock lifecycle before its feature PR. Platform key protection also needs runtime fencing and controlled-buffer cleanup after a key has been loaded. River and EVY release requires the Core lock lifecycle and the matching host cleanup fixtures on iOS and Android.

File a Core issue to add `lock` and `unlock` to `SecretsStore`, using [store.rs](https://github.com/freenet/freenet-core/blob/e7d0b06c9326f377d250bf8344baaac2ba2658c6/crates/core/src/wasm_runtime/secrets_store/store.rs).

| Event | iOS signal | Android signal | What happens |
| --- | --- | --- | --- |
| Phone locks | `protectedDataWillBecomeUnavailable` | `ACTION_SCREEN_OFF` | Fence new signing and private-data operations, finish in-flight recovery writes within the shutdown budget, invalidate sessions and destroy application WebViews. Release app-owned plaintext copies and wipe controlled buffers, the KEK and every derived key |
| Phone unlocks | `protectedDataDidBecomeAvailable` | `ACTION_USER_PRESENT` | Core reloads the KEK and derived keys through the Keychain or Keystore. The host opens fresh sessions and application contexts and reloads approved application state |

River holds room signing keys and decrypted records in its web UI for local signing. Follow the cleanup requirements in [1.3 Single-application host](03-host.md#opening-suspending-and-reopening-an-app). Use the [application connections in 1.2 Embedded node and mobile SDK](02-sdk.md#application-connections) to replace the application session generation, close private-event routes and cancel prompts.

Inventory each plaintext copy and its owner. On iOS and Android, lock the phone with a River signing key already loaded in page memory. Test session fencing, object disposal and controlled-buffer wiping. Verify Core's zeroizing wrappers with owned test buffers and drop observers ([#5599](https://github.com/freenet/freenet-core/issues/5599)).

```mermaid
stateDiagram-v2
    [*] --> Locked: phone starts
    Locked --> Ready: Alice unlocks, key found
    Locked --> KeyLost: Alice unlocks, key missing
    Ready --> Locked: Alice locks her phone
    KeyLost --> Ready: Alice imports her backup file
    KeyLost --> [*]: Alice forgets the application
```

| State | What the host does |
| --- | --- |
| `Locked` | Returns `Locked` to delegate calls until Alice unlocks. The chat delegate's room secret rotation for rooms Alice owns also waits for the unlock |
| `KeyLost` | Report the missing installation key, retain the encrypted generation and offer application backup restore or Forget. |

When the key is lost, the host quarantines the encrypted generation, creates a replacement installation key in Keychain or Keystore, and stages a supported backup under that key. Persist the quarantine and activation record before opening the restored application. A failed restore retains the quarantined files for retry.

### Forget

Forget resets the application's local installation. The host shows the affected identity, records, keys and backup credentials before the user confirms.

Keep a nonsecret cleanup journal outside the data generation being deleted. The application's lifecycle coordinator:

1. Records cleanup pending, disables backup runs, fences new work and invalidates the identity/session generation.
2. Stops delegates, network connections and the node. Releases the WebView, native private buffers, signing keys and derived-key caches.
3. Deletes current and predecessor delegate records, registrations, declared host records, local backup keys, folder-access grants, temporary exports, snapshots and local public contract caches.
4. Deletes the installation KEK through Core's `KekBackend::delete` and clears node credentials and storage.
5. Verifies deletion in application storage, Keychain or Keystore and host records. Resumes unfinished cleanup on restart before creating a new identity.
6. Reports deletion failures and retained off-device data, then completes the journal after verification.

Erasing the KEK makes retained copies of its encrypted files unreadable. Public room messages remain on Freenet, exported backups remain usable with their recovery code, and the user's other devices keep their own identities. Alice needs her backup to regain an owner key for a room she controls.

A new identity receives a new installation key and fresh sessions. Test Forget during backup setup, export and restore; earlier callbacks remain fenced.

## Application data inventory

Each matching iOS and Android build compiles a trusted `application-inventory/1` registry for River and EVY. The signed release references its inventory ID and schema version; the build policy admits that ID and exact component identities. Export, migration, restore and Forget use this registry.

Each record-set entry declares `id`, `owner`, `schema_version`, storage namespace, export adapter, required coverage, device-only classification and Forget action. Each delegate entry declares exact code/parameters, admitted role and supported generations. The backup manifest authenticates the registry digest and the captured coverage. Missing required sets or substituted registrations fail before staging.

| Record set | Owner and coverage | Export and Forget |
| --- | --- | --- |
| River room identities, room secrets and outbound DMs | Chat delegate; every indexed room and supported predecessor namespace | Export/import; delete and unregister on Forget |
| EVY root seed, private addresses and exact pending signed operations | EVY delegate; every declared feature/purchase scope | Export/import; delete and unregister on Forget |
| Identity/release metadata and migration checkpoints | Host lifecycle coordinator; one complete generation | Export/import compatible state; delete on Forget |
| Drafts, preferences, watched-room/listing demand, block lists and terms/consent choices | Host/reader; identity-bound application records | Export/import; delete on Forget |
| User publisher approvals and key choices | Trusted host; user-selected trust records | Export/import subject to current build policy; delete on Forget |
| Host lifecycle checkpoints | Host; snapshot, activation and pending-operation reconciliation references | Export recoverable references; receiving installation recreates local transaction/control journals |
| Device credentials | Host/platform; KEK, node keys, sessions, sync member/coordinator keys, backup master key, folder grants | Coverage report marks device-only; Forget deletes keys/grants and local copies |
| Build-pinned publisher configuration | Signed native build; public publisher keys, permitted code and inventory definitions | Installed build supplies it; retained through identity reset |
| Public contract caches and UI documents | Node/data layer; release dependencies of drafts, purchases and pending operations | Manifest declares required retained evidence; Forget clears local caches |

Delegate pending records own signed operation bytes and replay context. Host checkpoints own lifecycle progress and reference those operation IDs/digests. Cross-record verification checks both; receiving installations recreate local authority and transaction handles. [1.10 Backup and restore](10-backup-and-restore.md) defines capture and staged activation.

On iOS and Android, inventory fixtures enumerate every required record set, test backup coverage and verify the declared Forget rule for user trust records and build-pinned public configuration.

## Acceptance

- On Android 9 to 11 and Android 15 and later, the node key has `setUnlockedDeviceRequired(true)`. On Android 12 to 14 it does not, and Alice keeps River's data after she removes her lock screen.
- On iOS and Android, locking fences signing, destroys application WebViews, releases native private-data caches and wipes controlled Core/plaintext buffers. Delegate calls return `Locked` until unlock. Tests verify owned-buffer wiping, key-wrapper disposal and stale-session rejection, then obtain fresh contexts and protected state on unlock. A missing key returns `KeyLost` and keeps the encrypted store until import or forget.
- On iOS and Android, Forget during export, backup setup or post-restore key storage fences earlier callbacks. Termination during cleanup resumes the remaining deletions before a new identity starts. Key or folder-grant deletion failures remain visible and retryable.
- On iOS and Android, Forget stops the application, clears local public/private stores and registrations, deletes the KEK and backup keys, and verifies platform cleanup. Retained KEK-encrypted copies become unreadable.
- On iOS and Android, restore one application backup after key loss and restart during recovery. Startup selects the complete restored generation and preserves the quarantine until cleanup is verified.
- The backup integration suite in [1.10 Backup and restore](10-backup-and-restore.md#acceptance) passes with the platform key, lock and Forget suite in this plan.
