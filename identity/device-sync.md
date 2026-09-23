# Device sync

Parent: [Identity and recovery](README.md).

Alice hides her direct message thread with Bob on her phone while her offline laptop sends Bob a new direct message. Both devices change the same `OutboundDmStore` record, which River's chat delegate uses for outbound message plaintext and hidden threads ([chat_delegate.rs](https://github.com/freenet/river/blob/main/common/src/chat_delegate.rs)). Sync preserves both revisions. River's rule resolves them: a thread stays hidden only while its hide time is at or after the latest message in it, so the laptop's new message shows the thread again on both devices.

## 1. Enrollment and encryption

Build continuous sync as a parallel track based on [RFC #5587](https://github.com/freenet/freenet-core/issues/5587). A user selects which applications and private data join the sync group. Enrollment requires proof from the user's recovery or already authorized device authority.

- Authenticate the caller's full delegate identity through Core before binding it to a stable sync namespace.
- Encrypt records before publication and authenticate namespace, revision and encryption-key epoch. That epoch is a counter inside the sync group's records within one contract instance.
- Preserve concurrent siblings and deletion records, so a late device cannot resurrect deleted private data.
- Keep device enrollment, revocation and encryption-key epochs explicit. Removing a device rotates future access under the group's policy.
- Show which earlier material a revoked device could read. Key rotation protects future updates, while earlier copies remain on that device.
- Support bidirectional phone, tablet and desktop updates, including long offline periods.
- Give foreground sync byte, time and retry budgets. Use configurable bounded shards and measure small-record updates on cellular links.
- Publish signed membership transitions and preserve conflicts in competing device-list updates until authorized resolution.
- Keep recoverable encrypted copies and report incomplete synchronization. Network contracts provide best-effort availability.

Resident delegates can continue work only while their hosting peer runs. Mobile background suspension still follows the SDK lifecycle.

## 2. Core dependencies

The whitepaper describes the intended pattern: a shared-secret contract holds an encrypted, replicated copy of private delegate state that only the delegates holding the symmetric key can read, and it marks the end-to-end delegate flow partial ([trust boundaries](https://github.com/freenet/paper-1/blob/main/sections/06-trust.tex), [status](https://github.com/freenet/paper-1/blob/main/sections/07-status.tex)). [RFC #5587](https://github.com/freenet/freenet-core/issues/5587) proposes a general-purpose sync delegate on top of it.

Core dependencies include [private cross-peer sync #4560](https://github.com/freenet/freenet-core/issues/4560), [delegate contract operations reaching the network #5542](https://github.com/freenet/freenet-core/issues/5542), [resident delegates #5467](https://github.com/freenet/freenet-core/issues/5467) and [delegate subscription persistence #5493](https://github.com/freenet/freenet-core/pull/5493). All four are open or proposed. Test these integrations through the [mobile SDK acceptance cases](../freenet-mobile/README.md#8-acceptance-cases).

## 3. Delivery and acceptance

| Phase | Delivers | Done when |
| --- | --- | --- |
| Device sync | Enrollment, encrypted records, concurrent changes and revocation | Offline devices converge without losing conflicts, reviving deletions or granting revoked future access. |

This track has its own release gate, separate from the [Marketplace](../marketplace/README.md) launch profile in the [identity plan](README.md#4-delivery-and-acceptance).
