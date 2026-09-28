# 1.10 Thin-peer role and cellular data budgets

## Repositories

| Repository | Role | Work in this plan |
| --- | --- | --- |
| [freenet-core](https://github.com/freenet/freenet-core) | Modified | Thin role in the connect protocol, connection manager, ring and serving-peer selection, subscription delivery and lifecycle configuration; cellular budget accounting, cap enforcement and role and traffic diagnostics |
| `freenet-appkit` | Modified | Workload test definitions for the iOS and Android device runs |
| [paper-1](https://github.com/freenet/paper-1) | Used | Peers and ring section as the single-role baseline |
| [river](https://github.com/freenet/river) | Used | Join, read and send flows from 1.8 Reference apps and compatibility fixtures as the active-use workload |

## Purpose

Mobile release requires thin-peer networking within cellular budgets. Milestone 1 (Freenet mobile AppKit) proves this profile on real iOS and Android devices. Milestone 2 (EVY mobile app) inherits the same node-wide limits. Full-peer phone profiles are development-only.

## Prerequisites

The workloads and device matrix from [1.1 Mobile feasibility and supported profiles](01-feasibility.md), SDK integration from [1.2 Embedded node and mobile SDK](02-sdk.md), and upstream agreement on the Core role protocol. Work proceeds together, with upstream support and passing budgets required by release acceptance in [1.9 Developer package and release acceptance](09-release.md).

Status: proposed Core work and a release blocker. The evidence recorded on 2026-09-22 identifies [smartphone discussion #811](https://github.com/freenet/freenet-core/discussions/811) as the nearest upstream thread, with a dedicated thin-role issue pending filing. The [whitepaper's peers and ring section](https://github.com/freenet/paper-1/blob/main/sections/03-primitives.tex) describes a single peer role. These are recorded findings. Recheck them against the selected Core revision and record the proposal issue and accepted protocol before release.

## Scope and trust boundary

A thin peer opens terminal connections to serving full peers for its own reads, writes and subscriptions. On-device Core retains contract verification, delegate execution, signing and protected secrets. Serving full peers handle onward routing, fallback routing, hosting and subscription roots. Treat returned state as input for local verification.

| Core area | Required change |
| --- | --- |
| Connect protocol | Negotiate a versioned thin role and acknowledge it explicitly. Accept only thin-role connections for the release profile. |
| Connection manager | Retain terminal edges and their negotiated role across completion, reconnect and network changes. |
| Ring and serving-peer selection | Assign network routing/hosting to full peers. Bound serving connections, selection attempts and retries, with capacity and reachability errors. |
| Subscription delivery | Deliver only authorized active demand down terminal edges. Define unsubscribe, resubscribe and cleanup after disconnect. |
| Lifecycle and configuration | Persist the selected role, release downstream state and preserve thin behavior across startup and Wi-Fi/cellular changes. |
| SDK and diagnostics | Expose negotiated role, serving state, traffic counters, exhausted budgets and actionable failure reasons. |

An unsupported protocol or role fails visibly and retries within the configured budget while preserving the thin role. Exhausted attempts leave a visible disconnected state and retain local work. Only explicit development-fixture profiles may request a full-peer role.

Specify how thin nodes reach gateways and select replacement serving peers, including capacity limits and backoff. Test cleanup when peers disappear abruptly and deduplicate subscription demand after reconnect. Pin the client Unsubscribe capability with [1.2 Embedded node and mobile SDK](02-sdk.md) and prove that released demand stops consuming the cellular budget while other active sessions retain service.

## Cellular budget contract

Numerical thresholds, supported carriers, device coverage and test durations remain to be established. 1.1 Mobile feasibility and supported profiles supplies repeatable workloads and measurements. This plan owns explicit upload/download ceilings and enforcement. Approve them before release acceptance in 1.9 Developer package and release acceptance.

| Workload | Fix in the test definition | Required limits and measurements |
| --- | --- | --- |
| Foreground idle | Duration, subscribed contracts, state sizes and remote update rate | Separate upload/download bytes per interval, including keepalives and subscription maintenance. |
| Active use | River join/read/send sequence, message/state sizes, update rate and archive-fetch policy | Separate upload/download bytes per operation and workload, plus sustained/peak rates over defined windows. |
| Reconnect and network transition | Offline duration, stale state, pending work, Wi-Fi/cellular path and retry schedule | Upload/download bytes per reconnect, cumulative retry bytes, attempts and recovery time. |
| Serving-peer loss | Forced disconnects, unavailable candidates, repeated failures and recovery window | Upload/download bytes per loss and across the full failure window, bounded replacement attempts and subscription-repair traffic. |
| Traffic-accounting overhead | Counter collection, persistence, diagnostic/report export and instrumented comparison runs | Upload/download bytes added by accounting or reporting, plus CPU, memory and battery cost. |
| Total cellular use | All active apps, host work and shared protocol overhead over an approved period | Node-wide upload/download caps. Include retries, archive downloads and background-transition traffic. |

Count bytes at the network layer as well as application payloads. Include bootstrap traffic, framing, encryption, retransmission, failed requests, repair and shared overhead. Record each counter's measurement layer and reconcile SDK counters with platform counters or controlled packet traces on each supported OS. Account for other device traffic in the test setup and state the uncertainty in estimating carrier-billed usage.

Attribute app traffic where possible and charge shared overhead once to the total node budget. Product scheduling in [2.5 Shared node, data and lifecycle](../2-evy-mobile-app/05-lifecycle.md) divides this budget among apps.

Reserve bounded upload/download allowances inside the caps for counter delay, in-flight packets and teardown. Set byte and time limits from device measurements. Trigger cap enforcement when the remaining upload or download budget reaches its reserve, leaving that allowance to complete shutdown within the hard cap.

1. Persist usage and the exhausted-budget state, pause queued network work and retain durable operations. Show the cap and the condition for resuming.
2. Release affected downstream subscription demand and require serving peers to stop delivery. Close affected serving connections if release is unavailable, unconfirmed or traffic continues, within the reserved byte/time limits. Count teardown and late packets against the reserve.
3. At a per-app cap, release that app's demand. Other demand remains eligible within its allocation and the node-wide limits. At a node-wide cap, release all downstream demand and close all cellular serving connections.
4. Stop automatic reconnects, resubscriptions and retries for the exhausted scope. Preserve this state through restart, foreground resume and network changes. Resume only when the approved budget policy grants a new allowance, using the thin role and normal reconciliation rules.

## Upstream work and carrier evidence

File and link the role-design proposal, then track negotiation, terminal edges, serving-peer selection, subscription delivery and carrier acceptance against it. Preserve the behaviors covered by [GET routing for subscribed contracts #4222](https://github.com/freenet/freenet-core/issues/4222) and [placement migration #4440](https://github.com/freenet/freenet-core/issues/4440).

Recorded carrier evidence includes [mobile network restrictions #5051](https://github.com/freenet/freenet-core/discussions/5051) and [relay fallback #2925](https://github.com/freenet/freenet-core/issues/2925), recorded as closed without an implementation. Supported carrier paths need direct-transport or an implemented fallback proof. [Wake recovery #4951](https://github.com/freenet/freenet-core/issues/4951) supplies a resume regression case. Issue status and discussion notes are research evidence, while pinned builds and device runs establish release support.

## Acceptance

- Real iOS and Android devices complete River's [flows in 1.8 Reference apps and compatibility fixtures](08-reference-apps.md#river-acceptance-cases) through terminal connections while Core verifies state and runs signing delegates locally.
- Traces show application traffic and bounded protocol overhead on the phone. Serving full peers handle onward routing and network hosting.
- Unsupported roles, incompatible versions and exhausted serving capacity produce visible failures. Retry, restart, resume and network-change tests preserve the thin role.
- Malformed state, wrong contract identities and forged updates fail on-device validation. Serving peers receive only the application's authorized network payloads, while signing keys stay in the on-device protected boundary.
- Idle, active, reconnect, serving-peer-loss and accounting-overhead tests pass their approved upload/download budgets and total cellular caps. Publish workload definitions, revisions, devices, carriers, durations and traces with the results.
- Loss of a serving peer preserves pending operation identity, refreshes state and reconciles outcomes before safe retry. Repeated losses exhaust bounded attempts visibly.
- Keep remote publishers sending continuously as the upload and download stop thresholds are reached in separate runs. Test working, unavailable and unconfirmed subscription release. Network-layer traces must show terminal delivery ending within the teardown deadline and reserved bytes, with total use inside the hard caps. Continued publisher activity must leave the capped phone connection stopped.
- Restart, foreground resume and Wi-Fi/cellular changes preserve the exhausted state and suppress automatic traffic until a new allowance permits it. Retain pending operation IDs and exact bytes throughout.

Milestone 2 (EVY mobile app) adds [2.7 Multi-application acceptance](../2-evy-mobile-app/07-acceptance.md). Run the continuous-publish cap cases with both apps subscribed. Per-app caps preserve the other app's eligible demand, while a node-wide cap stops both streams within the shared reserve. Closing one session preserves the other's active subscriptions while its budgets permit.
