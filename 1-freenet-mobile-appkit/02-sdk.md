# 1.2 Embedded node and mobile SDK

## Repositories

| Repository | Role | Work in this plan |
| --- | --- | --- |
| [freenet-core](https://github.com/freenet/freenet-core) | Modified | New `crates/mobile` interface, complete node-task teardown, offline startup, host-supplied key backend and host records |
| [freenet-appkit](https://github.com/glesage/freenet-appkit) | Modified | Swift package for iOS and Kotlin library for Android, with network-path monitoring |
| [river](https://github.com/freenet/river) | Used | Web client that runs against the embedded node |

## Purpose

Run an embedded Freenet node inside River's iOS and Android app. The Swift package on iOS and the Kotlin library on Android do three things:

- start and stop the node
- report its status
- run the WebView host

River's web client talks to the node itself, over the node's loopback WebSocket, as it does in a desktop browser.

Each installation owns one node, one store and one encryption key.

Agree the interface and Core changes with Core's maintainers before writing the code.

## Architecture

```mermaid
flowchart TD
  River[River web client in a WebView] -->|loopback WebSocket| Core[Embedded Freenet Core]
  River -->|shell-bridge messages| Host[WebView host: Swift on iOS, Kotlin on Android]
  Host -->|start, stop, status| Mobile[crates/mobile]
  Host -->|key load, store, delete| Mobile
  Mobile --> Core
  Core --> Store[Node store and encrypted secret store]
  Core <--> Network[Freenet gateways and peers]
```

| Part | What it does |
| --- | --- |
| River's web client | Reads and writes rooms, registers its chat delegate and resubscribes after a reconnect |
| WebView host | Loads River, handles shell-bridge messages, watches the network path and the app's foreground state |
| `crates/mobile` | Wraps Core for Swift and Kotlin: node lifecycle, status, settings, key backend and host records |
| Core | Verifies state, runs contracts and delegates, and talks to peers |

## SDK interface and packages

Add `crates/mobile` to freenet-core with this interface and generate the Swift bindings for iOS and the Kotlin bindings for Android from it with [UniFFI](https://mozilla.github.io/uniffi-rs/latest/).

| Interface item | What it provides |
| --- | --- |
| `MobileNode` | `new(settings)`, `start()`, `stop()`, `status()`, `info()` with the loopback port and River's URL, and `wait_for_peers()` |
| `NodeSettings` | Host-supplied data, config, secret, cache and log folders; network or local mode; gateway overrides; preferred loopback port; Wasm backend |
| `NodeEventListener` | Status changes, peer count and failures, implemented in Swift and Kotlin |
| `WebBundle` and `WebBridge` | Serve River's bundle files from the node and parse shell-bridge JSON messages, so iOS and Android share one implementation |
| `KekBackend` | Callbacks the host implements to load, store and delete the node encryption key. See [Keys and host records](#keys-and-host-records) |
| Host records | Get, put, delete and list for the host's own records. See [Keys and host records](#keys-and-host-records) |
| `MobileError` | Typed errors. See [Requests, events and errors](#requests-events-and-errors) |

Packages:

| Platform | Package | Targets |
| --- | --- | --- |
| iOS | XCFramework inside a Swift package | arm64 devices and the iOS Simulator |
| Android | AAR inside a Kotlin library | arm64-v8a and x86_64 |

## Node lifecycle and connectivity

### Start, stop and reconnect

One owner inside `crates/mobile` runs start, reconnect and stop one at a time. A repeated call returns the current state.

The node runs only while River is in the foreground. Locking the phone backgrounds the app, so it also stops the node.

```mermaid
stateDiagram-v2
  direction LR
  [*] --> Stopped
  Stopped --> Starting: app comes to the foreground
  Starting --> Running
  Starting --> KeyLost: installation key missing
  Running --> Reconnecting: network path change
  Reconnecting --> Running
  Running --> Stopping: app backgrounded or phone locked
  Reconnecting --> Stopping: app backgrounded or phone locked
  Stopping --> Stopped: node stopped
```

For example, Alice reads "Skate club" on the bus and then locks her phone:

1. The WebView host gives River about 2 seconds to save its drafts.
2. The host destroys River's WebView.
3. The host calls `stop()`. Core shuts down within one deadline and releases the loopback port, the store and the keys it holds.
4. When Alice unlocks and opens River again, the host starts the node and opens a fresh WebView.

Rules:

- Give every node-owned background task a retained cancellation and join handle, including tasks started during construction and transport startup. Track shared process-wide runtime tasks separately.
- `stop()` requests shutdown and lets node-owned tasks finish their cleanup within the shutdown deadline. It then cancels and joins any remaining node-owned tasks within that same deadline.
- `stop()` finishes only when every node-owned task has ended and the port, listeners, store and held keys are released. A remaining task or resource returns `IncompleteShutdown`. Keep lifecycle operations serialized until the remaining tasks and resources are reclaimed.
- Complete Core's task-teardown work tracked by [#6048](https://github.com/freenet/freenet-core/issues/6048) before the first iOS and Android release. Verify the selected fix against the task monitor and each registered task, using [Core's task-monitor implementation](https://github.com/freenet/freenet-core/blob/8942fd239b2b53e606ffb1e26ee986623008afb2/crates/core/src/node/background_task_monitor.rs) as the source baseline.
- Report the loopback port the node picked. Reuse the previous port so River keeps the same web origin and storage. If that port is taken, pick a free one and report it.
- Watch the network path with `NWPathMonitor` on iOS and `ConnectivityManager` on Android. On a change, rejoin Freenet. River's web client re-reads and resubscribes its rooms when its WebSocket reconnects ([river#759](https://github.com/freenet/river/pull/759)).
- Restart the node after a node failure while the app process keeps running.
- Turn off legacy telemetry and OpenTelemetry on every start, after the saved config is merged.
- Deliver listener callbacks on the iOS and Android main thread, so a slow listener cannot hold up the node's own threads.

### Offline startup

Alice opens River on the subway with no signal. She still sees "Skate club" and can write a message.

| Stage | What happens |
| --- | --- |
| Start | The node opens its store and the loopback API before it joins Freenet |
| Before the first join | River reads its stored rooms and its chat delegate. Core returns `PeerNotJoined` for network operations, and River keeps the unsent message in its chat delegate |
| After the first join | River sends the kept message and refreshes its rooms |

Core changes:

- Resolve gateway hostnames inside the join loop, so startup finishes offline.
- Serve stored contracts and delegate storage before the first join.
- Report "joined" separately from "WebSocket connected".
- Refresh gateway discovery when connectivity returns, and retry.

### Transport profile

Use one recorded transport profile for the first iOS and Android release:

| Setting | Release profile | Evidence |
| --- | --- | --- |
| `transport-quic` | Explicitly `off`; record the effective mode at startup | [Core 0.2.152 QUIC modes](https://github.com/freenet/freenet-core/blob/8942fd239b2b53e606ffb1e26ee986623008afb2/crates/core/src/transport/quic.rs#L82) |
| Congestion controller | Core's resolved default, recorded with its version | [Core transport configuration](https://github.com/freenet/freenet-core/blob/8942fd239b2b53e606ffb1e26ee986623008afb2/crates/core/src/config.rs) |
| `bandwidth-limit`, `total-bandwidth-limit` | Unset; measure traffic under [1.8 Thin-peer protocol](08-thin-peer.md#traffic-measurement) | [Node-wide UDP egress cap #5964](https://github.com/freenet/freenet-core/pull/5964), [per-connection streaming cap #6051](https://github.com/freenet/freenet-core/pull/6051) |
| `min-bandwidth-per-connection` | Record the resolved value with the cap settings | [Core transport configuration](https://github.com/freenet/freenet-core/blob/8942fd239b2b53e606ffb1e26ee986623008afb2/crates/core/src/config.rs) |

Core 0.2.152 maps `prefer` to `shadow`; application traffic uses the UDP transport. A later transport profile is an explicit release change with new iOS and Android connectivity, traffic, memory and task-cleanup evidence. Record configured and effective settings in the [release support matrix in 1.1 Mobile feasibility and supported profiles](01-feasibility.md#release-profile-evidence).

### Local network access

The host handles the iOS local-network prompt and Android's `ACCESS_LOCAL_NETWORK` permission.

- With access, the node may use gateways and peers on the Wi-Fi network.
- Without access, the node uses public gateways.
- Test both answers on iOS and Android.

## Requests, events and errors

River's web client sends its requests over the loopback WebSocket with freenet-stdlib's web API. Core matches each reply to its request as it does in a desktop browser. The Swift and Kotlin packages carry no contract or delegate calls.

The packages report node status and these typed errors:

| Error | Meaning | What River's app shows |
| --- | --- | --- |
| `StartFailed` | The node could not start | A retry screen |
| `KeyLost` | The installation key is missing | The key-loss screen |
| `UpdateRequired` | Peers refuse this build's Core version | "Update River", with a link to the App Store or Google Play |
| `IncompleteShutdown` | Stop passed its deadline with a node-owned task, port, store or key still held | Nothing; the host logs it and finishes teardown before another start |
| `NoGateways` | No gateway is known | A "no connection" banner |

## Keys and host records

| Item | What `crates/mobile` adds |
| --- | --- |
| Node encryption key | One generic host-supplied key backend in Core. The host implements its `load`, `store` and `delete` callbacks through UniFFI: Swift with the iOS Keychain, Kotlin with the Android Keystore |
| Host records | The host's private records, such as River's notification choice, are secrets in Core's existing encrypted secret store. They sit under a reserved host namespace. No key leaves Core |
| Missing key | Core records the backend in `secrets_dir/kek_backend` and loads the key only from it. A missing key returns `KeyLost` |

Use [kek.rs](https://github.com/freenet/freenet-core/blob/8942fd239b2b53e606ffb1e26ee986623008afb2/crates/core/src/config/kek.rs) and [#4137](https://github.com/freenet/freenet-core/issues/4137) as implementation references. Stopping the node releases the key and every key Core derived from it.

## Wasm runtime and storage

### Running Wasm

Run contracts and delegates with the [Pulley interpreter](https://docs.wasmtime.dev/examples-pulley.html) in iOS and Android release builds. The first release uses the fixed-reservation profile measured in [1.1 Mobile feasibility and supported profiles](01-feasibility.md#device-limits).

| Setting | Value |
| --- | --- |
| Wasm linear-memory reservation | 256 MiB per instance |
| iOS Store replacement | After 4 instances |
| iOS executors | At most 2 |
| Android executors and Store replacement | Measured per ABI and pinned in the release support matrix |
| Android ABIs | arm64-v8a and x86_64 |

- Check that contracts and delegates give the same results on iOS and Android, including memory growth and returned buffers.
- Measure memory, run time and capacity failures on the exact release builds.
- Adopt smaller reservations once an upstream Core release handles moving guest memory. Repeat the contract, delegate, memory-growth, capacity and lifecycle tests on iOS and Android before changing the profile.
- Add armeabi-v7a once smaller reservations are adopted and a 32-bit Android phone passes these tests.
- Change executor and Store limits only through a measured profile update. Record each setting and build digest in the release support matrix.

### Storage

The host supplies installation-specific data, config, secret, cache and log folders. Its settings take precedence over the saved config.

- Keep local-mode and network-mode stores apart. Discard a saved config whose folder, mode or gateway source differs.
- Use Core's default storage and memory settings. Record the resolved values in the release support matrix.
- Keep rebuildable web-app caches apart from secrets.
- Turn off Core's secret snapshots, so the phone keeps only each secret's current value.
- Keep store ownership and paths across node restarts and iOS container moves.

## Maintainer review

- Does the `crates/mobile` interface and the UniFFI approach suit Core?
- Is the generic host-supplied key backend acceptable in Core?
- Is a reserved host namespace in the secret store acceptable?
- Which Core changes are needed for offline startup and mobile Wasm execution?

## Acceptance

- On iOS and Android, River runs against its installation's own embedded node.
- Start, stop and reconnect follow the state diagram. Locking the phone and backgrounding the app both stop the node.
- On iOS and Android, stop releases every node-owned task, the port, store and keys within its deadline, or returns `IncompleteShutdown`.
- Run repeated start/stop cycles within one live app process on iOS and Android. Cover normal stop, a shutdown timeout and a startup failure. Per-generation task counters show zero live node-owned tasks after completed teardown; stale callbacks cease, the stopped generation's samplers stop updating counters, and the port and store can be reused. Record shared process-wide runtime tasks and caches separately; shared task counts remain stable across cycles and caches stay within their configured bounds.
- The release support matrix records the configured and effective transport settings. A profile change passes the affected iOS and Android connectivity, traffic, memory and lifecycle tests.
- After a restart, the node reuses its previous loopback port. With that port taken, it reports a new port.
- Offline startup shows River's stored rooms and chat delegate before the first join.
- The Keychain backend on iOS and the Keystore backend on Android load, store and delete the node key. A missing key returns `KeyLost`.
- Host records survive a restart and stay inside Core's encrypted secret store.
- Pulley execution passes the measured profile on iOS and on both Android ABIs.
- Local-network permission answers work across network changes on iOS and Android.
- A test peer that requires a newer Core gives `UpdateRequired` on iOS and Android.
