# SDUI identity and permissions

Plan ID: 4.4. Bind reader requests to an existing authorized app/user session and present permission outcomes safely.

Prerequisites: [identity and protected records, 1.5](../1-freenet-mobile-appkit/05-identity.md), [host admission, 1.3](../1-freenet-mobile-appkit/03-host.md), [multi-app authority, 2.2](../2-evy-mobile-app/02-sessions.md), [installation, 2.3](../2-evy-mobile-app/03-installation-and-updates.md), [grants, 2.4](../2-evy-mobile-app/04-permissions.md), and [readers, 4.3](03-readers.md). This plan owns reader bindings and UI behavior. The foundation owns caller authentication, delegate namespace policy, protected storage, grant persistence, recovery and revocation.

## Session binding

The host supplies an opaque session handle after it verifies the application and selected content. Every reader operation uses that handle. The host associates it with the application identity, verified content reference, user, installation and session generation through its existing interfaces.

Screen definitions, route parameters, expressions and delegate payloads are untrusted data. A publisher-supplied app or user ID carries only the meaning the domain schema gives it. The host derives authorization from its session. Delegates apply policy using Core's attested caller and their own verified records, as [foundation delegate access](../1-freenet-mobile-appkit/06-data-and-operations.md) specifies.

Reader callbacks carry request and session correlation from the adapter. Expired-session callbacks leave the active screen unchanged. Embedded SDUI and custom content in one authorized page share its session. Switching applications, users or targets follows the host's session rules and releases scoped reader handles.

## Permission bindings

The bundle declares required and optional capabilities under [4.2](02-bundles.md). Components and actions refer to those capabilities by typed name. The host checks the current grant and target before each protected step, including resumed work.

| Reader request | Host result | Reader behavior |
| --- | --- | --- |
| Use a declared capability | Scoped handle or typed result | Continue the declared action |
| Use a capability needing consent | Trusted host prompt | Keep the form and show that authorization is pending |
| User declines or revokes access | Typed denial | Explain the affected feature and preserve recoverable input |
| Platform lacks the adapter | Typed unavailable result | Use the declared optional fallback or block the required flow |
| Session expires or device locks protected data | Typed session or locked-state result | Release protected views and offer the host's resume flow |

The host draws permission, identity-selection, signing-approval and recovery prompts outside publisher-controlled content. The reader can request a prompt and display its result. Trusted host UI supplies the application identity and requested scope. Newly declared access follows the foundation's consent policy.

A photo picker supplies the chosen item through a bounded handle scoped to the action and session. Camera, files, clipboard, maps, notifications and outside links follow the same adapter boundary. Validate returned handles and targets before use. Media, previews and automatic loads use the host's network policy as well as explicit button actions.

[River's notification component](https://github.com/freenet/river/blob/main/ui/src/components/app/notifications.rs) supplies source evidence for a permission-dependent UI. Reader bindings and cross-platform denial/unavailable behavior are milestone 4 work.

## Protected data and signing

Bind private form fields and saved drafts to approved protected-store operations from [1.5](../1-freenet-mobile-appkit/05-identity.md) and [1.6](../1-freenet-mobile-appkit/06-data-and-operations.md). Delegates perform private operations and signing under their policy. The reader receives the allowed projection or result. Keys, node credentials and service secrets remain behind their owning interfaces.

Clear reader-held private values when the host signals lock, logout, revocation or session expiry, according to the host's retention policy. Saving, recovery and deletion use that same policy. Redact private values from validation reports, component diagnostics, preview recordings and exported support reports.

Applications that share delegate code and parameters use [2.2's tested namespace policy](../2-evy-mobile-app/02-sessions.md). Reader-local component IDs and storage keys add UI addressing within that scope. Host authorization determines who can access it.

## Acceptance

- Forged app/user fields, expired sessions, unknown handles and cross-app callbacks fail through the host adapter before protected work.
- Real browser, iOS and Android tests distinguish permission denial, unavailable adapters, locked data and expired sessions while preserving permitted drafts.
- Revocation during an action or queued operation stops newly unauthorized steps. The foundation continues tracking any submitted mutation.
- Two applications using the same delegate code and parameters retain the namespace isolation established by the foundation.
- Publisher content cannot obtain protected handles by imitating a host prompt. Signing and recovery use trusted UI.
- Exported diagnostics and recorded previews pass checks for private field and secret disclosure.
