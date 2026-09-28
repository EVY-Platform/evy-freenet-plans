# 5.3 Device sync and authoring collaboration

Optional consumer sync synchronizes selected private application records across authorized devices. Optional authoring collaboration shares bounded live editing batches and presence hints among participants who opt in per project. Each track has its own dependencies and acceptance gate.

## Repositories

| Repository | Role | Work in this plan |
| --- | --- | --- |
| [freenet-core](https://github.com/freenet/freenet-core) | Modified | `crates/mobile` gains sync group enrollment, encrypted record exchange, key epochs, membership transitions and budget-bound shards; sync delegate RFC #5587, #4560, #5542, #5467, PR #5493 and PR #5728 verified on the selected build |
| [evy](https://github.com/EVY-Platform/evy) | Modified | Sync selection, device enrollment and budget screens in the iOS and Android apps |
| `freenet-app-builder` | Modified | Collaboration-session shard contracts, presence hints and live-session checkpoint commits |
| [river](https://github.com/freenet/river) | Used | `OutboundDmStore` hidden-thread merge fixture |
| [paper-1](https://github.com/freenet/paper-1) | Used | Trust boundaries and status sections on private state replication |

## Consumer device sync

Prerequisites:

- [1.5 Identity, keys and local protection](../1-freenet-mobile-appkit/05-identity.md).
- [1.6 Application protocols, data and operations](../1-freenet-mobile-appkit/06-data-and-operations.md).
- [1.3 Single-application host](../1-freenet-mobile-appkit/03-host.md).
- [2.2 Multi-application sessions and authority](../2-evy-mobile-app/02-sessions.md).
- [2.4 Identity, permissions and device access](../2-evy-mobile-app/04-permissions.md).
- The Core integrations below.

Mobile sync inherits the required [gate in 1.10 Thin-peer role and cellular data budgets](../1-freenet-mobile-appkit/10-thin-peer.md). Consumer sync can ship independently of visual authoring and live collaboration.

### 1. Enrollment and encryption

A user selects the applications and private data that join a sync group. Enrollment requires proof from the user's recovery authority or an already authorized device. The protocol follows the encrypted private-state approach proposed in [RFC #5587](https://github.com/freenet/freenet-core/issues/5587).

- Authenticate the full delegate identity before binding it to a stable sync namespace. Apply the [app/user admission policy in 1.3 Single-application host](../1-freenet-mobile-appkit/03-host.md) and the [shared-delegate policy in 2.2 Multi-application sessions and authority](../2-evy-mobile-app/02-sessions.md).
- Encrypt records before publication. Authenticate the namespace, revision and encryption-key epoch with the ciphertext.
- Treat the encryption-key epoch as a counter in the sync group's records within one contract instance. [1.7 Upgrades and migration](../1-freenet-mobile-appkit/07-migration.md) handles component re-keying separately.
- Preserve concurrent revisions and deletion records. Application code supplies the domain merge rules.
- Publish signed membership transitions. Retain competing device-list changes as conflicts until authorized resolution.
- Revocation rotates future access under the group's policy. Report which earlier material the revoked device could retain.
- Support bidirectional phone, tablet and desktop changes through long offline periods.
- Bound foreground bytes, elapsed work and retries. Use configurable bounded shards and measure small-record changes on cellular connections.
- Retain recoverable encrypted copies and expose incomplete synchronization. Network contract availability depends on surviving hosts.

Resident delegate work runs while its hosting peer is active. Phone suspension follows the [lifecycle in 1.2 Embedded node and mobile SDK](../1-freenet-mobile-appkit/02-sdk.md), and [2.5 Shared node, data and lifecycle](../2-evy-mobile-app/05-lifecycle.md) schedules traffic within the shared node's cellular budget.

#### River conflict fixture

River's [chat delegate](https://github.com/freenet/river/blob/main/common/src/chat_delegate.rs) is evidence for an application-specific merge fixture. Alice hides a direct-message thread on her phone while her offline laptop sends a new message. Both change `OutboundDmStore`, which holds outbound plaintext and hidden-thread state.

Retain both revisions. Apply River's rule that a thread stays hidden only while its hide time is at or after the latest message in it. The later message therefore shows the thread again on both devices. Pin the application revision used by this fixture and test its actual merge behavior.

### 2. Core dependencies

The whitepaper describes a shared-secret contract containing an encrypted replicated copy of private delegate state. Delegates holding the symmetric key can read it. Its [trust boundaries](https://github.com/freenet/paper-1/blob/main/sections/06-trust.tex) and [status](https://github.com/freenet/paper-1/blob/main/sections/07-status.tex) are design evidence. The links below require verification against the selected Core build before release.

| Integration | Plan evidence | Required test |
| --- | --- | --- |
| General sync delegate | [RFC #5587](https://github.com/freenet/freenet-core/issues/5587) | Authenticated enrollment and encrypted record exchange |
| Private cross-peer synchronization | [#4560](https://github.com/freenet/freenet-core/issues/4560) | Two peers exchange only authorized private records |
| Delegate operations reaching the network | [#5542](https://github.com/freenet/freenet-core/issues/5542) | Remote reads and writes reach the intended contract |
| Resident delegates | [#5467](https://github.com/freenet/freenet-core/issues/5467) | Work resumes on a running peer within its lifecycle policy |
| Hosting demand from delegate subscriptions | [PR #5493](https://github.com/freenet/freenet-core/pull/5493) | Active subscriptions maintain the expected hosting demand |
| Delegate subscriptions across restart | [PR #5728](https://github.com/freenet/freenet-core/pull/5728) | Restart restores authorized subscription demand and reconciles missed changes |

[1.2 Embedded node and mobile SDK](../1-freenet-mobile-appkit/02-sdk.md) owns API exposure and callback integration. [1.3 Single-application host](../1-freenet-mobile-appkit/03-host.md) and [2.4 Identity, permissions and device access](../2-evy-mobile-app/04-permissions.md) own the authority dependencies.

### 3. Delivery and acceptance

Enrolled offline devices converge under application merge rules, retain conflicts, preserve deletions and enforce revoked future access.

Consumer tests cover forged enrollment, copied delegate parameters, replayed membership, conflicting rosters, key-epoch changes, long-offline devices, late deletions and interrupted upload. The River fixture preserves outbound plaintext and applies its hide-time rule on both devices.

Measure sync bytes and retry behavior under the approved workload budgets in 1.10 Thin-peer role and cellular data budgets. Test node restart, mobile suspension, unavailable replicas and storage exhaustion. [5.2 Extended customer backup and recovery](02-recovery.md) may retain additional copies, while the sync gate reports its own coverage and recovery prerequisites.

## Optional real-time collaboration

Prerequisite: the released [visual-authoring client and durable checkpoint protocol in 4.8 EVY Developer visual authoring](../4-sdui/08-developer.md#durable-checkpoint-protocol). That protocol owns project membership, signed operations, conflicts and checkpoints. Live sessions add the following scope and acceptance gate.

### Session scope and retention

Use separate collaboration-session shard contracts for live operations and optional presence. Bind each shard to the project, a verified membership epoch, participants, protocol version and capacity profile. Validate signed editing operations under the checkpoint membership rules. A live session periodically commits durable checkpoints through 4.8 EVY Developer visual authoring.

Cap participants, operations, bytes and fan-out. Batch at a fixed maximum cadence. Expire local presence hints after a configured age. Keep presence metadata minimal and apply the project's visibility policy. The client treats presence as advisory display data.

Participants stop renewing session shards when a session ends. A shard remains available while a host retains it, can be evicted under budget pressure, and can be republished by any holder. The UI describes retention on those terms. Durable checkpoints and required audit records follow their own retention policy.

A reconnecting client merges the verified checkpoint and remaining session operations by stable ID. Preserve uncheckpointed local edits when a shard is unavailable. Membership changes close or rebind the session under the new verified epoch, with stale edits handled by the checkpoint repair rules.

### Collaboration acceptance

- Opt-in sessions converge under concurrent edits, reordered/duplicate batches, reconnects, member removal and conflicting operations.
- Periodic checkpoint publication survives shard loss and client termination, with uncheckpointed local work recoverable from its journal.
- Participant, byte, operation and cadence limits hold under full fan-out workloads. Mobile runs pass the inherited cellular profile.
- Stale presence expires locally. Ending a session stops renewals and leaves durable checkpoint access usable.
- The local editing and checkpoint suite in 4.8 EVY Developer visual authoring continues to pass with live collaboration disabled or unavailable.
