# Plan 2.4: Identity, permissions and device access

## Purpose

Provide trusted multi-app permission UX, revocable per-app grants, scoped device access and authorized identity sharing. Keep installation, permission, identity and recovery decisions outside application-controlled content.

## Prerequisites

[Identity 1.5](../1-freenet-mobile-appkit/05-identity.md) for base protection, deletion and app-specific export/import, [base authorization in 1.3](../1-freenet-mobile-appkit/03-host.md#base-authorization-and-device-access), and [session isolation 2.2](02-sessions.md). [Installation 2.3](03-installation-and-updates.md) supplies update and setup decisions.

## Per-app grants and trusted prompts

Use the grant records and enforcement boundary defined in 1.3. Store grants and publisher trust outside application-readable storage. Show the requesting application and the permitted operation and target scope in trusted host UI.

- Present required and optional capabilities from verified bundle metadata for each application. Prompt when the user first needs an ungranted capability.
- Show newly declared access before an update gains it. Changed delegates and setup require installation approval.
- Let the user review and revoke each app's grants. Every protected operation and queued action uses the current grant.
- Require explicit authorization when sharing identity or private records between applications, WebViews and native contexts. Shared delegate installations also pass [2.2's namespace policy](02-sessions.md#delegate-namespace-policy).
- Route delegate prompts and selected files or photos only to the authorized requesting operation and session. Display typed denial, unavailable, locked-device and expired-handle results.

The supported adapter set, delegate startup approval and foreground alert scope remain governed by [1.3](../1-freenet-mobile-appkit/03-host.md#base-authorization-and-device-access) and [1.1](../1-freenet-mobile-appkit/01-feasibility.md#scope-and-acceptance). Runtime work stays subject to current authority and [2.5's shared budgets](05-lifecycle.md).

[Navigation 2.6](06-navigation.md) owns app-management screens and handoffs. Optional reader integration belongs to [SDUI identity 4.4](../4-sdui/04-identity.md).

## Acceptance

Test trusted prompts, expanded permissions, immediate revocation, locked devices and web/native handoffs with River and Atlas. Queued work rechecks authority. Revoking one app's grant stops its further use while the other app retains only its own authorized access. Identity and private-record sharing require explicit approval, and replies return only to the approved request and session.

Use [1.3's admission issue table](../1-freenet-mobile-appkit/03-host.md#host-admission-and-permission-dependencies) for pinned implementation evidence. The combined product gate is [2.7](07-acceptance.md).
