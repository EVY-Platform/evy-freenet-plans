# 4.8 EVY Developer visual authoring

Add visual SDUI editing, preview, import and deterministic checkpoint export to the code-based Developer workflows. This plan owns the editor and durable checkpoint protocol.

Prerequisites:

- [3.6 Contribution and release workspace](../3-attribution-remuneration-payment/06-developer.md)
- [1.5 Identity, keys and local protection](../1-freenet-mobile-appkit/05-identity.md)
- [1.6 Application protocols, data and operations](../1-freenet-mobile-appkit/06-data-and-operations.md)
- [4.1 SDUI format and compatibility](01-format.md)
- [4.2 SDUI bundles and publication](02-bundles.md)
- [4.3 SDUI hosts and readers](03-readers.md)
- [4.5 SDUI actions and delegate protocols](05-actions.md)
- [4.6 SDUI data and operation presentation](06-data.md)
- [4.7 SDUI commerce and attribution](07-commerce.md)

[5.3 Device sync and authoring collaboration](../5-optional-extensions/03-sync-and-collaboration.md#optional-real-time-collaboration) adds real-time sessions. Repository-authored SDUI uses CLI/CI publication independently of this plan.

## Repositories

| Repository | Role | Work in this plan |
| --- | --- | --- |
| `freenet-app-builder` | Created | Editor, project model, EVY importer, schema-driven editors, preview, validation, deterministic export, authoring-project contract and checkpoint protocol |
| [evy](https://github.com/EVY-Platform/evy) | Modified | Canvas, row factories, action editor, design system and schema generation reused; `web/` Developer service clients integrated; `services/attribution` gains the checkpoint-evidence path and checkpoint author registration |
| `freenet-sdui` | Used | Released schema packages and web reader for preview |
| `freenet-appkit` | Used | Memory host adapter and publication tooling |
| [freenet-core](https://github.com/freenet/freenet-core) | Used | Operation journal in `crates/mobile` from 1.6 Application protocols, data and operations; fdev conformance #5344 and merge properties #5320 for contract tests; traffic issues #5153 and #5050 |

## Scope and implementation

Build the visual extension in a dedicated `freenet-app-builder` workspace using TypeScript, React and Vite, with Bun for development and tests. Integrate the existing Developer service clients and release workflows. Reuse [EVY's](https://github.com/EVY-Platform/evy) canvas, row factories, action editor, design system and schema generation where they match the released Freenet interfaces.

Separate the project model and EVY importer from canvas, catalogue, configuration, binding/action editors, preview and export. Import schemas through released AppKit/SDUI packages. Source schemas and row names are centralized in the [component catalogue of 4.1 SDUI format and compatibility](01-format.md#components-and-source-catalogue).

The canvas edits SDUI. Publishers continue writing custom application code in their chosen tools. New domain behavior uses delegate/schema development. New executor primitives follow the [release rules in 4.5 SDUI actions and delegate protocols](05-actions.md).

## Project and editing model

A project records application identity and targets, custom web build references, flows, pages, components, routes, themes, languages, actions, typed views, logical resources and domain-artifact descriptors. It also holds sample scenarios, capability references and source-to-artifact evidence. Link to proposals and review status through Developer's existing service interfaces.

Large binary assets use content references, verified digests and upload progress through an explicitly supported storage adapter. Bundle runtime assets under [4.2 SDUI bundles and publication](02-bundles.md).

Apply edits immediately and append them to a local draft journal with stable IDs. Undo appends a safe inverse. The checkpoint protocol below defines the supported operations, signatures, conflicts and save batches. Expose conflicting values and an explicit resolution action. Local editing, offline work and checkpoint publication form this plan's authoring gate.

## Schema catalogue and editors

Generate configuration controls from released JSON Schema. Provide curated editors for typed bindings, selectors, action steps, delegate arguments/results, routes, responsive layout and accessible labels.

A binding picker shows a data source and its typed fields. An action editor shows the available primitive versions and domain operations. Query controls show permitted indexes and result limits. Keep domain decoding and business calculations in the declared adapters. Presentation expressions use the limits from [4.1 SDUI format and compatibility](01-format.md#values-and-expressions).

Explain fields in plain language. An advanced view exposes the underlying schema and protocol reference. Component insertion supplies required states and flags missing accessible labels.

## Preview

Embed the released web reader and declared-action executor through a deterministic memory host adapter. Use typed delegate-result fixtures and fake identity, network, signing, device and payment adapters by default. An explicitly selected development environment runs real Core and delegates through the adapter selected by [4.3 SDUI hosts and readers](03-readers.md). Label that environment and its possible effects before connecting.

Provide recorded user-flow playback and these scenarios:

- Responsive web sizes and iOS/Android semantic frames.
- Light, dark and high-contrast themes, large text and right-to-left text.
- Loading, stale, empty, offline, error, permission-denied and unavailable-adapter states.
- Sample identities, a River room and domain-specific typed results.
- Pending, superseded and unresolved operations, with simulated checkout and evidence outcomes when enabled.

Mobile frames approximate layout. Native conformance uses real SwiftUI and Compose test applications. Shared fixtures compare memory preview with live delegate behavior, and fixed clock/locale settings make playback repeatable.

## Validation and import

Validate continuously during editing and again before export. Errors block publication. Warnings require acknowledgement or the applicable policy approval.

| Check | Example finding |
| --- | --- |
| Schema and protocol agreement | An action argument differs from its delegate schema |
| Artifact integrity | Exported bytes differ from the reviewed checkpoint mapping |
| Reader and host capabilities | A selected target lacks a required primitive |
| Bindings and routes | A missing data field, unknown action or unreachable page |
| Resource declaration | A query or prepared target exceeds the declared resource scope |
| Accessibility | An icon button lacks a label or a form error has no accessible association |
| Limits | Oversized inline data, excessive action work or an unbounded list |
| Commercial readiness | The owning service reports incomplete review or ineligible evidence |

Import EVY flows, pages and rows into the released project schema. Preserve stable IDs where possible, normalize entities and relationships, parse typed values, map resource references to logical bindings, and resolve actions against supported steps and delegate protocols. Map each row to a catalogue component or composition.

Convert only bounded supported expressions. Produce explicit repair tasks for unsupported behavior, domain work needing a delegate change and features needing a new executor primitive. Keep the imported source and a conversion report alongside the checkpoint evidence. Validate the resulting checkpoint before export.

## Checkpoints and export

Export a validated checkpoint under the protocol below. Pin schema packages, reader builds, domain artifacts and exporter version. Deterministic export produces the same application files and mapping for those exact inputs. The base publication tool owns archive signing and publication versioning.

Preserve a custom web entry point and relative assets. Generate a reader-only entry point for a project that selects that target. Package the web reader under [reader packaging in 4.3 SDUI hosts and readers](03-readers.md#reader-packaging) and validate every declared native reader requirement. Custom native distribution remains a separately identified build.

Submit exact signed checkpoint evidence through [3.6 Contribution and release workspace](../3-attribution-remuneration-payment/06-developer.md). For commercial products, the [checkpoint evidence path](#checkpoint-evidence) connects the reviewed mapping to the attribution service. Contribution review, certification authority and earnings remain with their milestone 3 (Attribution, remuneration and payment) owners.

## Durable checkpoint protocol

Store signed mutable project state and export a verified checkpoint for review and publication.

### State and signatures

Publish a versioned canonical encoding and shared codec fixtures for:

```text
project identity, protocol version, membership epoch and roster digest
flows, pages, components, themes and typed artifact references
relationships with stable item IDs and ordered position tokens
signed operations, causal references, conflicts and tombstones
checkpoint digest, operation frontier and predecessor references
```

Each operation has a stable ID, author, membership epoch, causal parents and canonical payload. Its signature binds the full payload and project context. `CreateEntity`, `SetProperty`, `InsertChild`, `MoveChild`, `RemoveChild`, `TombstoneEntity` and `RestoreEntity` have typed payloads. Relationship operations use stable relationship-item IDs.

Signing uses the protected host/delegate path. Membership authorizes writes. Publish a clear visibility policy for project contents and signed records stored on Freenet. Private source material requires an approved encrypted-storage and key-sharing profile before upload. Keep signing keys in protected host/delegate interfaces, private credentials in their owning protected stores, and service credentials with their service owners.

### Merge and conflict rules

Merge signed operations by ID as a set. Duplicate delivery preserves the same operation. Conflicting bytes under one ID remain inspectable and block affected export. A causally later property write replaces the earlier write named in its history. Concurrent writes retain all competing values. A resolution names every conflicting predecessor and the chosen value.

Stable position tokens order relationship items. Operation IDs break ties between concurrent insertions. Concurrent moves of one item remain a conflict requiring resolution.

A concurrent deletion hides an entity, retains its edits and records a tombstone. Restore names that deletion and resolves retained values. Broken references, relationship cycles and unresolved conflicts in included entities or their dependencies block checkpoint export.

### Membership epochs

The owner signs an immutable roster and base checkpoint for each epoch. The roster and its authorized operations share one authoring-project contract instance. An epoch is a partition of that state. A membership change creates an owner-signed successor epoch with predecessor references.

Every delta carries the roster record with the operations it authorizes. A delta missing its required roster is rejected as a whole and can be re-offered with the roster attached. Validators then use the same signed authority to evaluate all included operations.

The exporter's current epoch is the highest owner-signed roster whose base checkpoint it has merged. Record that roster's digest with the checkpoint and attribution evidence. Conflicting successor rosters at the same epoch number block export until the owner signs a resolution naming the competing rosters.

An offline client reports the epoch last merged into its journal. It retains earlier-epoch edits locally. An authorized current member applies those edits to the current checkpoint and signs them, preserving conflict and source evidence. The export and certification workflow verifies the epoch and roster reference it accepts and records its observation. UI status distinguishes a local offline checkpoint from a verified shared checkpoint.

### Checkpoints and compaction

A checkpoint contains canonical entity state, the included operation frontier, conflicts, tombstones, membership epoch and predecessor references. Publication requires structural validation and resolved conflicts throughout the exported content and its dependencies. Retain the signed checkpoint and source-to-artifact mapping for [review and certification under 4.7 SDUI commerce and attribution](07-commerce.md).

Coalesce local edits deterministically into bounded checkpoint batches before they become shared signed operations. Shared operations retain their identity. Compaction verifies which operations the source checkpoint includes, then creates an owner-signed successor checkpoint and epoch. Preserve predecessor references and required audit evidence under the project's retention policy.

Use the foundation's operation journal for checkpoint submission and uncertain-outcome reconciliation. The authoring client shows checkpoint outcomes and retries publication through durable host operations. Track a pending save until a verified readback of the expected digest marks it as shared. Local project drafts, mutable shared project state and exact published archives have separate identities and retention rules.

### Capacity and traffic

Set a signed, versioned capacity profile with bounded roster size, entity count, encoded state size, causal metadata, tombstones, conflicts, batch bytes and operations. Start with a reserved allowance of 2,048 operations and 1 MiB per roster member per epoch. Define which encoded bytes consume that allowance and reserve space for roster and checkpoint metadata.

The admission and conflict-retention rules must be merge-closed. Any two valid states must merge within the contract's complete encoded-size limit, including divergent histories signed by the same member. Specify deterministic handling of over-budget or conflicting histories and preserve their required audit evidence. Prove these rules with codec and merge fixtures before selecting the wire-format release.

Advance a validated checkpoint or split a project before exhausting the published capacity. Bound save batches and enforce update-rate limits in the client and service. Contract validation uses deterministic state rules. The client and service own wall-clock rate enforcement.

Measure payload bytes, protocol overhead and update counts against the published authoring profile. Mobile authoring also inherits the [cellular budgets in 1.10 Thin-peer role and cellular data budgets](../1-freenet-mobile-appkit/10-thin-peer.md). The [traffic issue #5153](https://github.com/freenet/freenet-core/issues/5153) and [update-volume issue #5050](https://github.com/freenet/freenet-core/issues/5050) are source context for this batching requirement. Record the measured profile with the checkpoint release.

### Checkpoint acceptance

- Real contract tests cover associative, commutative and idempotent merge, repeated/grouped deltas and full-state/delta equivalence through [fdev conformance](https://github.com/freenet/freenet-core/pull/5344) and its [merge properties](https://github.com/freenet/freenet-core/issues/5320).
- Test malformed signatures, cross-project replay, missing rosters, successor-roster conflicts, stale epochs and removal of a member with offline edits.
- Concurrent writes, moves and deletions preserve conflicts. Resolution and restoration produce a valid checkpoint with intact evidence.
- Test broken references, cycles, conflicting IDs and maximum encoded size, including two divergent valid states from one member.
- Thousands of local edits produce bounded save batches. Restart and uncertain-submission tests recover the journal and verify the saved digest.
- Compaction preserves required predecessor evidence, and deterministic export reproduces the same files from the checkpoint and pinned inputs.
- Single-author and offline checkpoint workflows pass.

## Checkpoint evidence

This plan adds the checkpoint evidence path to the attribution service for projects that select visual authoring. It sits beside the [repository evidence path in 4.7 SDUI commerce and attribution](07-commerce.md#sdui-artifact-integration). A release that combines repository and visually authored content uses both paths.

| Authoring path | Reviewed source and build evidence |
| --- | --- |
| Visual authoring | Exact signed checkpoint from the [durable checkpoint protocol](#durable-checkpoint-protocol), project identity, membership epoch and roster digest, author-operation evidence, accepted contribution references, and pinned exporter version and inputs |

The checkpoint evidence path maps its reviewed inputs to the same digests, versions, artifacts and capability IDs as the repository evidence path in 4.7 SDUI commerce and attribution. Changed checkpoint content creates a new evidence revision and requires renewed review.

The attribution service owns these checks and their signed decisions. The editor submits evidence and displays the result.

- Register a checkpoint author by verifying a signed request, the author's project membership and control of the signing key. Bind the verified author key to the contributor's `ActorId` lineage and retain the registration evidence.
- Verify the project identity, membership epoch, owner-signed roster and roster digest against the exact signed checkpoint. Verify included author-operation signatures, causal references and the operation frontier against that checkpoint and the membership authority for each operation.
- Bind contributor claims and co-contributor signatures to that exact evidence revision. Record the verified checkpoint and roster digests with the acceptance and source-to-artifact mapping. Apply the existing product-scoped review, role-separation and challenge rules through [3.2 Attribution workflow and allocation weights](../3-attribution-remuneration-payment/02-attribution.md).
- Require renewed review when checkpoint content changes. Preserve the signed evidence behind earlier accepted revisions.

A checkpoint author's recovery profile follows the [contributor recovery profile in 4.7 SDUI commerce and attribution](07-commerce.md#contributor-recovery-profile). It names the authorized recovery authority and project/identity evidence it accepts. Project membership establishes project access.

## Acceptance

- A new author creates, previews, validates and publishes a reader-only project and a custom web project with embedded SDUI.
- Playwright flows cover create, edit, undo, conflict resolution, import, validation, restart recovery and publish-and-open using released readers.
- Thousands of typing and drag edits coalesce into batches within fixed byte, operation and update-rate budgets. A crash preserves the acknowledged local journal.
- The checkpoint suite above passes with real contract execution and offline/reconnect cases.
- Repeated export of the same checkpoint and pinned inputs produces identical files and source mappings.
- Representative EVY imports retain supported behavior and report every unsupported item with a repair path.
- Browser preview agrees with real delegate fixtures.
- The builder itself passes keyboard and screen-reader tests, and preview recordings and reports redact protected data.
- Checkpoint certification verifies registered author lineage, project identity, epoch, roster signatures/digest and included operation signatures against the exact checkpoint. Substituted checkpoints, unauthorized authors and invalid successor lineage fail.
- Changed checkpoint content requires a new evidence revision and renewed review.
- Certification detects changed screens, actions, schemas, reader builds and domain artifacts against the reviewed checkpoint mapping.
