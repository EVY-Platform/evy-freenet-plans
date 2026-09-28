# 4.2 SDUI bundles and publication

Package optional SDUI content in an ordinary Freenet application archive.

Prerequisites: [1.4 Application bundles](../1-freenet-mobile-appkit/04-bundles.md), [2.3 Installation and updates](../2-evy-mobile-app/03-installation-and-updates.md), and [4.1 SDUI format and compatibility](01-format.md). This plan owns the SDUI artifact layout, schema checks and publication of SDUI content. The foundation owns archive signing, safe extraction, publication references and release retention.

## Repositories

| Repository | Role | Work in this plan |
| --- | --- | --- |
| `freenet-appkit` | Modified | Application definition gains the SDUI descriptor; the packaging CLI validates SDUI documents |
| `freenet-sdui` | Modified | Validation library consumed by the packager |
| [freenet-core](https://github.com/freenet/freenet-core) | Used | `fdev website publish` and the website container as the unchanged publication base |

## Artifacts

Extend the foundation's application definition with an optional `sdui` descriptor. The archive layout below fixes every SDUI path, so the descriptor records only versions and requirements. It carries the SDUI interface version, required component versions, action and view protocol versions, the delegate aliases it calls and executor step versions. Contract and delegate references reuse the foundation's artifact and initialization descriptors.

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
    "executor_steps": { "read_resource": "1", "call_delegate": "1", "submit": "1" }
  }
}
```

| Path | Contents |
| --- | --- |
| `index.html` | Publisher's web entry point |
| `ui/sdui/ui.json` | Versioned screens, routes, themes and language references |
| `ui/sdui/actions/` | Declared actions, logical resources and view bindings |
| `ui/sdui/schemas/` | Action, view and typed delegate request/result schemas |

These paths add to the base archive layout. Contracts and delegates retain the foundation's paths and identity rules. Resolve every path within the verified archive. Use relative paths and bundle required assets or reference content served by the node under the host policy.

A custom web app with SDUI keeps its entry point and assets. Dedicated native builds use the base publication and distribution rules.

## Versions and schema checks

Keep version identities separate:

| Version | Identifies |
| --- | --- |
| Container publication | One signed release under the application identity |
| Application-definition format | The base manifest schema |
| SDUI interface and component versions | The screens and semantics a reader must support |
| Action, view and delegate protocols | Typed arguments, results and domain encodings |
| Executor step versions | The installed primitives each action uses |

The packager validates all SDUI documents against pinned schema packages. It checks references, routes, required components and permissions. It also checks artifact hashes and domain descriptors. Load screens, actions and schemas from one verified archive snapshot.

Apply the foundation's file, download, expansion and memory caps to the complete archive. Apply the [screen limits in 4.1 SDUI format and compatibility](01-format.md) before activation. An unsupported required component blocks that SDUI target with a specific requirement report.

## Publication

Keep predecessor references with the domain artifacts under the [migration rules in 1.7 Upgrades and migration](../1-freenet-mobile-appkit/07-migration.md). SDUI descriptors carry the references needed by the host's shared migration adapter.

Publication uses the [release tooling in 1.4 Application bundles](../1-freenet-mobile-appkit/04-bundles.md).

## Acceptance

- Publish a custom web archive with SDUI documents through the base release tooling.
- Preserve the custom web entry point, relative assets and application behavior during SDUI export and update.
- Reject invalid paths and missing artifacts before publication.
- Interrupted installation and delegate changes pass the foundation's permission and migration tests.
- Record complete archive size and measured download cost against the supported mobile profile.

Source evidence: Freenet's [website publication](https://freenet.org/build/manual/publish-a-website/), [container implementation](https://github.com/freenet/freenet-core/tree/main/crates/website-contract) and [fdev website command](https://github.com/freenet/freenet-core/blob/main/crates/fdev/src/website.rs) provide the publication base. SDUI descriptors and packaging checks are proposed additions.
