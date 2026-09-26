# Plan 1.1: Mobile feasibility and supported profiles

## Purpose

Establish supported River WebView and custom Swift/Kotlin profiles from pinned builds and reproducible real-device evidence. Measure the workloads that set mobile limits and release budgets.

## Prerequisites

The selected [River scope in 1.8](08-reference-apps.md#river-scope) and proposed [1.10 role](10-thin-peer.md). Develop the device profile alongside [1.2](02-sdk.md) and 1.10.

## Recorded evidence

Source versions, local-build notes and issue states here are recorded planning evidence. Plan 1.1 rechecks them against pinned revisions and real-device results.

| Evidence | What to verify |
| --- | --- |
| [Rust client API](https://github.com/freenet/freenet-stdlib/blob/main/rust/src/client_api.rs), [River browser](https://github.com/freenet/river/blob/main/ui/Cargo.toml) and [CLI](https://github.com/freenet/river/blob/main/cli/Cargo.toml) dependencies | Rust stdlib has browser and native transports. Exercise their request encodings and errors with shared fixtures. |
| Existing [TypeScript SDK](https://github.com/freenet/freenet-stdlib/tree/main/typescript) | Preserve its supported web path and use it as a protocol comparison baseline. |
| Local Core `ios` branch, `crates/mobile` and `freenet-ios` package | Partial [UniFFI](https://mozilla.github.io/uniffi-rs/latest/) wrapper and iOS packaging. Verify build and device coverage, then complete Android packaging. |
| Local Atlas iOS demo using `FreenetWebRuntime` | Browser-client evidence through a WebView. Verify native application behavior separately. Core's branch records the [mobile WebView protocol](https://github.com/freenet/freenet-core/blob/ios/docs/mobile-web-runtime-protocol.md). |
| Recorded Core stdlib 0.12.0 and [migration library status](https://github.com/freenet/freenet-migrate#status) targeting 0.8.x with unreleased APIs | Pin compatible Core, stdlib, bindings and migration-library versions or a tested adapter before measurement. [Atlas fixtures](08-reference-apps.md#atlas-recorded-evidence-and-pinned-identity) record their own compatibility constraints. |

## Scope and acceptance

- Publish a support matrix for the River WebView route and custom Swift/Kotlin route. Record device models, OS versions, Android ABIs, compiler and dependency revisions, required adapters and unsupported operations.
- Prove reads, updates, subscriptions and actual delegate calls on real iOS and Android devices. Compare canonical bytes, cancellation, errors and callback ordering against shared protocol fixtures.
- Measure cold/warm startup, time to show cached data, package size, memory, CPU, battery, storage, large-record copying and subscription throughput. Separate SDK/binding costs from Core execution and UI costs. Establish device limits and test durations from these workloads.
- Run carrier NAT, UDP-filtering, Wi-Fi/cellular transition and resume tests under 1.10. Publish separate upload/download measurements and the approved limits for each workload.
- Use a foreground lifecycle for the first release. Save journals and drafts, stop transport work and shut down Core as the host backgrounds. Resume through a fresh session, state refresh and reconciliation.
- Scope message alerts to updates received while the host runs in the foreground. Show that scope in setup and settings. A supported notification is a hint to refresh verified state. Background delivery requires a delivery service, privacy policy, platform behavior and release approval before it becomes a product promise.
- Review the complete iOS and Android distribution packages, including downloaded website content, contract/delegate Wasm, interpreter use, signing, entitlements, permissions and lifecycle behavior. Record policy sources, review results and required changes for each distribution channel.

Acceptance requires reproducible device results for both platforms and an explicit supported-profile decision. Compilation establishes build coverage. Device runs establish usable behavior, and [1.9](09-release.md) applies the release gates.
