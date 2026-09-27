# 4.2 SDUI bundles and publication

Package optional SDUI content in an ordinary Freenet application archive.

Prerequisites: [1.4 Application bundles](../1-freenet-mobile-appkit/04-bundles.md), [2.3 Installation and updates](../2-evy-mobile-app/03-installation-and-updates.md), and [4.1 SDUI format and compatibility](01-format.md). This plan owns the SDUI artifact layout, schema checks and web-reader packaging. The foundation owns archive signing, safe extraction, publication references and release retention.

## Repositories

| Repository | Role | Work in this plan |
| --- | --- | --- |
| `freenet-appkit` | Modified | Application definition gains the SDUI descriptor; the packaging CLI validates SDUI documents and copies the web reader into `ui/sdui/web/` |
| `freenet-sdui` | Modified | Validation library and pinned web-reader build consumed by the packager |
| [freenet-core](https://github.com/freenet/freenet-core) | Used | `fdev website publish` and the website container as the unchanged publication base |

## Artifacts

Extend the foundation's application definition with an optional `sdui` descriptor. The archive layout below fixes every SDUI path, so the descriptor records only versions and requirements. It carries the SDUI interface version, required component versions, action and view protocol versions, the delegate aliases it calls, executor step versions and the bundled reader build. Contract and delegate references reuse the foundation's artifact and initialization descriptors.

Proposed descriptor inside `app_definition.json`:

```json
{
  "sdui": {
    "interface_version": "1",
    "components": { "appkit.button": "1", "appkit.input": "1", "appkit.list_item": "1" },
    "protocols": {
      "actions": { "river.sendMessage": "1", "river.createRoom": "1" },
      "views": { "river.room": "1" },
      "delegates": ["river.chat"]
    },
    "executor_steps": { "read_resource": "1", "call_delegate": "1", "submit": "1" },
    "reader_build": { "version": "1.0.3", "digest": "sha256:3f9c…" }
  }
}
```

| Path | Contents |
| --- | --- |
| `index.html` | Publisher's web entry point, or a generated reader-only page |
| `ui/sdui/ui.json` | Versioned screens, routes, themes and language references |
| `ui/sdui/actions/` | Declared actions, logical resources and view bindings |
| `ui/sdui/schemas/` | Action, view and typed delegate request/result schemas |
| `ui/sdui/web/` | Pinned web-reader build and its required runtime assets |

These paths add to the base archive layout. Contracts and delegates retain the foundation's paths and identity rules. Runtime assets include JavaScript, any selected SDK Wasm and bindings, CSS, fonts and icons. Resolve every path within the verified archive. Use relative paths and bundle required assets or reference content served by the node under the host policy.

| Web target | Entry-point behavior |
| --- | --- |
| Reader-only | Generated `index.html` loads the bundled reader and `ui/sdui/ui.json` |
| Custom web app with SDUI | Preserve its entry point and assets. Embed `<freenet-web src="ui/sdui/ui.json">` or the React export from [4.3 SDUI hosts and readers](03-readers.md) |

Native readers load the same screen documents through the verified installation. Their renderer and executor ship with the installed host application. Dedicated native builds use the base publication and distribution rules.

## Versions and schema checks

Keep version identities separate:

| Version | Identifies |
| --- | --- |
| Container publication | One signed release under the application identity |
| Application-definition format | The base manifest schema |
| SDUI interface and component versions | The screens and semantics a reader must support |
| Action, view and delegate protocols | Typed arguments, results and domain encodings |
| Executor step versions | The installed primitives each action uses |
| Web-reader build | Exact bundled rendering and adapter code |

The packager validates all SDUI documents against pinned schema packages. It checks references, argument and result types, routes, required components, permissions, resource targets, and the bundled reader's supported versions. It also checks artifact hashes and domain descriptors. Load screens, actions and schemas from one verified archive snapshot, and record the selected delegate code, parameters and protocol versions in the session.

Apply the foundation's file, download, expansion and memory caps to the complete archive, including reader assets. Apply the [screen limits in 4.1 SDUI format and compatibility](01-format.md) and the [action limits in 4.5 SDUI actions and delegate protocols](05-actions.md) before activation. An unsupported required component or action primitive blocks that SDUI target with a specific requirement report. The host can offer another declared, verified application target through [4.3 SDUI hosts and readers](03-readers.md).

## Initialization and publication

Readers ask the host to perform declared initialization using the base application descriptors. Contract creation uses its declared initial-state and parameter rules. Delegate registration uses its verified artifact and parameters. The host obtains the required consent, including approval for delegate changes. A resource created by an application action declares that lifecycle explicitly.

Keep predecessor references with the domain artifacts under the [migration rules in 1.7 Upgrades and migration](../1-freenet-mobile-appkit/07-migration.md). SDUI descriptors carry the references needed by the host's shared migration adapter.

Publication uses the [release tooling in 1.4 Application bundles](../1-freenet-mobile-appkit/04-bundles.md). Visual authoring exports a validated [checkpoint defined in 4.8 EVY Developer visual authoring](08-developer.md#durable-checkpoint-protocol) and records the exact schema, reader and domain-artifact inputs. For participating commercial products, [4.7 SDUI commerce and attribution](07-commerce.md) supplies the checkpoint-to-artifact mapping to attribution. Certification and publication observations follow the commercial owner rules.

Each release includes its reader and assets in the archive download. Measure that cost in the [reader profile of 4.3 SDUI hosts and readers](03-readers.md), including mobile update traffic within the inherited cellular budget.

## Acceptance

- Publish and open a reader-only archive and a custom web archive with embedded SDUI through the base release tooling.
- Preserve the custom web entry point, relative assets and application behavior during SDUI export and update.
- Reject mismatched action/delegate schemas, undeclared resource access, invalid paths, missing artifacts and an incompatible bundled reader before publication.
- Web and native readers select the same verified screen/action/schema snapshot and domain references.
- An unsupported native reader retains a usable installation and reports the required update or alternate target.
- Initialization, interrupted installation and delegate changes pass the foundation's permission and migration tests.
- Record complete archive size and measured download cost, including the reader build, against the supported mobile profile.

Source evidence: Freenet's [website publication](https://freenet.org/build/manual/publish-a-website/), [container implementation](https://github.com/freenet/freenet-core/tree/main/crates/website-contract) and [fdev website command](https://github.com/freenet/freenet-core/blob/main/crates/fdev/src/website.rs) provide the publication base. SDUI descriptors and packaging checks are proposed additions.
