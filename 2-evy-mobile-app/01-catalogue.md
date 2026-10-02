# 2.1 EVY shell and curated catalogue

## Repositories

| Repository | Role | Work in this plan |
| --- | --- | --- |
| [evy](https://github.com/EVY-Platform/evy) | Modified | iOS and Android shell and app catalogue |
| [atlas](https://github.com/freenet/atlas) | Modified | Atlas bundle and support page |
| [river](https://github.com/freenet/river) | Modified | River share links |
| [freenet-appkit](https://github.com/glesage/freenet-appkit) | Used | Mobile SDK and host packages |
| [freenet-core](https://github.com/freenet/freenet-core) | Used | Embedded node and share links |
| [web](https://github.com/freenet/web) | Used | EVY open page and share-link docs |

## Purpose

This plan builds EVY, one iOS app and one Android app that list River and Atlas and open each in its own in-app WebView. Both apps run on one embedded node in the thin-peer role. In milestone 2 (EVY mobile app), "app" means River or Atlas, and "EVY" means the phone app. EVY starts from River's store build in [1.9 Testing and release](../1-freenet-mobile-appkit/09-testing-and-release.md). It installs each app under [1.4 Application bundles](../1-freenet-mobile-appkit/04-bundles.md#installing-a-copy) and opens it through [1.3 Single-application host](../1-freenet-mobile-appkit/03-host.md).

Alice opens EVY on her phone and taps River. EVY installs River's release bundle, and River shows her private room "Skate club". She copies an invite link, Bob taps it on his phone, and EVY opens River's join screen. Atlas sits next to River on home and opens the apps it finds in its index.

## The catalogue

EVY's release configuration is one `catalogue.json` that the iOS and Android builds both bundle. Each entry pins an app by its website container key.

```jsonc
{
  "store_age_rating": 16,                                                      // EVY's rating in the App Store and Google Play
  "apps": [
    {
      "name": "River",                                                         // shown on home and in the store index
      "publisher": "<River publisher>",                                        // shown in the store index
      "website_container_key": "raAqMhMG7KUpXBU2SxgCQ3Vh4PYjttxdSWd9ftV7RLv",  // from River's publish rules
      "age_rating": 16,                                                        // from the app's rating questionnaire
      "support_url": "<River support page>"                                    // from the app's store requirements
    },
    {
      "name": "Atlas",
      "publisher": "<Atlas curator>",
      "website_container_key": "771DvtPMwt2PumPyrFvsz7fpvU1gogcmb5qtS1yYEEH9", // from Atlas's README
      "age_rating": 16,
      "support_url": "<Atlas support page>"
    }
  ]
}
```

The keys come from [River's publish rules](https://github.com/freenet/river/blob/main/.claude/rules/river-publish.md) and [Atlas's README](https://github.com/freenet/atlas/blob/main/README.md). Each app keeps its key across releases, because the packaging CLI passes the app's pinned container Wasm on every publication ([the archive and its definition in 1.4 Application bundles](../1-freenet-mobile-appkit/04-bundles.md#the-archive-and-its-definition)). Atlas's index contract takes a new key when its code changes, and its website container key stays the same. The iOS and Android builds fail when an entry lacks a key or an age rating.

Home shows one tile per entry with its name and installed version. The first tap installs the app, after the first-download size prompt from [store requirements in 1.9 Testing and release](../1-freenet-mobile-appkit/09-testing-and-release.md#store-requirements).

## Atlas in EVY

| Work | What Atlas does |
| --- | --- |
| Definition | The release build gains `app_definition.json` with one component, the index contract with `IndexParams` (root key and slug `default`) and `setup: none`. It declares no permissions. |
| Publication | The release build publishes through the packaging CLI from [1.4 Application bundles](../1-freenet-mobile-appkit/04-bundles.md#publishing-and-evidence). The CLI passes Atlas's own [`web_container_contract.wasm`](https://github.com/freenet/atlas/tree/main/contracts/web-container) with `--contract-wasm`, so the container key stays `771D...`. fdev stamps the Unix time as the version, so Atlas's first release through the CLI jumps once above its hand-typed version of about 10. Later releases need no hand-typed version ([atlas#53](https://github.com/freenet/atlas/issues/53)). Before the first release, check that fdev signs with Atlas's root key. |
| Filter | Safe search stays on by default and hides entries whose landing page is rated other than general audience ([main.rs](https://github.com/freenet/atlas/blob/main/ui/src/main.rs)). Entries with no rating still show. The rating reads only page text, so an image-only site can pass ([atlas#11](https://github.com/freenet/atlas/issues/11)). The toggle lives in `localStorage`, which the sandboxed frame denies, so it returns to on at each load. |
| Report | Each entry card gains a Report button. Reports go to an inbox the curator monitors. Today users report entries in Atlas's River room ([atlas#52](https://github.com/freenet/atlas/issues/52)). The curator removes a reported entry with [`atlasctl remove`](https://github.com/freenet/atlas/blob/main/cli/src/main.rs), which tombstones it for every reader. |
| Support URL | Atlas publishes a support page with contact details. Its catalogue entry holds the link. |

## Opening links and alerts

EVY opens Freenet share links ([share links manual](https://freenet.org/build/manual/share-links/), [#5726](https://github.com/freenet/freenet-core/issues/5726)). A share link keeps its target in the URL fragment, and browsers never send the fragment to a server. EVY accepts three forms of the same target on iOS and Android.

| Form | River example | How it reaches EVY |
| --- | --- | --- |
| EVY link | `https://<EVY link domain>/open#raAq.../?invitation=<code>` | Universal link on iOS and App Link on Android, from the `apple-app-site-association` and `assetlinks.json` files on EVY's link domain |
| `freenet:` link | `freenet:raAq.../?invitation=<code>` | EVY registers the `freenet:` scheme on iOS and Android. It also accepts `freenet://`, as Core's handler does ([#5753](https://github.com/freenet/freenet-core/pull/5753), [#5756](https://github.com/freenet/freenet-core/pull/5756)) |
| freenet.org link | `https://freenet.org/open#raAq.../?invitation=<code>` | The freenet.org/open page's "Open in Freenet" button emits the `freenet:` form ([web#184](https://github.com/freenet/web/pull/184), [web#186](https://github.com/freenet/web/pull/186)) |

EVY checks each link with the rules of Core's `freenet:` handler ([#5753](https://github.com/freenet/freenet-core/pull/5753)). The contract ID must decode from base58 to 32 bytes, and the path must hold no dot segments. EVY's tests run Core's [`share-link-vectors.json`](https://github.com/freenet/freenet-core/blob/main/crates/core/tests/data/share-link-vectors.json). EVY then turns the target into the path `/v1/contract/web/<website container key>/<path>?<query>` and passes the path and query to the app unchanged.

On a phone without EVY, the browser loads the `/open` page on EVY's link domain. The browser keeps the fragment, so EVY's server never receives the invite code. The page shows App Store and Google Play buttons to install EVY. Once EVY is installed, Bob taps the invite link again and EVY opens it.

River builds invite links from the page's own URL ([invite_member_modal.rs](https://github.com/freenet/river/blob/main/ui/src/components/members/invite_member_modal.rs)). Inside EVY that URL is the node's loopback address. So the host bridge gives River its link base `https://<EVY link domain>/open#raAq.../`, which is EVY's link domain followed by River's container key, and Alice's invite reads `https://<EVY link domain>/open#raAq.../?invitation=<code>`. River reads `invitation` from its URL ([app.rs](https://github.com/freenet/river/blob/main/ui/src/components/app.rs)), and its [portable invite code](https://github.com/freenet/river/blob/main/ui/src/components/room_list/join_with_code_modal.rs) works as it does today. Each invite holds one invitee's signing key and works for one person ([river#566](https://github.com/freenet/river/issues/566)). Draft [river#567](https://github.com/freenet/river/pull/567) makes an invite sent by direct message River's main action and keeps the link for people not yet on River.

```mermaid
flowchart LR
  T[Bob taps the invite] --> V{Link passes the share-link checks?}
  V -- no --> B[EVY shows the broken-link message]
  V -- yes --> C{Website container key in catalogue.json?}
  C -- no --> E[EVY shows the not-in-EVY message]
  C -- yes --> I{River installed?}
  I -- no --> N[Install River] --> O
  I -- yes --> O[Open River at the same path and query]
  O --> J[River shows its join screen]
```

A tap while EVY's node joins follows [Opening, suspending and reopening an app in 1.3 Single-application host](../1-freenet-mobile-appkit/03-host.md#opening-suspending-and-reopening-an-app), which keeps the link target ([#5745](https://github.com/freenet/freenet-core/issues/5745), [#5750](https://github.com/freenet/freenet-core/pull/5750)).

- Atlas's Open turns an entry's [`Locator`](https://github.com/freenet/atlas/blob/main/common/src/types.rs) into a link ([state.rs](https://github.com/freenet/atlas/blob/main/common/src/state.rs)). A `Freenet` or `AppResource` locator becomes a `/v1/contract/web/<website container key>/` path. For a catalogue key, EVY switches to that app. For any other key, EVY shows the not-in-EVY message and keeps Atlas on screen.
- An `External` locator is an https URL. Atlas indexes only Freenet sites ([atlas#34](https://github.com/freenet/atlas/pull/34)), and [atlas#35](https://github.com/freenet/atlas/issues/35) purges its 36 external entries, so new External entries come only from the curator.
- EVY opens an https URL in the system browser on iOS and Android. The URL arrives as the shell's `open_url` message, which River uses ([river#203](https://github.com/freenet/river/issues/203)), or as a `target="_blank"` link, which Atlas's Open uses. The WebView host validates both as [Shell-bridge messages in 1.3 Single-application host](../1-freenet-mobile-appkit/03-host.md#shell-bridge-messages) describes.
- River tags each alert with its room ([notifications.rs](https://github.com/freenet/river/blob/main/ui/src/components/app/notifications.rs)). EVY records which app sent the alert. A tap opens that app and returns the tag, so a River alert tapped while Atlas is on screen opens "Skate club". In a browser, a tap after the tab closes loses the tag ([#4939](https://github.com/freenet/freenet-core/issues/4939)), and EVY's native alert keeps it. The target check and refresh follow [1.3 Single-application host](../1-freenet-mobile-appkit/03-host.md#base-authorization-and-device-access).

## Settings

EVY's settings say that alerts arrive only while EVY is open ([message alerts in 1.1 Mobile feasibility and supported profiles](../1-freenet-mobile-appkit/01-feasibility.md#message-alerts)). Each app has its own page.

| Row | What it does | River example |
| --- | --- | --- |
| Permissions | Lists the app's grants through Core's grant API from [1.3 Single-application host](../1-freenet-mobile-appkit/03-host.md#asking-for-a-permission). EVY asks for `notifications` the first time the user opens an app that declares it. The user changes or revokes an answer here and in the matching iOS or Android system setting. | EVY asked the first time Bob opened River, and the page shows `notifications` granted. Atlas's page says Atlas uses no permissions, and opening Atlas raises no prompt. |
| Storage | Shows the bytes the app uses on the phone, from [diagnostics in 1.3 Single-application host](../1-freenet-mobile-appkit/03-host.md#diagnostics). | River's room copies, delegate records and web storage |
| Remove | Deletes the installed copy and the app's grants. Keys and records stay. | Alice installs River again and "Skate club" is back. |
| Forget | Deletes the app's keys and records after a confirmation, and reports what it could not delete. [Forgetting one app in 2.2 Two apps on one node](02-shared-node.md#forgetting-one-app) keeps the other app's records readable. | Forgetting River leaves Atlas as it was. |
| Diagnostics | Exports one report for this app through the iOS or Android share sheet. It holds the app's own connection state, subscriptions, grants, storage and failures, plus the node's role and data budget. Redaction follows [diagnostics in 1.3 Single-application host](../1-freenet-mobile-appkit/03-host.md#diagnostics). | Nothing from Atlas. River's invite codes are redacted as keys, because each carries the invitee's signing key and the room secrets ([members.rs](https://github.com/freenet/river/blob/main/ui/src/components/members.rs)). |

## Store index and age check

The store index answers [App Store Review Guideline 4.7](https://developer.apple.com/app-store/review/guidelines/) (mini apps). EVY builds it from `catalogue.json` and shows it in settings on iOS and Android.

- Each row lists the app's name, publisher, age rating, website container key, support URL and EVY link.
- River and Atlas are rated at or below `store_age_rating` and open with no age question. An entry rated above it shows an age mark on home.
- EVY asks for the user's birth year the first time the user opens that entry. EVY keeps the answer in its settings and opens the app only when the age meets the entry's rating.

## Acceptance

- On iOS and Android, a clean EVY install lists River and Atlas from `catalogue.json`. The first tap installs the app and opens it, and River shows "Skate club". A build with an entry that lacks a key or rating fails.
- Atlas's release bundle publishes through the packaging CLI to container `771D...` at a Unix-time version and opens in EVY on iOS and Android. Safe search is on by default, and Report reaches the curator's inbox. Atlas's Open on a catalogue app switches to that app, and Open on any other key keeps Atlas on screen.
- On iOS and Android, an External fixture entry, added with `atlasctl add` to the test index from [1.9 Testing and release](../1-freenet-mobile-appkit/09-testing-and-release.md#atlas-today-and-pinned-identity), opens in the system browser. A River `open_url` link opens there too.
- On iOS and Android, Bob taps Alice's invite with River not installed, once in each of the three link forms. EVY installs River, passes the invitation unchanged, and River shows its join screen for "Skate club". The same holds when Bob taps during node start. A browser without EVY loads the `/open` page with the App Store and Google Play buttons, and EVY's server log holds no invite code.
- EVY's link checks pass every vector in Core's `share-link-vectors.json`. A link that fails them shows the broken-link message. A link for a key outside the catalogue shows the not-in-EVY message. A River alert tapped while Atlas is on screen opens "Skate club".
- On iOS and Android, opening River in EVY for the first time asks for `notifications` once, and opening Atlas asks nothing. Revoking River's `notifications` grant on River's settings page stops River's alerts. Remove keeps River's keys and records, and Forget asks first and reports what it could not delete. River's diagnostics export holds no Atlas data and no invite codes, keys or message bodies.
- On iOS and Android, each store index link opens its app. A test entry rated above EVY's store rating opens only after the age question.
- Home, settings and the store index pass VoiceOver and Dynamic Type on iOS, and TalkBack and font scaling on Android.
