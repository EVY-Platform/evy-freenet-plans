# 3.2 Device sync

## Repositories

| Repository | Role | Work in this plan |
| --- | --- | --- |
| [evy](https://github.com/EVY-Platform/evy) | Modified | "Link a device" and "Linked devices" screens in SwiftUI and Compose. Sync library in the EVY delegate; sync and link contracts; merge rules for EVY records |
| [freenet-core](https://github.com/freenet/freenet-core) | Used | Delegate GET, SUBSCRIBE and UPDATE on the network |
| [freenet-stdlib](https://github.com/freenet/freenet-stdlib) | Used | Delegate interface |
| [freenet-appkit](https://github.com/glesage/freenet-appkit) | Used | Swift package and Kotlin library calls to the EVY delegate |

## Purpose

This plan syncs the EVY delegate's records between Alice's iOS and Android devices. Both devices subscribe to contracts, such as Bob's skateboard purchase contract. Core delivers updates to both ([Reads and subscriptions in 2.4 SDUI data and actions](../2-evy-on-freenet/04-data-and-actions.md#reads-and-subscriptions)).

This plan syncs the device-local records held by [The EVY delegate in 2.4 SDUI data and actions](../2-evy-on-freenet/04-data-and-actions.md#the-evy-delegate):

| Record | What both devices receive |
| --- | --- |
| `root_seed` | The seed that derives Alice's EVY keys |
| `pending/<service>/<id>` | Pending operations and their replay context |
| `addresses/<id>` | Private address-book entries |

The EVY delegate follows the sync design proposed in [RFC #5587](https://github.com/freenet/freenet-core/issues/5587), which builds on the encrypted CRDT sync RFC [#4560](https://github.com/freenet/freenet-core/issues/4560):

- One group seed, held only by Alice's linked devices, derives the keys that encrypt, sign and address each record.
- Records live as ciphertext in sync contracts. Two concurrent writes stay as two values until the EVY delegate resolves them.
- The stable `evy` namespace lets devices on different EVY builds sync.

The EVY delegate compiles the sync code as a library. This supports Core's one-way messages between delegates. Adopting RFC #5587 also requires agreement on the proposal and an owner for the work.

## Linking and removing a device

| Step | Who | What happens |
| --- | --- | --- |
| 1. Start | Alice, on her iOS phone | EVY's "Link a device" screen shows a QR code with a one-time key and the key of a short-lived link contract |
| 2. Scan | Alice, on her Android tablet | On a new EVY install, "Link to my other device" scans the code. The tablet writes its own one-time key to the link contract |
| 3. Compare | Both devices | Each shows a 6-digit code derived from both one-time keys. Alice confirms on her iOS phone that they match |
| 4. Join | iOS phone, then Android tablet | The phone encrypts the group seed to the tablet's one-time key and sends it. The tablet's EVY delegate discards its initial `root_seed` and reads the sync contracts. The tablet now holds Alice's EVY keys and pending records |

The exchange follows Core's rendezvous design for device pairing ([#992](https://github.com/freenet/freenet-core/issues/992)).

Alice removes the Android tablet on the iOS phone's "Linked devices" screen. The phone creates a new group seed and sends it to the remaining devices. The removal screen lists the records the tablet keeps, including Alice's EVY keys. To revoke its ability to sign as Alice, she uses Forget on the tablet, following [Forget in 1.5 Identity, keys and local protection](../1-freenet-mobile-appkit/05-identity.md#forget).

EVY proposes this exchange and seed rotation in RFC #5587 as its device-revocation design.

A phone restored from the backup in [3.1 Automated backup](01-backup.md) holds the group seed from the file. It rejoins the group when the backup's group seed still matches the current group.

## Resolving conflicts

On the train to Saturday's pickup, Alice's iOS phone is offline. She edits her skateboard listing, adds a photo of the wheels and closes EVY. The signed edit waits in the EVY delegate as `pending/marketplace/<item id>`, as [Offline writes in 2.4 SDUI data and actions](../2-evy-on-freenet/04-data-and-actions.md#offline-writes) describes. At the pickup, she confirms the handover on her Android tablet. The tablet clears the skateboard's pending records. When the phone reconnects, the devices hold different values:

| Record | iOS phone, offline on the train | Android tablet, at the pickup | After the merge |
| --- | --- | --- | --- |
| Pending edit of the skateboard listing | New photo of the wheels | Cleared when Alice confirmed the handover | The edit stays, marked as for a sold item. EVY asks Alice to discard it or start a new listing from it |
| Skateboard status | `pickup_pending`, last read | `sold` | Both read `sold` from Marketplace's contracts through Core ([What is cloned in 2.7 EVY Marketplace](../2-evy-on-freenet/07-marketplace.md#what-is-cloned)) |

The EVY delegate also syncs the private address-book records from [The EVY delegate in 2.4 SDUI data and actions](../2-evy-on-freenet/04-data-and-actions.md#the-evy-delegate). Concurrent address edits retain both values for Alice to choose or combine; the resolved record replaces the siblings. Each purchase keeps the sealed address copy signed into its acceptance message.

The EVY delegate applies these merge rules:

- Keep an edit when it conflicts with a concurrent clear.
- Hold a pending edit when the item's contract shows `sold`. Ask Alice to discard it or use it in a new listing.
- Records that only one device changed take that device's value.
- The resolved value replaces both concurrent values on every device, as RFC #5587 proposes.

## Traffic and lifecycle

- On iOS and Android, each device syncs while EVY is in the foreground ([Foreground lifecycle in 1.1 Mobile feasibility and supported profiles](../1-freenet-mobile-appkit/01-feasibility.md#foreground-lifecycle)). The tablet receives an edit the next time Alice opens EVY, provided the sync state remains available within the pinned Core build's hosting budget.
- Sync bytes count under the [cellular budget contract in 1.8 Thin-peer role and cellular data budgets](../1-freenet-mobile-appkit/08-thin-peer.md#cellular-budget-contract). At a cap, sync pauses with the rest of the node's network work. EVY proposes shards smaller than 2 to 4 MiB in RFC #5587. Cellular tests that sync one pending record determine the shard size.
- If peers drop a sync contract, a device that holds a copy puts it again, as River restores a room in [Lost network state in 1.6 Application protocols, data and operations](../1-freenet-mobile-appkit/06-data-and-operations.md#lost-network-state).
- The group seed is an EVY delegate record in the node's encrypted secret store. Forgetting EVY deletes its owned root seed, group seed, private addresses and pending operations and revokes its sessions and grants, following [Forget in 1.5 Identity, keys and local protection](../1-freenet-mobile-appkit/05-identity.md#forget). Backup cleanup follows [Forget and backup cleanup in 3.1 Automated backup](01-backup.md#forget-and-backup-cleanup), including EVY's separate backup key, folder access and active exports. The shared node KEK continues protecting other applications' data. Whole-node reset erases that KEK and resets every application attached to the store.

[Core retention and delivery research](../UPSTREAM_ISSUES.md#core-retention-and-delivery-research) covers stronger retention and availability while every linked device's node is stopped. This plan adopts those guarantees when Core supplies them. Recovery uses a device that still holds the records or the backup from [3.1 Automated backup](01-backup.md).

## What Core still needs

| Need | Issue |
| --- | --- |
| Agreement on the sync design that the EVY delegate's library follows | [RFC #5587](https://github.com/freenet/freenet-core/issues/5587) |
| Delegate UPDATE reaches contracts beyond the local store. GET and SUBSCRIBE reach the network ([#5615](https://github.com/freenet/freenet-core/pull/5615)). The EVY delegate reads a sync contract before its first UPDATE | [#5542](https://github.com/freenet/freenet-core/issues/5542) |
| Delegate subscriptions register hosting demand while the node runs and restore subscriptions when it restarts | [#4669](https://github.com/freenet/freenet-core/issues/4669) |
| Delegate GET distinguishes a missing sync contract from a failed lookup. A new device creates an empty group only after confirming the contract is missing | [stdlib #131](https://github.com/freenet/freenet-stdlib/issues/131) |

## Acceptance

- On iOS and Android, Alice links her Android tablet to her iPhone. Her EVY keys and pending records reach the tablet, and the tablet finds Bob's skateboard purchase through her item. The same works with an Android phone linking an iPad.
- On iOS and Android, a device that scans the QR code receives the group seed only after Alice confirms matching 6-digit codes.
- On iOS and Android, the train-and-pickup case ends with the skateboard sold on both devices and the wheels edit kept and marked, on a pinned evy revision.
- On iOS and Android, removing a device restricts subsequent changed records to the remaining linked devices. The removal screen lists the records the removed device keeps.
- On iOS and Android, a device offline for a week, or killed during an upload, converges when EVY next opens with sync state retained within the pinned Core hosting budget. Eviction recovery uses a device holding a copy or its backup; stronger delivery guarantees follow Core retention work.
- On iOS and Android, two devices on different EVY delegate builds still sync.
- On iOS and Android, sync traffic on cellular stays inside the caps in 1.8 Thin-peer role and cellular data budgets, and sync pauses at a cap.
- On iOS and Android, forgetting EVY makes the synced records unreadable on that device and leaves the other device working.
