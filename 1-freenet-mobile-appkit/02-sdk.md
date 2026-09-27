# 1.2 Embedded node and mobile SDK

## Repositories

| Repository | Role | Work in this plan |
| --- | --- | --- |
| [freenet-core](https://github.com/freenet/freenet-core) | Modified | `crates/mobile` delivers the owned API, UniFFI Swift and Kotlin bindings, Keychain and Keystore key backends, per-platform Wasm profiles and build scripts |
| `freenet-appkit` | Modified | Swift package and Kotlin library that wrap the bindings, package the XCFramework and AAR builds and add platform key-store adapters |
| [freenet-stdlib](https://github.com/freenet/freenet-stdlib) | Used | Client API request correlation, with an upstream request-ID extension as one selectable option |

## Purpose

Manage embedded Core, transport, lifecycle and platform bindings. The host supplies authenticated sessions, grants and storage paths. Core verifies contract state and executes delegates on the device. Serving full peers perform network routing and hosting.

## Prerequisites

Compatible versions and profiles from [1.1 Mobile feasibility and supported profiles](01-feasibility.md), the host authority interface in [1.3 Single-application host](03-host.md), key protection in [1.5 Identity, keys and local protection](05-identity.md) and role support from [1.10 Thin-peer role and cellular data budgets](10-thin-peer.md) for release operation.

## Owned API

| Operation | Required behavior |
| --- | --- |
| Start, stop and status | Serialize lifecycle transitions, define repeated-call results and retain the configured thin role. |
| Get and put | Validate code, original parameter bytes and returned instance identity. |
| Update by delta or full state | Correlate the result and preserve an uncertain outcome after timeout. |
| Subscribe and release | Return owned handles, reference-count demand and bound downstream traffic after release. |
| Register, unregister and message delegates | Authenticate the app/user/session and check current grants through the host. |
| Delegate startup and prompts | Apply the trusted host's installation and permission policy, including approved foreground startup. |
| Events and cancellation | Include SDK request and session identity, typed errors and submission uncertainty. Deliver callbacks on the platform's expected executor and reject expired-session callbacks. |

Build the mobile crate from a clean Core main with UniFFI Swift and Kotlin bindings and deliver this whole API, including delegate operations, full-state updates, structured events and iOS and Android build scripts. Apply the [prototype learnings in 1.1 Mobile feasibility and supported profiles](01-feasibility.md#prototype-learnings).

The recorded stdlib protocol correlates by response variant and contract key. Select and test safe request serialization or an upstream request-ID extension. SDK request IDs identify transport work. Application operation IDs in [1.6 Application protocols, data and operations](06-data-and-operations.md#operation-identity-and-journal) survive retries and restarts.

Client Unsubscribe is recorded as upcoming. Until the pinned API supports it, a subscription ends with its client connection. Publish and test a bounded cleanup strategy with 1.10 Thin-peer role and cellular data budgets that preserves other sessions' demand. Host-side reference counting alone establishes local demand, while network tests establish released traffic.

Every privileged call, including loopback calls, uses a trusted host-to-Core path bound to the verified app, content reference, user and session. [Session admission #5264](https://github.com/freenet/freenet-core/issues/5264) is recorded upstream work. [1.3 Single-application host](03-host.md) owns base authority policy. [2.2 Multi-application sessions and authority](../2-evy-mobile-app/02-sessions.md#delegate-namespace-policy) adds shared-node delegate namespace rules.

## Runtime, packaging and lifecycle

- Compile native Rust libraries and reproducible Swift/Kotlin bindings. Package Apple device/simulator builds and Android device/emulator builds for the selected ABIs with build scripts and checksums.
- Execute standard contract/delegate Wasm on the on-device node. The iOS profile uses the [Pulley interpreter](https://docs.wasmtime.dev/examples-pulley.html). Select and record the Android profile's Wasm backend per ABI through 1.1 Mobile feasibility and supported profiles and test both profiles with the same fixtures. Keep compiled caches local, bounded and keyed by backend/engine version.
- Test execution deadlines, memory growth, host-call cancellation, runtime shutdown and returned bytes/errors against desktop fixtures. Recorded Core defaults of 256 MiB per Wasm instance and 50 MiB per contract state are configuration evidence. Establish mobile limits through 1.1 Mobile feasibility and supported profiles and set an explicit mobile module-cache size because iOS lacks cgroup limits.
- Carry explicit role and host-supplied storage paths through restart, reinstall and container relocation. Keep fixture stores separate from network stores.
- Use one coordinator for startup, reconnect and shutdown. Save host journals before teardown, invalidate callbacks and release ports, runtime resources and store locks. Exercise termination during every transition.
- On network changes, rejoin and restore active subscriptions under the same thin role when [budget policy in 1.10 Thin-peer role and cellular data budgets](10-thin-peer.md#cellular-budget-contract) permits traffic. The recorded address-derived ring location and gateway rejoin behavior need explicit thin-role integration. Refresh state before application code reconciles pending mutations.

The SDK integrates and packages iOS Keychain and Android Keystore backends and any selected signing adapter. [1.5 Identity, keys and local protection](05-identity.md) owns protection guarantees, exposure limits and authorized export. Test locked-device, invalidated-key and unsupported-algorithm results on real devices against [Apple key protection](https://developer.apple.com/documentation/security/protecting-keys-with-the-secure-enclave) and [Android Keystore](https://developer.android.com/privacy-and-security/keystore).

[1.6 Application protocols, data and operations](06-data-and-operations.md) owns journals, the retained inventory of owned signed state, bounded authorized repair of missing network copies under the same identity, and readback evidence. [1.7 Upgrades and migration](07-migration.md) owns component and publisher upgrades. A local GET can use cached state, so label observation provenance and use a separate network retrieval when testing remote availability.

## Acceptance

Acceptance requires concurrent request isolation, real delegate calls, safe cancellation, bounded subscription cleanup and repeated start/stop/reconnect on both platforms. Verify pending work and original operation IDs through termination, and keep release traffic within 1.10 Thin-peer role and cellular data budgets.

Regression sources: [response correlation #5048](https://github.com/freenet/freenet-core/issues/5048), [streaming PUT #5458](https://github.com/freenet/freenet-core/issues/5458), [UPDATE lookup #5475](https://github.com/freenet/freenet-core/pull/5475), [timeout uncertainty #3465](https://github.com/freenet/freenet-core/issues/3465), [wake recovery #4951](https://github.com/freenet/freenet-core/issues/4951) and [missed updates #4681](https://github.com/freenet/freenet-core/issues/4681). Record the pinned revision and outcome when testing each behavior.
