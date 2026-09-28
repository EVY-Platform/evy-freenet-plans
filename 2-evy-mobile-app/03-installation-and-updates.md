# 2.3 Installation and updates

## Repositories

| Repository | Role | Work in this plan |
| --- | --- | --- |
| [evy](https://github.com/EVY-Platform/evy) | Modified | Per-app staged installation, activation, retention and rollback on the shared node in the iOS and Android apps |
| `freenet-appkit` | Used | Installation checks, activation and rollback from 1.4 Application bundles |
| [freenet-migrate](https://github.com/freenet/freenet-migrate) | Used | Migration from 1.7 Upgrades and migration |
| [river](https://github.com/freenet/river) | Used | Update fixture that must preserve Atlas's session |
| [atlas](https://github.com/freenet/atlas) | Used | Update fixture that must preserve River's session |

## Purpose

Own verified installation and staged release activation across the curated applications. Resolve each selected application identity to verified content, keep sessions on compatible releases and preserve other applications' work during an update.

The workflow uses the shared [single-app installation rules in 1.4 Application bundles](../1-freenet-mobile-appkit/04-bundles.md#installing-a-copy). Milestone 1 (Freenet mobile AppKit) implements and accepts its single-app path through 1.3 Single-application host, 1.4 Application bundles and 1.7 Upgrades and migration. This plan composes that foundation per app on a shared node.

## Prerequisites

[Bundle tooling, publication references and installation rules in 1.4 Application bundles](../1-freenet-mobile-appkit/04-bundles.md#installing-a-copy), [1.7 Upgrades and migration](../1-freenet-mobile-appkit/07-migration.md) and [2.2 Multi-application sessions and authority](02-sessions.md).

## Staged installation and activation

Run the [single-app installation rules in 1.4 Application bundles](../1-freenet-mobile-appkit/04-bundles.md#installing-a-copy) independently for each application. 1.4 Application bundles owns candidate verification, version conflicts and rollback rules. [1.3 Single-application host](../1-freenet-mobile-appkit/03-host.md#activating-a-release) owns activation. 1.7 Upgrades and migration owns staged migration.

- Associate every candidate and installation decision with its full application identity and selected session.
- Check [shared-delegate policy in 2.2 Multi-application sessions and authority](02-sessions.md#delegate-namespace-policy) before admitting setup that could share a private namespace with another application.
- Activation waits for the changed-access decision.
- Activate at that application's session boundary. Keep its pending operations linked to their [original content references defined in 1.6 Application protocols, data and operations](../1-freenet-mobile-appkit/06-data-and-operations.md#operation-identity-and-journal).
- Preserve the other application's active release, authority, callbacks and pending work through successful or failed activation.

## Retention and recovery choices

Apply the [retained-copy and rollback policy in 1.4 Application bundles](../1-freenet-mobile-appkit/04-bundles.md#installing-a-copy) to each application.

Updating River preserves Atlas's active session and pending work, and updating Atlas preserves River's.

## Acceptance

Test interrupted activation, replayed content, same-version divergence, rollback, data changes, failed migration and cleanup with pending work. Each session retains a consistent usable release and the original content references of pending operations. Updating one app preserves the other's session and authorized work.

Conflicting shared-delegate installations pass [namespace policy in 2.2 Multi-application sessions and authority](02-sessions.md#delegate-namespace-policy) or fail admission.
