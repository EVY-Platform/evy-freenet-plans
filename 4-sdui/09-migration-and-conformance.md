# SDUI migration and conformance

Plan ID: 4.9. Upgrade screen and form definitions safely and prove equivalent domain behavior across web, iOS and Android readers.

Prerequisites: [shared upgrade rules, 1.7](../1-freenet-mobile-appkit/07-migration.md), [host installation, 2.3](../2-evy-mobile-app/03-installation-and-updates.md), [format, 4.1](01-format.md), [bundles, 4.2](02-bundles.md), [readers, 4.3](03-readers.md), [actions, 4.5](05-actions.md), and [data bindings, 4.6](06-data.md). Paid-flow fixtures add [4.7](07-commerce.md). Authoring import/export fixtures add [4.8](08-developer.md).

## Ownership and scope

The foundation owns contract/delegate re-keying, publisher continuity, protected-record migration, operation journals and atomic installation. This plan adds reader compatibility, screen/form conversion and cross-target fixtures. Application-owned adapters perform domain data conversion under the foundation rules.

Use the same verified screen/action/schema snapshot throughout a session. Activation follows the host's release-switching rules. The selected delegate code, parameters and protocols remain recorded with that session and its durable operations.

## Compatibility and activation

Publish a compatibility matrix covering application-definition, SDUI interface, component, action-step, view and delegate-protocol versions. Generate schema comparisons and test every supported upgrade pair. State the support window for native reader releases and stored form schemas.

| Change | Required handling |
| --- | --- |
| Compatible screen or text change | Validate the snapshot and activate through the host |
| Optional component unsupported | Validate and use its declared safe fallback |
| Required component or primitive unsupported | Retain a compatible release and report the required reader/host update |
| Bundled web reader incompatible with its screens | Block publication |
| Route or form schema change | Run the declared conversion or preserve the saved data for explicit repair |
| Contract, delegate or publisher identity change | Invoke the foundation's migration and consent flow |
| Current shared data exceeds supported schemas | Present a compatibility error and retain recoverable local work |

[River's predecessor registries](../1-freenet-mobile-appkit/07-migration.md) and [freenet-migrate](https://github.com/freenet/freenet-migrate) supply domain migration evidence. SDUI consumes the foundation's verified descriptors and adapter results. Reader-form compatibility requires its own fixtures.

## Form and route upgrades

Identify a saved form by application/user scope, stable form ID, schema version and originating definition reference. The host retains its protected stored copy during conversion. A conversion declares supported source/target schemas, field mappings, defaults and validation rules. It uses bounded installed logic or an approved domain adapter through the foundation interfaces.

Keep canonical domain values separate from formatted display strings. Test null, missing values, decimal and timestamp conversions. Present fields needing repair explicitly. Obtain confirmation for destructive changes under the application's declared policy. Commit the converted form only after validation and preserve a recoverable source until the migration policy permits cleanup.

Validate restored routes and parameters against the activated release. Map a renamed route through an explicit versioned rule, or offer a supported destination with the saved draft retained. Preserve focus and navigation semantics when a compatible page resumes.

A changed draft can start a new operation through the foundation. Submitted operations retain their original identity, payload and protocol/content references. Reader upgrades reconnect to their journal entries and display reconciliation outcomes. [Paid operations](07-commerce.md) also retain their original commercial bindings.

## Cross-target suite

Use shared protocol and behavior fixtures with fixed locale, time zone, clock, randomness and sample identity. Run real delegates alongside deterministic preview fixtures. Record Core, SDK, reader, schema and domain-artifact versions with results.

| Fixture | Required observation |
| --- | --- |
| [Atlas](../1-freenet-mobile-appkit/08-reference-apps.md) | Equivalent query or update through SDUI and custom web/native controls, preserving the published index identity |
| River signing | Equivalent canonical signing inputs, prepared bytes and observed message result |
| [Paid pilot](../3-attribution-remuneration-payment/08-marketplace.md) | Equivalent checkout terms, domain completion evidence and original payment bindings |
| Reader-only and embedded pages | Matching actions and errors while custom entry points, assets and navigation keep working |
| Forms and language | Compatible draft recovery, route validation, locale fallback and right-to-left layout |
| Accessibility | Browser keyboard/screen reader, VoiceOver and TalkBack control semantics and focus |
| Authority failures | Denial, unavailable adapters, locked data, revoked grants and forged session fields |
| Lifecycle failures | Force termination, network changes, duplicate/late callbacks and interrupted activation |
| Resource limits | Bounded rendering, expressions, action expansion, storage and subscription demand |

Compare values, domain results, navigation events, operation records and typed errors. Platform-specific layout can vary while semantic and accessibility results agree. Component snapshots supplement these behavior checks.

## Acceptance

- Every supported reader/profile passes the shared schema, codec and behavior suite, including real SwiftUI and Compose applications on devices.
- Form upgrades cover compatible fields, renamed/removed fields, failed conversions, interrupted writes and explicit repair while preserving a recoverable source.
- An incompatible update keeps a usable installation and required pending-work artifacts. Rollback follows the foundation's version and authority rules.
- Updates during a submitted operation or checkout retain original operation and commercial bindings through reconciliation.
- Custom web/native acceptance passes alongside reader-only and embedded SDUI tests.
- Mobile tests run under the required [thin-peer cellular profile](../1-freenet-mobile-appkit/10-thin-peer.md), including reader and archive-update traffic.
- Release reports separate source inspection, compilation, simulator runs and real-device results and list the supported version matrix.
