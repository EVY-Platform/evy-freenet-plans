# 3.2 Device sync

## Repositories

| Repository | Role | Work in this plan |
| --- | --- | --- |
| [evy](https://github.com/EVY-Platform/evy) | Modified | "Link a device" and "Linked devices" screens in SwiftUI and Compose. Sync library in the EVY delegate; sync and link contracts; merge rules for EVY records |
| [freenet-core](https://github.com/freenet/freenet-core) | Modified | Delegate network operations and proposed trusted mobile calls for device credential signing and seed unwrapping |
| [freenet-stdlib](https://github.com/freenet/freenet-stdlib) | Used | Delegate interface |
| [freenet-appkit](https://github.com/glesage/freenet-appkit) | Modified | Swift and Kotlin bindings for the proposed device credential calls and EVY delegate sync interface |

## Purpose

This plan syncs the EVY delegate's records between Alice's iOS and Android devices. Both devices subscribe to contracts, such as Bob's skateboard purchase contract. Core delivers updates to both ([Reads and subscriptions in 2.4 SDUI data and actions](../2-evy-on-freenet/04-data-and-actions.md#reads-and-subscriptions)).

This plan syncs the device-local records held by [The EVY delegate in 2.11 EVY delegate and private records](../2-evy-on-freenet/11-delegate-and-private-records.md#the-evy-delegate):

| Record | What both devices receive |
| --- | --- |
| `root_seed` | The seed that derives Alice's EVY keys |
| `pending/<service>/<id>` | Pending operations and their replay context |
| `addresses/<id>` | Private address-book entries |

The EVY delegate follows the sync design proposed in [RFC #5587](https://github.com/freenet/freenet-core/issues/5587), which builds on the encrypted CRDT sync RFC [#4560](https://github.com/freenet/freenet-core/issues/4560):

- Each membership epoch has a group seed that derives purpose-separated encryption and addressing keys. Each device has its own signing and key-agreement credentials; contracts authorize writes against the epoch's signed membership manifest.
- Records live as ciphertext in sync contracts. Two concurrent writes stay as two values until the EVY delegate resolves them.
- The stable `evy` namespace and versioned record envelopes provide the compatibility boundary between supported EVY builds.

The EVY delegate compiles sync code as a library using Core's existing one-way delegate messages. This plan proposes the protocol below for RFC #5587. Implementation starts after protocol agreement, security review and assignment of a named owner. The proposed work includes host and delegate integration for device credentials.

## Membership and authority

The first device creates a random group ID and becomes its membership coordinator. Membership changes use one coordinator and one separate recovery authority:

| Part | Required state and authority |
| --- | --- |
| Device credentials | Each installation creates an Ed25519 membership/write key, an X25519 envelope key and a random replica ID. Private credentials stay in device-only protected host storage on iOS and Android. Trusted host calls sign membership/data requests and unwrap epoch seeds for the EVY delegate. The runtime binds each call to the active EVY identity and verified sync context. The backup coverage report lists these credentials as device-only |
| Coordinator | One current member serializes link, removal and coordinator-transfer requests. A durable journal reserves each membership sequence and saves one complete signed manifest before publication. Retries replay its exact bytes. The journal and signing authority are device-only |
| Recovery authority | A separate Ed25519 recovery key establishes the group at creation. Alice saves it with its monotonic generation journal in a separately encrypted recovery file and verifies a recovery drill. The recovery key remains outside the linked devices' routine sync and backup records. Each use locks the journal, reserves a higher authority generation and saves its signed recovery checkpoint before publication |
| Membership manifest | First form a canonical descriptor containing group ID, authority generation, sequence, predecessor digest, coordinator public key, member signing/envelope keys, removed member IDs, record-format requirements and encrypted checkpoint digests. Hash that descriptor, then create member seed envelopes bound to its digest. The final signed manifest contains the descriptor and envelope digests. The coordinator signs ordinary changes; the recovery authority signs higher-generation recovery checkpoints |
| Ordering | Compare authority generation first and sequence second. An ordinary successor must extend the accepted predecessor and be signed by its authorized coordinator. A transfer names the next coordinator. Each device persists its accepted manifest digest and ordering floor before it accepts the epoch seed or writes data |
| Seed delivery | Each epoch creates a fresh seed and wraps it separately to every retained member's envelope key, binding group ID, epoch, member ID and descriptor digest as authenticated context. The coordinator retains the manifest, encrypted envelopes and checkpoint until every retained member acknowledges installation or a later membership change removes that member |
| Data writes | Each encrypted record envelope binds group ID, epoch, namespace, schema version, member ID, replica ID, causal context and ciphertext. Its member signature authorizes the write against the epoch manifest. Fresh epoch contracts and addressing keys separate each epoch's writes. Contract parameters pin the group ID, epoch and signed manifest digest; supplied manifest evidence must match that digest and verify through the group's authority chain before a member signature authorizes a write |

The membership contract has a fixed address derived from its code, group ID and recovery verifying key. Its state retains signed authority changes and fork evidence under deterministic merge rules. Encrypted checkpoints are content-addressed by their bytes; their digests are computed before the descriptor and their contract parameters are independent of the final manifest.

The coordinator verifies that its latest journal entry matches a verified current manifest before processing the next request. Failed lookups leave membership work pending. Concurrent requests enter that same queue; a removal takes effect when its manifest, seed envelopes and checkpoint are durable, the coordinator has read them back through another peer, and the local epoch switch is committed. Other members apply that change when they refresh the manifest. A member returning online refreshes membership before publishing its queued records.

Coordinator transfer is a journaled membership change signed by the current coordinator. The target acknowledges its saved coordinator journal before activation; the former coordinator retires its authority after committing the transfer. After a crash, both follow the committed transfer record. A coordinator restored from ordinary backup rejoins as a fresh device.

Conflicting signed manifests with the same predecessor or ordering position produce a visible membership conflict and preserve both pieces of evidence. Devices pause membership changes and data publication until the recovery authority publishes a higher-generation checkpoint naming the accepted branch and evidence digests. This gives one explicit recovery path for a fork. Recovery also replaces a lost coordinator: Alice verifies retained-device checkpoints, chooses the surviving members, creates a fresh seed and coordinator, and signs the higher generation with the recovery key. When the recovery journal's highest generation cannot be established from its saved copy and verified group evidence, Alice creates a new group from her recovered records and pairs devices again.

### Linking a device

Pairing uses Core's rendezvous proposal ([#992](https://github.com/freenet/freenet-core/issues/992)) as prior art. The protocol and its test vectors are reviewed with RFC #5587.

| Step | Who | What happens |
| --- | --- | --- |
| 1. Start | Alice, on the coordinator's iOS or Android device | EVY creates a random 256-bit invitation secret, invitation ID and ephemeral X25519 key, with a 10-minute local expiry. The QR code binds them to the group ID, current manifest digest and link-contract key |
| 2. Scan | Alice, on the new Android or iOS device | The new installation creates its device credentials and fresh replica ID. It sends its public credentials and ephemeral key with proof of the invitation secret |
| 3. Compare | Both devices | Each shows a 6-digit code from the full pairing transcript: group and invitation IDs, current manifest digest, both ephemeral keys and both devices' public credentials. Alice confirms the codes on both devices |
| 4. Approve | Coordinator | It accepts at most three authenticated candidate transcripts per invitation, permits one outstanding invitation and consumes the invitation on approval, expiry or the third failed attempt. It journals a membership change binding the approved device credentials |
| 5. Join | Both devices | The coordinator publishes the new epoch manifest, checkpoint and member-specific seed envelopes. The new device verifies the manifest and transcript binding, unwraps its envelope and stages the group's records. It activates the imported EVY identity through [1.10 Backup and restore](../1-freenet-mobile-appkit/10-backup-and-restore.md#staged-restore-transaction) before opening the application |

Expired, consumed or replayed invitations produce a fresh-pairing prompt. A process restart expires an incomplete invitation. A membership change during pairing requires a new invitation against the current manifest. The protocol limits link-contract size and candidate messages, and ignores unauthenticated candidates before counting expensive cryptographic work.

### Removing a device

Alice requests removal from a remaining iOS or Android device. The coordinator confirms the named device and commits the next epoch through the serialized membership path. It signs a checkpoint of the current records and causal metadata, rotates the group seed, re-encrypts the checkpoint into the new epoch and issues envelopes to the remaining devices. Concurrent removal requests are applied in order against the resulting membership. Removing the coordinator first transfers its role or uses the recovery authority.

An offline remaining device obtains its retained envelope when EVY next opens, verifies the complete membership chain and current checkpoint, and merges its queued edits with the checkpoint's causal context and tombstones. The coordinator keeps the envelope and checkpoint available within the supported hosting budget and can republish its retained copy. Until it installs the current epoch, the returning device keeps its edits locally and reports that sync is waiting for membership refresh.

The removal screen states the effective epoch and which remaining devices have acknowledged it. Future sync access is restricted by that epoch. The removed device retains the EVY signing keys and plaintext it already received. Local Forget erases its local copy under [1.5 Identity, keys and local protection](../1-freenet-mobile-appkit/05-identity.md#forget); control of those application signing keys follows their application's own revocation rules. A device that is offline at removal can retain and edit its previous-epoch copy; those writes stay outside the new epoch until an authorized member explicitly reviews and imports their data.

## Recovery and mixed versions

The EVY delegate's `ExportRecords` and `ImportRecords` include the sync group ID, accepted manifest and ordering floor, supported epoch seeds, encrypted checkpoint references, record-schema versions, causal contexts and tombstones. [3.1 Automated backup](01-backup.md) captures them with the user's records in one consistent snapshot. The separate recovery file holds the recovery key and generation journal; routine backups cover user data and group recovery context.

| Situation | Recovery rule |
| --- | --- |
| A fresh device restores an ordinary backup | Restore its records locally, generate fresh device credentials and a fresh replica ID, then ask the current coordinator to approve membership through pairing. Restored counters and credentials serve as historical evidence; the fresh replica starts its own counter. Group writes begin after it has installed the current manifest and merged its snapshot with current causal metadata |
| The backup predates a removal or seed rotation | Treat its epoch as historical. The current coordinator approves a new device and supplies a current envelope, or Alice uses the separate recovery authority. Possession of an earlier seed or backup alone grants access to that earlier snapshot |
| A removed device restores its backup | It recovers the records it held. Joining the current group requires a new approval by its current membership authority |
| All devices are lost | Alice restores user data and uses the separately held recovery authority to select a fresh coordinator and member set in a higher generation. It rotates the seed and publishes a new checkpoint. With user data alone, Alice creates a new group and pairs devices again |
| A retained device has edits from an earlier epoch | Merge their original causal context with current records and tombstones. Preserve concurrent edits as siblings. User approval of a recovered draft creates a new current-epoch operation after normal target-state and permission checks |
| Tombstones or causal history approach the storage cap | Pause additions that exceed the cap and offer device cleanup or a new checkpoint. Compact history only after every retained member acknowledges a checkpoint that includes it. Rejoining restored devices merge against that checkpoint before publishing |

Each record envelope has a major schema version, required features and a versioned merge rule. The `evy` namespace names the single application dataset. Both iOS and Android builds run compatibility fixtures for every supported pair of delegate releases. Readers preserve unknown optional fields byte-for-byte. An unsupported major version or required feature pauses writes to the EVY dataset, preserves its signed bytes and shows the required EVY update. Migration publishes a new format only after all retained devices support it or Alice removes the incompatible devices. Membership and causal metadata remain independently readable throughout the migration.

Keep adapter versions and private-record schema versions in the shared compatibility registry consumed by readers, delegate, backup and migration. Unsupported required versions retain exact authenticated bytes and pause EVY dataset writes. Resume after every retained device supports the format or an authorized membership removal excludes it, then verify checkpoint/causal continuity before writing.

## Resolving conflicts

On the train to Saturday's pickup, Alice's iOS phone is offline. She edits her skateboard listing, adds a photo of the wheels and closes EVY. The signed edit waits in the EVY delegate as `pending/marketplace/<item id>`, as [Offline writes in 2.4 SDUI data and actions](../2-evy-on-freenet/04-data-and-actions.md#offline-writes) describes. At the pickup, she confirms the handover on her Android tablet. The tablet clears the skateboard's pending records. When the phone reconnects, the devices hold different values:

| Record | iOS phone, offline on the train | Android tablet, at the pickup | After the merge |
| --- | --- | --- | --- |
| Pending edit of the skateboard listing | New photo of the wheels | Cleared when Alice confirmed the handover | The edit stays, marked as for a sold item. EVY asks Alice to discard it or start a new listing from it |
| Skateboard status | `pickup_pending`, last read | `sold` | Both read `sold` from Marketplace's contracts through Core ([What is cloned in 2.7 EVY Marketplace](../2-evy-on-freenet/07-marketplace.md#what-is-cloned)) |

The EVY delegate also syncs the private address-book records from [The EVY delegate in 2.11 EVY delegate and private records](../2-evy-on-freenet/11-delegate-and-private-records.md#the-evy-delegate). Concurrent address edits retain both values for Alice to choose or combine; the resolved record replaces the siblings. Each purchase keeps the sealed address copy signed into its acceptance message.

The EVY delegate applies these merge rules:

- Keep an edit when it conflicts with a concurrent clear.
- Hold a pending edit when the item's contract shows `sold`. Ask Alice to discard it or use it in a new listing.
- Records that only one device changed take that device's value.
- The resolved value replaces both concurrent values on every device, as RFC #5587 proposes.

## Traffic and lifecycle

- On iOS and Android, each device syncs while EVY is in the foreground ([Foreground lifecycle in 1.1 Mobile feasibility and supported profiles](../1-freenet-mobile-appkit/01-feasibility.md#foreground-lifecycle)). The tablet receives an edit the next time Alice opens EVY, provided the sync state remains available within the pinned Core build's hosting budget.
- Sync bytes count under the [cellular budget contract in 1.11 Cellular data and resource budgets](../1-freenet-mobile-appkit/11-cellular-data-and-resource-budgets.md#cellular-budget-contract). At a cap, sync pauses with the rest of the node's network work. EVY proposes shards smaller than 2 to 4 MiB in RFC #5587. Cellular tests that sync one pending record determine the shard size.
- If peers drop a sync contract, a device that holds a copy puts it again, as River restores a room in [Lost network state in 1.6 Application protocols, data and operations](../1-freenet-mobile-appkit/06-data-and-operations.md#lost-network-state).
- Epoch seeds and group records live in the EVY delegate's encrypted secret store; member credentials and the coordinator journal use device-only host storage. Forgetting EVY deletes its owned root seed, epoch seeds, group records, private addresses, pending operations and device credentials, and revokes its sessions and grants, following [Forget in 1.5 Identity, keys and local protection](../1-freenet-mobile-appkit/05-identity.md#forget). Backup cleanup follows [Forget and backup cleanup in 3.1 Automated backup](01-backup.md#forget-and-backup-cleanup), including EVY's separate backup key, folder access and active exports. Forget erases that installation's KEK and verifies deletion of its complete local store. Each linked EVY installation keeps its own node, store and device credentials.

[Core retention and offline delivery in 1.6 Application protocols, data and operations](../1-freenet-mobile-appkit/06-data-and-operations.md#core-retention-and-offline-delivery) covers stronger retention and availability while every linked device's node is stopped. This plan adopts those guarantees when Core supplies them. Recovery uses a device that still holds the records or the backup from [3.1 Automated backup](01-backup.md).

## What Core still needs

Core maintainers agree #5587's protocol and approve the trusted device-signing/seed-unwrapping interfaces before their feature PRs. The EVY identity owner records security review and implementation ownership. Member-specific credentials support device removal and seed rotation while keeping routine application keys in the delegate; this optional feature releases after the agreed Core scope and iOS and Android pairing, revocation and recovery fixtures pass.

| Need | Issue |
| --- | --- |
| Agree the sync protocol, complete security review and name an owner. Cover the membership, recovery and mixed-version rules above, including host signing and seed-unwrapping calls with Swift and Kotlin bindings | [RFC #5587](https://github.com/freenet/freenet-core/issues/5587) |
| Delegate UPDATE reaches contracts beyond the local store. GET and SUBSCRIBE reach the network ([#5615](https://github.com/freenet/freenet-core/pull/5615)). The EVY delegate reads a sync contract before its first UPDATE | [#5542](https://github.com/freenet/freenet-core/issues/5542) |
| Delegate subscriptions register hosting demand while the node runs and restore subscriptions when it restarts | [#4669](https://github.com/freenet/freenet-core/issues/4669) |
| Delegate GET distinguishes a missing sync contract from a failed lookup. Create fresh groups with a new random group ID. For an existing group with a missing contract, recover a retained copy or explicitly create a new group | [stdlib #131](https://github.com/freenet/freenet-stdlib/issues/131) |

## Acceptance

- On iOS and Android, Alice links her Android tablet to her iPhone. Her EVY keys and pending records reach the tablet, and the tablet finds Bob's skateboard purchase through her item. The same works with an Android phone linking an iPad.
- On iOS and Android, pairing binds both devices' credentials and the current manifest to matching 6-digit codes confirmed on both devices. Fixtures cover transcript substitution, expired/replayed invitations, membership changes, three failed attempts and process restart. A valid approval creates one membership change.
- On iOS and Android, the train-and-pickup case ends with the skateboard sold on both devices and the wheels edit kept and marked, on a pinned evy revision.
- On iOS and Android, removal installs a fresh epoch with envelopes for the remaining members. The removed device's key fails authorization on the new contracts. The removal screen lists the effective epoch, acknowledgements and retained plaintext/application signing keys. Offline members refresh the epoch before publishing and preserve concurrent edits.
- On iOS and Android, a device offline for a week, or killed during an upload, converges when EVY next opens with sync state retained within the pinned Core hosting budget. Eviction recovery uses a device holding a copy or its backup; stronger delivery guarantees follow Core retention work.
- On iOS and Android, every supported pair of EVY delegate builds exchanges versioned records with the same merge result and preserved optional fields. An unsupported required format pauses EVY dataset writes, retains recoverable bytes and shows an update action. Format migration waits for every retained member's support.
- On iOS and Android, sync traffic on cellular stays inside the caps in [1.11 Cellular data and resource budgets](../1-freenet-mobile-appkit/11-cellular-data-and-resource-budgets.md#cellular-budget-contract), and sync pauses at a cap.
- On iOS and Android, forgetting EVY makes the synced records unreadable on that device and leaves the other device working.

- On iOS and Android, concurrent removals serialize through one coordinator journal. Termination before and after publication or activation replays one signed manifest. Coordinator transfer recovers to one authorized successor. A conflicting signed branch pauses publication and resumes only after a verified higher-generation recovery checkpoint.
- On iOS and Android, a member offline through two rotations receives its current seed envelope and checkpoint after restart. Replayed manifests and substituted envelope recipients fail validation. A lost coordinator is replaced through the separate recovery authority; ordinary backup restore requests membership as a fresh device.
- On iOS and Android, restore a backup made before removal, before a deletion and before a record-schema upgrade. The new installation receives fresh device and replica IDs, obtains current authorization and merges against current tombstones. A removed device's old backup grants its historical data; current group access requires fresh approval.
- On iOS and Android, a restored replica produces unique causal dots while its original device remains active. Tombstone compaction requires every retained member's checkpoint acknowledgement, and capacity exhaustion preserves records with a visible recovery action.
