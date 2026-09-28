# 4.3 SDUI hosts and readers

Render the same screen definitions in browsers, SwiftUI and Jetpack Compose through adapters to the released host interfaces.

Prerequisites:

- [1.1 Mobile feasibility and supported profiles](../1-freenet-mobile-appkit/01-feasibility.md)
- [1.2 Embedded node and mobile SDK](../1-freenet-mobile-appkit/02-sdk.md)
- [1.3 Single-application host](../1-freenet-mobile-appkit/03-host.md)
- [2.2 Multi-application sessions and authority](../2-evy-mobile-app/02-sessions.md)
- [2.3 Installation and updates](../2-evy-mobile-app/03-installation-and-updates.md)
- [2.4 Identity, permissions and device access](../2-evy-mobile-app/04-permissions.md)
- [2.5 Shared node, data and lifecycle](../2-evy-mobile-app/05-lifecycle.md)
- [4.1 SDUI format and compatibility](01-format.md)
- [4.2 SDUI bundles and publication](02-bundles.md)

Mobile releases inherit [1.10 Thin-peer role and cellular data budgets](../1-freenet-mobile-appkit/10-thin-peer.md).

## Repositories

| Repository | Role | Work in this plan |
| --- | --- | --- |
| `freenet-sdui` | Modified | Web reader packages exporting `<freenet-web>` and `FreenetWeb`, the pinned web-reader build for the packager, SwiftUI and Compose readers and reader tests |
| [freenet-stdlib](https://github.com/freenet/freenet-stdlib) | Modified | Rust-stdlib browser Wasm package with JS and TS bindings, adopted after the measurement gate |
| `freenet-appkit` | Modified | Reader host adapter: target selection, reader limits and session routing; the packaging CLI copies the web reader into `ui/sdui/web/`, generates reader-only `index.html` and checks reader support |
| [evy](https://github.com/EVY-Platform/evy) | Modified | iOS and Android apps build the native readers in |
| [atlas](https://github.com/freenet/atlas) | Used | One fixture run through all three readers |
| [freenet-core](https://github.com/freenet/freenet-core) | Used | Core's shell for browser loading, CSP and session tests |

## Reader boundary

Keep generated models, rendering, action execution and SDK transport in separate packages. Readers draw application content and emit typed events. The [executor in 4.5 SDUI actions and delegate protocols](05-actions.md) runs declared steps through the host. The foundation owns sessions, grants, storage, operation journals, subscriptions and node lifecycle. [4.4 SDUI identity and permissions](04-identity.md) binds the reader to those interfaces.

| Reader function | Browser | iOS | Android |
| --- | --- | --- | --- |
| Models | Generated TypeScript | Generated Swift | Generated Kotlin |
| Controls | Accessible HTML through React | SwiftUI | Jetpack Compose |
| State delivery | Browser events | Async streams and UI actor updates | Coroutines, Flow and UI-thread updates |
| Navigation | Browser history and focus restoration | Platform navigation | Platform navigation |
| SDK adapter | Supported browser client through the authorized host connection | Released Swift bindings | Released Kotlin bindings |

Apply rendering changes on the platform's UI thread. Contain component failures and route callbacks by the host session generation.

## Browser package

Use TypeScript, React and Vite with published npm packages and Bun workspace scripts. Keep the protocol independent of React. Export both:

- `<freenet-web src="ui/sdui/ui.json">` for reader-only pages and custom applications in any framework, including a Rust web UI.
- `FreenetWeb` for React applications.

The reader receives a verified in-bundle screen path and an authorized host adapter. Test the built output in Core's supported shell and a development harness. Core's shell establishes the browser session and applies its sandbox policy.

Use relative assets. Bundle SDK Wasm, JavaScript bindings, CSS, fonts and icons when the selected build needs them. Load media through the host's approved paths. Component error boundaries report stable component IDs with redacted diagnostics. Lists use bounded windows. Keyboard handling, focus and browser history follow [4.1 SDUI format and compatibility](01-format.md).

## Reader packaging

This plan extends the [packager in 4.2 SDUI bundles and publication](02-bundles.md) to ship the web reader in every SDUI archive. The `sdui` descriptor gains the bundled reader build:

```json
{
  "sdui": {
    "reader_build": { "version": "1.0.3", "digest": "sha256:3f9c…" }
  }
}
```

| Path | Contents |
| --- | --- |
| `index.html` | Publisher's web entry point, or a generated reader-only page |
| `ui/sdui/web/` | Pinned web-reader build and its required runtime assets |

| Web target | Entry-point behavior |
| --- | --- |
| Reader-only | Generated `index.html` loads the bundled reader and `ui/sdui/ui.json` |
| Custom web app with SDUI | Preserve its entry point and assets. Embed `<freenet-web src="ui/sdui/ui.json">` or the `FreenetWeb` React export |

The web-reader build is its own version identity: the exact bundled rendering and adapter code. The packager checks the bundled reader's supported versions against the archive's SDUI documents. Reader assets count toward the archive caps in 4.2 SDUI bundles and publication.

Each release includes its reader and assets in the archive download. Measure that cost in this plan's reader profile, including mobile update traffic within the inherited cellular budget.

## Browser SDK measurement gate

A reusable [Rust-stdlib](https://github.com/freenet/freenet-stdlib/blob/main/rust/src/client_api.rs) browser Wasm package with JS/TS bindings is proposed work in this plan. Compare it with the existing [TypeScript SDK](https://github.com/freenet/freenet-stdlib/tree/main/typescript) under the same host authorization and fixtures. Select the reader adapter only after publishing measurements and supported-version results.

Measure reads, updates, subscriptions and delegate calls. Compare encodings, typed errors, request correlation, cancellation and callback ordering. Record compressed download size, startup, memory, large-record copying, subscription throughput, delegate calls and transferred bytes. Set acceptance budgets before the adoption run and report failures against them.

Record Core, stdlib, binding, reader and migration-library revisions, browser/device versions, workloads and adapter configuration. Measure embedded Core separately from binding and rendering costs. Keep the River integration from milestone 1 (Freenet mobile AppKit) on its selected application SDK path. This reusable browser package is a milestone 4 (SDUI) deliverable.

## Native readers and target selection

Ship SwiftUI and Compose readers with the host application. Fetch publisher screen and action definitions as verified data through [4.2 SDUI bundles and publication](02-bundles.md). New native controls arrive through an installed-host release.

Use the existing embedded node and shared-node scheduler. Set reader limits for rendering, actions, subscriptions, storage and per-app traffic inside the host's total budgets. Measure idle, active, reconnect and archive-update traffic on real iOS and Android devices using the required thin-peer profile. Background behavior and message-alert promises follow the mobile foundation.

A host selects only a declared target whose requirements it supports. If native SDUI needs a newer reader, retain a compatible installation and explain the requirement. An available custom web target or endorsed native application can be offered through the host's normal opening flow. A target change follows host session and permission rules.

Custom pages and embedded SDUI share their page's authorized session and selected release. Two EVY applications use separate sessions over the shared node.

## Native integration evidence

Use the pinned bindings and device evidence from [1.2 Embedded node and mobile SDK](../1-freenet-mobile-appkit/02-sdk.md). Add SwiftUI and Compose reader tests to that support matrix. Record reader-specific costs and compatibility results with the released profile.

## Acceptance

- Browser, SwiftUI and Compose readers render one Atlas screen fixture.
- The packager builds a reader-only archive and a custom web archive with embedded SDUI, and both publish through the base release tooling.
- The packager rejects an incompatible bundled reader before publication.
- Reader-only and embedded web exports pass Core-shell loading, CSP, navigation and asset tests.
- The browser adapter decision includes reproducible comparison results and numerical acceptance budgets.
- Device tests cover UI-thread delivery, cancellation, late callbacks, termination, reconnect and resource exhaustion.
- Closing a reader preserves custom-page behavior.
- Required-feature failures retain a usable target and give an actionable requirement report.
- Mobile idle, active, reconnect and update workloads pass the inherited cellular limits with reader overhead included.
