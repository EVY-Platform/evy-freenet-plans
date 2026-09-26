# SDUI hosts and readers

Plan ID: 4.3. Render the same screen definitions in browsers, SwiftUI and Jetpack Compose through adapters to the released host interfaces.

Prerequisites: [mobile feasibility, 1.1](../1-freenet-mobile-appkit/01-feasibility.md), [SDK, 1.2](../1-freenet-mobile-appkit/02-sdk.md), [host admission, 1.3](../1-freenet-mobile-appkit/03-host.md), [multi-app sessions, 2.2](../2-evy-mobile-app/02-sessions.md), [installation, 2.3](../2-evy-mobile-app/03-installation-and-updates.md), [device access, 2.4](../2-evy-mobile-app/04-permissions.md), [shared-node lifecycle, 2.5](../2-evy-mobile-app/05-lifecycle.md), [SDUI format, 4.1](01-format.md), and [bundles, 4.2](02-bundles.md). Mobile releases inherit [thin-peer and cellular acceptance, 1.10](../1-freenet-mobile-appkit/10-thin-peer.md).

## Reader boundary

Keep generated models, rendering, action execution and SDK transport in separate packages. Readers draw application content and emit typed events. The [executor](05-actions.md) runs declared steps through the host. The foundation owns sessions, grants, storage, operation journals, subscriptions and node lifecycle. [Plan 4.4](04-identity.md) binds the reader to those interfaces.

| Reader function | Browser | iOS | Android |
| --- | --- | --- | --- |
| Models | Generated TypeScript | Generated Swift | Generated Kotlin |
| Controls | Accessible HTML through React | SwiftUI | Jetpack Compose |
| State delivery | Browser events | Async streams and UI actor updates | Coroutines, Flow and UI-thread updates |
| Navigation | Browser history and focus restoration | Platform navigation | Platform navigation |
| SDK adapter | Supported browser client through the authorized host connection | Released Swift bindings | Released Kotlin bindings |

Schedule bounded executor and projection work away from the UI thread. Apply rendering changes on the platform's UI thread. Contain component failures, release view demand on close, and route callbacks by the host session generation.

## Browser package

Use TypeScript, React and Vite with published npm packages and Bun workspace scripts. Keep the protocol independent of React. Export both:

- `<freenet-web src="ui/sdui/ui.json">` for reader-only pages and custom applications in any framework, including a Rust web UI.
- `FreenetWeb` for React applications.

The reader receives a verified in-bundle screen path and an authorized host adapter. The [packager](02-bundles.md) copies the build to `ui/sdui/web/`. Test the built output in Core's supported shell and a development harness. Core's shell establishes the browser session and applies its sandbox policy.

Use relative assets. Bundle SDK Wasm, JavaScript bindings, CSS, fonts and icons when the selected build needs them. Load media through the host's approved paths. Component error boundaries report stable component IDs with redacted diagnostics. Lists use bounded windows. Keyboard handling, focus and browser history follow [4.1](01-format.md).

## Browser SDK measurement gate

A reusable [Rust-stdlib](https://github.com/freenet/freenet-stdlib/blob/main/rust/src/client_api.rs) browser Wasm package with JS/TS bindings is proposed work in this plan. Compare it with the existing [TypeScript SDK](https://github.com/freenet/freenet-stdlib/tree/main/typescript) under the same host authorization and fixtures. Select the reader adapter only after publishing measurements and supported-version results.

Measure reads, updates, subscriptions and delegate calls. Compare encodings, typed errors, request correlation, cancellation and callback ordering. Record compressed download size, startup, memory, large-record copying, subscription throughput, action steps, delegate calls and transferred bytes. Set acceptance budgets before the adoption run and report failures against them.

Record Core, stdlib, binding, reader and migration-library revisions, browser/device versions, workloads and adapter configuration. Measure embedded Core separately from binding and rendering costs. Keep milestone 1's River integration on its selected application SDK path. This reusable browser package is a milestone 4 deliverable.

## Native readers and target selection

Ship SwiftUI and Compose readers and their executor integrations with the host application. Fetch publisher screen and action definitions as verified data through [4.2](02-bundles.md). New supported action compositions arrive in application bundles. New native controls or executor primitives arrive through an installed-host release.

Use the existing embedded node and shared-node scheduler. Set reader limits for rendering, actions, subscriptions, storage and per-app traffic inside the host's total budgets. Measure idle, active, reconnect and archive-update traffic on real iOS and Android devices using the required thin-peer profile. Background behavior and message-alert promises follow the mobile foundation.

A host selects only a declared target whose requirements it supports. If native SDUI needs a newer reader, retain a compatible installation and explain the requirement. An available custom web target or endorsed native application can be offered through the host's normal opening flow. A target change follows host session and permission rules.

Custom pages and embedded SDUI share their page's authorized session and selected release. Closing an embedded reader releases its own demand while the rest of the application continues. Two EVY applications use separate sessions over the shared node.

## Native integration evidence

Use the pinned bindings and device evidence from the [mobile SDK plan](../1-freenet-mobile-appkit/02-sdk.md). Add SwiftUI and Compose reader tests to that support matrix. Record reader-specific costs and compatibility results with the released profile.

## Acceptance

- Browser, SwiftUI and Compose readers run one Atlas fixture through real Core and delegates with equivalent domain results.
- Reader-only and embedded web exports pass Core-shell loading, CSP, navigation and asset tests.
- The browser adapter decision includes reproducible comparison results and numerical acceptance budgets.
- Device tests cover UI-thread delivery, cancellation, late callbacks, termination, reconnect and resource exhaustion.
- Closing a reader preserves custom-page behavior and another application's active subscriptions.
- Required-feature failures retain a usable target and give an actionable requirement report.
- Mobile idle, active, reconnect and update workloads pass the inherited cellular limits with reader overhead included.
