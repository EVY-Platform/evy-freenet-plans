# 4.1 SDUI format and compatibility

Milestone 4 (SDUI) adds screens described as data. A browser, iOS or Android reader turns those descriptions into controls. Applications choose SDUI for complete interfaces or selected pages.

Prerequisites:

- [1.4 Application bundles](../1-freenet-mobile-appkit/04-bundles.md)
- [1.3 Single-application host](../1-freenet-mobile-appkit/03-host.md)
- [2.2 Multi-application sessions and authority](../2-evy-mobile-app/02-sessions.md)
- [2.3 Installation and updates](../2-evy-mobile-app/03-installation-and-updates.md)
- [2.4 Identity, permissions and device access](../2-evy-mobile-app/04-permissions.md)
- [1.6 Application protocols, data and operations](../1-freenet-mobile-appkit/06-data-and-operations.md)

This plan owns the screen format, component catalogue, navigation, accessibility and compatibility rules. The [milestone 4 (SDUI) scope and release gates](../README.md#4-sdui) cover delivery boundaries and the required mobile foundation.

## Repositories

| Repository | Role | Work in this plan |
| --- | --- | --- |
| `freenet-sdui` | Created | Versioned JSON Schema, generated TypeScript, Rust, Swift and Kotlin models, value model and display expressions, component catalogue, navigation, accessibility, value and formatting fixtures and schema comparison |
| [evy](https://github.com/EVY-Platform/evy) | Used | The 21 row-type schemas as source material for the catalogue |

## Format and compatibility

Publish versioned JSON Schema and generated TypeScript, Rust, Swift and Kotlin models. A screen document describes flows, pages, stable component IDs, relationships, routes, themes and language resources. It names required component versions and host capabilities.

Define these rules in the schema and shared fixtures:

- Values explicitly select a literal, typed reference or bounded expression, as [Values and expressions](#values-and-expressions) defines. Braces inside a literal remain text.
- Each component declares property types, binding slots, events, accessible meaning, and loading, empty, error and disabled states.
- Required unknown components or incompatible versions block the affected page before activation. Optional components carry a validated safe fallback with compatible bindings and events.
- Unknown executable behavior fails validation. Optional extension fields use declared namespaces and versions.
- Publish a schema comparison that classifies additions, removals and type changes. Required features and exact supported versions determine compatibility.
- Validate at authoring, publication and load time. Errors identify a component or schema path while private values stay redacted.

## Values and expressions

Define a common value model for null, missing, booleans, integers, decimals, strings, bytes, timestamps, durations, lists and objects. Shared fixtures fix numeric ranges, decimal encoding, overflow, comparisons, conversions and missing-value behavior. Host-supplied time, randomness, locale and time zone have deterministic substitutes in tests.

Every binding explicitly selects a literal, reference or expression. References address a declared view, immutable route parameters, a form value or temporary display state. Display expressions provide presence checks, fallbacks, boolean and string comparisons, and locale-aware formatting. Evaluation is side-effect-free. Bound input size, nesting and evaluation steps.

Proposed binding example:

```json
{
  "id": "send-button",
  "type": "appkit.button",
  "title": { "literal": "Send" },
  "actions": {
    "tap": {
      "action": "river.sendMessage",
      "args": {
        "room": { "ref": "param:roomOwner" },
        "text": { "ref": "local:draft.text" }
      }
    }
  }
}
```

The final schema release fixes the serialized component names and reference syntax.

## Components and source catalogue

Use the 21 EVY row types as the v1 component catalogue. The linked schemas are source material for adaptation. The Freenet schemas, readers and adapters are proposed milestone 4 (SDUI) work. Pin source revisions when generating the release catalogue.

| Group | Source schemas |
| --- | --- |
| Content | [Text](https://github.com/EVY-Platform/evy/blob/dev/types/schema/sdui/definitions/text.schema.json), [Heading](https://github.com/EVY-Platform/evy/blob/dev/types/schema/sdui/definitions/heading.schema.json), [Button](https://github.com/EVY-Platform/evy/blob/dev/types/schema/sdui/definitions/button.schema.json), [TextAction](https://github.com/EVY-Platform/evy/blob/dev/types/schema/sdui/definitions/text_action.schema.json), [TextExpand](https://github.com/EVY-Platform/evy/blob/dev/types/schema/sdui/definitions/text_expand.schema.json) |
| Input | [Input](https://github.com/EVY-Platform/evy/blob/dev/types/schema/sdui/definitions/input.schema.json), [TextArea](https://github.com/EVY-Platform/evy/blob/dev/types/schema/sdui/definitions/text_area.schema.json), [Dropdown](https://github.com/EVY-Platform/evy/blob/dev/types/schema/sdui/definitions/dropdown.schema.json), [InlinePicker](https://github.com/EVY-Platform/evy/blob/dev/types/schema/sdui/definitions/inline_picker.schema.json), [TextSelect](https://github.com/EVY-Platform/evy/blob/dev/types/schema/sdui/definitions/text_select.schema.json), [Calendar](https://github.com/EVY-Platform/evy/blob/dev/types/schema/sdui/definitions/calendar.schema.json), [TimeslotPicker](https://github.com/EVY-Platform/evy/blob/dev/types/schema/sdui/definitions/timeslot_picker.schema.json) |
| Collections | [InputList](https://github.com/EVY-Platform/evy/blob/dev/types/schema/sdui/definitions/input_list.schema.json), [ListItem](https://github.com/EVY-Platform/evy/blob/dev/types/schema/sdui/definitions/list_item.schema.json), [Search](https://github.com/EVY-Platform/evy/blob/dev/types/schema/sdui/definitions/search.schema.json), [PhotoGallery](https://github.com/EVY-Platform/evy/blob/dev/types/schema/sdui/definitions/photo_gallery.schema.json) |
| Layout | [VerticalContainer](https://github.com/EVY-Platform/evy/blob/dev/types/schema/sdui/definitions/vertical_container.schema.json), [HorizontalContainer](https://github.com/EVY-Platform/evy/blob/dev/types/schema/sdui/definitions/horizontal_container.schema.json), [TabContainer](https://github.com/EVY-Platform/evy/blob/dev/types/schema/sdui/definitions/tab_container.schema.json) |
| Device | [Map](https://github.com/EVY-Platform/evy/blob/dev/types/schema/sdui/definitions/map.schema.json), [SelectPhoto](https://github.com/EVY-Platform/evy/blob/dev/types/schema/sdui/definitions/select_photo.schema.json) |

Browser media, including map tiles, uses bundled bytes or content served by the node under Core's sandbox policy. External asset storage needs its own supported service and permission profile.

## Navigation

Routes have stable IDs and typed parameters. Readers support opening or replacing a page, sheets, full-screen views and tab selection. Native navigation emits the same semantic events used by browser tests. The host controls external URL operations and deep-link admission.

Validate restored routes and parameters against the active release. Unknown routes return a defined navigation error. Deep links supply navigation arguments. [4.6 SDUI data and operation presentation](06-data.md) owns form snapshots, draft saving and recovery.

## Accessibility and language

| Document supplies | Reader supplies |
| --- | --- |
| Stack direction, alignment and size categories | Platform layout and spacing |
| Named window size classes | Resizing behavior |
| Safe-area and keyboard intent | Platform insets and input handling |
| Named theme tokens | Colors, fonts, radii and shadows |
| Control purpose, label and reading order | Accessible HTML, SwiftUI accessibility or Compose semantics |

Require accessible labels for non-text controls. Specify headings, lists, inputs, errors and live updates. Preserve keyboard focus through updates and navigation. Support large text, high contrast, reduced motion and right-to-left layout. Compare control meaning and behavior across platforms while allowing platform layout differences.

Strings use literals or keys in verified language files. The host supplies locale and time zone. Resolve a key through the requested locale, its language fallback, then the declared default locale. Development shows a missing-key diagnostic. Production uses declared fallback text. Machine translation follows an explicit user or application policy.

## Limits and failure handling

Set versioned limits for document bytes, component count, nesting, text and media sizes, expression work, list windows and update frequency. Window long lists. Stop an excessive update before applying it and report the limit reached. Required malformed components block the page. Optional malformed components use their validated fallback. Schema and action errors block publication or page activation.

[4.9 SDUI migration and conformance](09-migration-and-conformance.md) owns activation and upgrade tests.

## Acceptance

- Each catalogue component has published schema, event, fallback and accessibility fixtures that validate against the schema.
- Shared value fixtures cover null, missing, numeric ranges, decimal encoding, overflow, comparisons and conversions, and validate against the schema.
- Shared formatting fixtures fix locale, time zone and current time.
- Schema validation rejects unknown fields, unknown component types, invalid required components and incompatible schemas.
