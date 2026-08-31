# AppKit Web Reader

**Parent plan:** [AppKit + EVY](README.md). **Depends on:** [AppKit SDUI](blocks-02-appkit-sdui.md), [Runtime](blocks-03-appkit-runtime.md), [Data Bindings](blocks-04-appkit-data-bindings.md).

The Web Reader is the reference browser renderer for AppKit applications: it loads a signed release record and SDUI definition, connects to the user's local Freenet peer, and renders the application inside Freenet's web container security model. It is the fastest way to exercise AppKit semantics and doubles as the builder's preview engine.

It ships *after* the mobile readers, not before: Freenet's web platform still has open gaps — contract apps run in opaque-origin iframes where origin-keyed storage throws ([#5165](https://github.com/freenet/freenet-core/issues/5165), by design), per-app real origins are an unresolved design issue ([#5254](https://github.com/freenet/freenet-core/issues/5254)), and the permission manifest was shipped and reverted ([#4014](https://github.com/freenet/freenet-core/issues/4014)) — tracked in [README item 8](README.md). Everything below is built to be testable outside the container while those land.

## 1. Technology

Use TypeScript, React, and Vite. Use the official `@freenetorg/freenet-stdlib` package for the WebSocket connection to the local peer, and Bun for workspace scripts if aligned with the rest of AppKit, while preserving standard npm package output.

React is chosen because EVY's builder and web rendering code already use it, the accessibility ecosystem is mature, and component-level error boundaries are practical. The AppKit protocol itself stays framework-neutral.

Package layout and entry points:

```text
packages/web-reader/
  loader/  shell/  components/  runtime-adapter/
  freenet-provider/  local-store/  extensions/  diagnostics/

<AppKitReader appRef=... host=... />
createAppKitHost(config)
registerRendererExtension(extension)
```

## 2. Loading and trust

1. obtain an app/release reference from the container URL, Atlas, or an explicit link;
2. fetch and verify the signed release record ([Foundation §2](blocks-01-appkit-foundation.md#2-release-record));
3. compare required capabilities with the reader ([Foundation §4](blocks-01-appkit-foundation.md#4-capabilities-and-extensions));
4. ask the trusted host for required permissions — the untrusted app iframe cannot draw its own trusted prompt ([Runtime §7](blocks-03-appkit-runtime.md#7-security));
5. fetch the SDUI definition and referenced theme/language bundles;
6. render cached state and start active subscriptions.

## 3. Rendering

Map AppKit semantic components to accessible HTML. Use CSS variables for theme tokens and CSS layout primitives rather than inline absolute positioning.

Required behaviours:

- keyboard navigation and focus restoration;
- visible loading, stale, error, empty, and disabled states;
- route changes reflected in history where safe;
- responsive layouts using AppKit size classes;
- component-level error boundaries;
- deterministic test IDs derived from stable component IDs;
- optional reduced motion and high contrast support.

Virtualize large lists, but do not hide an oversized contract design behind UI optimisation — [Data Bindings §3](blocks-04-appkit-data-bindings.md#3-contract-provider-and-declared-views) requires sharding and indexes first.

## 4. Local state

The plan is IndexedDB behind a small wrapped interface for drafts, cached verified state, host-supplied permission grants, and pending operations, namespaced per app instance. Until per-app real origins land ([#5254](https://github.com/freenet/freenet-core/issues/5254)), that storage throws inside the container ([#5165](https://github.com/freenet/freenet-core/issues/5165)), so the reader feature-detects storage and degrades to in-memory state: drafts survive a route change, not a tab close, and the UI says so.

Do not store delegate secrets in browser storage under any mode. Sensitive operations go through delegates using the Freenet API.

## 5. Sandbox and packaging

Package all required JavaScript, CSS, fonts, and icons with the webapp unless a verified content reference is explicitly supported. Do not rely on external CDNs.

Vite decisions:

- `base: "./"` for container-relative assets;
- no runtime code generation or `eval`;
- split bundles by reader core and optional installed extensions;
- produce a deterministic manifest of artifact hashes;
- test the built output through an actual Freenet container (packaged with `freenet.toml`, the [fdev build manifest](https://freenet.org/build/manual/manifest/)), not only a dev server.

## 6. Extensions

Extensions are registered by the trusted host from signed installed packages ([SDUI §3](blocks-02-appkit-sdui.md#3-extensions)). They receive a narrow rendering API and runtime action interface — never the raw Freenet API, other apps' local data, or delegate secrets.

Unknown optional extension components render a declared fallback. Unknown required extensions block the page with an explanation.

## 7. Builder preview

The [App Builder](blocks-07-app-builder.md) embeds this same published reader package with a `MemoryProvider` and a draft definition stream. Preview-only tools, selection outlines, and drag targets live outside the reader component tree so production semantics stay unchanged.

## 8. Delivery

| Phase | Delivers | Done when |
| --- | --- | --- |
| 1. Shell and loader | Release-record verification, capability checks, UI definition loading | Malformed or untrusted release records and SDUI fail safely with an explanation |
| 2. Standard renderer | Accessible React components and theme tokens | Keyboard and screen-reader checks pass for standard components |
| 3. Runtime and providers | Actions, expressions, contract subscriptions, local drafts | Active subscriptions stop when routes no longer use them |
| 4. Trusted-shell boundary | Permission prompts and extension registration outside app content | An app page cannot draw or imitate a trusted prompt |
| 5. Packaging | Vite build for Freenet web containers | A fixture app runs from a packaged container with no external application server |
| 6. Conformance and performance | Playwright flows, shared semantic traces, budgets for cold load, parsing, first render, and large lists | The same shared semantic traces pass on web, iOS, and Android |

References:

- [Freenet user interfaces](https://freenet.org/build/manual/components/ui/)
- [Freenet TypeScript SDK](https://freenet.org/build/manual/typescript-sdk/)
