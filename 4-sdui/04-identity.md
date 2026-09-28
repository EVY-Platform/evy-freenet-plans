# 4.4 SDUI identity and permissions

Bind reader requests to an existing authorized app/user session and present permission outcomes safely.

Prerequisites:

- [1.5 Identity, keys and local protection](../1-freenet-mobile-appkit/05-identity.md)
- [1.3 Single-application host](../1-freenet-mobile-appkit/03-host.md)
- [2.2 Multi-application sessions and authority](../2-evy-mobile-app/02-sessions.md)
- [2.3 Installation and updates](../2-evy-mobile-app/03-installation-and-updates.md)
- [2.4 Identity, permissions and device access](../2-evy-mobile-app/04-permissions.md)
- [4.3 SDUI hosts and readers](03-readers.md)

This plan owns reader bindings and UI behavior. The foundation owns caller authentication, delegate namespace policy, protected storage, grant persistence, recovery and revocation.

## Repositories

| Repository | Role | Work in this plan |
| --- | --- | --- |
| `freenet-sdui` | Modified | Reader session handle use, permission bindings, clearing of reader-held private values and diagnostics redaction |
| [freenet-core](https://github.com/freenet/freenet-core) | Modified | `crates/mobile` gains opaque session handles for readers |
| `freenet-appkit` | Modified | Reader prompt requests and scoped device handles |
| [river](https://github.com/freenet/river) | Used | Notification component as evidence for permission-dependent UI |

## Session binding

The host supplies an opaque session handle after it verifies the application and selected content. Every reader operation uses that handle. The host associates it with the application identity, verified content reference, user, installation and session generation through its existing interfaces.

Screen definitions, route parameters, expressions and delegate payloads are untrusted data. A publisher-supplied app or user ID carries only the meaning the domain schema gives it. The host derives authorization from its session. Delegates apply policy using Core's attested caller and their own verified records, as [1.6 Application protocols, data and operations](../1-freenet-mobile-appkit/06-data-and-operations.md) specifies.

Reader callbacks carry request and session correlation from the adapter. Expired-session callbacks leave the active screen unchanged. Embedded SDUI and custom content in one authorized page share its session. Switching applications, users or targets follows the host's session rules and releases scoped reader handles.

## Permission bindings

The bundle declares required and optional capabilities under [4.2 SDUI bundles and publication](02-bundles.md). Components refer to those capabilities by typed name. The host checks the current grant and target before a component uses a protected capability.

| Reader request | Host result | Reader behavior |
| --- | --- | --- |
| Use a declared capability | Scoped handle or typed result | Use the handle or result in the component |
| Use a capability needing consent | Trusted host prompt | Keep the form and show that authorization is pending |
| User declines or revokes access | Typed denial | Explain the affected feature and preserve recoverable input |
| Platform lacks the adapter | Typed unavailable result | Use the declared optional fallback or block the required flow |
| Session expires or device locks protected data | Typed session or locked-state result | Release protected views and offer the host's resume flow |

The host draws permission, identity-selection, signing-approval and recovery prompts outside publisher-controlled content. The reader can request a prompt and display its result. Trusted host UI supplies the application identity and requested scope. Newly declared access follows the foundation's consent policy.

A photo picker supplies the chosen item through a bounded handle scoped to the action and session. Camera, files, clipboard, maps, notifications and outside links follow the same adapter boundary. Validate returned handles and targets before use. Media, previews and automatic loads use the host's network policy as well as explicit button actions.

[River's notification component](https://github.com/freenet/river/blob/main/ui/src/components/app/notifications.rs) supplies source evidence for a permission-dependent UI. Reader bindings and cross-platform denial/unavailable behavior are milestone 4 (SDUI) work.

## Protected data and signing

Delegates perform private operations and signing under their policy. The reader receives the allowed projection or result. Keys, node credentials and service secrets remain behind their owning interfaces.

Clear reader-held private values when the host signals lock, logout, revocation or session expiry, according to the host's retention policy. Redact private values from validation reports, component diagnostics and exported support reports.

Applications that share delegate code and parameters use the [tested namespace policy in 2.2 Multi-application sessions and authority](../2-evy-mobile-app/02-sessions.md). Reader-local component IDs and storage keys add UI addressing within that scope. Host authorization determines who can access it.

## Acceptance

- Forged app/user fields, expired sessions, unknown handles and cross-app callbacks fail through the host adapter before protected work.
- Real browser, iOS and Android tests distinguish permission denial, unavailable adapters, locked data and expired sessions.
- Two applications using the same delegate code and parameters retain the namespace isolation established by the foundation.
- Publisher content cannot obtain protected handles by imitating a host prompt. Signing and recovery use trusted UI.
- Exported diagnostics pass checks for private field and secret disclosure.
