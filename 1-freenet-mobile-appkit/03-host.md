# 1.3 Single-application host

## Repositories

| Repository | Role | Work in this plan |
| --- | --- | --- |
| [freenet-core](https://github.com/freenet/freenet-core) | Modified | `crates/mobile` gains caller admission, trusted calls, session authority, release activation at session boundaries and the host side of the SDK authority and policy hooks. This plan needs two Core changes: an embedder-supplied `UserInputPrompter` that never spawns a browser on iOS or Android, and grant table codes for each app permission with a call that sets a grant and a public API. The [admission table](#freenet-issues-being-worked-on-that-are-required) lists the Core issues each release checks |
| `freenet-appkit` | Modified | Host bridge, iOS and Android WebView hosts, shell-bridge message handling and diagnostics redaction |
| [river](https://github.com/freenet/river) | Used | River's web UI and chat delegate are the first hosted app |
| [freenet-stdlib](https://github.com/freenet/freenet-stdlib) | Used | The delegate manifest ([stdlib #136](https://github.com/freenet/freenet-stdlib/pull/136)) and `RequestUserInput` |

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

Delegates have broken that last rule in practice. An identity delegate authorized any calling web app ([raven#64](https://github.com/freenet/raven/pull/64)), and Ghostkeys took the attested app identity as enough to export and delete keys ([ghostkeys#28](https://github.com/freenet/ghostkeys/pull/28)).

Core's device-node delegate secret store uses the full delegate key as its namespace. [1.5 Identity, keys and local protection](05-identity.md#protected-keys-and-records) owns key and record protection.

In the hosted source profile, the per-user secret context derives from a shell-minted token stored in browser local storage. Verify its binding and isolation against the selected Core build before relying on it.

## Trusted calls

Some calls act with the app's authority. Examples are registering River's chat delegate and asking it to sign Alice's invitation of Carol. The host sends each of these calls to Core over a trusted path tied to:

- the verified app (River), by its full application container identity
- the exact release it runs, by the verified release reference supplied at installation
- the user (Alice) and the installation ID
- the current session generation

The host treats the release reference as an opaque value. [1.4 Application bundles](04-bundles.md#publishing-and-evidence) defines its encoding.

The host supplies the [caller hooks in 1.2 Embedded node and mobile SDK](02-sdk.md#caller-hooks):

- The authority hook checks the current grant, target and session before each delegate call.
- The policy hook checks the trusted installation and permission decisions, including approved foreground startup.

The host routes each response only to its authorized requester and discards expired-session callbacks. Core's web-app attestation identifies a contract, while user, installation and session bindings require the trusted host path.

The trusted path covers calls over the node's local WebSocket port. Core mints a token for any contract ID to any loopback client. A client that sends no Origin header gets full API access ([#3011](https://github.com/freenet/freenet-core/pull/3011), [client API exposure](https://github.com/freenet/freenet-core/blob/main/docs/client-api-exposure.md)). So another app on the same phone can connect to that port and claim to be River. [Session admission #5264](https://github.com/freenet/freenet-core/issues/5264) tracks the Core change that rejects its calls, and the [admission table](#freenet-issues-being-worked-on-that-are-required) holds its release check.

## Browser and native hosts

| Profile | Application execution | Required boundary |
| --- | --- | --- |
| River mobile | River's web code in a WebView, with files served by embedded Core | Trusted shell/bridge admission, isolated web storage and bounded node access |
| Custom native | Installed Swift/Kotlin UI calling the SDK | Trusted in-process calls with session authority |
| Browser | Publisher web code inside Core's sandboxed frame | Core shell admission, storage and capability enforcement |

[1.1 Mobile feasibility and supported profiles](01-feasibility.md) confirmed that River's and Atlas's web UIs run in WKWebView and Android WebView, served by the embedded node from their pinned website containers ([device results](https://github.com/glesage/freenet-appkit/blob/main/docs/device-results.md#river-and-atlas-in-the-webview)).

The host must:

- Keep node credentials and privileged bridge methods in trusted code, and authenticate each caller, including loopback and alternate API paths.
- Bind frames, WebView messages and native calls to the verified session, and validate message source, navigation and target before forwarding requests.
- Scope cookies, web storage, caches, file access and native handles by application and user, and preserve the declared storage lifetime across reloads and restarts.
  - River runs in Core's shell page, inside a sandboxed frame with an opaque origin and no web storage of its own. Core's shell keeps its records in the loopback origin's local storage, such as its `freenet_notify:<key>` alert consent record ([#5165](https://github.com/freenet/freenet-core/issues/5165)).
  - The WebView keys web storage by origin, and the origin includes the host name and the node's loopback port. `localhost`, `127.0.0.1` and `[::1]` are three origins ([#4330](https://github.com/freenet/freenet-core/issues/4330)), so the host always loads `127.0.0.1`. The host asks the node for the port from the last run and takes a new free port only when that one is taken. After a stop, the host waits until the port is free before it starts the node again. The shell then keeps its records across restarts.
- Handle each [shell-bridge message](#shell-bridge-messages) from River's frame.
- Apply the node-only web sandbox policy to app code and loaded media, and route outside services, embedded pages and external links through approved adapters. The WebView host enforces this policy itself, because a page script can get around Core's in-frame shims ([#4845](https://github.com/freenet/freenet-core/issues/4845), [#4846](https://github.com/freenet/freenet-core/issues/4846), [#5123](https://github.com/freenet/freenet-core/issues/5123)).
- Validate deep-link application identities, destinations and parameters before routing. External and native handoffs get explicit authority before they touch keys or private data.

### Shell-bridge messages

River's frame posts `__freenet_shell__` messages to Core's shell for anything its opaque origin cannot do. The host's bridge script in the shell page receives each one first.

| Message | What Core's shell does | What the host does |
| --- | --- | --- |
| `notification_enable_prompt` | Shows an Enable button, calls `Notification.requestPermission()` from its own frame and replies `notification_status` ([#4801](https://github.com/freenet/freenet-core/pull/4801), [#5094](https://github.com/freenet/freenet-core/pull/5094)) | Replies `notification_status` with River's stored `notifications` answer, with no new prompt |
| `notification` | Shows a browser alert when the browser permission and the app's stored consent allow it | Shows a native alert when River holds the `notifications` grant. After a stored denial, River's alerts stay in-app |
| `clipboard` | Writes the text with no grant after a user tap, at most once per second and at most 2,048 characters ([#3748](https://github.com/freenet/freenet-core/pull/3748), [#4015](https://github.com/freenet/freenet-core/pull/4015)) | Writes the text with no grant and no prompt, under the same three rules as Core's shell. Android 13 and later shows a short system confirmation |
| `download` | Saves the file, at most one every 2 seconds | Hands the file to the approved files adapter |
| `open_url` | Opens an http or https URL in a new tab | Validates the URL and opens it through the approved external-link adapter |
| `navigate` | Moves the frame within the same app, or loads another app's shell | Validates the app identity and destination as for a deep link |

River's web UI copies invite links with `document.execCommand('copy')` inside its own frame ([util.rs](https://github.com/freenet/river/blob/main/ui/src/util.rs)), so those copies need no host involvement.

## Freenet issues being worked on that are required

| Requirement | Github links | Release check |
| --- | --- | --- |
| Core-authenticated app admission | [Session admission #5264](https://github.com/freenet/freenet-core/issues/5264) | Bind verified app identity to the connection or trusted in-process caller. Reject caller-selected identities on every equivalent path |
| Private delegate response routing | A delegate's notification output goes to every client that has messaged that delegate ([#4682](https://github.com/freenet/freenet-core/pull/4682)). Core withholds it from non-local connections ([#5211](https://github.com/freenet/freenet-core/pull/5211)). A delegate hop is not a privacy boundary ([#5363](https://github.com/freenet/freenet-core/pull/5363)). All delegates share one lossy notification channel ([#5561](https://github.com/freenet/freenet-core/issues/5561)) | Targeted replies and autonomous private events reach only authorized sessions. The host filters them per session, because Core routes them by client connection |
| Declared, revocable permissions and per-app embedding | [Permissions #4014](https://github.com/freenet/freenet-core/issues/4014), [security discussion #5380](https://github.com/freenet/freenet-core/discussions/5380) | Enforce grants at each permission use, including page-initiated access |
| Fresh consent for expanded access | [Permissions #4014](https://github.com/freenet/freenet-core/issues/4014) is the open tracker. [#4090](https://github.com/freenet/freenet-core/pull/4090) lists the gaps an implementation must close. [#5730](https://github.com/freenet/freenet-core/pull/5730) is the working precedent for revocable grants | A changed manifest prompts before any new access, and grants remain revocable |
| Durable, isolated web storage | [Storage #5165](https://github.com/freenet/freenet-core/issues/5165), [sandbox/storage #5254](https://github.com/freenet/freenet-core/issues/5254) | Reload and termination preserve only authorized records |
| Delegate prompts | Core's `RequestUserInput` message in the [stdlib delegate interface](https://github.com/freenet/freenet-stdlib/blob/main/rust/src/delegate_interface.rs). Open prompt bugs are [#5749](https://github.com/freenet/freenet-core/issues/5749), [#5537](https://github.com/freenet/freenet-core/issues/5537) and [#4966](https://github.com/freenet/freenet-core/issues/4966). Core drops a prompt from a delegate that another delegate called ([#5364](https://github.com/freenet/freenet-core/issues/5364)). Local mode drops prompts ([#5273](https://github.com/freenet/freenet-core/issues/5273)) | Trusted prompts identify the requester and return only to the authorized request. Each answer binds to its own prompt ([ghostkeys#24](https://github.com/freenet/ghostkeys/issues/24)). Prompt tests run the node in network mode |

## Activating a release

The host runs a release only after installation has verified it and supplied its release reference.

- Activate a release only at a session boundary. Each session runs one release and its selected component and protocol versions.
- Create a fresh session generation for each activated release.
- Clear the WebView cache for the app at that boundary. Core's web responses carry an `ETag` but no `Cache-Control` header, so an open WebView keeps running the old build ([#5323](https://github.com/freenet/freenet-core/issues/5323)). A cached old River UI keeps writing to a room contract's old key after a re-key ([river#580](https://github.com/freenet/river/issues/580)).
- Reject callbacks from older session generations.
- Keep the previous release active when activation is interrupted.

Subscriptions keep refreshing application data within a session.

## Opening, suspending and reopening an app

[1.2 Embedded node and mobile SDK](02-sdk.md#start-stop-and-reconnect) owns node start and stop, including an offline start. The host owns the app's session.

When Alice opens River on the subway with no signal:

1. The host loads River's website container from the node's store, without waiting for a peer.
2. River shows "Skate club" from her phone's copy. Her sends wait until the node first joins, as [1.2 Embedded node and mobile SDK](02-sdk.md#start-stop-and-reconnect) describes.
3. Once the node has a peer, the host fetches any update to River's container. A new release activates at the next session boundary.

Online, loading the stored container first saves about 0.5 s on the public network ([cached-app finding in 1.1 Mobile feasibility and supported profiles](https://github.com/glesage/freenet-appkit/blob/main/docs/findings.md#smaller-items)).

While the node joins, Core answers a page request it cannot serve from the store with its connecting page, and that page sends the WebView to the dashboard. So an invite link Bob opens during node start can lose its target ([#5745](https://github.com/freenet/freenet-core/issues/5745)). [#5750](https://github.com/freenet/freenet-core/pull/5750) keeps the link's URL.

When the user leaves the app, the host ends the session. When the user reopens it, the host creates a new session with fresh authority.

Core's token for River's page stays valid until it goes unused for 24 hours, and it survives a disconnect ([#1976](https://github.com/freenet/freenet-core/pull/1976)). So the host's session generation ends River's authority. After a node restart, Core closes the WebSocket with code 4401 and the shell reloads River's frame ([#4781](https://github.com/freenet/freenet-core/pull/4781)). River also reloads its own frame on `AUTH_TOKEN_INVALID`, which races the shell's reload ([river#522](https://github.com/freenet/river/issues/522)).

## Base authorization and device access

A grant is the user's stored answer to one permission for one app. The host stores grants in Core's grant table, `app_capability_grants`, from [#5730](https://github.com/freenet/freenet-core/pull/5730).

- Each grant key holds a user scope, the app and a permission code. Core has one code today, `Background`.
- Core lists and revokes grants over loopback HTTP: `GET /permission/grants`, `POST /permission/grants/revoke` and the `/permission/apps` page ([#5744](https://github.com/freenet/freenet-core/pull/5744)).
- Core writes a grant only when the user answers its own prompt, and its Rust grant functions are `pub(crate)`.

This plan needs Core to add a code for each permission, a call that sets a grant and a public API that `crates/mobile` uses to get, set, revoke and list grants.

| Field | River example |
| --- | --- |
| App, by container contract ID | River |
| User scope | `Node`, which on Bob's phone is Bob. Core writes only this scope today ([#5736](https://github.com/freenet/freenet-core/issues/5736)) |
| Permission code | `notifications` |
| Answer | Granted or denied |

Removing an app deletes its grants. Store publisher trust decisions outside application-readable storage, as Core does for grants.

### Asking for a permission

The bundle's `permissions` field in [1.4 Application bundles](04-bundles.md#the-archive-and-its-definition) declares each permission as required or optional. The host asks in trusted host UI at one of three moments:

| Moment | Who starts it | When the host asks |
| --- | --- | --- |
| At first run | The host | The user first runs an app that declares `notifications` |
| When the UI needs it | App code, through the host bridge from web code or the SDK from Swift/Kotlin code | The app requests another declared permission that has no answer yet |
| First use | The host | An action needs another declared permission that has no answer yet |

On iOS and Android, River's `app_definition.json` declares `notifications`:

1. Bob first runs River, in River's store build or inside EVY. The host asks for `notifications` and stores Bob's answer as a grant in Core's table.
2. Bob taps "Enable notifications" in River's [notification modal](https://github.com/freenet/river/blob/main/ui/src/components/room_list/notification_modal.rs), or sends his first message, and River posts `notification_enable_prompt`. The host replies with the stored answer and shows no new prompt.
3. River posts a `notification` for a new message in "Skate club". The host shows a native alert when Bob allowed notifications. After a denial, River's alerts stay in-app.
4. Bob changes his answer in the host's permission screen and in the matching iOS or Android system setting.

Atlas declares no permissions, so running Atlas never raises a prompt. In a browser, Core's shell keeps its own timing, as in [Shell-bridge messages](#shell-bridge-messages).

- Requests for undeclared permissions fail.
- For a permission asked when the UI needs it or at first use, a stored denial answers later requests for 7 days, Core's cool-off, so app code gets one prompt per cool-off. The user can change the answer in the host's permission screen.
- A first-run denial of `notifications` stays until Bob changes it in the host's permission screen. River's `notification_enable_prompt` never asks again.
- Core denies a prompt that nobody answers within 60 seconds and stores nothing ([#3811](https://github.com/freenet/freenet-core/pull/3811)). When the first-run prompt gets no answer, the host asks again the next time Bob runs River.
- After the trusted prompt, the host asks for the matching iOS or Android system permission if the phone lacks it.

### Using a grant

- Recheck grants before each protected operation and before queued work runs. Revocation stops further use at once.
- Prompt before an update adds a permission. Changed delegates and setup require installation approval.
- Require explicit authorization when sharing identity or private records between WebViews and native contexts.
- Return typed results: granted, denied, unavailable, locked device or expired handle. Bind selected files or photos to the requesting operation and session.

Camera, photos, files, notifications, clipboard, location, maps, contacts and outside services use only the adapters in the selected release profile. River's [notification integration](https://github.com/freenet/river/blob/main/ui/src/components/app/notifications.rs) is an application fixture. Notification taps validate the target and refresh application state before showing it. Alerts arrive only while the host is in the foreground, as [1.1 Mobile feasibility and supported profiles](01-feasibility.md#message-alerts) confirmed on iOS and Android.

#### Background runs and delegate prompts

A delegate that needs startup runs or wake-ups declares them, with `Background`, in its Wasm manifest ([stdlib #136](https://github.com/freenet/freenet-stdlib/pull/136)). River's chat delegate declares no manifest. It rotates private-room secrets when a room update arrives ([subscription.rs](https://github.com/freenet/river/blob/main/delegates/chat-delegate/src/subscription.rs)), and its room subscriptions survive a node restart ([#5728](https://github.com/freenet/freenet-core/pull/5728)).

When an app registers a delegate whose manifest lists startup runs or wake-ups, Core raises the `Background` consent itself, through the prompter's `prompt_capability` call. The mobile host answers that call from the installation approval, so the user sees no second prompt.

Manifests can also declare wake-ups ([#5747](https://github.com/freenet/freenet-core/pull/5747)). Core fires a wake-up only while the app holds the `Background` grant. On iOS and Android, wake-ups and other background work run only while the SDK lifecycle keeps the node running.

Core always builds its own `DashboardPrompter` (`p2p_impl.rs`), and its `user_input` module is `pub(crate)`. With no dashboard tab open, that prompter spawns `xdg-open` on iOS and Android. This plan needs Core to let an embedder supply the `UserInputPrompter` and never spawn a browser on iOS or Android. The mobile host's prompter shows delegate prompts in trusted native screens. Browser hosts use Core's own prompt. Runs that nobody started, such as lifecycle runs and wake-ups, can also raise prompts ([#5749](https://github.com/freenet/freenet-core/issues/5749)).

## Diagnostics

Expose per-app connection state, subscription demand, last observation time, pending-operation counts, storage use, verified release, grants and typed failures. Exported reports redact keys, message bodies, session tokens, private references and private records by default. Harvest logged delegate replies with conversation keys and backup secrets ([harvest#94](https://github.com/freenet/harvest/issues/94)), and River logged the WebSocket URL's query string ([river#700](https://github.com/freenet/river/pull/700)).

## Acceptance

- Open River's real web UI on iOS and Android and exercise join, read, send, deep links, reload, termination and reconnect. A native fixture proves the declared SDK support level.
- Forged app identities, frames, bridge messages, loopback requests and expired sessions fail admission. App code stays within its supported network and storage policy.
- On iOS and Android, each shell-bridge message from River's frame follows the host's rule in [Shell-bridge messages](#shell-bridge-messages).
- Targeted delegate replies and autonomous private results reach only authorized sessions.
- Activation happens only at a session boundary, creates a fresh session generation, clears the app's WebView cache and rejects old-generation callbacks. Interrupted activation keeps the previous release active.
- Suspension invalidates the session, and reopening obtains fresh authority. After a node restart, River's page reloads and reconnects.
- On iOS and Android in Airplane Mode, River opens from its stored container and shows "Skate club".
- On iOS and Android, an invite link Bob opens during node start opens River at the invite.
- On iOS and Android, Core's shell keeps its local storage across a restart because the host loads `127.0.0.1` on the last loopback port.
- Trusted prompts, expanded permissions, immediate revocation, locked devices and web/native handoffs enforce base authorization. Queued work rechecks authority.
- On iOS and Android, the host asks for `notifications` once, when Bob first runs River, and stores his answer as a grant in Core's table. River's `notification_enable_prompt` from the notification modal's Enable button and from Bob's first message, and River's `notification` posts, get the stored answer with no new prompt. After a denial, River's alerts stay in-app. Running Atlas raises no prompt. Undeclared requests fail, and removing River deletes its grants.
- On iOS and Android, a `clipboard` message writes with no prompt and no grant. The host refuses a write without a user tap or within one second of the last write, and writes at most 2,048 characters.
- On iOS and Android, Core's `Background` consent for River's chat delegate takes its answer from the installation approval, and no delegate prompt opens a browser.
- Resource-exhaustion and malicious-input tests contain failure to the affected request or session.
- Each required browser or native admission path passes on the pinned Core build before that profile ships.

## One node per app

| Platform | Node placement | Cross-app requests |
| --- | --- | --- |
| iOS | Each app embeds its own node, as a full or thin peer. Apps from one developer team may share one node store in an App Group container, run by whichever app is in the foreground. That app closes the store and releases file locks before suspension. | A foreground app switch through universal links, carrying one request and one reply |
| Android | Each app embeds its own node. A node app may also offer a bound service that other apps call, protected by a permission. | An intent with a result, or calls to the bound service |
