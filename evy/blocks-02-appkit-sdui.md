# AppKit SDUI

**Parent plan:** [AppKit + EVY](README.md).

AppKit SDUI is a portable, versioned UI description: screens defined as data, rendered by web, SwiftUI, and Jetpack Compose readers. It starts from EVY's existing JSON Schema model of flows, pages, rows, bindings, and actions, and removes the EVY- and marketplace-specific assumptions. The format preserves one UI *meaning* across platforms, not identical pixels; it updates live through a Freenet contract; and accessibility, validation, and failure behaviour are part of the protocol, not renderer courtesy.

## 1. Document model

Retain the useful EVY hierarchy:

```text
AppDefinition
  metadata
  theme
  flows[]
    pages[]
      rows[]
```

A flow is a user journey, a page is one screen, and a row/component is the smallest renderable unit. Persist IDs and relationships explicitly so components can be edited independently.

## 2. Standard components

Start with a deliberately small v1 set:

```text
Text, Heading, Button, Image, Icon
Input, TextArea, Toggle, Dropdown, DateTime
List, Search, Card
Vertical, Horizontal, Tabs, Spacer, Divider
MapPlaceholder, FilePicker, PhotoPicker
```

Every component defines its semantic purpose, required and optional properties, supported bindings and action triggers, accessibility role/label behaviour, empty/loading/error/disabled states, and fallback behaviour on readers with limited support.

Do not add a component merely to reproduce a specific EVY screen. Product-specific presentations should usually be compositions or namespaced extensions.

## 3. Extensions

Use namespaced component types:

```text
appkit.text
appkit.list
marketplace.price
river.member-list
```

The release record declares required extensions ([Foundation §4](blocks-01-appkit-foundation.md#4-capabilities-and-extensions) sets the compatibility rules). Readers never run code downloaded from an SDUI document: an extension is an installed, signed renderer package, or a composition of standard components. The [runtime](blocks-03-appkit-runtime.md) applies the same rule to actions.

## 4. Bindings and actions

The SDUI schema references, but does not implement, the protocols in [AppKit Runtime](blocks-03-appkit-runtime.md) and [Data Bindings](blocks-04-appkit-data-bindings.md).

Example:

```json
{
  "id": "send-button",
  "type": "appkit.button",
  "title": "Send",
  "visible": "{length(local:draft.message) > 0}",
  "actions": {
    "tap": [
      {
        "run": "message.send",
        "args": {
          "thread": "{param:threadId}",
          "body": "{local:draft.message}"
        }
      }
    ]
  }
}
```

Keep values typed in the protocol. EVY's current string-heavy format can be supported by a migration reader, but v1 should distinguish literal strings, binding references, expressions, numbers, booleans, lists, and objects.

## 5. App-definition contract

The contract stores normalized entities and a protocol version, not one nested JSON blob:

```text
flows: Map<FlowId, Flow>
pages: Map<PageId, Page>
rows: Map<RowId, Row>
themes: Map<ThemeId, Theme>
relationships: ordered lists using stable item IDs
```

Updates are operations:

```text
CreateEntity
SetProperty
InsertRelationshipItem
MoveRelationshipItem
RemoveRelationshipItem
TombstoneEntity
RestoreEntity
```

Each operation has a stable ID, author, causal parent information where required, and validation rules. The merge must be associative, commutative, and idempotent — the merge laws Core is starting to enforce with removal as the sanction ([freenet-core#5320](https://github.com/freenet/freenet-core/issues/5320)); every contract in these plans passes `fdev` conformance from its first commit ([README item 7](README.md)). Property conflicts use a documented deterministic rule and remain inspectable by the builder.

## 6. Layout and platform adaptation

The protocol specifies intent rather than absolute screen coordinates:

- stack direction, spacing, alignment, emphasis, and size categories;
- responsive breakpoints expressed as named size classes;
- platform-safe areas and keyboard handling delegated to readers;
- native navigation and controls preferred where semantics match;
- optional visual tokens for colour, typography, radius, and elevation.

The builder may preview common device classes, but cannot promise pixel identity across platforms.

## 7. Accessibility and localisation

Require accessible labels for non-text controls and define heading, list, button, input, error, and live-region semantics. Readers map these to ARIA, SwiftUI accessibility, and Android semantics.

Visible strings can be literals for simple apps or localisation keys backed by a signed language bundle. Readers define locale fallback order. Do not use machine translation implicitly at runtime without user or app policy.

## 8. Validation and failure handling

Validation occurs at four points:

1. builder edit time;
2. before publishing an operation;
3. inside the app-definition contract where feasible;
4. in the reader before rendering.

A malformed required component blocks the affected page with a useful error. A malformed optional component may render a safe placeholder. Readers never interpret malformed actions as executable text.

## 9. Code generation and tooling

- JSON Schema files are the public specification;
- a deterministic generator emits TypeScript, Rust, Swift, and Kotlin models;
- generated code is checked into release artifacts, not hand-edited;
- a schema diff tool labels changes as compatible, conditionally compatible, or breaking;
- fixture apps cover simple forms, lists, navigation, messaging, and marketplace flows;
- a visual playground runs without a Freenet network for component development.

## 10. Migration from EVY

1. classify current row types as standard, extension, or deprecated;
2. add typed values while retaining a compatibility parser for old strings;
3. move existing action parsing behind the new runtime interface;
4. convert flat EVY records to normalized AppKit entities;
5. run old and new renderers against shared fixtures;
6. migrate builder output only after semantic parity is proven.

The [App Builder's importer](blocks-07-app-builder.md#11-migration-from-evy) is the tool that applies this strategy to existing EVY applications.

## 11. Delivery

| Phase | Delivers | Done when |
| --- | --- | --- |
| 1. EVY-neutral schemas | Flows, pages, rows, themes, actions, and bindings without product fields | No product-specific database or payment concept remains in the protocol |
| 2. Protocol v1 | Required fields, component semantics, accessibility, layout, extensions | Unknown required components fail safely and visibly |
| 3. Edit operations | Deterministic insert, move, update, and delete operations | Concurrent builder edits converge to the same definition |
| 4. Platform models | TypeScript, Rust, Swift, and Kotlin types and validators | One fixture application passes schema validation in every language |
| 5. Conformance fixtures | Expected semantic output for every component and edge case | Web, iOS, and Android readers agree on navigation, bindings, actions, and error states |
| 6. App-definition contract | Readers subscribe to versioned UI state and deltas | An app updates its UI contract and active readers receive the change; the contract passes `fdev` conformance |

References:

- [EVY SDUI source repository](https://github.com/EVY-Platform/evy)
- [Freenet contracts](https://freenet.org/build/manual/components/contracts/)
