# 4.5 SDUI actions and delegate protocols

Execute bounded declared actions and define an optional typed domain convention over Freenet delegate messages.

Prerequisites:

- [1.2 Embedded node and mobile SDK](../1-freenet-mobile-appkit/02-sdk.md)
- [1.6 Application protocols, data and operations](../1-freenet-mobile-appkit/06-data-and-operations.md)
- [1.3 Single-application host](../1-freenet-mobile-appkit/03-host.md)
- [2.2 Multi-application sessions and authority](../2-evy-mobile-app/02-sessions.md)
- [2.4 Identity, permissions and device access](../2-evy-mobile-app/04-permissions.md)
- [4.2 SDUI bundles and publication](02-bundles.md)
- [4.4 SDUI identity and permissions](04-identity.md)

This plan owns the executor, its step versions and the typed request/result convention. Application protocols and SDK delegate messaging remain foundation interfaces that custom applications use directly.

## Repositories

| Repository | Role | Work in this plan |
| --- | --- | --- |
| `freenet-sdui` | Modified | Declared-action executor, step versions, typed delegate convention codecs and the River adapter fixture |
| [freenet-core](https://github.com/freenet/freenet-core) | Modified | `crates/mobile` gains the executor host interface: authority rechecks, journal integration and budget enforcement |
| [atlas](https://github.com/freenet/atlas) | Used | Domain operation run through a declared action and custom controls |
| [river](https://github.com/freenet/river) | Used | Concrete signing protocol behind the adapter fixture |

## Convention boundary

[1.6 Application protocols, data and operations](../1-freenet-mobile-appkit/06-data-and-operations.md) owns Core message formats, caller attestation, autonomous events and River's concrete signing fixtures. This plan adds schemas and typed adapters for generic readers. A correlated action completion requires its matching request and active session. Unsolicited output uses a separate validated event path through the foundation's authorized delivery interface.

## Declared actions

Definitions in `ui/sdui/actions/` name resources, input/output schemas and required step versions. Allow bounded sequences, conditional branches and action composition. Bound the total expanded work across nested calls. A release profile sets numerical limits for steps, call depth, input/output bytes, expression depth, concurrent requests and elapsed time.

| Step | Result or effect |
| --- | --- |
| Invoke a declared action | Typed child result within the parent action's budget |
| Read or observe a resource | Host snapshot or owned view demand through [4.6 SDUI data and operation presentation](06-data.md) |
| Call a delegate | Typed projection, prepared operation or structured error |
| Submit prepared data | Foundation operation handle and subsequent outcome events |
| Read, write or observe local data | Authorized record result from the selected storage adapter |
| Use a device or service | Scoped handle, typed result, denial or unavailable result |
| Obtain time or randomness | Host-supplied value with deterministic test substitutes |
| Cancel or close | Release cancellable work and reader demand through the host |

A new composition of supported steps arrives in a bundle. A new primitive requires a released executor implementation. Native executors update with the host. Bundled browser executors update through verified reader packaging and declare the host capabilities they need.

Definitions, schemas and selected delegate artifacts come from one verified release. Before executing a protected step, the host rechecks session authority, grants and the concrete target. The executor uses the [journal in 1.6 Application protocols, data and operations](../1-freenet-mobile-appkit/06-data-and-operations.md) for operation identity, exact submitted bytes, reconciliation and retry. Nested actions declare how their side effects map to those durable operations.

For example, `river.sendMessage` reads the room, sends typed signing arguments to the chat delegate, validates the prepared result and requests submission. A later view shows the host's observed outcome. `river.createRoom` can use a delegate's authorized Core request to create the room under the domain's contract and parameter rules.

## Typed delegate convention

Define an optional SDUI-facing request/result convention with version negotiation and typed schemas. An application adapter validates the envelope and maps it to the pinned domain protocol, preserving canonical signing bytes. A delegate can also implement the convention directly as a separately versioned protocol. Release deterministic codecs and fixtures for every supported language.

Ship domain decoding and protocol translation in the application's verified delegate Wasm. Generic readers contain the released protocol codecs and executor primitives. An adapter calling another delegate must satisfy the foundation's immediate-caller policy. A changed delegate follows the normal installation and migration checks. Custom application builds can also use their own code adapters.

| Field | Request | Result |
| --- | --- | --- |
| Protocol version | Selected SDUI-facing convention and domain-schema versions | Echoed |
| Request ID | Unique within the active session | Echoed |
| Operation reference | Durable foundation operation ID when the call changes state | Preserved in the corresponding operation result |
| Body | Typed arguments and bounded source-record bytes | Typed projection, prepared bytes and target, or structured error |

Transport request IDs correlate one exchange. Durable operation IDs follow the user operation across retries and restarts under the foundation rules. Pure view calls use request correlation without allocating a mutation journal entry.

Specify canonical encodings, numeric ranges, byte ownership and error variants. Distinguish permission denial, unavailable adapter, invalid input, protocol mismatch, conflict and uncertain outcome. Bound payload and delegate-context sizes by both the selected Core version and the reader profile. Use the delegate-context limit recorded in [1.6 Application protocols, data and operations](../1-freenet-mobile-appkit/06-data-and-operations.md) and pin the effective value in release fixtures.

Reject conflicting reuse of a request ID, unknown handles, mismatched protocols and expired-session completions. Validate the complete result before exposing it to bindings or starting a side effect. Measure copies across the SDK boundary for large records.

Domain adapters own record decoding, source identity and signature checks, canonical signing inputs, projections, business calculations, preparation and reconciliation. A prepared update still passes host authorization and contract validation. Contracts enforce the shared-state rules for every writer.

## Execution limits and security

Treat definitions and results as untrusted input. Validate action names, arguments, declared data paths, returned targets and prepared bytes. A delegate-proposed shard or contract reference must fit the declared resource and query policy before the host fetches or submits it.

Run bounded work away from the UI thread. Apply host limits for storage, subscriptions, event frequency, memory and device operations as well as the executor's own work limits. Cancel overdue work and report which budget ended it. Preserve the durable operation journal for work already prepared or submitted. Direct networking, native objects and signing keys stay behind approved interfaces.

## Acceptance

- An Atlas domain operation works through a declared action and custom web/native controls using the same protocol fixtures and domain results.
- Real Core/delegate integration agrees with deterministic [preview fixtures in 4.8 EVY Developer visual authoring](08-developer.md#preview).
- A new application bundle supplies its domain delegate and action definitions and runs on released generic readers. An unsupported primitive fails compatibility checks before execution.
- Canonical request/result encodings, structured errors, byte ownership and correlation agree across browser, Swift and Kotlin bindings.
- The River adapter maps the SDUI convention to the foundation's concrete protocol fixtures with identical canonical signing bytes and domain outcomes. Version negotiation and typed-error fixtures run as this plan's acceptance.
- Malformed results, forged authority, undeclared targets, conflicting request IDs and excessive nested work fail before unauthorized effects.
- Duplicate, canceled, unsolicited and late responses reach only their valid handler. Retry and restart cases retain the foundation's operation identity and exact prepared bytes.
