# 1.9 Developer package and release acceptance

## Repositories

| Repository | Role | Work in this plan |
| --- | --- | --- |
| `freenet-appkit` | Modified | Developer package: River WebView starter, Swift and Kotlin examples, version matrix, setup, diagnostics export and release checklist |
| [freenet-core](https://github.com/freenet/freenet-core) | Used | Pinned Core, `crates/mobile` and thin-role builds named in the version matrix |
| [river](https://github.com/freenet/river) | Used | Starter application and the release flows in 1.8 Reference apps and compatibility fixtures |

## Purpose

Own the developer-facing package, supported-version matrix, setup instructions, diagnostic export and release checklist. Provide a River WebView starter plus Swift/Kotlin SDK examples for the supported native route. Include iOS and Android build commands, pinned dependencies, artifact verification, fixture setup, lifecycle integration and distribution instructions for both platforms.

## Prerequisites

The accepted plans below, plus the required thin-peer implementation and budgets in [1.10 Thin-peer role and cellular data budgets](10-thin-peer.md).

- [1.1 Mobile feasibility and supported profiles](01-feasibility.md)
- [1.2 Embedded node and mobile SDK](02-sdk.md)
- [1.3 Single-application host](03-host.md)
- [1.4 Application bundles](04-bundles.md)
- [1.5 Identity, keys and local protection](05-identity.md)
- [1.6 Application protocols, data and operations](06-data-and-operations.md)
- [1.7 Upgrades and migration](07-migration.md)
- [1.8 Reference apps and compatibility fixtures](08-reference-apps.md)

The prerequisite 1.8 Reference apps and compatibility fixtures covers River's release flows and the bounded Atlas compatibility fixtures. Atlas's hosted product flows have a separate [2.7 Multi-application acceptance](../2-evy-mobile-app/07-acceptance.md).

## Acceptance

| Release test | Passing evidence |
| --- | --- |
| Independent build | A second developer builds and installs the defined application from the starter instructions on iOS and Android. |
| River behavior | [1.8 Reference apps and compatibility fixtures](08-reference-apps.md#river-acceptance-cases) passes join, read, send, reconnect, restart and interrupted-upgrade cases through River's UI and real delegate. |
| Thin-peer release | Upstream role support is implemented, role-preserving failure tests pass and all measured cellular budgets in [1.10 Thin-peer role and cellular data budgets](10-thin-peer.md) pass. |
| Safety and durability | Host authority, protected keys, durable operations, app-specific encrypted export/import and supported migrations pass their owning plans. |
| Device limits and accessibility | Startup, memory, battery, storage exhaustion, keyboard, focus, large text and screen-reader tests pass on the declared devices. |
| Distribution | Reproducible iOS and Android packages and platform-review evidence cover the complete runtime and downloaded-content behavior on both platforms. |
| Diagnostics | Reports identify versions, node role, lifecycle state, observation provenance, pending-operation status and budget failures. Apply [host redaction in 1.3 Single-application host](03-host.md#diagnostics) to keys, tokens, message content and private references. |

Restart durability and migration are release requirements. [5.2 Extended customer backup and recovery](../5-optional-extensions/02-recovery.md) and [5.3 Device sync and authoring collaboration](../5-optional-extensions/03-sync-and-collaboration.md) are optional extensions of that foundation.
