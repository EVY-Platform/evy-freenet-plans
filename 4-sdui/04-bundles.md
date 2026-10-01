# 4.4 SDUI bundles and publication

## Repositories

| Repository | Role | Work in this plan |
| --- | --- | --- |
| `freenet-appkit` | Modified | The packaging CLI copies `ui/sdui/` and the web reader into the bundle, writes the `sdui` field and the `predecessors` lists, writes a reader-only `index.html` and runs the SDUI checks. The iOS and Android WebView hosts run an app's web UI in a hidden WebView to move delegate secrets |
| [freenet-core](https://github.com/freenet/freenet-core) | Modified | `crates/mobile` carries contracts forward from the `predecessors` lists for native readers. `fdev website publish` stays unchanged and runs with each app's pinned container Wasm, as in 1.4 Application bundles |
| `freenet-sdui` | Used | The validator, the component and step catalogue, and the web reader build |
| [freenet-migrate](https://github.com/freenet/freenet-migrate) | Used | `migrate_contract` for contract carry-forward |
| [river](https://github.com/freenet/river) | Used | Example bundle and its two predecessor registries |

## Purpose

This plan puts the files from [4.1 SDUI format](01-format.md), [4.2 SDUI readers](02-readers.md) and [4.3 SDUI actions and data](03-actions-and-data.md) into the release bundle from [1.4 Application bundles](../1-freenet-mobile-appkit/04-bundles.md). It adds the `sdui` field and the `predecessors` lists to `app_definition.json`, and the SDUI checks to the packaging CLI. River's next version carries the "Invite member" sheet. EVY's native readers run no River code, so this plan also sets how EVY carries Alice's "Skate club" room and keys to that version.

## SDUI files in the bundle

The packaging CLI copies the app repository's `ui/sdui/` folder into the release folder and adds the web reader under `ui/sdui/web/`. Hosts detect SDUI from the file `ui/sdui/ui.json`.

```text
index.html              # River's Dioxus web app (1.4 Application bundles)
contracts/              # as in 1.4 Application bundles
app_definition.json     # as in 1.4 Application bundles, plus the sdui field and predecessors lists
ui/sdui/ui.json         # routes, views and forms, such as "Invite member" (4.1 SDUI format)
ui/sdui/actions/        # actions, such as new-invitation (4.3 SDUI actions and data)
ui/sdui/schemas/        # chat delegate messages, such as CreateInvitation (4.3 SDUI actions and data)
ui/sdui/web/reader.js   # web reader, copied in by the packaging CLI (4.2 SDUI readers)
```

Every bundle keeps a web app at `index.html`, as 1.4 Application bundles requires. River keeps its own and can embed `<freenet-web src="ui/sdui/ui.json">` where an SDUI screen goes. For an app with no web code of its own, the packaging CLI writes an `index.html` that loads `ui/sdui/web/reader.js` and holds one `<freenet-web src="ui/sdui/ui.json">` element.

The packaging CLI writes the `sdui` field into `app_definition.json` from the files under `ui/sdui/`. EVY reads it to [pick the native reader or the WebView](02-readers.md#native-readers-in-evy) before it parses any screen.

```jsonc
"sdui": {                                                        // written by the packaging CLI from ui/sdui/
  "format_version": "1.0",                                       // format_version of ui/sdui/ui.json (4.1 SDUI format)
  "components": ["button", "heading", "input", "list_item",      // component types River's screens use
                 "text", "text_area", "horizontal_container", "vertical_container"],
  "steps": ["call_delegate", "device", "permission", "random",   // step types River's actions use (4.3 SDUI actions and data)
            "submit", "time"]
}
```

## Packaging checks

The packaging CLI runs these checks in step 1 (Validate) of [publishing in 1.4 Application bundles](../1-freenet-mobile-appkit/04-bundles.md#publishing-and-evidence). A failed check stops the release before `fdev website publish` runs.

| Check | Fails when, with a River example |
| --- | --- |
| Schema and limits | A file under `ui/sdui/` fails the validator from the pinned `freenet-sdui` version, which checks the schema and the limits in 4.1 SDUI format |
| References | A route or button names a route or action missing from `ui/sdui/`, such as an "Invite member" route whose `new-invitation` action is not in `actions/` |
| Delegate schemas | The input or reply of `new-invitation`'s delegate call differs from the `CreateInvitation` schema, or the call names a delegate alias missing from `components` |
| Permissions | A screen or action names a permission that `app_definition.json` does not declare. River declares `notifications` |
| Types and versions | A file uses a format version, component type or step type that the pinned catalogue or the reader in `ui/sdui/web/` lacks |
| Predecessors | A `predecessors` list differs from the app's registry file |

## Publication

SDUI files are ordinary files in the archive. The packaging CLI publishes them with the rest of the bundle through the unchanged `fdev website publish`, with `--contract-wasm` and River's pinned container Wasm, so River's container key stays the same. Its saved copy and its readback through a node other than the publishing node cover every file under `ui/sdui/`, as [Publishing and evidence in 1.4 Application bundles](../1-freenet-mobile-appkit/04-bundles.md#publishing-and-evidence) sets. [3.2 Release certification](../3-attribution-remuneration-payment/02-certification.md) certifies the readback bytes, so it certifies the SDUI files with the rest of River's version.

Each component entry in `app_definition.json` gains a `predecessors` list. The packaging CLI copies it from the app's [predecessor registry](../1-freenet-mobile-appkit/07-migration.md#predecessor-registry), oldest first. Delegate entries also copy `delegate_key` and `irregular_key`.

```jsonc
"alias": "river.room",                                                                                  // room contract entry, other fields as in 1.4 Application bundles
"predecessors": [                                                                                       // copied from common/legacy_room_contracts.toml
  { "version": "V1", "code_hash": "415d03916cccddca057d343ce0f5c8dc89606221d0b260f3dfc7344f64dd5b38" }, // oldest, V2 to V31 follow
  { "version": "V32", "code_hash": "e765339ba3039f937256f4b6f7e8683d43f90e158f5d80f0dd45afdca69911e5" } // newest earlier version, probed first
]
```

## Migration in native readers

River's web app runs its own migrations when a new version first starts, as [1.7 Upgrades and migration](../1-freenet-mobile-appkit/07-migration.md#purpose) sets. When Alice opens River's new version in EVY's native reader, EVY takes these steps instead.

| Step | Who | What happens |
| --- | --- | --- |
| 1. Find old contracts | `crates/mobile` | Looks up River's stored contracts in Core's [contract index](https://github.com/freenet/freenet-core/blob/main/crates/core/src/contract/storages/redb.rs), which maps each instance to its code hash. An instance whose code hash is in a `predecessors` list is an old one. Core keeps its parameter bytes beside its state ([state_store.rs](https://github.com/freenet/freenet-core/blob/main/crates/core/src/wasm_runtime/state_store.rs)), such as `ChatRoomParametersV1 { owner }` with Alice's verifying key |
| 2. Carry forward | `crates/mobile` | Runs freenet-migrate's [`migrate_contract`](https://github.com/freenet/freenet-migrate/blob/main/README.md) with its default `NewestFirstWins` policy and PUTs the state it finds under the new key. The new contract validates that state |
| 3. Move delegate secrets | WebView host | Runs only when a delegate's key changed. Opens River's `index.html` in a hidden WebView, with River's own session, data store and secret scope from [2.2 Two apps on one node](../2-evy-mobile-app/02-shared-node.md). River's web UI runs [`migrate_delegate_secrets`](https://github.com/freenet/river/blob/main/ui/src/components/app/freenet_api/delegate_migration.rs) and stores its `signing_key:` entries again from `room:<owner key>`, as it does in a browser. The host closes the WebView when the page has loaded and no delegate call is open |
| 4. Retry | `crates/mobile` | Runs a failed or interrupted step again on the next start. The old data stays in place, so a failure loses nothing |

Step 2 needs a new contract that accepts its predecessor's state bytes. River's room contract does, because fields added to its state since V1 carry `#[serde(default)]` ([room_state.rs](https://github.com/freenet/river/blob/main/common/src/room_state.rs)). The host uses step 3 because Core's own copy-forward of delegate secrets stays disabled, as [Delegate secret export and import in 1.7 Upgrades and migration](../1-freenet-mobile-appkit/07-migration.md#delegate-secret-export-and-import) notes. [Core RFC #5255](https://github.com/freenet/freenet-core/issues/5255) proposes a Core-side move and is blocked on a core-mediated deposit path.

## Acceptance

- River's bundle with `ui/sdui/` publishes through the packaging CLI and the unchanged `fdev website publish` with River's pinned container Wasm, and River's container key stays the same. Readback through an independent node matches every file under `ui/sdui/`, and River's `index.html` and assets stay byte-identical to a build without `ui/sdui/`.
- A fixture app with no web code of its own opens its screens in a browser from the generated `index.html`.
- The packaging CLI rejects one failing fixture per check in the table before `fdev website publish` runs, and writes an `sdui` field that matches the files.
- In EVY on iOS and Android, a River version with a new room contract carries "Skate club" and Bob's "Skate session Saturday?" forward while only the native reader runs.
- In EVY on iOS and Android, a River version with a new chat delegate key moves Alice's room and signing keys through the hidden WebView on first start. Closing EVY during the move keeps the old data, and the next start runs the move again.
