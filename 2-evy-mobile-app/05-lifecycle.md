# Plan 2.5: Shared node, data and lifecycle

## Purpose

Own scheduling and resource allocation across applications. Combine subscription demand through the SDK, isolate app caches/journals and allocate per-app limits for work, storage, subscriptions and traffic. Apply [1.10's accounting and cap-enforcement rules](../1-freenet-mobile-appkit/10-thin-peer.md#cellular-budget-contract) to the shared node.

## Prerequisites

[1.2 node lifecycle](../1-freenet-mobile-appkit/02-sdk.md), [1.6 durable operations](../1-freenet-mobile-appkit/06-data-and-operations.md), [2.2 authority](02-sessions.md), [2.3 installation](03-installation-and-updates.md) and [1.10 cellular limits](../1-freenet-mobile-appkit/10-thin-peer.md).

## Scheduling and lifecycle

| App state | Scheduled work |
| --- | --- |
| Selected, host foregrounded | UI requests and active subscriptions within its allocation and the node's total limits. |
| Unselected, host foregrounded | Retained sessions and explicitly budgeted pending work/subscriptions. Suspend excess demand and show its freshness when reopened. |
| Closed app session | Release its demand and reject its late callbacks. Retain drafts and pending work under the host's data policy. |
| Host backgrounded | Save durable work and follow [1.1's foreground-only node lifecycle](../1-freenet-mobile-appkit/01-feasibility.md#scope-and-acceptance) on iOS and Android. |
| Foreground resume | Show labeled cached state, refresh within budget, recheck grants and reconcile uncertain operations before retry. |

On app suspension, save acknowledged drafts and journal changes, release that app's cancellable demand and invalidate its session. Reopening establishes fresh authority, shows retained state with its observation time, and reconciles pending operations.

Closing one app preserves the node and other active sessions within their remaining budgets. Retained compatible archives and artifacts needed by pending work remain subject to [2.3's storage policy](03-installation-and-updates.md#retention-and-recovery-choices).

## Acceptance

Concurrent River and Atlas workloads pass the shared thin-node limits, including idle, active, reconnect and serving-peer loss. One app's closure, excessive demand or failed refresh preserves the other's permitted work. Termination and storage exhaustion preserve committed drafts and journals.

Cross-app subscription isolation, retained records after app removal, separate authorized data deletion, and per-app/node-wide cap enforcement pass the later [2.7 product suite](07-acceptance.md). The [1.6 foundation tests](../1-freenet-mobile-appkit/06-data-and-operations.md#data-and-operation-acceptance) exercise two consumers within one application.
