# 1.6 Application protocols, data and operations

## Repositories

| Repository | Role | Work in this plan |
| --- | --- | --- |
| [freenet-core](https://github.com/freenet/freenet-core) | Modified | Record response arrival times in the mobile API; test and fix local update response timing |
| [freenet-appkit](https://github.com/glesage/freenet-appkit) | Modified | River read, draft, send, invitation and recovery tests on iOS and Android |
| [river](https://github.com/freenet/river) | Modified | Save and recover drafts and pending signed messages; show save and send conflicts |
| [freenet-stdlib](https://github.com/freenet/freenet-stdlib) | Used | Client API and delegate interface |

## Purpose

Save River's drafts and pending signed messages, record when read responses arrive, and test recovery on iOS and Android.

Bob types "Skate session Saturday?" in the "Skate club" room:

1. River saves his draft and confirms when storage finishes.
2. Bob taps send. River reads the retained room, [signs the message locally](https://github.com/freenet/river/blob/78307756805f3e02399791dda142c86b83780b8f/ui/src/signing.rs) and saves the exact signed operation. After storage acknowledges it, River shows it as pending and submits it when the node is ready.
3. After Core saves the room, River checks that its state contains the message.
4. After an interruption, River recovers the last acknowledged draft or pending message. Reconnect tests check that an independent peer receives the message.

Test River's web UI through its direct WebSocket session adapter and a native SDK fixture on iOS and Android after outages, restarts and release changes. Both use the [application transport adapter in 1.2 Embedded node and mobile SDK](02-sdk.md#requests-events-and-errors).

| Deliverable | Section |
| --- | --- |
| Tests of River's invitation signing and the SDK's delegate calls | [Calling a delegate](#calling-a-delegate) |
| Response arrival times, saved drafts and pending messages | [Reads and local data](#reads-and-local-data) |
| Local confirmation, retries, duplicate handling and reconnect tests | [Sending updates](#sending-updates) |
| Tests of River restoring a room that peers dropped | [Lost network state](#lost-network-state) |

## How a send works

| Part | Responsibility |
| --- | --- |
| River | Read the room, sign the message, save recovery records and show the result |
| Host | Check River's session, permission and room target, and route private replies |
| Application transport adapter | Queue requests and match replies to the current connection under [1.2 Embedded node and mobile SDK](02-sdk.md#requests-events-and-errors). The host supplies caller authority. |
| Chat delegate | Store the draft and pending message, and check who may read or change them |
| Room contract | Check the signature and merge the message into room state |

SDK operations and host checks follow [1.2 Embedded node and mobile SDK](02-sdk.md) and [1.3 Single-application host](03-host.md).

```mermaid
sequenceDiagram
    participant River
    participant Delegate as Chat delegate
    participant Core as Core through the application connection
    River->>Core: Read retained room
    Core-->>River: Room state
    River->>River: Sign message with Bob's room key
    River->>Delegate: Save exact signed operation and draft context
    alt Save acknowledged
        Delegate-->>River: Durable save acknowledged
        River->>River: Show pending message
        River->>Core: Submit saved operation when ready
        Core->>Core: Validate, merge and save room
        Core-->>River: Local update response
        River->>Core: Read or observe room
        Core-->>River: State containing the message
        River->>Delegate: Clean up with version checks
    else Save failed
        Delegate-->>River: Storage error
        River->>River: Keep draft and show recovery action
    end
```

The chat delegate acknowledges durable storage before River submits the operation or clears the composer. Save failures keep the draft available and show a recovery action. Once River confirms the message in locally stored room state, cleanup uses version checks to preserve later edits and remains the final write. Local acceptance and independent-peer delivery have separate evidence under [Sending updates](#sending-updates).

| Check | Requirement |
| --- | --- |
| Exact release | Load River's real delegate and room contract on the release's Core and stdlib versions. Keep the code, parameter bytes and protocols from [1.4 Application bundles](04-bundles.md) fixed for the session ([#5617](https://github.com/freenet/freenet-core/issues/5617)) |
| Repeatable messages | Supply fixed time and random values through test interfaces. Check that River's room contract imports no host clock ([#5465](https://github.com/freenet/freenet-core/issues/5465)) |
| References returned by a delegate | Apply the target and query limits from [1.3 Single-application host](03-host.md) before River follows the reference |

## Calling a delegate

Core and stdlib supply delegate messaging. This plan tests River's existing invitation flow through the mobile SDK on iOS and Android, using River's real chat delegate and the Core version included in the release.

### Alice invites Carol

Alice invites Carol to "Skate club" through River's [chat delegate](https://github.com/freenet/river/blob/78307756805f3e02399791dda142c86b83780b8f/common/src/chat_delegate.rs):

1. River sends Carol's membership details, the room key and a request ID to the delegate.
2. The delegate returns a 64-byte signature with the same request ID.
3. River checks the signature against Alice's public key and combines it with Carol's membership details into a [signed membership record](https://github.com/freenet/river/blob/78307756805f3e02399791dda142c86b83780b8f/common/src/room_state/member.rs).

The test verifies the delegate's signature, then tests River's [local signing fallback](https://github.com/freenet/river/blob/78307756805f3e02399791dda142c86b83780b8f/ui/src/signing.rs) after a failed call or signature check. River defines its message format and signs chat messages in its own code.

### Work supplied by other plans

| Plan | Work supplied |
| --- | --- |
| [1.2 Embedded node and mobile SDK](02-sdk.md) | Swift on iOS and Kotlin on Android delegate calls, reply matching, errors and safe transfer of message data |
| [1.3 Single-application host](03-host.md#trusted-calls) | Checks on the app, user, installation, permissions and session; private reply routing |
| [1.4 Application bundles](04-bundles.md#the-archive-and-its-definition) | River's `river.chat/1` message format and supported versions for each release |

### Checks before release

| Test | Required result |
| --- | --- |
| Message compatibility | Exact request and reply bytes, request IDs, signing inputs and error strings match River's format. A separate test checks its existing `SignMessage` request |
| Invalid messages | Changed content under a reused request ID, unknown handles, malformed replies and values outside number or size limits produce errors. Include oversized results and delegate context under the release's [stdlib limits](https://github.com/freenet/freenet-stdlib/blob/7782c176a622efc3f284ce4710b4f184c4986405/rust/src/delegate_interface.rs) |
| Failed calls | Missing signing keys, unsupported requests and delegate errors reach the app as defined errors |
| Caller permissions | The host checks the app, user, installation, permission and session under 1.3 Single-application host. The delegate checks Core's caller identity and any required proof. Forged claims such as "I am Alice" produce errors |
| Private replies | Replies reach authorized sessions. The host discards replies for expired sessions |
| Other delegate operations | Separate SDK tests exercise contract reads, writes, subscriptions, calls to another delegate and user prompts |
| Runs started by Core | Separate SDK tests check permissions and private replies for room updates, startup and wake-ups. They cover runs with no calling app or request ID, and room notifications with empty parameters |

## Reads and local data

Use Core's contract reads, subscriptions and delegate private store. Record response arrival times and save River's drafts and signed messages waiting to be sent.

### Bob opens "Skate club"

The mobile API records when Bob's phone receives the room state and passes that time to River. Alice's message may carry a creation time from her device. River keeps these times separate because the clocks can differ and the received copy can be older than the network's latest state.

| Test | Required result |
| --- | --- |
| Room list and conversation read the same room | Each screen receives its own result through [reply matching in 1.2 Embedded node and mobile SDK](02-sdk.md#matching-replies-to-requests) |
| Read also requests room updates | River waits for subscription confirmation before relying on update notifications ([#2501](https://github.com/freenet/freenet-core/pull/2501)) |
| Open River before the node joins | River reads the saved room through [1.2 Embedded node and mobile SDK](02-sdk.md#start-stop-and-reconnect) |
| Close one screen while another watches the room | The remaining screen keeps its subscription through [1.2 Embedded node and mobile SDK](02-sdk.md#subscriptions-and-application-demand) |

### Where River saves data

| Record | Where it lives | How long it lasts |
| --- | --- | --- |
| Drafts, signed messages waiting to be sent and private records | The chat delegate's private store | River removes completed or discarded drafts and pending messages. [1.5 Identity, keys and local protection](05-identity.md#forget) deletes the app's private data on forget |
| Messages already added to the room | The node's room copy on disk | Core keeps the copy within the [storage budget in 1.2 Embedded node and mobile SDK](02-sdk.md#storage). Subscriptions give it a higher retention priority; eviction can still delete it ([#4212](https://github.com/freenet/freenet-core/pull/4212)) |

[1.5 Identity, keys and local protection](05-identity.md) supplies encryption, locking and deletion; [1.10 Backup and restore](10-backup-and-restore.md) supplies application snapshots. [1.2 Embedded node and mobile SDK](02-sdk.md#storage) keeps only current secret values. This plan tests River's records with those settings.

### Bob's saved draft

Saving drafts and exact signed messages in the chat delegate lets Bob resume after an app restart or background node stop. River delivery requires the record format, export/migration coverage and iOS and Android recovery fixtures.

File a River issue to retain drafts and exact pending signed messages in the chat delegate across app restarts and background node stops. Keep signing in the page. Acknowledge the signed-operation save before submitting it; measure storage latency and schedule recovery saves ahead of background refresh ([river#512](https://github.com/freenet/river/issues/512)).

Implementation references: [River CAS requests #345](https://github.com/freenet/river/issues/345) and [Mail's per-device drafts delegate #56](https://github.com/freenet/mail/pull/56).

| Work | Required result |
| --- | --- |
| Save each draft under a small separate key | Typing updates the draft record independently of the room record |
| Use `GetVersionedRequest` and `CasStoreRequest` | Two screens or a background run editing the same draft detect a conflicting save ([river#347](https://github.com/freenet/river/pull/347)) |
| Batch edits and flush on pause or backgrounding | Mark a save complete after storage acknowledges it. Reopening restores the last acknowledged draft |
| Save the exact signed operation before submission | Include the room target, exact parameters, source release and operation identity. Reopening retries the saved operation through [Sending updates](#sending-updates) |
| Set limits on record count and size | Enforce River's local-store limits and report a failed save when a limit or storage capacity is reached ([#5560](https://github.com/freenet/freenet-core/issues/5560)) |
| Keep every saved record discoverable | Account for other records in the same scope and the 4,096-key listing limit ([store.rs](https://github.com/freenet/freenet-core/blob/99612051c535ff7f18ce7c40857ecd236bbbdd46/crates/core/src/wasm_runtime/secrets_store/store.rs)) |
| Include draft and pending-message keys in River's export and migration index | Backup and restore preserve these records through [1.10 Backup and restore](10-backup-and-restore.md); release migration uses [1.7 Upgrades and migration](07-migration.md) |

### Core retention and offline delivery

Contract pinning, persistence and demand restoration support recovery when demand eviction removes a contract or every mobile node is stopped. Stronger retention and delivery claims require the implementation and eviction/restart evidence; the release fixtures below test the declared hosting budget.

Core stores contract state and sends it to peers. This plan tests cached reads, acknowledged delegate saves and reconnect delivery while Core retains the room state. Storage tests fill the Core build's hosting budget and record which room copies it retains or evicts.

Reconnect tests retain room state within the Core build's hosting budget. Adopt stronger Core retention and offline delivery guarantees after eviction and restart tests pass, including availability while all mobile nodes holding the data are stopped.

| Thread | Scope | Status checked 2026-10-07 |
| --- | --- | --- |
| [#5041 Bounded local contract pin](https://github.com/freenet/freenet-core/issues/5041) | Quota-bounded API to keep selected contracts on the user's node through normal demand eviction | Open design proposal with an exploratory fork |
| [#4651 Contract storage design](https://github.com/freenet/freenet-core/issues/4651) | Evaluates on-disk persistence and a targeted backstop for newly published contracts until a second replica exists | Open design question |
| [#4785 Persist hosting demand across restart](https://github.com/freenet/freenet-core/issues/4785) | Restores live subscriptions for contracts with prior client demand after a node restart | Open follow-up proposal |
| [#3465 PUT propagation reliability](https://github.com/freenet/freenet-core/issues/3465) | Tracks locally applied PUTs whose reported results or remote propagation are unreliable | Open; assigned to iduartgomez |
| [#3611 PUT forwarding acknowledgements and retries](https://github.com/freenet/freenet-core/pull/3611) | Adds hop-level forwarding acknowledgements and retries for in-flight PUT operations | Merged 2026-03-21 |
| [#5515 Repair dropped broadcast UPDATEs](https://github.com/freenet/freenet-core/pull/5515) | Adds resynchronization for rate-limited broadcasts; [#5527](https://github.com/freenet/freenet-core/issues/5527) tracks repair latency when a throttle window suppresses another request | Merged 2026-09-02; latency follow-up open |

Evaluate future Core releases for local retention, subscription recovery and in-flight retries. A successful client PUT confirms local persistence. Network propagation continues asynchronously, as [#3626](https://github.com/freenet/freenet-core/pull/3626) specifies.

## Sending updates

This plan adds interrupted-send recovery on iOS and Android. River saves the exact signed operation before submission, as [Bob's saved draft](#bobs-saved-draft) specifies.

Track saves, local room state and delivery independently:

| Result | What it confirms |
| --- | --- |
| The delegate acknowledges a save | The saved draft or exact signed message |
| Core stores the update, then River reads the message in the phone's room state | The message in the locally stored room, while Core keeps that room hosted |
| An independent peer reads the message | Evidence that the message reached another node |

Test Core's response timing with forwarding to a peer blocked. Core must answer after saving locally and let River read the saved message. Adjust Core if the release fails this check on its [forwarding path](https://github.com/freenet/freenet-core/blob/99612051c535ff7f18ce7c40857ecd236bbbdd46/crates/core/src/operations/update/op_ctx_task.rs).

| What happens to Bob's send | Required result |
| --- | --- |
| His phone loses signal after joining, or Wi-Fi stays connected without internet | River retains the signed operation in its durable queue. A locally accepted operation follows Core's retained-state propagation; a pending submission resumes after reconnect. With the room state retained within Core's hosting budget, an independent peer reads it |
| River starts without signal, before the node's first join | Save the exact signed operation and show it as pending under [Offline startup in 1.2 Embedded node and mobile SDK](02-sdk.md#offline-startup). Restart restores the queue; an independent peer reads the message after joining |
| River stops after the message reaches the locally stored room | With the room state retained within Core's hosting budget, River reads it back after restart and checks that a peer receives it after reconnecting |
| River stops before the send result arrives | River checks the room and retries any saved signed message with the same bytes. An interrupted save leaves the last acknowledged draft save |
| The same signed message arrives twice | The room contains one copy. River's message ID derives from its signature ([message.rs](https://github.com/freenet/river/blob/78307756805f3e02399791dda142c86b83780b8f/common/src/room_state/message.rs)) |
| Validation or storage fails | River keeps the recoverable draft and shows the error returned through [1.2 Embedded node and mobile SDK](02-sdk.md#requests-events-and-errors) |

Test the save completion, version checks and cleanup order in [How a send works](#how-a-send-works).

### Preparing and restoring a room

- River's application adapter restores known rooms with `GET { return_contract_code: false, subscribe: true }`. It merges the returned state as its baseline and submits locally held missing changes through delta UPDATEs. New/missing rooms use recovery PUTs; failed or timed-out GETs enter the supplied fallback/retry route. [River PR #759](https://github.com/freenet/river/pull/759) supplies this behavior. On iOS and Android, measure known-room reconnect, missing-state deltas, fresh-room PUTs, `NotFound`, errors and timeouts with independent readback and exact signed-operation replay. Room retention follows the storage budget in [1.2 Embedded node and mobile SDK](02-sdk.md#storage).
- Read a room absent from the node before updating it. If Core returns `NotFound`, keep the draft and report the room unavailable. An owner with a saved copy uses [Lost network state](#lost-network-state). Test this first-send case ([#5724](https://github.com/freenet/freenet-core/issues/5724), [River GET/fallback recovery](https://github.com/freenet/river/pull/759)).
- Apply the durable-queue profile from [Offline startup in 1.2 Embedded node and mobile SDK](02-sdk.md#offline-startup). Recover acknowledged drafts and exact signed operations before joining; submit pending operations when the node is ready and restore subscriptions through the existing reconnect route.
- After reopening or release activation, read saved drafts and pending messages from the delegate and read each room from the node. Confirm recovery after those reads complete.

Test reconnect delivery through Core's [state comparison](https://github.com/freenet/freenet-core/blob/99612051c535ff7f18ce7c40857ecd236bbbdd46/crates/core/src/ring/interest.rs). Cellular traffic follows [1.8 Thin-peer protocol](08-thin-peer.md); update rate limits follow [1.11 Cellular data and resource budgets](11-cellular-data-and-resource-budgets.md#cellular-budget-contract).

### Conflicting changes

| Change | Work in this plan |
| --- | --- |
| Alice edits the room settings on her phone and laptop | Test the [higher-version winner](https://github.com/freenet/river/blob/78307756805f3e02399791dda142c86b83780b8f/common/src/room_state/configuration.rs) and tell Alice when her edit was overridden. Acceptance of equal-version edits depends on the upstream convergence fix in [river#703](https://github.com/freenet/river/issues/703) |
| A ban changes the room secret while Bob has a draft | Keep the draft. River checks Bob's current membership and the room secret before deciding whether to sign it again and send it |
| Peers merge changes in different orders or receive duplicates | Run `fdev verify-merge` and test actual room states after those deliveries. Check the verification report for inconclusive results ([#5725](https://github.com/freenet/freenet-core/issues/5725)) |

## Lost network state

Test River's recovery flow when remote peers lose a room and Alice's phone still holds a copy. Use an isolated test network with fixed gateways and no live-network peers ([#5552](https://github.com/freenet/freenet-core/issues/5552)). Keep Alice's copy while removing the remote copies.

1. Run River's owner-room subscription request and confirm that the subscription took.
2. Remove the remote copies of "Skate club" and exercise River's failed-subscription recovery.
3. River submits Alice's saved copy to the same room contract.
4. An independent peer reads the restored room. Record the recovery time.

River requests owner-room subscriptions through `EnsureRoomSubscription` ([river#235](https://github.com/freenet/river/pull/235), [river#276](https://github.com/freenet/river/pull/276)). Core supplies [network interest](https://github.com/freenet/freenet-core/pull/5615) and [subscription restoration after restart](https://github.com/freenet/freenet-core/pull/5728). River's [re-PUT handler](https://github.com/freenet/river/blob/78307756805f3e02399791dda142c86b83780b8f/ui/src/components/app/freenet_api/response_handler/subscribe_response.rs) waits 20 seconds before submitting the saved copy. Use the controlled test setup to establish remote loss. The 20-second wait is a retry delay.

| Condition | Required check |
| --- | --- |
| Owner-room subscription | [Core PR #5855](https://github.com/freenet/freenet-core/pull/5855) supplies delegate local hosting demand for eviction and renewal accounting; [PR #5728](https://github.com/freenet/freenet-core/pull/5728) supplies persistent subscriptions. Verify restoration, renewal, unsubscribe and node sleep/resume on the selected mobile build; acknowledgement evidence uses [#5565](https://github.com/freenet/freenet-core/issues/5565) |
| Delegate subscription limit | Exercise the 256-subscription cap and eviction of the least recently notified room. Check River's resubscription on start and reconnect ([#5623](https://github.com/freenet/freenet-core/pull/5623), [#5622](https://github.com/freenet/freenet-core/issues/5622)) |
| Room lookup fails | River's UI uses the client subscription result to decide how to recover. Test missing rooms and failed lookups; delegate GET returns `None` for both ([stdlib #131](https://github.com/freenet/freenet-stdlib/issues/131)) |
| A room above 1 MiB, sent through NAT | Require an independent peer to read the restored room. Resolve any failure before accepting this case ([#5643](https://github.com/freenet/freenet-core/issues/5643)) |
| Hosting and retry timing | Measure room retention and recovery time on the release build, within the mobile storage budget. Use those results to choose River's retry timing ([hosting-demand accounting](https://github.com/freenet/freenet-core/pull/5855), [subscription restoration](https://github.com/freenet/freenet-core/pull/5728)) |

## Acceptance

Run these scenarios with River's real code, room contract and chat delegate on the release's Core version, on iOS and Android. Swift on iOS and Kotlin on Android also exercise the native delegate API from [1.2 Embedded node and mobile SDK](02-sdk.md).

| Scenario | Required result |
| --- | --- |
| Alice invites Carol | All [delegate-call checks](#calling-a-delegate) pass, including exact message bytes, request IDs, error strings, invalid inputs and a 64-byte signature verified with Alice's key |
| Two screens read the same room | Replies reach the correct requests. Arrival times describe phone receipt; message creation times remain app-supplied values |
| Bob edits a draft in two sessions; storage fills up or a save fails | Draft conflicts have a defined outcome. Failed saves report an error and recovery retains the last acknowledged save |
| River stops during draft saving, sending or cleanup | Recovery follows [Sending updates](#sending-updates). A failed operation save keeps the draft and blocks submission. A lost reply replays the same signed operation after reconciliation; the room holds one copy and versioned cleanup preserves later edits |
| Peer forwarding stalls | Core answers after local persistence and River reads the message in room state. Restart preserves that local result within the hosting budget |
| Signal drops; Wi-Fi has no internet; River starts before the first join | Save signed operations durably, restart offline and restore the pending queue. After reconnect or first join, an independent peer reads each message within the declared hosting budget. A repeated operation leaves one copy; a socket-write success keeps acceptance pending until room-state verification |
| A room is absent before its first update | River reads first. `NotFound` keeps the draft and enters the defined unavailable-room or recovery outcome |
| Settings conflict, messages repeat or the room secret changes | Replay a queued operation alongside concurrent remote updates and verify the contract merge. The [conflicting-change checks](#conflicting-changes) pass. Changed authority or retention rules produce a defined recovery outcome; River keeps affected drafts and verifies current membership and secrets before creating a replacement operation |
| Permission is revoked, the device locks or a session expires | The host enforces [1.3 Single-application host](03-host.md) and [1.5 Identity, keys and local protection](05-identity.md). Saved drafts remain protected. Forged identities fail, and calls between delegates, private replies and Core-started runs use only their verified authority |
| Remote room copies disappear while Alice retains hers | The [isolated recovery test](#lost-network-state) restores the same room contract and an independent peer reads it, including a room above 1 MiB through NAT |
| A release activates or changes delegate versions | Drafts and pending signed messages survive activation and the record migration in [1.7 Upgrades and migration](07-migration.md). Incompatible versions and message formats report defined errors with recoverable drafts |
| A backup is restored | Drafts and pending signed messages return through [1.10 Backup and restore](10-backup-and-restore.md#restore), and each room refreshes from the network |
