# 4.1 SDUI format

## Repositories

| Repository | Role | Work in this plan |
| --- | --- | --- |
| `freenet-sdui` | Created | JSON Schema for `ui/sdui/ui.json`<br>Generated TypeScript, Rust, Swift and Kotlin models<br>Validator, expression evaluator, schema comparison and shared fixtures |
| [evy](https://github.com/EVY-Platform/evy) | Used | [Flow, page and row schemas](https://github.com/EVY-Platform/evy/tree/dev/types/schema/sdui) as the source for 8 components |
| [river](https://github.com/freenet/river) | Used | Room list, conversation, members and "Invite member" screens as the fixtures |

## Purpose

This plan defines the screen document `ui/sdui/ui.json`, which describes an app's screens as data. It owns the schema, values and bindings, the components River's screens use, navigation, accessibility, language, limits and compatibility rules. Carol describes River's "Invite member" sheet in this format. Alice opens the sheet from the member list of "Skate club" to invite Bob. The document sits under `ui/sdui/` in a release bundle from [1.4 Application bundles](../1-freenet-mobile-appkit/04-bundles.md#the-archive-and-its-definition). Copying an invite link needs no permission. The host writes it under the rules in [Shell-bridge messages in 1.3 Single-application host](../1-freenet-mobile-appkit/03-host.md#shell-bridge-messages).

## Screen documents

The format adapts EVY's [flow, page and row schema](https://github.com/EVY-Platform/evy/blob/dev/types/schema/sdui/evy.schema.json), which already has rows with triggers, sheets and `visible` conditions. This plan changes 4 parts of it.

| Part | EVY today | This plan |
| --- | --- | --- |
| IDs | UUIDs for flows, pages and rows | Stable string IDs, such as `invite-member` |
| Values | Brace strings, such as `{formatCurrency($datum.price)}` | Typed value objects, see [Values and expressions](#values-and-expressions) |
| Navigation | `{navigate(<flow UUID>,<page UUID>,{id: ...})}` and `{show(<row UUID>)}` | Routes with typed parameters, see [Navigation](#navigation) |
| Writes | Inline `{create(evy.messages, ...)}` | A declared action ID, such as `copy-invite-link` |

Carol's sheet carries River's [invite modal](https://github.com/freenet/river/blob/main/ui/src/components/members/invite_member_modal.rs) into this format. The rows for the invite code and the invitation message repeat the pattern of the link rows.

```jsonc
{
  "format_version": "1.0",                                         // major and minor, see Compatibility
  "routes": [{
    "id": "invite-member",                                         // route ID, stable across releases
    "presentation": "sheet",                                       // opens over the members page, as River's modal does
    "params": { "room": "string" },                                // base58 owner key of "Skate club"
    "title": { "literal": "Invite Member" },                       // literal, shown as written, braces stay text
    "actions": { "open": { "action": "new-invitation",             // declared action, runs when the sheet opens
                           "args": { "room": { "ref": "param:room" } } } },
    "rows": [
      { "id": "invite-link", "type": "input",                      // EVY's input row, read-only without a destination
        "source": { "ref": "view:invitation.url" } },              // reference to an output of a declared view
      { "id": "copy-link", "type": "button",                       // label is an expression, "Copied!" after a copy
        "label": { "expr": ["if", { "ref": "local:copied" }, "Copied!", "Copy Link"] },
        "actions": { "tap": { "action": "copy-invite-link" } } },  // declared action that writes the clipboard
      { "id": "close", "type": "button", "label": { "literal": "Close" },
        "actions": { "tap": { "close": true } } }                  // navigation that closes the sheet
    ]
  }]
}
```

freenet-sdui generates the TypeScript, Rust, Swift and Kotlin models from the schema. It ships one validator that every tool and reader runs. An error names the component ID and schema path and never includes field values. The validator limits a document to 256 KiB, a route to 500 components, nesting to 16 levels and an expression to 1,000 steps. Readers render 50 list rows at a time, so a long "Skate club" history scrolls in windows. These are starting values, set from River's four screens.

## Values and expressions

Every bound property holds one of three value objects. A `literal` is shown as written. A `ref` reads one value, and its prefix names the source. An `expr` is an operator followed by its arguments, where a JSON string is a literal and a `ref` object reads a value. Values are strings, booleans, integers within 2^53, lists, objects and null. A timestamp is integer milliseconds since the Unix epoch in UTC. A missing field reads as null.

| Prefix | Reads | Example |
| --- | --- | --- |
| `param:` | A route parameter, fixed for one route entry | `param:room` |
| `view:` | An output of a declared view | `view:invitation.url` |
| `form:` | A form field value | `form:message.text`, Bob's unsent "Skate session Saturday?" |
| `local:` | Display state for the open page | `local:copied` |

Expressions use `or`, `if`, `eq`, `not`, `concat`, `count` and `time`. They read references and change nothing. River's fallback room name is `["or", { "ref": "view:room.name" }, "this chat room"]`.

## Components

freenet-sdui adapts 8 of EVY's 21 [row schemas](https://github.com/EVY-Platform/evy/tree/dev/types/schema/sdui/definitions), pinned to one EVY commit.

| Component | River use |
| --- | --- |
| `heading`, `text` | "Rooms" above the [room list](https://github.com/freenet/river/blob/main/ui/src/components/room_list.rs), and its empty state "Create a room or join one with an invite code." |
| `button` | "Invite Member", "Copy Link", "New Invitation", "Close". It gains an `icon` for the close button at the top of the invite modal |
| `input`, `text_area` | The read-only "Invitation link:", the message box "Type your message..." |
| `list_item` | One room, one member such as "Invited by You", one message. It gains a `detail` text for the message time |
| `vertical_container`, `horizontal_container` | Page layout, "Copy Link" beside the link |

## Navigation

A route has a stable ID, typed parameters and a presentation, `page` or `sheet`. A route's `open` trigger runs an action when the route opens. A tap runs an action, opens a route or closes one. Alice taps "Invite Member" in the member list, which runs `{ "open": "invite-member", "args": { "room": { "ref": "param:room" } } }`. "Close" runs `{ "close": true }`. An unknown route ID or a parameter of the wrong type returns the `route_not_found` error, and the reader stays on the current page.

## Accessibility and language

- The document names stack direction, alignment, size categories, theme tokens and each control's purpose and label. Each reader maps these to its platform's layout, colors and fonts. It applies the OS or browser settings for text size, contrast, reduced motion and right-to-left layout.
- Labels reach ARIA in the browser, SwiftUI accessibility on iOS and Compose semantics on Android. Reading order is row order, and a `heading` row reads as a heading. A button with an `icon` and no label needs an `a11y_label`, such as "Close" on the invite modal's icon button.
- Strings are literals, and River ships English only. The `time` operator formats with the locale and time zone of the phone or browser, as River's [`format_time_local`](https://github.com/freenet/river/blob/main/ui/src/util.rs) does.

## Compatibility

`format_version` is major and minor. A reader loads any document with its major version. It ignores properties from a newer minor version. It renders an unknown component type through that component's `fallback`, a component the reader knows. A component with no usable fallback stops its route, and the reader shows the minimum reader version it needs. Each bundle carries its own web reader, so these rules matter most for the native readers built into EVY on iOS and Android. freenet-sdui's schema comparison classifies each change between two schema versions as minor or major.

| Change in a new schema version | Class | Example |
| --- | --- | --- |
| Add an optional property, or a component type with a fallback | Minor | `search`, with `input` as its fallback |
| Add a required property, remove a property or component, or change a property's type | Major | `detail` on `list_item` becomes an object |

## Acceptance

- The fixtures for the 8 components, River's four screens and the "Invite member" sheet validate against the schema.
- The generated Swift models on iOS and Kotlin models on Android decode and re-encode every fixture to the same JSON, as do the TypeScript and Rust models.
- Validation rejects unknown fields, unknown component types without a fallback, an icon button without a label or `a11y_label`, and documents over any limit. Each error names the component ID and schema path without field values.
- Value fixtures cover null, missing fields, the integer range, timestamps and each operator. With a fixed locale, time zone and current time, the evaluator gives the same result in TypeScript, in Swift on iOS and in Kotlin on Android.
- The schema comparison classifies each fixture change pair as the compatibility table says. A reader fixture for format version 1.0 renders a format version 1.1 document through its fallbacks.
