# 1.1 Mobile feasibility and supported profiles

## Repositories

| Repository | Role | Work in this plan |
| --- | --- | --- |
| `freenet-appkit` | Created | iOS and Android WebView demos, measurement harness, support matrix and device results |
| [freenet-core](https://github.com/freenet/freenet-core) | Modified | New `crates/mobile` started from clean main, with Pulley conformance runs on iOS and Android |
| [freenet-stdlib](https://github.com/freenet/freenet-stdlib) | Used | Rust client API transports and the TypeScript SDK as the protocol comparison baseline |
| [freenet-migrate](https://github.com/freenet/freenet-migrate) | Used | Pinned compatible version or tested adapter before measurement |
| [river](https://github.com/freenet/river) | Used | Pinned browser UI and CLI builds for the WebView route |
| [atlas](https://github.com/freenet/atlas) | Used | Browser Wasm client behind the WebView demos |

## Purpose

Establish supported River WebView and custom Swift/Kotlin profiles from pinned builds and reproducible real-device evidence. Measure the workloads that set mobile limits and release budgets.

## Prerequisites

The selected [River scope in 1.8 Reference apps and compatibility fixtures](08-reference-apps.md#river-scope) and proposed [1.10 Thin-peer role and cellular data budgets](10-thin-peer.md). Develop the device profile alongside [1.2 Embedded node and mobile SDK](02-sdk.md) and 1.10 Thin-peer role and cellular data budgets.

## Recorded evidence

Source versions, local-build notes and issue states here are recorded planning evidence. This plan rechecks them against pinned revisions and real-device results.

| Evidence | What to verify |
| --- | --- |
| [Rust client API](https://github.com/freenet/freenet-stdlib/blob/main/rust/src/client_api.rs), [River browser](https://github.com/freenet/river/blob/main/ui/Cargo.toml) and [CLI](https://github.com/freenet/river/blob/main/cli/Cargo.toml) dependencies | Rust stdlib has browser and native transports. Exercise their request encodings and errors with shared fixtures. |
| Existing [TypeScript SDK](https://github.com/freenet/freenet-stdlib/tree/main/typescript) | Preserve its supported web path and use it as a protocol comparison baseline. |
| Earlier local iOS prototype (Core `ios` branch) | Build the mobile crate again from a clean Core main with [UniFFI](https://mozilla.github.io/uniffi-rs/latest/) Swift and Kotlin bindings, iOS and Android packaging and equal device coverage. Carry forward the [prototype learnings](#prototype-learnings). |
| Atlas browser client in a WebView | Build fresh iOS and Android WebView demos on Atlas's browser Wasm client for browser-client evidence. Define the WebView host to Wasm client protocol in the new crate from the [prototype learnings](#prototype-learnings). Verify native application behavior separately. |
| Recorded Core stdlib 0.12.0 and [migration library status](https://github.com/freenet/freenet-migrate#status) targeting 0.8.x with unreleased APIs | Pin compatible Core, stdlib, bindings and migration-library versions or a tested adapter before measurement. [Atlas fixtures in 1.8 Reference apps and compatibility fixtures](08-reference-apps.md#atlas-recorded-evidence-and-pinned-identity) record their own compatibility constraints. |

## Prototype learnings

The earlier local iOS prototype proved the behaviors below. The fresh build starts from a clean Core main, applies each one on iOS and Android and re-tests it on real devices.

| Learning | Apply in |
| --- | --- |
| Run Wasm through the Pulley interpreter on JIT-less targets. Run the conformance suite (contract round trips, out-of-bounds traps, backend refusal) on every backend. | [runtime in 1.2 Embedded node and mobile SDK](02-sdk.md#runtime-packaging-and-lifecycle) |
| Own one process-wide async runtime in the mobile crate and build the node inside it. Install no process-global signal or abort handlers. Stop is an explicit call. | [1.2 Embedded node and mobile SDK](02-sdk.md#runtime-packaging-and-lifecycle) |
| Use the node's loopback WebSocket as the client API. Let the node pick a free loopback port at start, report it to the host and pass the resolved port explicitly so a persisted config never replaces it. | [owned API in 1.2 Embedded node and mobile SDK](02-sdk.md#owned-api), [1.3 Single-application host](03-host.md#browser-and-native-hosts) |
| Take data, config and log directories from the host. Keep local-mode and network-mode stores apart and discard a persisted config whose data directory or mode differs. | [storage paths in 1.2 Embedded node and mobile SDK](02-sdk.md#runtime-packaging-and-lifecycle) |
| Pass gateway overrides in Core's `--gateway` JSON shape. Fetch the public gateway index when network mode has no overrides. | [1.2 Embedded node and mobile SDK](02-sdk.md), [1.10 Thin-peer role and cellular data budgets](10-thin-peer.md#scope-and-trust-boundary) |
| Wait for at least one connected peer before the first network request, then retry reads for a bounded window. | [events in 1.2 Embedded node and mobile SDK](02-sdk.md#owned-api), [1.10 Thin-peer role and cellular data budgets](10-thin-peer.md) |
| Keep the WebView bridge to JSON commands and events. The Wasm client opens its own WebSocket to the loopback API. The host serves only a fixed set of bundle files, verified through a per-file SHA-256 manifest that carries a protocol version, and ignores unknown manifest keys. Android reproduces the generic layer byte for byte. | [1.3 Single-application host](03-host.md#browser-and-native-hosts), [archive in 1.4 Application bundles](04-bundles.md#the-archive-and-its-definition) |
| Test concurrent requests through one node actor, a two-peer contract exchange, leak thresholds tuned to measured noise, the update key-learning fallback and binding generation in CI. | [acceptance in 1.2 Embedded node and mobile SDK](02-sdk.md#acceptance), [fixtures in 1.8 Reference apps and compatibility fixtures](08-reference-apps.md#atlas-fixture-scope-and-acceptance) |

## Scope and acceptance

- Publish a support matrix for the River WebView route and custom Swift/Kotlin route. Record device models, OS versions, Android ABIs, compiler and dependency revisions, required adapters and unsupported operations.
- Prove reads, updates, subscriptions and actual delegate calls on real iOS and Android devices. Compare canonical bytes, cancellation, errors and callback ordering against shared protocol fixtures.
- Measure cold/warm startup, time to show cached data, package size, memory, CPU, battery, storage, large-record copying and subscription throughput. Separate SDK/binding costs from Core execution and UI costs. Establish device limits and test durations from these workloads.
- Run carrier NAT, UDP-filtering, Wi-Fi/cellular transition and resume tests under 1.10 Thin-peer role and cellular data budgets. Publish separate upload/download measurements and the approved limits for each workload.
- Use a foreground lifecycle for the first release. Save journals and drafts, stop transport work and shut down Core as the host backgrounds. Resume through a fresh session, state refresh and reconciliation.
- Scope message alerts to updates received while the host runs in the foreground. Show that scope in setup and settings. A supported notification is a hint to refresh verified state. Background delivery requires a delivery service, privacy policy, platform behavior and release approval before it becomes a product promise.
- Review the complete iOS and Android distribution packages, including downloaded website content, contract/delegate Wasm, interpreter use, signing, entitlements, permissions and lifecycle behavior. Record policy sources, review results and required changes for each distribution channel.

Acceptance requires reproducible device results for both platforms and an explicit supported-profile decision. Compilation establishes build coverage. Device runs establish usable behavior, and [1.9 Developer package and release acceptance](09-release.md) applies the release gates.
