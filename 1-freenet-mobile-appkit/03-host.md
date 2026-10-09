# 1.3 Single-application host

## Repositories

| Repository | Role | Work in this plan |
| --- | --- | --- |
| [freenet-core](https://github.com/freenet/freenet-core) | Modified | Caller admission, sessions and permissions |
| [freenet-appkit](https://github.com/glesage/freenet-appkit) | Modified | iOS and Android host bridge |
| [river](https://github.com/freenet/river) | Used | Hosted app fixture |
| [freenet-stdlib](https://github.com/freenet/freenet-stdlib) | Used | Delegate manifest and user input |

## Purpose

Run one application per mobile installation. River is the AppKit WebView test application on iOS and Android. EVY uses the same node SDK with its native SDUI readers on iOS and Android.

## Who controls what

### Application node and key scope

Each River or EVY installation owns its embedded node, node store, encryption key and host records. The application pins one published identity and its supported component code. EVY's Home, Hello and Marketplace features use that installation's node and one EVY delegate.

| Part | Responsibility |
| --- | --- |
| Host | Supply storage paths, own lifecycle and sessions, verify releases and enforce device permissions. |
| Trusted native screens | Show permission, identity, lock and recovery decisions. |
| Application | Own UI, data subscriptions and domain operations. |
| Core | Verify contract state, authenticate client connections and execute permitted delegates. |
| Delegate | Check the attested caller and operation context before reading secrets, signing or decrypting. |

[1.5 Identity, keys and local protection](05-identity.md#protected-keys-and-records) defines the application's private-data inventory and key protection. The EVY delegate derives internal feature and purchase signing keys from its root seed. Test unauthorized local clients and stale application sessions using [raven#64](https://github.com/freenet/raven/pull/64) and [ghostkeys#28](https://github.com/freenet/ghostkeys/pull/28) as regression references.

### Platform placement

| Platform | Application installation |
| --- | --- |
| iOS | River or EVY owns a node in its application sandbox, uses its own Keychain entries, and releases runtime/store locks at suspension. |
| Android | River or EVY owns a node in its application process and private files, uses its own Keystore entries, and releases runtime/store locks at suspension. |

River test builds and EVY test builds have separate application IDs and storage from their corresponding production installations. Each opens its own permitted application publication.

## Trusted calls

Bind protected calls to the owning application's verified publication, exact release, installation, user identity generation and current session. [1.4 Application bundles](04-bundles.md#release-references) defines the release reference for River's website and EVY's native UI publication.

The host checks the application's permitted component identities and declared device access before forwarding protected calls. A request retains its target and session through dispatch and result delivery. The [application connections in 1.2 Embedded node and mobile SDK](02-sdk.md#application-connections) define request matching and callback generations.

Authenticate the local node WebSocket, including clients that omit Origin ([#3011](https://github.com/freenet/freenet-core/pull/3011), [client API exposure](https://github.com/freenet/freenet-core/blob/e7d0b06c9326f377d250bf8344baaac2ba2658c6/docs/client-api-exposure.md)). Verify the selected application's connection binding under [Session admission #5264](https://github.com/freenet/freenet-core/issues/5264). Test caller-selected identities and equivalent API paths before releasing private data.

## Browser and native hosts

| Profile | Application execution | Required boundary |
| --- | --- | --- |
| River mobile | River's web code in a WebView, with files served by embedded Core | Trusted shell/bridge admission, isolated web storage and bounded node access |
| EVY native | SwiftUI on iOS and Compose on Android calling the SDK | Owning application, component policy and current session |
| River browser reference | River web code inside Core's sandboxed frame | Core authentication, storage and capability enforcement |

[1.1 Mobile feasibility and supported profiles](01-feasibility.md) confirmed that River's WebView and additional prototype measurements run in WKWebView and Android WebView, served by the embedded node from their pinned website containers ([device results](https://github.com/glesage/freenet-appkit/blob/1988c5cbdfc5c1f88065382de2a4f86093948b6e/docs/device-results.md#river-and-atlas-in-the-webview)).

Host requirements:

- Keep node credentials and privileged bridge methods in trusted code, and authenticate the owning application caller, including loopback and alternate API paths.
- Bind frames, WebView messages and native calls to the verified session, and validate message source, navigation and target before forwarding requests.
- Scope cookies, web storage, caches, file access and native handles within the application installation, and preserve the declared storage lifetime across reloads and restarts.
  - River runs in Core's shell page, inside a sandboxed frame with an opaque origin and no web storage of its own. Core's shell keeps its records in the loopback origin's local storage, such as its `freenet_notify:<key>` alert consent record ([#5165](https://github.com/freenet/freenet-core/issues/5165)).
  - The WebView keys web storage by origin, and the origin includes the host name and the node's loopback port. `localhost`, `127.0.0.1` and `[::1]` are three origins ([#4330](https://github.com/freenet/freenet-core/issues/4330)), so the host always loads `127.0.0.1`. The SDK selects and releases the loopback port under [1.2 Embedded node and mobile SDK](02-sdk.md#start-stop-and-reconnect). The trusted host and OS hold authoritative device-permission answers. Core holds delegate capability grants. The host keeps preferences and recovery metadata in its encrypted application records, and hydrates the shell from these stores for the selected origin. A fallback port starts a fresh shell session, recreates regenerable tokens and restores those records through the trusted bridge. Application code receives only its authorized records.
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
| `open_url` | Opens an http or https URL in a new tab | Validates the URL and opens it through the approved external-link adapter. Signed backend operations use the owning application's authenticated service client |
| `navigate` | Moves the frame within the same app, for a selected in-application destination | Keeps the pinned River application identity and validates the room destination |

River's web UI copies invite links with `document.execCommand('copy')` inside its own frame ([util.rs](https://github.com/freenet/river/blob/8cf54dd7799514851da7eab051e4cc43f797208d/ui/src/util.rs)), so those copies need no host involvement.

### Supporting backend access

EVY's native host calls payment and other supporting backends through their signed application protocols. It validates the operation, audience, challenge, policy and purchase context before dispatch. Ordinary external links carry navigation authority.

The local publisher tools handle archive, attribution and payout requests as [2.5 EVY authoring and publishing](../2-evy-on-freenet/05-developer.md#backend-requests) defines. Their credentials belong to the author's local workspace.

## Freenet issues being worked on that are required

Core maintainers agree the application/session binding, private-event routing and permission interfaces needed by the mobile host. These changes protect keys and private results from unauthorized local callers and keep consent attached to the right request. Record the accepted scope in the linked issues before feature PRs; release requires the checks below on the selected Core build. The AppKit host owns device consent, WebView enforcement and encrypted host records.

| Requirement | Github links | Release check |
| --- | --- | --- |
| Core-authenticated app admission | [Session admission #5264](https://github.com/freenet/freenet-core/issues/5264) | Bind verified app identity to the connection or trusted in-process caller. Reject caller-selected identities on every equivalent path |
| Private delegate response routing | A delegate's notification output goes to every client that has messaged that delegate ([#4682](https://github.com/freenet/freenet-core/pull/4682)). Core withholds it from non-local connections ([#5211](https://github.com/freenet/freenet-core/pull/5211)). A delegate hop is not a privacy boundary ([#5363](https://github.com/freenet/freenet-core/pull/5363)). All delegates share one lossy notification channel ([#5561](https://github.com/freenet/freenet-core/issues/5561)) | Targeted replies and autonomous private events reach only authorized sessions. The host filters them per session, because Core routes them by client connection |
| Declared, revocable permissions and per-app embedding | [Permissions #4014](https://github.com/freenet/freenet-core/issues/4014), [security discussion #5380](https://github.com/freenet/freenet-core/discussions/5380) | Enforce grants at each permission use, including page-initiated access |
| Fresh consent for expanded access | [Permissions #4014](https://github.com/freenet/freenet-core/issues/4014) is the open tracker. [#4090](https://github.com/freenet/freenet-core/pull/4090) lists the gaps an implementation must close. [#5730](https://github.com/freenet/freenet-core/pull/5730) is the working precedent for revocable grants | A changed manifest prompts before any new access, and grants remain revocable |
| Durable, isolated web storage | [Storage #5165](https://github.com/freenet/freenet-core/issues/5165) | Reload and termination preserve only authorized records |
| Delegate prompts | Core's `RequestUserInput` message in the [stdlib delegate interface](https://github.com/freenet/freenet-stdlib/blob/fca0848b78b12942f77422309bb07f76108940d6/rust/src/delegate_interface.rs). Open prompt bugs are [#5749](https://github.com/freenet/freenet-core/issues/5749), [#5537](https://github.com/freenet/freenet-core/issues/5537) and [#4966](https://github.com/freenet/freenet-core/issues/4966). Core drops a prompt from a delegate that another delegate called ([#5364](https://github.com/freenet/freenet-core/issues/5364)). Core holds a delegate that waits on a prompt off its contract loop, and [#5606](https://github.com/freenet/freenet-core/pull/5606) adds a byte cap and a time limit for those waiting requests. Local mode drops prompts ([#5273](https://github.com/freenet/freenet-core/issues/5273)) | Trusted prompts identify the requester and return only to the authorized request. Each answer binds to its own prompt ([ghostkeys#24](https://github.com/freenet/ghostkeys/issues/24)). Prompt tests run the node in network mode |

## Activating a release

The host verifies the release reference and build policy before activation.

| Change | Boundary | Retained work |
| --- | --- | --- |
| River website or executable/component change | Quiesce work, complete required migration/readback, then atomically select the release and create a fresh host session generation. Clear River’s WebView cache. | Encrypted drafts, exact pending operations and the application demand registry survive. Rebind them to the new session after compatibility checks. |
| Compatible EVY UI document | At idle Home, activate the winning drawable document generation within the current host session. | Application subscriptions keep running. Active flows and pending operations keep their exact signed document and bindings. |
| EVY reader/code/permission-policy change | Matching iOS and Android build admission, required migration and a fresh host session. | Preserve durable operations and restore application demand once under the new generation. |

An idle UI boundary changes the drawable document generation. Host session replacement changes caller authority and fences callbacks from the earlier generation. Both carry a separate identifier. Commit activation atomically; interruption selects the complete previous or successor release/generation. Follow [2.3 Native SDUI readers](../2-evy-on-freenet/03-readers.md#reading-the-application-ui-contract) for flow retention and [1.7 Upgrades and migration](07-migration.md#mobile-migration-interface) for code upgrades.

Use verified files despite Core cache headers ([#5323](https://github.com/freenet/freenet-core/issues/5323)). The River re-key fixture writes to the selected successor room ([river#580](https://github.com/freenet/river/issues/580)).

## Opening, suspending and reopening an app

[1.2 Embedded node and mobile SDK](02-sdk.md#start-stop-and-reconnect) owns node start and stop, including an offline start. The host owns the app's session.

When Alice opens River on the subway with no signal:

1. The host loads River's website container from the node's store, without waiting for a peer.
2. River shows "Skate club" from her phone's copy. Her sends wait until the node first joins, as [1.2 Embedded node and mobile SDK](02-sdk.md#start-stop-and-reconnect) describes.
3. Once the node has a peer, the host fetches any update to River's container. A new release activates at the next session boundary.

Online, loading the stored container first saves about 0.5 s on the public network ([cached-app source evidence](https://github.com/glesage/freenet-appkit/blob/1988c5cbdfc5c1f88065382de2a4f86093948b6e/docs/findings.md#smaller-items)).

Keep an invite link's URL while Core joins and serves its connecting page. Once the container is available, open Bob's invite at its intended target. Test [#5745](https://github.com/freenet/freenet-core/issues/5745) with the fix in [#5750](https://github.com/freenet/freenet-core/pull/5750).

When the user leaves the app or locks the device, the host fences new signing and private-data operations, flushes queued recovery writes within the lifecycle budget, ends the session, destroys River's WebView and disposes of EVY's private native view state. It releases application-owned decrypted records, signing-key copies, bridge buffers and native key caches. Core applies the [lock sequence in 1.5 Identity, keys and local protection](05-identity.md#locking-and-unlocking). The host records the lifetime and cleanup mechanism of each plaintext copy; zeroization claims apply to buffers whose ownership and wiping it controls. On reopening after unlock, it creates a fresh River WebView or EVY native context and session, then loads protected state again.

End River's authority through the host session generation. Core's page token can survive a disconnect and remain valid until it goes unused for 24 hours ([#1976](https://github.com/freenet/freenet-core/pull/1976)). After a node restart, Core closes the WebSocket with code 4401 and the shell reloads River's frame ([#4781](https://github.com/freenet/freenet-core/pull/4781)). River also reloads its own frame on `AUTH_TOKEN_INVALID`, which races the shell's reload ([river#522](https://github.com/freenet/river/issues/522)).

## Base authorization and device access

The application's component declaration identifies required and optional device permissions. Trusted host code stores the user's choices in installation records and combines them with current OS permission status. Core's delegate capability grants, including `Background`, keep their Core-defined meaning ([#5730](https://github.com/freenet/freenet-core/pull/5730), [#5744](https://github.com/freenet/freenet-core/pull/5744)).

River's `notifications` choice is an application setting enforced by its native adapter. The adapter answers shell requests from that choice and OS status. A delegate consent prompt runs through the embedder's `UserInputPrompter`, as [Background runs and delegate prompts](#background-runs-and-delegate-prompts) specifies.

Forget clears the installation's permission records and regenerable tokens. Build-pinned public publisher keys and execution policy remain part of the installed build. User publisher approvals, key choices and identity-specific trust records belong to the encrypted inventory and are deleted by Forget under [1.5 Identity, keys and local protection](05-identity.md#application-data-inventory).

### Asking for a permission

The matching iOS and Android build profile admits declared device adapters. Trusted native UI handles the concrete triggers below; the application/session owns each result.

| Operation | Trigger and stored result |
| --- | --- |
| River notifications | First run asks once and stores the answer. Later shell enable requests receive that answer plus current OS status. A denial keeps alerts in-app until the user changes the host/system setting. |
| File save/import or backup folder | The user selects the operation in recovery UI and chooses a file/folder through the system picker. The coordinator receives an operation-scoped handle; persistent backup folder grants bind to identity generation. |
| Marketplace photo selection | The user taps Select photo and chooses through the iOS or Android system picker. The reader validates the selected bytes and current operation before publication. |
| Clipboard and external link | A user tap invokes the declared bounded copy or validated navigation adapter. The host checks authority at dispatch. |
| Additional device access | The owning plan names the shipping flow, consent trigger and revocation rule before the build profile admits it. |

River’s `app_definition.json` declares optional `notifications`. On first run the host saves the answer, then requests the matching OS permission if needed. The notification modal’s Enable button and first send receive that saved answer. Native alerts require both consent and OS permission; Bob can change either in the host/system settings. River’s [notification modal source](https://github.com/freenet/river/blob/8cf54dd7799514851da7eab051e4cc43f797208d/ui/src/components/room_list/notification_modal.rs) supplies the fixture.

An unanswered trusted consent prompt expires after 60 seconds and saves no answer. First-run notification consent is offered on the next run. Recheck current session/generation after any native picker or prompt; stale callbacks expire. Delegate capability prompts follow [Background runs and delegate prompts](#background-runs-and-delegate-prompts).

### Using a grant

- Recheck grants before each protected operation and before queued work runs. Revocation stops further use at once.
- Prompt before an update adds a permission. Changed delegates and setup require installation approval.
- Require explicit authorization when sharing identity or private records between WebViews and native contexts.
- Return typed results: granted, denied, unavailable, locked device or expired handle. Bind selected files or photos to the requesting operation and session.

The selected shipping adapters are listed below. Each operation checks caller/session authority, signed context where used and current device consent. River's [notification integration](https://github.com/freenet/river/blob/8cf54dd7799514851da7eab051e4cc43f797208d/ui/src/components/app/notifications.rs) is an application fixture. Notification taps validate the target and refresh application state before showing it. Alerts arrive only while the host is in the foreground, as [1.1 Mobile feasibility and supported profiles](01-feasibility.md#message-alerts) confirmed on iOS and Android.

### Shipping device adapters

Store-build executable admission and user device consent are separate gates. The build policy admits exact component hashes. The host/reader checks consent for each declared device operation.

| Adapter | Shipping flow and trigger | Owner and enforcement |
| --- | --- | --- |
| Notifications | River first run and foreground room messages | Host; stored application choice plus OS status |
| Clipboard | River invite copy; EVY copy action after a user tap | Host/reader; tap, size and rate checks |
| Files | River download; manual backup save/import and EVY provider folder selection | Host recovery coordinator; operation/session-scoped handle |
| Photos | Marketplace Select photo | Native readers; system picker and operation-scoped selected bytes |
| External link | River open URL; EVY Stripe onboarding and support | Host/reader; validated HTTPS target and navigation authority |
| Maps | Marketplace pickup map | Native readers; signed public map point and supported map SDK |
| Internal route | River room invite; EVY Home and Marketplace navigation | Host/reader; identity, target and argument validation |

Expansion requires a named River or EVY flow, paired iOS and Android fixtures, exact build policy and declared consent trigger. Core #4014 is evidence for the broader permissions framework. Core #5254, checked 2026-10-09, concerns per-contract media origins; its adoption starts when a shipping River media-capture flow requires it.

### Background runs and delegate prompts

Core maintainers approve the public embedder-supplied `UserInputPrompter` interface before its feature PR. River and EVY need it to show delegate prompts and startup consent in trusted native UI on iOS and Android, with each answer bound to the requesting session.

A delegate that needs startup runs or wake-ups declares them, with `Background`, in its Wasm manifest ([stdlib #136](https://github.com/freenet/freenet-stdlib/pull/136)). River's chat delegate declares no manifest. It rotates private-room secrets when a room update arrives ([subscription.rs](https://github.com/freenet/river/blob/8cf54dd7799514851da7eab051e4cc43f797208d/delegates/chat-delegate/src/subscription.rs)), and its room subscriptions survive a node restart ([#5728](https://github.com/freenet/freenet-core/pull/5728)).

When an app registers a delegate whose manifest lists startup runs or wake-ups, Core raises the `Background` consent itself, through the prompter's `prompt_capability` call. The mobile host answers that call from the installation approval, so the user sees no second prompt.

Manifests can also declare wake-ups ([#5747](https://github.com/freenet/freenet-core/pull/5747)). Core fires a wake-up only while the app holds the `Background` grant. On iOS and Android, wake-ups and other background work run only while the SDK lifecycle keeps the node running.

File a Core issue to expose `UserInputPrompter` through Core's `user_input` module as a public interface the embedder supplies when creating the node. On iOS and Android, configure `p2p_impl.rs` with that prompter. Route delegate prompts and `Background` consent (`prompt_capability`) through it to trusted native screens. Browser hosts use Core's own prompt.

Use [p2p_impl.rs](https://github.com/freenet/freenet-core/blob/e7d0b06c9326f377d250bf8344baaac2ba2658c6/crates/core/src/node/p2p_impl.rs), [user_input.rs](https://github.com/freenet/freenet-core/blob/e7d0b06c9326f377d250bf8344baaac2ba2658c6/crates/core/src/contract/user_input.rs) and [#5749](https://github.com/freenet/freenet-core/issues/5749) as implementation references.

Contract notifications, lifecycle runs and wake-ups can also raise prompts ([#5749](https://github.com/freenet/freenet-core/issues/5749)). Show those prompts at once in the same trusted native screen. Identify the app that Core binds to the delegate because these runs have no caller. On iOS and Android, the node runs in the foreground, so the app is open when the prompt appears.

## Call and event bounds

Initial mobile interface fixtures use these explicit limits. A release profile may lower them. Raising them requires matching iOS and Android resource measurements and a versioned interface/build policy.

| Bound | Initial limit | Enforcement |
| --- | --- | --- |
| Authorized targets | Exact registered identities and parameter rules; at most 64 targets in one delegated operation | Core caller admission and both transport adapters |
| Queued requests | 128 per application connection; one submitted request awaiting reply until complete request-ID support passes | WebSocket session adapter and native SDK |
| Delegate request/query | 256 KiB canonical bytes; at most 32 query clauses and 256 returned rows per query | Core before delegate execution; session adapter/SDK before dispatch |
| Delegate reply/private event | 1 MiB each; recovery uses bounded chunks under the snapshot barrier | Core at output boundary; adapter/SDK before delivery |
| Autonomous events | 32 per second, burst 64; 64 queued events; overflow returns a typed resynchronization requirement | Core event router and adapters; data layer refreshes verified projections |
| Shell bridge message | 64 KiB serialized bytes; clipboard keeps its 2,048-character limit | Native WebView bridge before parsing/dispatch |
| Contract state | Core’s 50 MiB ceiling plus each application contract’s smaller cap | Core state validator and profile-specific reader/transport checks |

Recovery exports use the authenticated inventory, 10,000-secret/256 MiB ceiling and bounded capture deadline in [1.10 Backup and restore](10-backup-and-restore.md#export). Normal page actions use ordinary query limits. On iOS and Android, exercise exact-limit and one-over-limit payloads, target substitution, query floods, output overflow and stale events through River’s direct WebSocket route and the native SDK. Record which Core checks require upstream implementation before release.

## Diagnostics

Expose per-app connection state, subscription demand, last observation time, pending-operation counts, storage use, verified release, grants and typed failures. Exported reports redact keys, message bodies, session tokens, private references and private records by default. Test redaction of delegate replies, conversation keys, backup secrets and WebSocket query strings using [harvest#94](https://github.com/freenet/harvest/issues/94) and [river#700](https://github.com/freenet/river/pull/700).

## Acceptance

- On iOS and Android, River runs its pinned website publication in one WebView, using that installation's node and private store.
- On iOS and Android, EVY's native host starts one node and one EVY delegate for all its features. Home, Hello and Marketplace routes retain the same application identity and session.
- Authenticated connections and protected bridge methods reject substituted identities, forbidden components, invalid targets and expired sessions. Test loopback clients and equivalent local paths.
- Reload, lock, suspension, reconnect and restore reject earlier callbacks and preserve acknowledged drafts and pending operations. Lock disposes of River's WebView and EVY's private native buffers before fresh contexts open on unlock.
- On iOS and Android, test restart on the previous port and with that port occupied. The chosen loopback origin gets a fresh authorized session and restores the application's consent/preferences from trusted installation records.
- On iOS and Android, asking for notifications saves River's answer and combines it with OS permission status. A later shell request gets that answer. Revocation stops native delivery; the app keeps in-application alerts.
- Delegate prompts identify the owning application and request. Lock, cancellation and expiration close the prompt and prevent stale delivery.
- Diagnostics redact keys, tokens, decrypted messages and private references according to [Diagnostics](#diagnostics).
