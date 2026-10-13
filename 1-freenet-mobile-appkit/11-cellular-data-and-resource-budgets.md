# 1.11 Cellular data and resource budgets

## Repositories

| Repository | Role | Work in this plan |
| --- | --- | --- |
| [freenet-core](https://github.com/freenet/freenet-core) | Modified | Network-byte counters, cap teardown and client deltas |
| [freenet-appkit](https://github.com/glesage/freenet-appkit) | Modified | Budget journals and iOS/Android measurements |

## Purpose

Measure and enforce one installation's Freenet traffic, storage and subscription budgets on iOS and Android. [1.8 Thin-peer protocol](08-thin-peer.md) owns terminal connections and serving peers.

Owner: AppKit network lead. Measure cap values and reserves for release-profile acceptance.

## Accounting scope and external traffic

The cellular allowance is a measured budget for the installation's Freenet traffic. Include framing, failed decryption, bootstrap, repair, retries, leases and teardown in the accounting model. Enforce the budget by limiting node-controlled sends, requests, connections and subscriptions, and stopping work at a measured threshold that leaves a shutdown reserve. Compare socket counters with packet/platform evidence and charge shared overhead once. Report carrier-billed usage as an estimate with the measurement uncertainty and any traffic observed after shutdown.

| Traffic | Policy and measurement |
| --- | --- |
| Freenet website/assets and contract state | Measured node upload/download budgets, enforcement thresholds and shutdown reserves |
| Application HTTPS and OS file-provider traffic | Record bytes separately where measurable. Show the applicable application/provider network policy and measurement uncertainty. |
| Optional external downloads | Ask through the flow's declared consent and display expected size where known; use explicit adapter limits |

Release measurements show socket payload bytes, estimated node network-layer bytes, external application/provider bytes and estimated carrier-billed usage separately. Host settings label the allowance as a Freenet traffic budget, state its accounting scope and show usage estimates with their uncertainty.

## Shared cellular transfer optimisation

The Core network lead owns cellular transfer improvements in Core and the shared Freenet sync implementation. Applications use their selected dependencies' supplied defaults and adopt improvements through normal dependency updates. Record the exact implementation versions, defaults and test artifacts. The private-data sync design in [RFC #5587](https://github.com/freenet/freenet-core/issues/5587) supplies proposed shard/chunk sizing; the selected released sync implementation establishes its actual defaults.

| Work | Shared validation |
| --- | --- |
| Transfer sizing and shard/chunk efficiency | Measure initial cold fetch, reconnect, checkpoint transfer and restored-device recovery using the supplied defaults. Include ciphertext and envelope overhead and test supported iOS and Android carrier paths |
| Transport throughput and retries | Measure slow serving peers, packet loss, transient lookup failures, interrupted streams and retry traffic using the carrier cases in [1.8 Thin-peer protocol](08-thin-peer.md#carrier-evidence) |
| Default changes | Publish the selected shared implementation and measured results. Verify protocol compatibility, traffic accounting, budget enforcement and preservation of pending operations on iOS and Android |

[3.2 Device sync](../3-optional-extensions/02-sync.md#traffic-and-lifecycle) owns EVY pairing, record semantics, membership and recovery. This plan owns shared cellular transfer optimisation and its measurements. Application release checks exercise their workloads with the selected defaults and enforce the existing traffic allowance.

## Resource budgets

Each release profile records installation storage, website-cache retention, predecessor retention, subscription demand and pending-operation queue limits. Set numeric ceilings and capture/shutdown reserves from measurements before acceptance. Keep the releases and artifacts that saved drafts and pending messages require. A capacity failure preserves durable data and reports cleanup/update actions. All views share one application allowance.

## Cellular budget contract

The host enforces the Freenet traffic budget using raw socket measurements, estimated transport overhead and bounded shutdown. Release requires numerical thresholds, byte/time reserves and passing measurements on the selected Core build and iOS and Android artifacts. Carrier/platform comparisons report uncertainty separately from the node-controlled enforcement result.

[1.1 Mobile feasibility and supported profiles](01-feasibility.md#startup-and-network) measured the full-peer numbers in [Purpose in 1.8 Thin-peer protocol](08-thin-peer.md#purpose). Its [harness](https://github.com/glesage/freenet-appkit/tree/1988c5cbdfc5c1f88065382de2a4f86093948b6e/harness) `watch` scenario and Core's `node_traffic` counters measure each workload. Use those measurements to set thin-role upload and download ceilings. Select supported carriers, devices and test durations, then enforce the ceilings.

| Workload | Fix in the test definition | Required limits and measurements |
| --- | --- | --- |
| Foreground idle | Duration, subscribed contracts, state sizes and remote update rate | Separate upload/download bytes per interval, including keepalives, state summary exchanges and subscription maintenance. |
| Active use | River join/read/send sequence, message/state sizes, update rate and archive-fetch policy | Separate upload/download bytes per operation and workload, plus sustained/peak rates over defined windows. Record state bytes, Wasm bytes and updates the serving peer drops separately. |
| Reconnect and network transition | Offline duration, stale state, pending work, Wi-Fi/cellular path, retry schedule and a room state above 1 MiB | Upload/download bytes per reconnect, cumulative retry bytes, attempts and recovery time. |
| Serving-peer loss | Forced disconnects, unavailable candidates, repeated failures and recovery window | Upload/download bytes per loss and across the full failure window, bounded replacement attempts and subscription-repair traffic. |
| Traffic-accounting overhead | Counter collection, persistence, diagnostic/report export and instrumented comparison runs | Upload/download bytes added by accounting or reporting, plus CPU, memory and battery cost. |
| Total cellular use | Freenet node work plus shared protocol overhead over a measured period | Node-wide upload/download caps. Include retries, archive downloads and background-transition traffic. |

| Cost | Traffic to measure | Workloads that count it |
| --- | --- | --- |
| Client UPDATE | Core forwards the full post-merge state to its peer ([#4072](https://github.com/freenet/freenet-core/pull/4072)). Each message Bob sends to "Skate club" costs the whole room state | Active use, reconnect |
| Update rate limit | A serving peer silently drops more than about 10 UPDATEs per second for one sender address and contract ([Core update rate limit](https://github.com/freenet/freenet-core/pull/4285)). Phones behind one carrier NAT share that limit | Active use, reconnect |
| Subscription lease | After Core sends Unsubscribe upstream, a GET or PUT in the previous 8 minutes keeps delivery going until that lease ends ([Core subscription lease](https://github.com/freenet/freenet-core/issues/4738)) | Cap enforcement reserve |
| Contract code in transfers | PUT and GET resend contract Wasm that the receiver already holds. Behind a mobile hotspot this was over 95% of PUT bytes ([#5707](https://github.com/freenet/freenet-core/issues/5707)) | Active use, reconnect |
| River reconnect | River restores known rooms with code-free GET subscriptions, reconciles missing local state as deltas and uses recovery PUTs for fresh/missing rooms or failed/timed-out subscriptions ([River PR #759](https://github.com/freenet/river/pull/759)). Measure GET, delta and fallback PUT bytes separately, including retries and independent readback | Reconnect, serving-peer loss |
| Large-GET retries | A stalled stream restarts from its first fragment ([#4800](https://github.com/freenet/freenet-core/issues/4800)) | Reconnect, serving-peer loss |
| Large contracts | A peer fetches and verifies a contract's whole state before it reads any part ([discussion #678](https://github.com/freenet/freenet-core/discussions/678)). A first read of a large contract, such as Atlas's index, costs its full state | Active use |
| Protocol overhead | Interest-sync summaries were over half of outbound bytes ([#4965](https://github.com/freenet/freenet-core/issues/4965)). NeighborHosting sends the full hosted set to every peer every 5 minutes ([#5157](https://github.com/freenet/freenet-core/issues/5157)). Broadcast re-fan-out delivered each update about 18 times ([#5147](https://github.com/freenet/freenet-core/issues/5147)) | Foreground idle, total |
| Keepalives | Every connection pings every 5 s and backs off to 60 s when pings go unanswered ([#2404](https://github.com/freenet/freenet-core/pull/2404)) | Foreground idle, total |

Set these Core options explicitly for the thin role on cellular:

| Setting | Core default | Thin role on cellular |
| --- | --- | --- |
| `total-bandwidth-limit` ([config.rs](https://github.com/freenet/freenet-core/blob/99612051c535ff7f18ce7c40857ecd236bbbdd46/crates/core/src/config.rs)) | None | Set it as the node's rate cap in bytes per second. It caps rate, so the byte budgets here still apply |
| Send rate per connection | 10 Mbps ([#2936](https://github.com/freenet/freenet-core/pull/2936)) | Size the cap reserves from it, since it sets how fast a reserve drains |
| `min-number-of-connections`, `max-number-of-connections` | 10 and 20 | Lower the connection count. Combine these limits with the negotiated thin role ([#1628](https://github.com/freenet/freenet-core/pull/1628)) |
| `max-hosting-storage` | `clamp(RAM / 8, 128 MiB, 1 GiB)` | Set explicitly, as [Storage in 1.2 Embedded node and mobile SDK](02-sdk.md#storage) does. Development full-peer profiles set it too |

Expose Core's upload and download counters as `node_traffic` in `crates/mobile`. Core counts uploads at the UDP socket and downloads after successful decryption ([#3996](https://github.com/freenet/freenet-core/pull/3996), [#4024](https://github.com/freenet/freenet-core/pull/4024)). Carrier billing also includes packets that fail decryption. The harness's `watch` scenario records `node_traffic` for each workload. Core separately measures bandwidth per peer ([#4455](https://github.com/freenet/freenet-core/pull/4455)).

Implement raw receive-byte and packet counters at the UDP socket before decryption, including failed packets and UDP payload framing. Retain authenticated/payload counters for diagnostics. Estimate IP/UDP headers separately using packet counts and the measured network-path profile. The Core network lead owns this release dependency; completion requires comparison with controlled packet traces, rollover/restart recovery and delayed-sample reserve tests on iOS and Android. The SDK identifies each counter layer and overhead estimate.

For each workload:

- Record raw socket payload bytes and packet counts; estimate network-layer totals with the measured IP/UDP overhead.
- Include bootstrap traffic, framing, encryption, retransmission, failed requests, repair and shared overhead.
- Record each counter's measurement layer.
- Reconcile SDK counters with iOS and Android platform counters or controlled packet traces on each supported OS.
- Account for external application traffic, other device traffic, carrier/platform differences and late packets; report uncertainty in estimated carrier-billed usage.

Attribute app traffic where possible and charge shared overhead once to the total node budget.

Reserve bounded upload/download allowances inside the budgets for counter delay, in-flight packets, overhead uncertainty and teardown. Set numerical byte and time limits from device measurements. Trigger enforcement when the remaining upload or download budget reaches its reserve. Record the shutdown traffic, any reserve overrun and late traffic separately; include those observations in the usage estimate and release evidence.

1. Persist usage and the exhausted-budget state, pause queued network work and keep drafts and the phone's copy of each contract. Show the cap and the condition for resuming.
2. Release affected downstream subscription demand and request that serving peers stop delivery. Size the shutdown window from measured traffic and lease behavior. Close affected serving connections by the deadline if release is unavailable, unconfirmed or continues using the reserve. Count teardown traffic and record late packets and reserve overruns.
3. At a node-wide cap, release all downstream demand and close all cellular serving connections.
4. Stop automatic reconnects, resubscriptions and retries for the exhausted scope. Preserve this state through restart, foreground resume and network changes. Resume only when the approved budget policy grants a new allowance, using the thin role and normal reconciliation rules.

## Bandwidth improvements

### Client update deltas

Rollout requires matching sender/receiver fixtures and measured traffic reduction. The release profile records whether caps depend on this optimization.

File a Core issue for `RequestUpdate` to send a delta computed against the receiving peer's state summary. Each new message to "Skate club" then carries only the changes that peer needs, reducing cellular traffic. Use Core's broadcast delta handling for the receiving path.

Sources: [#4072](https://github.com/freenet/freenet-core/pull/4072) deferred the raw-delta wire format, `RequestUpdate` in [op_ctx_task.rs](https://github.com/freenet/freenet-core/blob/99612051c535ff7f18ce7c40857ecd236bbbdd46/crates/core/src/operations/update/op_ctx_task.rs), and [#2427](https://github.com/freenet/freenet-core/pull/2427) on computing deltas against the receiver's summary.

## Acceptance

- On iOS and Android, idle, active, reconnect, serving-peer loss and accounting-overhead workloads meet the measured upload/download budget criteria. Publish devices, carriers, durations, budget values, enforcement thresholds, byte/time reserves, payload counters, overhead estimates and packet traces.
- With remote publishers sending continuously, exhaust upload and download allowances separately. The node stops controlled traffic within the declared shutdown deadline and measured reserve criteria. Record late incoming traffic and reserve overruns, including failed-decryption traffic; a failed criterion requires a corrected release profile before acceptance.
- Restart, foreground resume and Wi-Fi/cellular changes preserve exhausted allowances and pending operations. A new allowance resumes reconciliation once.
- Settings and diagnostics distinguish the Freenet traffic budget, external application traffic and estimated carrier-billed usage. The estimates retain their measurement layers, uncertainty and late-traffic evidence.
- Storage and demand fixtures keep retained website releases, predecessor artifacts, drafts, pending signed messages and subscription leases within the installation budget.
