# AppKit Mobile Readers

**Parent plan:** [AppKit + EVY](README.md). **Depends on:** [AppKit SDUI](blocks-02-appkit-sdui.md), [Runtime](blocks-03-appkit-runtime.md), [Data Bindings](blocks-04-appkit-data-bindings.md). **Consumes, built separately:** [Freenet Mobile](../freenet-mobile/README.md).

The native readers render the same AppKit application definition with SwiftUI on iOS and Jetpack Compose on Android: native controls, navigation, accessibility, and performance, with cached state shown immediately and synchronization only while foregrounded. Network access and delegate operations go through Freenet Mobile on the device — each device holds its own delegate secrets (a cross-device trust anchor is future work, [Freenet Mobile §4](../freenet-mobile/README.md#4-future-improvement-a-delegate-trust-anchor)).

## 1. Shared contract, separate implementations

Do not use a WebView or React Native as the primary long-term renderer. Native renderers better match accessibility, navigation, input, camera/photo selection, secure storage, and platform lifecycle rules.

Share the protocol, not the code:

- generated models;
- expression/action specifications;
- JSON fixture definitions and semantic event traces;
- component behaviour requirements;
- stable component and route identifiers.

## 2. Platform packages

```text
iOS (Swift Package Manager)          Android (Gradle/Maven)
AppKitModels                         appkit-models
AppKitRuntime                        appkit-runtime
AppKitData                           appkit-data
AppKitSwiftUI                        appkit-compose
AppKitFreenetMobile                  appkit-freenet-mobile
AppKitTestFixtures                   appkit-test-fixtures
```

The iOS renderer uses `NavigationStack`, native sheets, `Observable`/async streams, and SwiftUI accessibility APIs, with structured local data in SQLite behind a small repository layer and root keys in Keychain. The Android renderer uses Compose Navigation, coroutines/Flow, Room or a small SQLite layer, and Android Keystore for root keys.

## 3. Component mapping

Each platform maintains a table from AppKit component type to native renderer. The protocol defines semantics; platform packages define presentation.

| AppKit component | iOS | Android |
| --- | --- | --- |
| `appkit.button` | SwiftUI `Button` | Material `Button` |
| `appkit.input` | `TextField`/`SecureField` | Compose text field |
| `appkit.list` | `List`/lazy stack | `LazyColumn` |
| `appkit.tabs` | tab view | navigation bar/tab row |
| `appkit.sheet` | `.sheet` | modal bottom sheet/dialog |

Unsupported optional presentation hints are ignored; unsupported required semantics are reported before the page opens ([Foundation §4](blocks-01-appkit-foundation.md#4-capabilities-and-extensions)).

## 4. Runtime, lifecycle, and local data

All renderer state changes happen on the platform UI actor/thread. Freenet Mobile and storage operations run asynchronously and emit typed events. Bindings subscribe through lifecycle-aware wrappers so inactive pages do not keep network subscriptions.

Backgrounding cancels network work, persists drafts and pending operations, and leaves the reader offline; resuming refreshes summaries before replaying pending updates — the lifecycle and offline rules of [Freenet Mobile §2.3](../freenet-mobile/README.md#23-lifecycle) and [Data Bindings §7](blocks-04-appkit-data-bindings.md#7-offline-updates).

Each reader locally keeps verified release records and SDUI definitions, the active contract cache, drafts and preferences, pending operations, route restoration state, and the installed extension list. Private delegate state stays inside Freenet Mobile/Core storage; readers receive only approved results.

## 5. The trusted host shell

The host application (EVY or another) owns, outside any app-controlled surface:

- app installation and update approval;
- capability and delegate permission prompts;
- external URL/app opening;
- extension installation;
- notification integration;
- account/device recovery UI.

An AppKit page cannot imitate these prompts; the shell uses a consistent, clearly separate presentation ([Runtime §7](blocks-03-appkit-runtime.md#7-security) states the rule; the [EVY App](blocks-09-evy-app.md) is the first implementation).

## 6. Platform capabilities

Declare platform capability differences in the reader capability set — camera, contacts, background notifications, maps, secure hardware. Apps mark them required or optional in the release record.

Push notifications are optional product integrations. They may say that data could have changed, but the reader always verifies current contract state after opening.

## 7. Delivery

Testing: generated model decode/encode tests; XCTest and Android unit tests for expressions and actions; snapshot tests only for stable component states, never as the sole correctness method; VoiceOver/TalkBack accessibility audits; fixture-driven navigation and form flows; lifecycle tests covering lock, background, force termination, resume, and network changes; real Freenet Mobile integration on physical devices; differential semantic traces against the web reference runtime.

| Phase | Delivers | Done when |
| --- | --- | --- |
| 1. Generated models | Swift Codable and Kotlin serialization models from AppKit schemas | Decode/encode round-trips match fixtures on both platforms |
| 2. Runtime cores | Shared semantic behaviour implemented natively per platform | Expression and action fixtures produce identical typed results |
| 3. Standard components | SwiftUI and Compose renderer catalogues | Standard components meet platform accessibility expectations |
| 4. Local stores | Cached contract values, drafts, routes, pending operations | Apps open from verified cached state with no network; pending writes survive process termination |
| 5. Freenet Mobile integration | Foreground get/update/subscribe and delegate calls | All connections and subscriptions stop after backgrounding |
| 6. Conformance | Same fixtures and semantic traces as the web reader | One fixture app completes the same user flow on web, iOS, and Android |
