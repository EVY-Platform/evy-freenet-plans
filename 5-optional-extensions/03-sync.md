# 5.3 Device sync

## Repositories

| Repository | Role | Work in this plan |
| --- | --- | --- |
| [freenet-core](https://github.com/freenet/freenet-core) | Modified | `crates/mobile` runs Core's sync delegate ([#5587](https://github.com/freenet/freenet-core/issues/5587)) in each app's secret scope and counts sync traffic against the cellular budgets |
| [river](https://github.com/freenet/river) | Modified | The chat delegate stores its records through the sync delegate. River saves unhides in `outbound_dms`, merges two concurrent copies of each record and gets a "Link a device" page in its web UI |
| [evy](https://github.com/EVY-Platform/evy) | Modified | Device list, link and remove screens, and the per-app sync switch, in the iOS and Android apps |
| `freenet-appkit` | Modified | The Swift and Kotlin packages expose linking, removal and sync status to the EVY iOS and Android apps |

## Purpose

This plan keeps River's private records the same on Alice's phone and her laptop. She owns "Skate club" and runs River in EVY on her iPhone or Android phone, and in the browser on her laptop. Core already syncs the room, because both nodes subscribe to "Skate club" ([Sending updates in 1.6 Application protocols, data and operations](../1-freenet-mobile-appkit/06-data-and-operations.md#sending-updates)). This plan syncs the records that live only in River's [chat delegate](https://github.com/freenet/river/blob/main/ui/src/components/app/chat_delegate.rs). Her signing key and room secret sit under `room:<owner key>`, her room list settings under `rooms_meta`, and her sent DMs and hidden threads under `outbound_dms`.

EVY uses Core's sync delegate from [RFC #5587](https://github.com/freenet/freenet-core/issues/5587). It encrypts each record with a group seed that only Alice's linked devices hold, and keeps two concurrent writes as two values for the app to resolve. The sync delegate runs in River's secret scope from [2.2 Two apps on one node](../2-evy-mobile-app/02-shared-node.md#forgetting-one-app). Only River joins, because Atlas has [no delegate](https://github.com/freenet/atlas/blob/main/ui/src/main.rs).

## Linking and removing a device

| Step | Who | What happens |
| --- | --- | --- |
| 1. Start | Alice, on the laptop | River's "Link a device" page shows a QR code with a one-time key and a short-lived contract for the exchange |
| 2. Scan | Alice, on the phone | EVY's link screen scans the code, and the phone writes its own one-time key to that contract |
| 3. Compare | Both devices | Each shows a 6-digit code derived from both keys. Alice confirms on the laptop that they match |
| 4. Join | Laptop | Sends the group seed encrypted to the phone's key. River's rooms, keys and sent DMs appear on the phone |

Alice removes the phone from any other linked device. That device makes a new group seed and sends it only to the devices that stay. The removal screen lists what the phone keeps, which is every record it synced before removal. #5587 lists device revocation as an open question, so EVY proposes this exchange and seed rotation there.

## Resolving conflicts

Alice hides her DM thread with Bob on her phone while offline. Meanwhile her laptop sends Bob "See you Saturday", which unhides the thread there. Both devices then hold a different `outbound_dms` value.

| Field | Phone | Laptop | After River's merge |
| --- | --- | --- | --- |
| `entries` | No new DM | The DM to Bob | Both hold the DM, matched by purge token |
| `hidden_threads` | Bob's thread hidden | Bob's thread unhidden | An unhide beats a concurrent hide, so the thread shows on both |

River adds this merge beside [`is_thread_hidden`](https://github.com/freenet/river/blob/main/common/src/chat_delegate.rs), which only filters. Today [`unhide_dm_thread`](https://github.com/freenet/river/blob/main/ui/src/components/app/chat_delegate.rs) deletes the hide entry and remembers the unhide only for the session. River saves each unhide in `outbound_dms` so the merge can see it. For room slots, River reuses the merge it runs when it [migrates delegates](https://github.com/freenet/river/blob/main/ui/src/components/app/freenet_api/delegate_migration.rs), which keeps the tombstones of rooms Alice left.

## Traffic and lifecycle

- On iOS and Android, the phone syncs only while EVY is in the [foreground](../1-freenet-mobile-appkit/01-feasibility.md#foreground-lifecycle). The laptop syncs whenever its node runs.
- Sync bytes count as River's traffic under the [cellular budget contract in 1.8 Thin-peer role and cellular data budgets](../1-freenet-mobile-appkit/08-thin-peer.md#cellular-budget-contract). At a cap, sync pauses with the rest of the node's network work. EVY asks #5587 for shards smaller than the proposed 2 to 4 MiB, sized from device runs that sync one DM and one hide on cellular.
- Forgetting River on the phone deletes River's secret, and with it the group seed. Core builds `SecretScope::User` ([user.rs](https://github.com/freenet/freenet-core/blob/main/crates/core/src/wasm_runtime/secrets_store/user.rs)) from the client connection, so check that the scope also applies when River's chat delegate calls the sync delegate.

## What Core still needs

| Need | Issue |
| --- | --- |
| The sync delegate, plus a request and reply call between two delegates | [RFC #5587](https://github.com/freenet/freenet-core/issues/5587) |
| Delegates fetch and update contracts they do not yet hold | [#5542](https://github.com/freenet/freenet-core/issues/5542) |
| Delegate subscriptions keep the sync contracts hosted. They already survive a restart ([PR #5728](https://github.com/freenet/freenet-core/pull/5728)) | [PR #5493](https://github.com/freenet/freenet-core/pull/5493) |
| The laptop syncs with River's tab closed | [#5467](https://github.com/freenet/freenet-core/issues/5467) |

## Acceptance

- On iOS and Android, Alice links her phone to River on her laptop, and her "Skate club" key, room secret and sent DMs appear on the phone.
- On iOS and Android, a phone that scans the QR code gets no group seed when Alice does not confirm or the 6-digit codes differ.
- On iOS and Android, the hide-and-send case ends with the DM on both devices and Bob's thread visible on both, on a pinned River revision.
- On iOS and Android, after Alice removes the phone, records she changes on the laptop do not reach it, and the removal screen lists what it kept.
- On iOS and Android, a phone offline for a week, or killed during an upload, loses no record and converges when EVY next opens, including DMs the laptop purged meanwhile.
- On iOS and Android, sync traffic on cellular stays inside the caps in 1.8 Thin-peer role and cellular data budgets, and sync pauses at a cap.
- On iOS and Android, forgetting River makes River's synced records unreadable on that phone, and leaves Atlas working and the laptop syncing.
