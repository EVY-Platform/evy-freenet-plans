# App Builder

**Parent plan:** [AppKit + EVY](README.md). **Depends on:** [AppKit Foundation](blocks-01-appkit-foundation.md), [SDUI](blocks-02-appkit-sdui.md), [Runtime](blocks-03-appkit-runtime.md), [Data Bindings](blocks-04-appkit-data-bindings.md), [Web Reader](blocks-05-appkit-web-reader.md). **Consumes, built separately:** [Product attribution app](../attribution/README.md).

The App Builder is a visual tool for creating, previewing, validating, and publishing AppKit applications — a non-expert assembles screens, flows, data bindings, and actions without editing code. It begins from EVY's React builder but targets neutral AppKit protocols and Freenet contracts.

The builder is one authoring tool, not the authority over the protocol: hand-written definitions and other builders remain valid, and every record it produces can be created and verified by another client.

## 1. Technology and repository

Use a standalone TypeScript/React/Vite repository, with Bun for development and tests. Reuse EVY's drag/drop canvas, row/component factories, action editor, design system, and generated schema approach where they match AppKit.

```text
freenet-app-builder/
  app/
    shell/  canvas/  catalogue/  configuration/
    bindings/  actions/  preview/  publishing/  collaboration/
  packages/
    project-model/
    migration-evy/
  tests/
```

The builder imports released `freenet-appkit` packages; it does not copy schema files.

## 2. Project model

A project includes:

```text
product identity and metadata
flows/pages/components
routes and parameters
theme and localisation
logical contract/delegate bindings
required/optional extensions and permissions
sample data and preview scenarios
extension dependencies
capability catalogue
product proposals, contributor claims, and attribution drafts
```

Secrets, private keys, and payment processor credentials never enter the project document.

## 3. Editing model

Every edit produces an operation with stable IDs:

```text
CreateEntity
SetProperty
InsertChild
MoveChild
RemoveChild
TombstoneEntity
RestoreEntity
```

The UI applies it optimistically, stores it locally, then submits it to the [app-definition contract](blocks-02-appkit-sdui.md#5-app-definition-contract). Undo creates an inverse operation where safe rather than deleting history. Conflicts show both values and an explicit resolution action.

## 4. Component catalogue and configuration

Generate configuration controls from AppKit JSON Schemas, with curated custom editors for complex fields: bindings and selectors, action pipelines, routes and parameters, message payload types, responsive layout, accessibility labels, and extension dependencies.

The builder explains terms in plain language and shows the underlying technical reference only in an advanced view.

## 5. Data and capability design

A user first adds a logical data source or delegate, then binds components to it. The builder reads a public schema/descriptor supplied by the domain package and offers compatible fields and actions.

Example:

```text
Data source: Marketplace listings
Kind: Contract
Readable views: list, listingById
Allowed updates: createListing, updateListingStatus
```

Users cannot invent arbitrary SQL-like queries: bindings follow the [declared-views rule](blocks-04-appkit-data-bindings.md#3-contract-provider-and-declared-views). The builder can generate local filters for small loaded collections or require a declared index/view for larger data.

## 6. Preview

Embed the released Web Reader with a `MemoryProvider`, as [Web Reader §7](blocks-05-appkit-web-reader.md#7-builder-preview) specifies. Preview modes:

- responsive web sizes plus iOS and Android semantic frames;
- light/dark/high-contrast themes;
- offline, loading, stale, empty, error, and permission-denied states;
- sample identity/message/marketplace data;
- recorded user-flow playback.

Mobile frames approximate layout only. Final native conformance runs through actual SwiftUI and Compose test applications.

## 7. Validation

Continuous validation checks:

- schema and component requirements;
- unknown actions, functions, and extensions;
- missing data bindings and routes;
- capability and permission declarations;
- unreachable pages and broken references;
- accessibility labels and form errors;
- unsupported reader versions;
- oversized inline data or unbounded collection assumptions;
- attribution readiness: allocation totals, complete acceptance chains (verdicts, size estimates and any tiebreak, closed challenge windows), and snapshot/signature checks as defined by the [enforced workflow](../attribution/README.md#4-enforced-workflow).

Errors block publishing; warnings require acknowledgement or policy approval.

## 8. Attribution workflow

The builder hosts the proposal, review, size-validation, and challenge flows of the [attribution app](../attribution/README.md#4-enforced-workflow) under the client rules its [client-integration section](../attribution/README.md#11-client-integration) sets: every check lives in the contract, previews match the ledger's arithmetic exactly, and units display as non-currency weights.

## 9. Publishing

Publishing creates:

1. validated app-definition state or artifact;
2. optional web container using the AppKit Web Reader;
3. signed [release record](blocks-01-appkit-foundation.md#2-release-record) and artifact hashes;
4. attribution policy version, capability catalogue, and snapshot references, plus activated acceptance IDs;
5. optional Atlas discovery metadata.

The builder sends signing requests to a delegate/maintainer tool. It never reads the private product key.

## 10. Collaboration and offline use

The builder stores projects locally and can edit offline. On reconnect it merges operations with the app-definition contract. Show presence only as an optional hint; correctness depends on operation merging, not a central collaboration server.

Large binary assets use content references and upload progress, not inline base64 fields.

## 11. Migration from EVY

Build an importer that applies the [SDUI migration strategy](blocks-02-appkit-sdui.md#10-migration-from-evy):

- reads EVY flows/pages/rows and converts resource references to AppKit logical bindings;
- converts string expressions and actions to typed syntax;
- maps each row type to a standard or namespaced extension component;
- reports unsupported behaviour rather than silently dropping it;
- preserves stable IDs where possible.

## 12. Delivery

Testing: Playwright tests for creation, editing, undo, conflict, validation, and publishing; shared AppKit fixture projects; real Freenet contract tests for collaborative/offline operations; accessibility testing of the builder itself; publish-and-open tests using released readers; migration tests against representative EVY applications; attribution tests for invalid totals, incomplete chains, size tiebreaks, challenges, and conflicting releases.

| Phase | Delivers | Done when |
| --- | --- | --- |
| 1. Extract EVY builder core | Neutral canvas, row catalogue, configuration, and action editor | No EVY product field remains in the core editing model |
| 2. Adopt AppKit schemas | Generated controls and validation from released definitions | The builder validates against released packages, never copied schemas |
| 3. Binding and capability editor | Contracts, delegates, local state, parameters, and messages | Unbounded query assumptions are blocked at edit time |
| 4. Operation-based persistence | Offline/collaborative edits through the app-definition contract | Concurrent edits converge; conflicts are visible with explicit resolution |
| 5. Real reader preview | Web reader embed plus mobile semantic frames | Preview uses the released reader, not a separate approximation |
| 6. Publishing workflow | Build, validate, attribute, sign, publish | A new user publishes a simple app without editing code; it opens in web, iOS, and Android readers; releases activate accepted proposals with a verified snapshot |
