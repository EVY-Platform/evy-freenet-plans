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

The hard cap covers every cellular network-layer byte sent or received by the installation's Freenet node, including framing, failed decryption, bootstrap, repair, retries, leases and teardown. Compare socket-level counters with packet/platform evidence and reserve for delayed accounting. Charge protocol overhead once to the application total.

| Traffic | Policy and measurement |
| --- | --- |
| Freenet website/assets and contract state | Node hard upload/download caps and reserves |
| Application HTTPS and OS file-provider traffic | Record bytes separately where measurable. Show the applicable application/provider network policy and measurement uncertainty. |
| Optional external downloads | Ask through the flow's declared consent and display expected size where known; use explicit adapter limits |

Release measurements show node bytes, external application/provider bytes and estimated total application usage separately. Host settings explain which traffic the node cap covers.

## Resource budgets

Each release profile records installation storage, website-cache retention, predecessor retention, subscription demand and pending-operation queue limits. Set numeric ceilings and capture/shutdown reserves from measurements before acceptance. Keep the releases and artifacts that saved drafts and pending messages require. A capacity failure preserves durable data and reports cleanup/update actions. All views share one application allowance.

## Cellular budget contract

Counting packets before decryption and ending serving-peer delivery lets the installation enforce its cellular allowance; release requires the selected Core build and iOS and Android measurements below.

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
| River reconnect | River re-subscribes each room with a full-state `Put { subscribe: true }` and holds outbound updates until each PUT reply arrives ([river#561](https://github.com/freenet/river/issues/561)) | Reconnect, serving-peer loss |
| Large-GET retries | A stalled stream restarts from its first fragment ([#4800](https://github.com/freenet/freenet-core/issues/4800)) | Reconnect, serving-peer loss |
| Large contracts | A peer fetches and verifies a contract's whole state before it reads any part ([discussion #678](https://github.com/freenet/freenet-core/discussions/678)). A first read of a large contract, such as Atlas's index, costs its full state | Active use |
| Protocol overhead | Interest-sync summaries were over half of outbound bytes ([#4965](https://github.com/freenet/freenet-core/issues/4965)). NeighborHosting sends the full hosted set to every peer every 5 minutes ([#5157](https://github.com/freenet/freenet-core/issues/5157)). Broadcast re-fan-out delivered each update about 18 times ([#5147](https://github.com/freenet/freenet-core/issues/5147)) | Foreground idle, total |
| Keepalives | Every connection pings every 5 s and backs off to 60 s when pings go unanswered ([#2404](https://github.com/freenet/freenet-core/pull/2404)) | Foreground idle, total |

Set these Core options explicitly for the thin role on cellular:

| Setting | Core default | Thin role on cellular |
| --- | --- | --- |
| `total-bandwidth-limit` ([config.rs](https://github.com/freenet/freenet-core/blob/e7d0b06c9326f377d250bf8344baaac2ba2658c6/crates/core/src/config.rs)) | None | Set it as the node's rate cap in bytes per second. It caps rate, so the byte budgets here still apply |
| Send rate per connection | 10 Mbps ([#2936](https://github.com/freenet/freenet-core/pull/2936)) | Size the cap reserves from it, since it sets how fast a reserve drains |
| `min-number-of-connections`, `max-number-of-connections` | 10 and 20 | Lower the connection count. Combine these limits with the negotiated thin role ([#1628](https://github.com/freenet/freenet-core/pull/1628)) |
| `max-hosting-storage` | `clamp(RAM / 8, 128 MiB, 1 GiB)` | Set explicitly, as [Storage in 1.2 Embedded node and mobile SDK](02-sdk.md#storage) does. Development full-peer profiles set it too |

Expose Core's upload and download counters as `node_traffic` in `crates/mobile`. Core counts uploads at the UDP socket and downloads after successful decryption ([#3996](https://github.com/freenet/freenet-core/pull/3996), [#4024](https://github.com/freenet/freenet-core/pull/4024)). Carrier billing also includes packets that fail decryption. The harness's `watch` scenario records `node_traffic` for each workload. Core separately measures bandwidth per peer ([#4455](https://github.com/freenet/freenet-core/pull/4455)).

Implement a raw receive-byte counter at the socket before decryption for cap enforcement, including failed packets and transport framing. Retain decoded/payload counters for diagnostics. The Core network lead owns this release dependency; completion requires comparison with controlled packet traces, rollover/restart recovery and delayed-sample reserve tests on iOS and Android. The SDK exposes both counters with their measurement layers.

For each workload:

- Count network-layer bytes and application payloads.
- Include bootstrap traffic, framing, encryption, retransmission, failed requests, repair and shared overhead.
- Record each counter's measurement layer.
- Reconcile SDK counters with iOS and Android platform counters or controlled packet traces on each supported OS.
- Account for other device traffic and report uncertainty in estimated carrier-billed usage.

Attribute app traffic where possible and charge shared overhead once to the total node budget.

Reserve bounded upload/download allowances inside the caps for counter delay, in-flight packets and teardown. Set byte and time limits from device measurements. Trigger cap enforcement when the remaining upload or download budget reaches its reserve, leaving that allowance to complete shutdown within the hard cap.

1. Persist usage and the exhausted-budget state, pause queued network work and keep drafts and the phone's copy of each contract. Show the cap and the condition for resuming.
2. Release affected downstream subscription demand and require serving peers to stop delivery. Count up to 8 minutes of delivery under the subscription lease against the reserve. Close affected serving connections if release is unavailable, unconfirmed or traffic continues, within the reserved byte/time limits. Count teardown and late packets against the reserve.
3. At a node-wide cap, release all downstream demand and close all cellular serving connections.
4. Stop automatic reconnects, resubscriptions and retries for the exhausted scope. Preserve this state through restart, foreground resume and network changes. Resume only when the approved budget policy grants a new allowance, using the thin role and normal reconciliation rules.

## Bandwidth improvements

### Client update deltas

Rollout requires matching sender/receiver fixtures and measured traffic reduction. The release profile records whether caps depend on this optimization.

File a Core issue for `RequestUpdate` to send a delta computed against the receiving peer's state summary. Each new message to "Skate club" then carries only the changes that peer needs, reducing cellular traffic. Use Core's broadcast delta handling for the receiving path.

Sources: [#4072](https://github.com/freenet/freenet-core/pull/4072) deferred the raw-delta wire format, `RequestUpdate` in [op_ctx_task.rs](https://github.com/freenet/freenet-core/blob/e7d0b06c9326f377d250bf8344baaac2ba2658c6/crates/core/src/operations/update/op_ctx_task.rs), and [#2427](https://github.com/freenet/freenet-core/pull/2427) on computing deltas against the receiver's summary.

## Acceptance

- On iOS and Android, idle, active, reconnect, serving-peer loss and accounting-overhead workloads meet the upload/download caps. Publish devices, carriers, durations, cap values, reserves and packet traces.
- With remote publishers sending continuously, exhaust upload and download allowances separately. Subscription release and connection shutdown end delivery within measured byte/time reserves.
- Restart, foreground resume and Wi-Fi/cellular changes preserve exhausted allowances and pending operations. A new allowance resumes reconciliation once.
- Storage and demand fixtures keep retained website releases, predecessor artifacts, drafts, pending signed messages and subscription leases within the installation budget.
