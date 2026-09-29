# 4.6 SDUI data and operation presentation

Bind controls to typed views, forms and local state, and display the send state of each update.

Prerequisites:

- [1.5 Identity, keys and local protection](../1-freenet-mobile-appkit/05-identity.md)
- [1.6 Application protocols, data and operations](../1-freenet-mobile-appkit/06-data-and-operations.md)
- [2.5 Shared node, data and lifecycle](../2-evy-mobile-app/05-lifecycle.md)
- [4.1 SDUI format and compatibility](01-format.md)
- [4.4 SDUI identity and permissions](04-identity.md)
- [4.5 SDUI actions and delegate protocols](05-actions.md)

The foundation owns storage and how updates are saved and sent. This plan owns the declarative binding and presentation layer.

## Repositories

| Repository | Role | Work in this plan |
| --- | --- | --- |
| `freenet-sdui` | Modified | Views, bindings, forms, protected-store bindings for private fields and drafts, saved state and send-status presentation |
| [freenet-core](https://github.com/freenet/freenet-core) | Used | Arrival times on reads in `crates/mobile` and update handling from 1.6 Application protocols, data and operations, and subscription handles from 1.2 Embedded node and mobile SDK |

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
| Send state | Read-only: draft, sent once Core answers, or rejected |

Private form fields and saved drafts use approved protected-store operations from [1.5 Identity, keys and local protection](../1-freenet-mobile-appkit/05-identity.md) and [1.6 Application protocols, data and operations](../1-freenet-mobile-appkit/06-data-and-operations.md). Saving, recovery and deletion of private values follow the host's retention policy.

A form declares validation feedback, submission action, save policy and discard policy. Submission captures one consistent snapshot of its values. An explicit action writes shared state. Keep recoverable input after validation failure, denied access or domain conflict.

Batch draft saves through the storage adapter and flush on pause, navigation and backgrounding according to the foundation lifecycle. Show whether a save is local, durable or waiting for storage. Restore only compatible form data under [4.9 SDUI migration and conformance](09-migration-and-conformance.md). Revocation and lock handling use [4.4 SDUI identity and permissions](04-identity.md).

## Send-status presentation

Bind a control to its draft and send state. Display the state with its next action: draft, sent once Core answers, or rejected when local validation fails. Core's answer means the phone's copy holds the update. A domain result follows the application's observation rule.

For a send Core hasn't answered, keep the draft and its signed bytes. Retrying sends those same bytes. Changing the content signs a new update. Reopening a page shows the draft, or the sent update from the node's copy.

For example, a seven-minute-old conversation with a five-minute maximum age displays its observation time and refreshes within the host budget. If a room-key rotation invalidates a reply that is still a draft, the delegate returns a conflict result and the reader keeps the draft for repair.

## Acceptance

- View fixtures cover loading, stale, missing, error and permission states, bounded shard queries and versioned caches.
- Identical locale, time zone, clock and input fixtures produce equal values and form snapshots across readers.
- Drafts survive supported restart and background flows. Storage failure produces a visible save status and preserves the recoverable copy.
- Closing a view releases its demand while other views continue. Late session events leave the new page unchanged.
- Duplicate responses, offline submission, termination before and after Core answers, and changed content show the correct send state.
- Rendering, navigation and repeated taps send each update once. Tests compare contract state as well as screen output.
