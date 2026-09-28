# 4.6 SDUI data and operation presentation

Bind controls to typed views, forms and local state, and display durable operation outcomes from the host.

Prerequisites:

- [1.5 Identity, keys and local protection](../1-freenet-mobile-appkit/05-identity.md)
- [1.6 Application protocols, data and operations](../1-freenet-mobile-appkit/06-data-and-operations.md)
- [2.5 Shared node, data and lifecycle](../2-evy-mobile-app/05-lifecycle.md)
- [4.1 SDUI format and compatibility](01-format.md)
- [4.4 SDUI identity and permissions](04-identity.md)
- [4.5 SDUI actions and delegate protocols](05-actions.md)

The foundation owns storage, journals, operation identity, idempotence and retry. This plan owns the declarative binding and presentation layer.

## Repositories

| Repository | Role | Work in this plan |
| --- | --- | --- |
| `freenet-sdui` | Modified | Views, bindings, forms, protected-store bindings for private fields and drafts, saved state and pending-operation presentation |
| [freenet-core](https://github.com/freenet/freenet-core) | Used | Bounded reads, subscription demand accounting, storage adapter and operation handles in `crates/mobile` from 1.6 Application protocols, data and operations |

## Views

Each view reads a [logical resource from 4.5 SDUI actions and delegate protocols](05-actions.md#logical-resources-and-query-policy). It names typed inputs and outputs, its allowed query within that resource's policy, result bounds and maximum age. Tie each view's subscription demand to its page or action lifetime. The host reference-counts shared demand and schedules refreshes within the total cellular budget. Closing one view releases its demand.

| View state | Meaning and presentation |
| --- | --- |
| `loading` | First read is pending. Show the declared placeholder |
| `ready` | A verified projection is available through the selected adapter |
| `stale` | Its age exceeds the view's limit. Show the value and observation time while refresh is pending |
| `missing` | The contract or record is absent. Show the declared empty or missing state |
| `error` | The bounded read failed. Show its typed error and permitted retry control |
| `permission_required` | A host grant is needed. Retain the current form and request trusted host UI |

Freshness uses the host-recorded response time, or an application timestamp whose meaning and verification the view declares. Label observation time separately from a publisher's data timestamp. The [client API evidence in 1.6 Application protocols, data and operations](../1-freenet-mobile-appkit/06-data-and-operations.md) owns response correlation and local-cache behavior.

Key cached projections by their resource identity and definition/delegate versions. Notify changed views and show stale metadata when restoring a cache. Cache retention and private-data protection use the foundation's storage policy.

## Bindings

Bindings use the [value model and display expressions in 4.1 SDUI format and compatibility](01-format.md#values-and-expressions). A reference resolves to a declared view output, an immutable route parameter, a form value or temporary display state. [Domain adapters under 4.5 SDUI actions and delegate protocols](05-actions.md) calculate business values.

Check binding paths at publication and page activation.

## Forms and saved state

| Value | Binding and lifetime |
| --- | --- |
| Route parameters | Typed and immutable for one route entry |
| Temporary display state | Scoped to the active reader session |
| Form draft | Versioned form ID, storage key, initial values and recovery policy |
| Saved private value | Approved protected-store operation, using the application's delegate where that is its storage profile |
| Operation status | Read-only projection of the host's durable operation record |

Private form fields and saved drafts use approved protected-store operations from [1.5 Identity, keys and local protection](../1-freenet-mobile-appkit/05-identity.md) and [1.6 Application protocols, data and operations](../1-freenet-mobile-appkit/06-data-and-operations.md). Saving, recovery and deletion of private values follow the host's retention policy.

A form declares validation feedback, submission action, save policy and discard policy. Submission captures one consistent snapshot of its values. An explicit action writes shared state. Keep recoverable input after validation failure, denied access or domain conflict.

Batch draft saves through the storage adapter and flush on pause, navigation and backgrounding according to the foundation lifecycle. Show whether a save is local, durable or waiting for storage. Restore only compatible form data under [4.9 SDUI migration and conformance](09-migration-and-conformance.md). Revocation and lock handling use [4.4 SDUI identity and permissions](04-identity.md).

## Pending-operation presentation

Bind a control to the operation handle returned by the host. Display the foundation's queued, submitted, rejected, accepted, superseded or unresolved outcome with its evidence and available next action. An accepted domain result follows the application's observation rule. A local submission response supplies only the status its owning interface guarantees.

For an unresolved send, keep the message pending while the host reconciles it. Retrying asks the host to resume the existing operation. Repairing its content requests a successor under the foundation rules. Canceling closes local cancellable work while the host continues tracking submitted mutations. Reopening a page reconnects to that operation by its durable reference.

For example, a seven-minute-old conversation with a five-minute maximum age displays its observation time and refreshes within the host budget. If a room-key rotation invalidates a queued reply, the delegate returns a conflict result and the reader keeps the draft for repair.

## Acceptance

- View fixtures cover loading, stale, missing, error and permission states, bounded shard queries and versioned caches.
- Identical locale, time zone, clock and input fixtures produce equal values and form snapshots across readers.
- Drafts survive supported restart and background flows. Storage failure produces a visible save status and preserves the recoverable copy.
- Closing a view releases its demand while other views continue. Late session events leave the new page unchanged.
- Duplicate responses, offline submission, timeout, reconciliation, superseded results and repair show the correct foundation outcome.
- Rendering, navigation and repeated taps preserve the host's durable-operation and idempotence rules. Tests compare journal results as well as screen output.
