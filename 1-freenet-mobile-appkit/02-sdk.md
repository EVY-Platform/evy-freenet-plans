# 1.2 Embedded node and mobile SDK

## Repositories

| Repository | Work in this plan |
| --- | --- |
| [freenet-core](https://github.com/freenet/freenet-core) | Embedded mobile interface, runtime changes and protected key storage |
| [freenet-appkit](https://github.com/glesage/freenet-appkit) | Swift SDK for iOS, Kotlin SDK for Android and platform integration |
| [freenet-stdlib](https://github.com/freenet/freenet-stdlib) | Public browser delegate methods and shared request-handling rules |

## Purpose

Run an embedded Freenet node inside each application installation. Expose its operations to Swift on iOS and Kotlin on Android, and support River's browser client inside an AppKit WebView.

Each installation owns one node, store and encryption key. All application features share its node.

Agree the architecture and Core changes with maintainers before specifying implementation details.

## Architecture

```mermaid
flowchart TD
  River[River in a WebView] --> Browser[Browser client]
  Fixture[Native SDK fixtures on iOS and Android] --> Native[Swift SDK on iOS / Kotlin SDK on Android]
  Browser --> Access[Application and session checks]
  Native --> Access
  Host[AppKit host policy and native prompts] --> Access
  Access --> Adapter[Request and event adapter]
  Adapter --> Core[Embedded Freenet Core]
  Coordinator[Installation lifecycle coordinator] --> Core
  Core --> Contracts[Contract and delegate execution]
  Core --> Store[Installation store and protected key]
  Core <--> Network[Freenet gateways and peers]
```

The host supplies access decisions. The SDK applies them to calls and events. The application data layer selects contracts and handles records. Core verifies state, executes delegates and exchanges data with peers.

## SDK interface and packages

Build the mobile interface in `crates/mobile` in freenet-core. Use [UniFFI](https://mozilla.github.io/uniffi-rs/latest/) to generate Swift bindings for iOS and Kotlin bindings for Android.

| Capability | SDK responsibility |
| --- | --- |
| Lifecycle | Start and stop the node, report status and recover connections |
| Contract reads and writes | Forward GET, PUT and UPDATE, including delta and full-state updates |
| Subscriptions | Deliver updates and restore the application's required contract set |
| Delegates | Register, unregister and message approved delegates |
| Prompts and permissions | Connect Core and application requests to trusted host decisions |
| Keys and locking | Use protected platform keys and control private access |
| Migration and recovery | Coordinate migration, export, restore and Forget |
| Traffic measurement | Report network use for the host's budget policy |

Preserve contract code, parameter bytes and record bytes through the bindings. Return each result to its originating caller and verify the returned contract identity.

- Package an XCFramework in the Swift package for iOS and an AAR in the Kotlin library for Android.
- Add the public browser methods needed for delegate registration, unregistration and messages.

## Node lifecycle and connectivity

### Start, stop and reconnect

One coordinator owns the node task and handles. It serializes all application lifecycle calls, including start, reconnect and stop. Define repeated-call results. Complete stop after the node task ends and the coordinator releases listeners, callbacks and store access.

```mermaid
stateDiagram-v2
  direction LR
  [*] --> Stopped
  Stopped --> Starting
  Starting --> Running
  Running --> Reconnecting: network path change
  Reconnecting --> Running
  Running --> Stopping
  Reconnecting --> Stopping
  Stopping --> Stopped
```

The host owns the application session. Reconnect replaces the connection. Locking, restore and Forget end affected sessions. Calls and callbacks belong to the current connection and session.

- Use the phone's network status to detect path changes on iOS and Android.
- Rejoin Freenet after a path change, restore required subscriptions and refresh retained state.
- Report the selected loopback port and prefer the previous port when available. Let the host recover its browser context when the port changes.
- Recover node failures while keeping the host process running.
- Disable Core telemetry on every start.

### Offline startup

The node opens its local store before joining Freenet. Users can read retained contracts and save recoverable pending changes offline. The node joins and resumes network work when connectivity returns.

- Resolve gateway hostnames during connection attempts so startup can complete offline.
- Refresh gateway discovery in the background and retry when connectivity returns.
- Add Core support for local reads, merges and subscription demand before the first join.
- Keep pending work recoverable when the selected Core build requires a network join before submission.

### Local network access

The host handles local-network consent on iOS and Android. The node can use permitted gateways and peers on the Wi-Fi network, and use public gateways when local access is denied.

- Connect node startup and reconnect to the host's permission decisions.
- Validate both permission outcomes on iOS and Android.

## Requests, events and errors

The transport adapter queues calls and routes replies and events under the caller's authority. River uses the browser route. Native fixtures test Swift on iOS and Kotlin on Android.

Requests retain their target, expected reply and owning session. Connection and session identifiers expire callbacks and prompts when their lifetime ends.

### Matching replies to requests

Allow one submitted request awaiting a reply per connection until Core and stdlib provide reliable request IDs on every enabled success and error path. Subscription updates and unsolicited delegate events continue while that request waits.

Cancellation removes queued work. Cancelling a submitted request ends the caller's wait while Core may still complete it. A timeout also leaves the outcome uncertain. Retain ownership until a terminal reply or connection reset, then check observed state before retrying a write.

For example, Bob cancels a room update while it is running. The message may still reach the room contract. River checks the room state before offering a retry.

- Apply the same queue, cancellation and reply-ownership rules to browser and native calls.
- Reject callbacks from ended connections and sessions.
- Reset a connection when reply ownership remains uncertain.
- Return errors the app can act on, including unavailable operations, uncertain writes and a required app update.
- Dispatch callbacks on the platform executor and keep slow listeners from delaying other delivery.
- Enable parallel requests after validating complete request-ID coverage.

## Subscriptions and application demand

The application data layer keeps one demand entry per contract and records why it is needed. Reasons include active records, retained drafts, pending operations and watched rooms. Screens observe the resulting data.

Retain demand while an application reason remains. Give pending-operation reconciliation priority over background refresh. Storage and cellular budgets bound the required contract set. The SDK restores that set once after reconnect.

For example, River's room list and conversation share one room subscription. Closing the conversation removes its reason. The room list and any pending message keep the subscription active.

- Accept the application's contract set and work priorities through the SDK.
- Release individual subscriptions when the selected client API supports it.
- Use reconnect and restoration to refresh the required set when cleanup follows the connection.
- End delivery on suspension, lock or stop.
- Preserve pending signed bytes and report stale observations when budgets suspend refresh work.

## Delegates and host permissions

Core runs approved delegates with application-defined messages and handlers. The host controls component access and presents trusted native prompts on iOS and Android.

Delegate prompts and private replies belong to the originating request and current session. Ending that session expires its prompts and private-event routes.

- Bind delegate registration, unregistration and messages to the application's approved component set.
- Expose host-supplied prompt handling through node construction, including delegate startup and capability requests.
- Combine declared device access, saved application consent and current OS permission status through the host's permission adapter.
- Apply equivalent access checks to browser calls, native calls and private-event delivery.

## Keys and private-data operations

### Keys and locking

Each installation uses its own protected encryption key and private records. The host supplies lock signals and disposes of application contexts. The SDK blocks private operations, clears controlled keys and buffers, and opens a fresh session on unlock.

- Integrate iOS Keychain storage and Android Keystore wrapping with Core's key backend.
- Implement and package required signing adapters for iOS and Android.
- Add Core secret-store lock and unlock operations and expose them through the SDK.
- Support key creation, loading, failure reporting and deletion.

### Migration and recovery

The lifecycle coordinator manages private-data work through the SDK. Applications supply record adapters. The owning plans define migration and recovery policy.

| Operation | SDK responsibility |
| --- | --- |
| Migration | Run the migration library with approved predecessor records and application adapters; report completion after verified readback |
| Export | Capture a consistent application snapshot before sealing it, with progress and cancellation |
| Restore | Stage and validate restored records, activate a complete set and open fresh sessions |
| Forget | Block new work, release resources and remove the installation's declared records and keys |

- Coordinate delegate secrets and host records as one application data set.
- Recover interrupted restore and deletion before opening the application.
- Resume ordinary work after a consistent export capture, while sealing finishes separately.

## Wasm runtime and storage

### Running Wasm

Use the [Pulley interpreter](https://docs.wasmtime.dev/examples-pulley.html) for contract and delegate execution in iOS and Android release builds. Validate the proposed execution model against both platforms' distribution requirements.

- Fix Core's host memory handling after Wasm memory grows so mobile instances can use smaller reservations.
- Agree the supported iOS and Android processor targets with maintainers.
- Validate equivalent contract and delegate results across both platforms.
- Measure memory use, execution time and throughput before setting mobile limits.
- Adopt Core executor and store defaults after the memory fix and device validation support them.

### Storage

The host supplies installation-specific data, configuration, secret, cache and log paths. Its chosen configuration takes precedence over persisted settings. Keep local-mode and network-mode stores separate.

- Set explicit memory, disk, cache and log budgets using device measurements.
- Separate rebuildable web-app caches from recovery records.
- Keep only current secret values; use application export for recovery.
- Preserve store ownership and usable paths through node restarts and platform data-folder changes.

## Traffic measurement

Expose sent and received network-byte counters through Swift on iOS and Kotlin on Android. Distinguish socket traffic from authenticated received traffic. Samples identify network path, timing and counter lifetime to retain usage across restarts.

- Add raw receive measurement before authentication for allowance enforcement.
- Preserve usage across counter resets, path changes and budget transitions in the host's persistent accounting.

## Work owned by other plans

| Plan | Responsibility |
| --- | --- |
| [1.1 Mobile feasibility and supported profiles](01-feasibility.md) | Device measurements, supported profiles and resource limits |
| [1.3 Single-application host](03-host.md) | Application sessions, component policy, native prompts and device permissions |
| [1.5 Identity, keys and local protection](05-identity.md) | Key protection, private-data inventory, locking and deletion policy |
| [1.6 Application protocols, data and operations](06-data-and-operations.md) | Record formats, application adapters and operation reconciliation |
| [1.7 Upgrades and migration](07-migration.md) | Migration policy and upgrade activation |
| [1.9 Testing and release](09-testing-and-release.md) | Release validation and distribution |
| [1.10 Backup and restore](10-backup-and-restore.md) | Snapshot, restore and recovery policy |
| [1.11 Cellular data and resource budgets](11-cellular-data-and-resource-budgets.md) | Allowances, traffic accounting and budget enforcement |

## Maintainer review

- Is the proposed embedded-node interface and UniFFI binding approach suitable?
- Can browser and native routes use the same request, session and authorization rules?
- Which Core changes are needed for offline startup, mobile Wasm execution, trusted prompts and locking?
- Which iOS and Android profiles should we validate first?

## Acceptance

- River and native SDK fixtures use an installation-owned embedded node on iOS and Android.
- The node starts offline, opens retained state and resumes network work when connectivity returns.
- Lifecycle calls and node recovery preserve store ownership and current-session delivery.
- Browser and native routes apply equivalent authorization, request ownership, cancellation and errors.
- Subscription restoration preserves the application's required contract set within its budgets.
- Delegates, prompts and private-data access follow host policy.
- Migration, export, restore and Forget preserve complete application records and recover interrupted work.
- Pulley execution and resource use pass iOS and Android profile validation.
- Local-network permission choices and traffic accounting work across network changes on both platforms.
