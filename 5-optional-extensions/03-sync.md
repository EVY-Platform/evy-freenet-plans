# 5.3 Device sync

## Repositories

| Repository | Role | Work in this plan |
| --- | --- | --- |
| [freenet-core](https://github.com/freenet/freenet-core) | Modified | Cellular sync accounting |
| [river](https://github.com/freenet/river) | Modified | River device sync and merge |
| [evy](https://github.com/EVY-Platform/evy) | Modified | iOS and Android device controls |
| [freenet-appkit](https://github.com/glesage/freenet-appkit) | Modified | SDK device-linking APIs |

## Purpose

This plan keeps River's private records the same on Alice's phone and her laptop. She owns "Skate club" and runs River in EVY on her iPhone or Android phone, and in the browser on her laptop. Core already syncs the room, because both nodes subscribe to "Skate club" ([Sending updates in 1.6 Application protocols, data and operations](../1-freenet-mobile-appkit/06-data-and-operations.md#sending-updates)). This plan syncs the records that live only in River's [chat delegate](https://github.com/freenet/river/blob/main/ui/src/components/app/chat_delegate.rs). These are the `room:<owner key>`, `rooms_meta` and `outbound_dms` entries that [Delegate secret export and import in 1.7 Upgrades and migration](../1-freenet-mobile-appkit/07-migration.md#delegate-secret-export-and-import) lists. River fills its other entries again from these at start, as that section describes.

River uses the sync design proposed in [RFC #5587](https://github.com/freenet/freenet-core/issues/5587), which builds on the encrypted CRDT sync RFC [#4560](https://github.com/freenet/freenet-core/issues/4560). The design encrypts each record with a group seed that only Alice's linked devices hold, and keeps two concurrent writes as two values for the app to resolve. #5587 is an open proposal with no owner yet.

River builds the sync logic as a library and compiles it into its chat delegate. The sync code then runs inside the chat delegate, in River's secret scope from [2.1 EVY catalogue and app hosting](../2-evy-mobile-app/01-catalogue-and-hosting.md#secret-scopes). Only River joins, because Atlas has [no delegate](https://github.com/freenet/atlas/blob/main/ui/src/main.rs).

## Linking and removing a device

| Step | Who | What happens |
| --- | --- | --- |
| 1. Start | Alice, on the laptop | River's "Link a device" page shows a QR code with a one-time key and a short-lived contract for the exchange |
| 2. Scan | Alice, on the phone | EVY's link screen scans the code, and the phone writes its own one-time key to that contract |
| 3. Compare | Both devices | Each shows a 6-digit code derived from both keys. Alice confirms on the laptop that they match |
| 4. Join | Laptop | Sends the group seed encrypted to the phone's key. River's rooms, keys and sent DMs appear on the phone |

The exchange has the shape of Core's rendezvous design for pairing ([#992](https://github.com/freenet/freenet-core/issues/992)). We track Core [#5764](https://github.com/freenet/freenet-core/issues/5764), passkeys that sync across a person's devices through iCloud Keychain on iOS or Google Password Manager on Android, as another way to link a device.

Alice removes the phone from any other linked device. That device makes a new group seed and sends it only to the devices that stay. The removal screen lists what the phone keeps, which is every record it synced before removal. The design proposed in #5587 lists device revocation as an open question, so EVY proposes this exchange and seed rotation there.

## Resolving conflicts

Alice hides her DM thread with Bob on her phone while offline. Meanwhile her laptop sends Bob "See you Saturday", which unhides the thread there. Both devices then hold a different `outbound_dms` value.

| Field | Phone | Laptop | After River's merge |
| --- | --- | --- | --- |
| `entries` | No new DM | The DM to Bob | Both hold the DM, matched by purge token |
| `hidden_threads` | Bob's thread hidden | Bob's thread unhidden | An unhide beats a concurrent hide, so the thread shows on both |

River already merges concurrent copies on one node:

- `CasStoreRequest` writes with a generation counter ([river#345](https://github.com/freenet/river/issues/345)).
- `reconcile_room_present` and `Rooms::merge_from_source` merge room slots and keep the tombstones of rooms Alice left.
- `merge_outbound_dms` merges DM entries one by one when River [migrates delegates](https://github.com/freenet/river/blob/main/ui/src/components/app/freenet_api/delegate_migration.rs).

The sync merge reuses the room-slot merge and `merge_outbound_dms`. Only the hide-versus-unhide rule is new. [`is_thread_hidden`](https://github.com/freenet/river/blob/main/common/src/chat_delegate.rs) only filters. [`unhide_dm_thread`](https://github.com/freenet/river/blob/main/ui/src/components/app/chat_delegate.rs) deletes the hide entry and remembers the unhide only for the session. River saves each unhide in `outbound_dms` so the merge can see it.

We track these River issues:

| Issue | Effect on sync |
| --- | --- |
| [river#420](https://github.com/freenet/river/issues/420) | Identity conflicts between two tabs or devices are last-writer-wins in `reconcile_room_present` |
| [river#703](https://github.com/freenet/river/issues/703) | Two owner devices that set the same `configuration_version` never converge, as [Sending updates in 1.6 Application protocols, data and operations](../1-freenet-mobile-appkit/06-data-and-operations.md#sending-updates) notes |
| [river#432](https://github.com/freenet/river/issues/432), [river#435](https://github.com/freenet/river/issues/435), [river#433](https://github.com/freenet/river/pull/433) | Portable sent DMs through `sender_ciphertext` let each device read its own sent DMs from room state. Sync then carries only the hidden threads from `outbound_dms` |

## Traffic and lifecycle

- On iOS and Android, the phone syncs only while EVY is in the [foreground](../1-freenet-mobile-appkit/01-feasibility.md#foreground-lifecycle).
- The laptop syncs whenever its node runs, also with River's tab closed ([#5467](https://github.com/freenet/freenet-core/issues/5467)). Core's lifecycle runs ([#5730](https://github.com/freenet/freenet-core/pull/5730)) and wake-ups ([#5747](https://github.com/freenet/freenet-core/pull/5747)) start the chat delegate while River holds the `Background` grant, as [background runs and delegate prompts in 1.3 Single-application host](../1-freenet-mobile-appkit/03-host.md#background-runs-and-delegate-prompts) describes.
- Sync bytes count as River's traffic under the [cellular budget contract in 1.8 Thin-peer role and cellular data budgets](../1-freenet-mobile-appkit/08-thin-peer.md#cellular-budget-contract). At a cap, sync pauses with the rest of the node's network work. We asked on #5587 for shards smaller than the proposed 2 to 4 MiB. Device runs that sync one DM and one hide on cellular set the size.
- The group seed lives in River's secret scope with the chat delegate's other records ([user.rs](https://github.com/freenet/freenet-core/blob/main/crates/core/src/wasm_runtime/secrets_store/user.rs)). Forgetting River on the phone deletes River's secret, and with it the group seed.

## What Core still needs

| Need | Issue |
| --- | --- |
| Agreement on the sync design that River's library follows | [RFC #5587](https://github.com/freenet/freenet-core/issues/5587) |
| Delegates update contracts they do not yet hold. GET and SUBSCRIBE reach the network ([#5615](https://github.com/freenet/freenet-core/pull/5615)). Before its first UPDATE to a sync contract, the sync code reads it, as [Sending updates in 1.6 Application protocols, data and operations](../1-freenet-mobile-appkit/06-data-and-operations.md#sending-updates) describes | [#5542](https://github.com/freenet/freenet-core/issues/5542) |
| Delegate subscriptions keep the sync contracts hosted, within the limits in [Lost network state in 1.6 Application protocols, data and operations](../1-freenet-mobile-appkit/06-data-and-operations.md#lost-network-state) | [#4669](https://github.com/freenet/freenet-core/issues/4669) |
| A delegate GET tells a missing sync contract from a failed lookup | [stdlib #131](https://github.com/freenet/freenet-stdlib/issues/131) |
| freenet-migrate released on freenet-stdlib 0.12. River runs freenet-migrate, which builds on stdlib 0.8, and manifests need stdlib 0.12 ([stdlib #136](https://github.com/freenet/freenet-stdlib/pull/136)). Harvest writes its manifest section by hand ([node_glue.rs](https://github.com/freenet/harvest/blob/main/delegates/harvest-delegate/src/node_glue.rs)) | To file |
| River's per-app scope in notification, lifecycle and wake-up runs on the phone, as [Core and AppKit requirements in 2.1 EVY catalogue and app hosting](../2-evy-mobile-app/01-catalogue-and-hosting.md#core-and-appkit-requirements) lists | [#5736](https://github.com/freenet/freenet-core/issues/5736) |

## Acceptance

- On iOS and Android, Alice links her phone to River on her laptop, and her "Skate club" key, room secret and sent DMs appear on the phone.
- On iOS and Android, a phone that scans the QR code gets no group seed when Alice does not confirm or the 6-digit codes differ.
- On iOS and Android, the hide-and-send case ends with the DM on both devices and Bob's thread visible on both, on a pinned River revision.
- On iOS and Android, after Alice removes the phone, records she changes on the laptop do not reach it, and the removal screen lists what it kept.
- On iOS and Android, a phone offline for a week, or killed during an upload, loses no record and converges when EVY next opens, including DMs the laptop purged meanwhile.
- On iOS and Android, sync traffic on cellular stays inside the caps in 1.8 Thin-peer role and cellular data budgets, and sync pauses at a cap.
- On iOS and Android, forgetting River makes River's synced records unreadable on that phone, and leaves Atlas working and the laptop syncing.
