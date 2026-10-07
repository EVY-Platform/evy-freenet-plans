# 3.2 Device sync

## Repositories

| Repository | Role | Work in this plan |
| --- | --- | --- |
| [evy](https://github.com/EVY-Platform/evy) | Modified | "Link a device" and "Linked devices" screens in SwiftUI and Compose. Sync library in the EVY delegate; sync and link contracts; merge rules for EVY records |
| [freenet-core](https://github.com/freenet/freenet-core) | Used | Delegate GET, SUBSCRIBE and UPDATE on the network |
| [freenet-stdlib](https://github.com/freenet/freenet-stdlib) | Used | Delegate interface |
| [freenet-appkit](https://github.com/glesage/freenet-appkit) | Used | Swift package and Kotlin library calls to the EVY delegate |

## Purpose

This plan keeps the EVY delegate's records the same on Alice's iPhone and her Android tablet. Core already keeps the contracts both devices read the same, such as Bob's skateboard purchase contract, because both subscribe to them ([Reads and subscriptions in 2.4 SDUI data and actions](../2-evy-on-freenet/04-data-and-actions.md#reads-and-subscriptions)). This plan syncs the records that live only in [The EVY delegate in 2.4 SDUI data and actions](../2-evy-on-freenet/04-data-and-actions.md#the-evy-delegate): `root_seed`, which gives Alice the same EVY keys on both devices, her pending operations in `pending/<service>/<id>` with their replay context, and her private address book in `addresses/<id>`.

The EVY delegate follows the sync design proposed in [RFC #5587](https://github.com/freenet/freenet-core/issues/5587), which builds on the encrypted CRDT sync RFC [#4560](https://github.com/freenet/freenet-core/issues/4560):

- One group seed, held only by Alice's linked devices, derives the keys that encrypt, sign and address each record.
- Records live as ciphertext in sync contracts. Two concurrent writes stay as two values until the EVY delegate resolves them.
- The namespace is `evy`, not the EVY delegate's code hash, so devices on different EVY builds still sync.

RFC #5587 proposes a sync delegate that app delegates call. Messages between delegates go one way in Core today, so the EVY delegate compiles the sync code in as a library. RFC #5587 is an open proposal with no owner yet.

## Linking and removing a device

| Step | Who | What happens |
| --- | --- | --- |
| 1. Start | Alice, on the iPhone | EVY's "Link a device" screen shows a QR code with a one-time key and the key of a short-lived link contract |
| 2. Scan | Alice, on the tablet | On a new EVY install, "Link to my other device" scans the code. The tablet writes its own one-time key to the link contract |
| 3. Compare | Both devices | Each shows a 6-digit code derived from both one-time keys. Alice confirms on the iPhone that they match |
| 4. Join | iPhone, then tablet | The iPhone sends the group seed encrypted to the tablet's one-time key. The tablet's EVY delegate drops the unused `root_seed` it made on first start and reads the sync contracts<br>--> Produces Alice's EVY keys and pending records on the tablet |

The exchange has the shape of Core's rendezvous design for device pairing ([#992](https://github.com/freenet/freenet-core/issues/992)).

Alice removes the tablet on the iPhone's "Linked devices" screen. The iPhone makes a new group seed and sends it only to the devices that stay. The tablet keeps every record it synced before removal, including Alice's EVY keys, and the screen lists them. To stop the tablet signing as Alice, she forgets EVY on it as [Forget in 1.5 Identity, keys and local protection](../1-freenet-mobile-appkit/05-identity.md#forget) describes. RFC #5587 lists device revocation as an open question, so EVY proposes this exchange and seed rotation there.

A phone restored from the backup in [3.1 Automated backup](01-backup.md) holds the group seed from the file. It rejoins the group, unless Alice removed a device after that backup.

## Resolving conflicts

On the train to Saturday's pickup, Alice's iPhone is offline. She edits her skateboard listing, adds a photo of the wheels and closes EVY. The signed edit waits in the EVY delegate as `pending/marketplace/<item id>`, as [Offline writes in 2.4 SDUI data and actions](../2-evy-on-freenet/04-data-and-actions.md#offline-writes) describes. At the pickup, she confirms the handover on her tablet, and the tablet clears the skateboard's pending records. When the iPhone reconnects, the two devices hold different values:

| Record | iPhone, offline on the train | Android tablet, at the pickup | After the merge |
| --- | --- | --- | --- |
| Pending edit of the skateboard listing | New photo of the wheels | Cleared when Alice confirmed the handover | The edit stays, marked as for a sold item. EVY asks Alice to discard it or start a new listing from it |
| Skateboard status | `pickup_pending`, last read | `sold` | Both read `sold` from Marketplace's contracts through Core ([What is cloned in 2.7 EVY Marketplace](../2-evy-on-freenet/07-marketplace.md#what-is-cloned)) |

The EVY delegate also syncs the private address-book records from [The EVY delegate in 2.4 SDUI data and actions](../2-evy-on-freenet/04-data-and-actions.md#the-evy-delegate). Concurrent address edits retain both values for Alice to choose or combine; the resolved record replaces the siblings. Each purchase keeps the sealed address copy signed into its acceptance message.

The EVY delegate's merge rules:

- An edit beats a concurrent clear, so a merge never loses Alice's work.
- A pending edit for an item that its contract shows as `sold` is never sent.
- Records that only one device changed take that device's value.
- The resolved value replaces both concurrent values on every device, as RFC #5587 proposes.

## Traffic and lifecycle

- On iOS and Android, each device syncs only while EVY is in the foreground ([foreground lifecycle in 1.1 Mobile feasibility and supported profiles](../1-freenet-mobile-appkit/01-feasibility.md#foreground-lifecycle)). An edit reaches the tablet when it next opens EVY and the sync state remains available within the pinned Core build's hosting budget.
- Sync bytes count under the [cellular budget contract in 1.8 Thin-peer role and cellular data budgets](../1-freenet-mobile-appkit/08-thin-peer.md#cellular-budget-contract). At a cap, sync pauses with the rest of the node's network work. We asked on RFC #5587 for shards smaller than the proposed 2 to 4 MiB. Device runs that sync one pending record on cellular set the size.
- If peers drop a sync contract, a device that holds a copy puts it again, as River restores a room in [Lost network state in 1.6 Application protocols, data and operations](../1-freenet-mobile-appkit/06-data-and-operations.md#lost-network-state).
- The group seed is an EVY delegate record in the node's encrypted secret store. Forgetting EVY deletes its owned root seed, group seed, private addresses and pending operations and revokes its sessions and grants, following [Forget in 1.5 Identity, keys and local protection](../1-freenet-mobile-appkit/05-identity.md#forget). Backup cleanup follows [Forget and backup cleanup in 3.1 Automated backup](01-backup.md#forget-and-backup-cleanup), including EVY's separate backup key, folder access and active exports. The shared node KEK continues protecting other applications' data. Whole-node reset erases that KEK and resets every application attached to the store.

Stronger retention and offline delivery, including availability while every linked device's node is stopped, follow the deferred [Core retention and delivery research](../UPSTREAM_ISSUES.md#core-retention-and-delivery-research). This plan adopts those guarantees when Core supplies them. Recovery uses a device that still holds the records or the backup from [3.1 Automated backup](01-backup.md).

## What Core still needs

| Need | Issue |
| --- | --- |
| Agreement on the sync design that the EVY delegate's library follows | [RFC #5587](https://github.com/freenet/freenet-core/issues/5587) |
| Delegates update contracts they do not yet hold. GET and SUBSCRIBE reach the network ([#5615](https://github.com/freenet/freenet-core/pull/5615)). Before its first UPDATE to a sync contract, the EVY delegate reads it | [#5542](https://github.com/freenet/freenet-core/issues/5542) |
| Delegate subscriptions register hosting demand while the node runs and restore subscriptions when it restarts | [#4669](https://github.com/freenet/freenet-core/issues/4669) |
| A delegate GET tells a missing sync contract from a failed lookup, so a new device never starts an empty group by mistake | [stdlib #131](https://github.com/freenet/freenet-stdlib/issues/131) |

## Acceptance

- On iOS and Android, Alice links her Android tablet to her iPhone. Her EVY keys and pending records reach the tablet, and the tablet finds Bob's skateboard purchase through her item. The same works with an Android phone linking an iPad.
- On iOS and Android, a device that scans the QR code gets no group seed when Alice does not confirm or the 6-digit codes differ.
- On iOS and Android, the train-and-pickup case ends with the skateboard sold on both devices and the wheels edit kept and marked, on a pinned evy revision.
- On iOS and Android, after Alice removes the tablet, records she changes on the iPhone do not reach it, and the removal screen lists what it kept.
- On iOS and Android, a device offline for a week, or killed during an upload, converges when EVY next opens with sync state retained within the pinned Core hosting budget. Eviction recovery uses a device holding a copy or its backup; stronger delivery guarantees follow Core retention work.
- On iOS and Android, two devices on different EVY delegate builds still sync.
- On iOS and Android, sync traffic on cellular stays inside the caps in 1.8 Thin-peer role and cellular data budgets, and sync pauses at a cap.
- On iOS and Android, forgetting EVY makes the synced records unreadable on that device and leaves the other device working.
