# 2.4 Identity, permissions and device access

## Repositories

| Repository | Role | Work in this plan |
| --- | --- | --- |
| [evy](https://github.com/EVY-Platform/evy) | Modified | Trusted permission prompts, grant review and revocation, identity and record sharing screens in the iOS and Android apps |
| [freenet-core](https://github.com/freenet/freenet-core) | Used | Grant records and enforcement boundary in `crates/mobile` from 1.3 Single-application host and key protection from 1.5 Identity, keys and local protection |
| `freenet-appkit` | Used | Device adapters from 1.3 Single-application host |
| [river](https://github.com/freenet/river) | Used | Notification and clipboard permission fixtures |
| [atlas](https://github.com/freenet/atlas) | Used | Second app in revocation and sharing tests |

## Purpose

Provide trusted multi-app permission UX, revocable per-app grants, scoped device access and authorized identity sharing. Keep installation, permission, identity and recovery decisions outside application-controlled content.

## Prerequisites

- [1.5 Identity, keys and local protection](../1-freenet-mobile-appkit/05-identity.md) for base protection, deletion and app-specific export/import
- [Base authorization in 1.3 Single-application host](../1-freenet-mobile-appkit/03-host.md#base-authorization-and-device-access)
- [2.1 EVY shell and curated catalogue](01-catalogue.md) for the account and settings area
- [2.2 Multi-application sessions and authority](02-sessions.md)
- [2.3 Installation and updates](03-installation-and-updates.md), which supplies update and setup decisions

## Per-app grants and trusted prompts

Use the grant records and enforcement boundary defined in 1.3 Single-application host. Store grants and publisher trust outside application-readable storage. Show the requesting application and the permitted operation and target scope in trusted host UI.

- Present required and optional capabilities from verified bundle metadata for each application. Prompt when the user first needs an ungranted capability.
- Show newly declared access before an update gains it. Changed delegates and setup require installation approval. This plan owns that changed-access decision, and [activation in 2.3 Installation and updates](03-installation-and-updates.md#staged-installation-and-activation) waits for it.
- Show each app's grants in the [account and settings area of 2.1 EVY shell and curated catalogue](01-catalogue.md#catalogue-and-shell). Let the user review and revoke them there. Every protected operation and queued action uses the current grant.
- Require explicit authorization when sharing identity or private records between applications, WebViews and native contexts. Shared delegate installations also pass [namespace policy in 2.2 Multi-application sessions and authority](02-sessions.md#delegate-namespace-policy).
- Route delegate prompts and selected files or photos only to the authorized requesting operation and session. Display typed denial, unavailable, locked-device and expired-handle results.

The supported adapter set, delegate startup approval and foreground alert scope remain governed by [1.3 Single-application host](../1-freenet-mobile-appkit/03-host.md#base-authorization-and-device-access) and [1.1 Mobile feasibility and supported profiles](../1-freenet-mobile-appkit/01-feasibility.md#message-alerts). Runtime work stays subject to current authority.

## Acceptance

Test trusted prompts, expanded permissions, immediate revocation, locked devices and web/native handoffs with River and Atlas. Queued work rechecks authority. Revoking one app's grant stops its further use while the other app retains only its own authorized access. Identity and private-record sharing require explicit approval, and replies return only to the approved request and session.

Use the [admission issue table in 1.3 Single-application host](../1-freenet-mobile-appkit/03-host.md#host-admission-and-permission-dependencies) for pinned implementation evidence.
