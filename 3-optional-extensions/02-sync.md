# 3.2 Device sync

## Repositories

| Repository | Role | Work in this plan |
| --- | --- | --- |
| [evy](https://github.com/EVY-Platform/evy) | Modified | "Link a device" screens in SwiftUI and Compose; sync in the EVY delegate |
| [freenet-core](https://github.com/freenet/freenet-core) | Used | Delegate network operations and the sync design in RFC #5587 |
| [freenet-stdlib](https://github.com/freenet/freenet-stdlib) | Used | Delegate interface |

## Purpose

This plan is an idea note for using EVY on two devices, such as Alice's iPhone and her Android tablet.

Contract data already reaches both devices: each one subscribes to Bob's skateboard purchase contract. Only the private records in [The EVY delegate in 2.4 SDUI data and actions](../2-evy-on-freenet/04-data-and-actions.md#the-evy-delegate) stay on one device:

| Record | What both devices would share |
| --- | --- |
| Root seed | The seed that derives Alice's EVY keys |
| Pending records | Signed changes waiting to be sent |
| Addresses | Alice's saved pickup addresses |
| Drafts | Unsent drafts |

Example: on the train, Alice's iPhone is offline. She edits her skateboard listing and adds a photo of the wheels. At the pickup she confirms the handover on her Android tablet. When the iPhone reconnects, both devices show the skateboard as sold. EVY keeps the wheels edit and asks Alice to discard it or start a new listing from it.

## Open problem: removing a device

All of Alice's EVY keys come from one root seed. A linked device receives that seed. After removal, it still holds the seed and can still sign as Alice. Real device removal needs EVY key rotation: a new root seed, new feature keys, and moving Alice's listings and open purchases to the new keys. This plan must solve that before release.

## When this becomes a plan

Work starts when users ask to use EVY on more than one device.

The plan would follow the encrypted sync design in [RFC #5587](https://github.com/freenet/freenet-core/issues/5587) and decide:

- how a second device pairs, for example with a QR code and a matching code on both screens
- how concurrent edits merge, such as the train-and-pickup example above
- how restore from [3.1 Automated backup](01-backup.md) or [1.10 Backup and restore](../1-freenet-mobile-appkit/10-backup-and-restore.md) joins a sync group
- how large sync checkpoints may be on mobile data, using the thin peer from [1.8 Thin-peer protocol](../1-freenet-mobile-appkit/08-thin-peer.md)

Each part needs matching iOS and Android tests, including iOS–Android pairs.

## Sources

- [RFC #5587](https://github.com/freenet/freenet-core/issues/5587): proposed delegate sync design
- [RFC #4560](https://github.com/freenet/freenet-core/issues/4560): encrypted CRDT sync that #5587 builds on
- [Core #5542](https://github.com/freenet/freenet-core/issues/5542): delegate UPDATE reaching contracts beyond the local store
- [stdlib #131](https://github.com/freenet/freenet-stdlib/issues/131): telling a missing contract apart from a failed lookup
- [Core #992](https://github.com/freenet/freenet-core/issues/992): rendezvous proposal, prior art for pairing
