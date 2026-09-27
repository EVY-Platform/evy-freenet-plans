# Plan 1.9: Developer package and release acceptance

## Purpose

Own the developer-facing package, supported-version matrix, setup instructions, diagnostic export and release checklist. Provide a River WebView starter plus Swift/Kotlin SDK examples for the supported native route. Include iOS and Android build commands, pinned dependencies, artifact verification, fixture setup, lifecycle integration and distribution instructions for both platforms.

## Prerequisites

Accepted plans [1.1](01-feasibility.md), [1.2](02-sdk.md), [1.3](03-host.md), [1.4](04-bundles.md), [1.5](05-identity.md), [1.6](06-data-and-operations.md), [1.7](07-migration.md) and [1.8](08-reference-apps.md), plus the required thin-peer implementation and budgets in [1.10](10-thin-peer.md).

The 1.8 prerequisite covers River's release flows and the bounded Atlas compatibility fixtures. Atlas's hosted product flows have a separate [2.7 gate](../2-evy-mobile-app/07-acceptance.md).

## Acceptance

| Release test | Passing evidence |
| --- | --- |
| Independent build | A second developer builds and installs the defined application from the starter instructions on iOS and Android. |
| River behavior | [1.8](08-reference-apps.md#river-acceptance-cases) passes join, read, send, reconnect, restart and interrupted-upgrade cases through River's UI and real delegate. |
| Thin-peer release | Upstream role support is implemented, role-preserving failure tests pass and all measured cellular budgets in [1.10](10-thin-peer.md) pass. |
| Safety and durability | Host authority, protected keys, durable operations, app-specific encrypted export/import and supported migrations pass their owning plans. |
| Device limits and accessibility | Startup, memory, battery, storage exhaustion, keyboard, focus, large text and screen-reader tests pass on the declared devices. |
| Distribution | Reproducible iOS and Android packages and platform-review evidence cover the complete runtime and downloaded-content behavior on both platforms. |
| Diagnostics | Reports identify versions, node role, lifecycle state, observation provenance, pending-operation status and budget failures. Apply [host redaction](03-host.md#diagnostics) to keys, tokens, message content and private references. |

Restart durability and migration are release requirements. [Broader customer recovery in 5.2](../5-optional-extensions/02-recovery.md) and [device sync in 5.3](../5-optional-extensions/03-sync-and-collaboration.md) are optional extensions of that foundation.
