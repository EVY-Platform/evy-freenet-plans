# 1.3 Single-application host

## Repositories

| Repository | Role | Work in this plan |
| --- | --- | --- |
| [freenet-core](https://github.com/freenet/freenet-core) | Modified | `crates/mobile` gains caller admission, trusted calls, session authority, release activation at session boundaries and the host side of the SDK authority and policy hooks. Core's grant table gains app permission codes and a public API. [session admission #5264](https://github.com/freenet/freenet-core/issues/5264), [permissions #4014](https://github.com/freenet/freenet-core/issues/4014), storage [#5165](https://github.com/freenet/freenet-core/issues/5165) and [#5254](https://github.com/freenet/freenet-core/issues/5254), `RequestUserInput` and delegate startup [#5730](https://github.com/freenet/freenet-core/pull/5730) are the pinned admission evidence |
| `freenet-appkit` | Modified | Host bridge, iOS and Android WebView hosts and diagnostics redaction |

## Purpose

Run one defined application's code through authorized access to a Freenet node. Own the core host bridge, caller admission, basic session authority, release activation, base authorization and diagnostic redaction.

The first mobile route is River's web UI in a WebView served by the embedded node. Custom Swift/Kotlin applications use the same SDK from [1.2 Embedded node and mobile SDK](02-sdk.md).

## Who controls what

| Part | Authority |
| --- | --- |
| Trusted host | Activate releases, create sessions, enforce grants, scope storage and route callbacks |
| Host-owned screens | Show installation, permission, identity and recovery decisions outside application-controlled content |
| Application code | Own screens and orchestration through the permitted host/SDK interfaces |
| Core | Enforce authenticated client access and attest the immediate caller to delegates |
| Delegate | Apply its policy to the attested caller and protect its secret namespace |

Core's device-node delegate secret store uses the full delegate key as its namespace. [1.5 Identity, keys and local protection](05-identity.md#protected-keys-and-records) owns key and record protection.

In the hosted source profile, the per-user secret context derives from a shell-minted token stored in browser local storage. Verify its binding and isolation against the selected Core build before relying on it.

## Trusted calls

Some calls act with the app's authority. Examples are registering River's chat delegate and asking it to sign Bob's message. The host sends each of these calls to Core over a trusted path tied to:

- the verified app (River), by its full application container identity
- the exact release it runs, by the verified release reference supplied at installation
- the user (Bob) and the installation ID
- the current session generation

The host treats the release reference as an opaque value. [1.4 Application bundles](04-bundles.md#publishing-and-evidence) defines its encoding.

The host supplies the [caller hooks in 1.2 Embedded node and mobile SDK](02-sdk.md#caller-hooks):

- **Authority**: checks the current grant, target and session before each delegate call.
- **Policy**: checks the trusted installation and permission decisions, including approved foreground startup.

The host routes each response only to its authorized requester and discards expired-session callbacks. Core's web-app attestation identifies a contract, while user, installation and session bindings require the trusted host path.

The trusted path covers calls over the node's local WebSocket port. If another app on the same phone connects to that port and claims to be River, Core rejects its calls. [Session admission #5264](https://github.com/freenet/freenet-core/issues/5264) tracks this Core change upstream, and the [admission table](#freenet-issues-being-worked-on-that-are-required) holds its release check.

## Browser and native hosts

| Profile | Application execution | Required boundary |
| --- | --- | --- |
| River mobile | River's web code in a WebView, with files served by embedded Core | Trusted shell/bridge admission, isolated web storage and bounded node access |
| Custom native | Installed Swift/Kotlin UI calling the SDK | Trusted in-process calls with session authority |
| Browser | Publisher web code inside Core's sandboxed frame | Core shell admission, storage and capability enforcement |

River's [UI package](https://github.com/freenet/river/blob/main/ui/Cargo.toml) and [bundle configuration](https://github.com/freenet/river/blob/main/ui/freenet.toml) are evidence for the WebView route. Pin and test the actual artifacts under 1.1 Mobile feasibility and supported profiles.

The host must:

- Keep node credentials and privileged bridge methods in trusted code, and authenticate each caller, including loopback and alternate API paths.
- Bind frames, WebView messages and native calls to the verified session, and validate message source, navigation and target before forwarding requests.
- Scope cookies, web storage, caches, file access and native handles by application and user, and preserve the declared storage lifetime across reloads and restarts.
- Apply the node-only web sandbox policy to app code and loaded media, and route outside services, embedded pages and external links through approved adapters.
- Validate deep-link application identities, destinations and parameters before routing, and ensure external/native handoffs obtain explicit authority for keys or private data.

## Freenet issues being worked on that are required

| Requirement | Github links | Release check |
| --- | --- | --- |
| Core-authenticated app admission | [Session admission #5264](https://github.com/freenet/freenet-core/issues/5264) | Bind verified app identity to the connection or trusted in-process caller. Reject caller-selected identities on every equivalent path |
| Private delegate response routing | Source snapshot describes locality-based delivery to local clients. [Admission #5264](https://github.com/freenet/freenet-core/issues/5264) covers the caller boundary | Targeted replies and autonomous private events reach only authorized sessions |
| Declared, revocable permissions and per-app embedding | [Permissions #4014](https://github.com/freenet/freenet-core/issues/4014), [security discussion #5380](https://github.com/freenet/freenet-core/discussions/5380) | Enforce grants at each permission use, including page-initiated access |
| Fresh consent for expanded access | [Permissions implementation #4086](https://github.com/freenet/freenet-core/pull/4086), [review findings #4090](https://github.com/freenet/freenet-core/pull/4090) | A changed manifest prompts before any new access, and grants remain revocable |
| Durable, isolated web storage | [Storage #5165](https://github.com/freenet/freenet-core/issues/5165), [sandbox/storage #5254](https://github.com/freenet/freenet-core/issues/5254) | Reload and termination preserve only authorized records |
| Delegate prompts | Core's `RequestUserInput` message in the [stdlib delegate interface](https://github.com/freenet/freenet-stdlib/blob/main/rust/src/delegate_interface.rs) | Trusted prompts identify the requester and return only to the authorized request |

## Activating a release

The host runs a release only after installation has verified it and supplied its release reference.

- Activate a release only at a session boundary. Each session runs one release and its selected component and protocol versions.
- Create a fresh session generation for each activated release.
- Reject callbacks from older session generations.
- Keep the previous release active when activation is interrupted.

Subscriptions keep refreshing application data within a session.

## Suspending and reopening an app

[1.2 Embedded node and mobile SDK](02-sdk.md#start-stop-and-reconnect) owns node start/stop but the host has to invalidate the session on app suspension, and establish fresh authority on re-open with a new session.

## Base authorization and device access

A grant is the user's stored answer to one permission for one app. The host stores grants in Core's grant table, `app_capability_grants`, next to the `Background` grant from [#5730](https://github.com/freenet/freenet-core/pull/5730). Core adds a code for each permission and a public API that `crates/mobile` uses to get, set, revoke and list grants.

| Field | River example |
| --- | --- |
| App, by container contract ID | River |
| User | Bob |
| Permission code | `notifications` |
| Answer | Granted, or denied until a cool-off ends |

Removing an app deletes its grants. Store publisher trust decisions outside application-readable storage, as Core does for grants.

### Asking for a permission

The bundle's `permissions` field in [1.4 Application bundles](04-bundles.md#the-archive-and-its-definition) declares each permission as required or optional. The host asks in trusted host UI at one of two moments:

| Moment | Who starts it | River example |
| --- | --- | --- |
| When the UI needs it | App code, through the host bridge from web code or the SDK from Swift/Kotlin code | River calls `Notification.requestPermission()` when Bob sends his first message |
| First use | The host, when an action needs a permission without a grant | River copies an invite link for Carol, and the host asks for `clipboard` |

- Requests for undeclared permissions fail.
- A stored denial answers later requests until its cool-off ends, so app code gets one prompt per cool-off. The user can change the answer in the host's permission screen.
- After the trusted prompt, the host asks for the matching iOS or Android system permission if the phone lacks it.

### Using a grant

- Recheck grants before each protected operation and before queued work runs. Revocation stops further use at once.
- Prompt before an update adds a permission. Changed delegates and setup require installation approval.
- Require explicit authorization when sharing identity or private records between WebViews and native contexts.
- Return typed results: granted, denied, unavailable, locked device or expired handle. Bind selected files or photos to the requesting operation and session.

Camera, photos, files, notifications, clipboard, location, maps, contacts and outside services use only the adapters in the selected release profile. River's [notification integration](https://github.com/freenet/river/blob/main/ui/src/components/app/notifications.rs) is an application fixture. Notification taps validate the target and refresh application state before showing it. The foreground/background delivery promise belongs to [1.1 Mobile feasibility and supported profiles](01-feasibility.md#message-alerts).

Each delegate's Wasm manifest declares `Background`. The mobile host writes that grant when the user approves the installation. It also supplies Core's `UserInputPrompter`, so delegate prompts use trusted native screens. Browser hosts use Core's own prompt. Background work runs only while the SDK lifecycle keeps the node running.

## Diagnostics

Expose per-app connection state, subscription demand, last observation time, pending-operation counts, storage use, verified release, grants and typed failures. Exported reports redact keys, message bodies, session tokens, private references and private records by default.

## Acceptance

- Open River's real web UI on iOS and Android and exercise join, read, send, deep links, reload, termination and reconnect. A native fixture proves the declared SDK support level.
- Forged app identities, frames, bridge messages, loopback requests and expired sessions fail admission. App code stays within its supported network and storage policy.
- Targeted delegate replies and autonomous private results reach only authorized sessions.
- Activation happens only at a session boundary, creates a fresh session generation and rejects old-generation callbacks. Interrupted activation keeps the previous release active.
- Suspension invalidates the session, and reopening obtains fresh authority.
- Trusted prompts, expanded permissions, immediate revocation, locked devices and web/native handoffs enforce base authorization. Queued work rechecks authority.
- On iOS and Android, River's first-message notification request and first clipboard use both reach the trusted prompt and store a grant in Core's table. Undeclared requests fail, a stored denial answers without a new prompt, and removing River deletes its grants.
- Resource-exhaustion and malicious-input tests contain failure to the affected request or session.
- Each required browser or native admission path passes on the pinned Core build before that profile ships.

## One node per app

| Platform | Node placement | Cross-app requests |
| --- | --- | --- |
| iOS | Each app embeds its own node, as a full or thin peer. Apps from one developer team may share one node store in an App Group container, run by whichever app is in the foreground. That app closes the store and releases file locks before suspension. | A foreground app switch through universal links, carrying one request and one reply |
| Android | Each app embeds its own node. A node app may also offer a bound service that other apps call, protected by a permission. | An intent with a result, or calls to the bound service |
