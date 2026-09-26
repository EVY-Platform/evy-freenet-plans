# Plan 2.3: Installation and updates

## Purpose

Own verified installation and staged release activation across the curated applications. Resolve each selected application identity to verified content, keep sessions on compatible releases and preserve other applications' work during an update.

The workflow uses the shared [per-app installation interface in 1.3](../1-freenet-mobile-appkit/03-host.md#single-app-installation-interface). Milestone 1 implements and accepts its single-app path through 1.3, 1.4 and 1.7. This plan composes that foundation per app on a shared node.

## Prerequisites

[Bundle tooling and publication references in 1.4](../1-freenet-mobile-appkit/04-bundles.md), [migration 1.7](../1-freenet-mobile-appkit/07-migration.md), the single-app installation interface and [2.2 session authority](02-sessions.md). [2.4](04-permissions.md) supplies multi-app consent and grant UX.

## Staged installation and activation

Run the [1.3 installation interface](../1-freenet-mobile-appkit/03-host.md#single-app-installation-interface) independently for each application. It owns candidate verification, version conflicts, staged migration, atomic activation and rollback rules.

- Associate every candidate and installation decision with its full application identity and selected session.
- Check [2.2's shared-delegate policy](02-sessions.md#delegate-namespace-policy) before admitting setup that could share a private namespace with another application.
- Obtain changed-access consent through [2.4](04-permissions.md) for the affected application.
- Activate at that application's session boundary. Keep its pending operations linked to their [original content references](../1-freenet-mobile-appkit/06-data-and-operations.md#operation-identity-and-journal).
- Preserve the other application's active release, authority, callbacks and pending work through successful or failed activation.

## Retention and recovery choices

Apply 1.3's retained-copy and rollback policy per application. [Lifecycle 2.5](05-lifecycle.md) allocates storage and download work within the shared budgets, preserving the artifacts required by both applications' pending operations. [Application management 2.6](06-navigation.md) shows each app's recovery and update choices.

Updating River preserves Atlas's active session and pending work, and updating Atlas preserves River's.

## Acceptance

Test interrupted activation, replayed content, same-version divergence, rollback, data changes, failed migration and cleanup with pending work. Each session retains a consistent usable release and the original content references of pending operations. Updating one app preserves the other's session and authorized work.

Expanded access obtains consent before activation. Conflicting shared-delegate installations pass [2.2's namespace policy](02-sessions.md#delegate-namespace-policy) or fail admission. The combined product suite belongs to [2.7](07-acceptance.md).
