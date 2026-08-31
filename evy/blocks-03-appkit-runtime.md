# AppKit Runtime

**Parent plan:** [AppKit + EVY](README.md). **Depends on:** [AppKit SDUI](blocks-02-appkit-sdui.md), [Data Bindings](blocks-04-appkit-data-bindings.md).

The runtime gives SDUI behaviour: it resolves data, evaluates expressions, runs actions, manages navigation and drafts, and reports errors the same way on web, iOS, and Android. Its design rule is that an app definition can never smuggle in code — everything it can do is either a pure, bounded expression or an allow-listed action that passes capability and permission checks first.

## 1. Scopes and values

Bindings use the reference grammar of [Data Bindings §1](blocks-04-appkit-data-bindings.md#1-reference-grammar) (`contract:`, `agent:`, `local:`, `param:`, `message:`), plus a runtime-only `session:` scope for temporary state. A binding cannot silently fall through to another namespace. Missing values return a typed `Missing` result rather than an empty string.

Standard values:

```text
null, missing, boolean, integer, decimal, string,
bytes-reference, date-time, duration, list, object
```

Define comparison, truth, null/missing handling, string conversion, and date behaviour precisely; do not rely on JavaScript coercion rules. Money is an ordinary typed domain object supplied by an application — the runtime performs no settlement or fee arithmetic.

## 2. Expressions

Expressions are pure and bounded. Initial functions:

```text
length, exists, coalesce
and, or, not
compare and equality
filter, map, first, any, all
formatDate, formatNumber
stringContains, startsWith, endsWith
```

Restrictions:

- no loops other than bounded collection functions;
- no network, file, clock, randomness, or secret access;
- no dynamic function names;
- maximum input size, nesting depth, collection length, and evaluation steps;
- a parser and abstract syntax tree, not `eval` or JavaScript execution.

For date/time, the runtime receives an explicit locale, time zone, and current-time value from the trusted host so tests remain deterministic.

## 3. Actions

An action has a stable name, typed arguments, required capability, cancellation policy, and typed result.

Core v1 actions:

```text
navigate.open
navigate.back
ui.showSheet
ui.closeSheet
local.set
local.remove
contract.update
contract.refresh
agent.request
message.send
file.select
file.open
clipboard.copy
```

Application extensions use namespaces such as `marketplace.createListing` and follow the [SDUI extension rule](blocks-02-appkit-sdui.md#3-extensions): installed signed packages only, never executable code from a document.

Execution pipeline:

```text
parse -> validate -> resolve arguments -> evaluate condition
-> capability check -> permission check -> execute adapter
-> normalize result -> update runtime state -> emit event
```

Each action receives an idempotency key when it can be retried. The runtime distinguishes validation failure, permission denied, offline/unavailable, contract rejection, cancelled by navigation or backgrounding, temporary transport failure, and unknown final state. Only explicitly safe failures are automatically retried.

## 4. Navigation

Use route IDs declared in the app definition rather than hard-coded platform paths. A route includes typed parameters and presentation style:

```text
push, replace, sheet, full-screen, tab-selection, external-handler
```

Readers maintain native navigation state but expose a shared semantic event log for testing and restoration. Deep links include the product and route identity plus signed/validated parameters where needed.

## 5. Drafts and forms

Draft state is local by default. Each flow declares its draft scope and key, initial values, field validation, submit action, and discard/recovery policy.

A form submit resolves a stable snapshot and passes it to one action. Individual fields do not write to shared contracts unless the app explicitly requests autosave.

## 6. Implementations

- the TypeScript implementation is the executable reference and powers the web reader and builder preview;
- Swift and Kotlin implementations use the same generated AST/value definitions;
- a small Rust validator/parser may serve publishing tools and contracts, but readers do not embed a second full runtime through FFI;
- shared JSON fixture traces define events, inputs, expected actions, and semantic output; every platform must replay them identically.

## 7. Security

- reject unknown actions before resolving sensitive arguments;
- never expose delegate secret material as a runtime value;
- permission prompts are rendered by the trusted host shell, never by the untrusted SDUI page ([the shell's full duties](blocks-06-appkit-mobile-readers.md#5-the-trusted-host-shell));
- cap expression and action payload sizes;
- redact values marked sensitive from diagnostics;
- prevent URLs, file references, and external app opens unless the release record declares the capability and the user permits it.

## 8. Delivery

Test pure expressions with property and differential tests. Test actions with real adapters where practical and fake in-memory providers only for protocol conformance.

| Phase | Delivers | Done when |
| --- | --- | --- |
| 1. Values and scopes | Common typed data model and path resolution rules | A binding never falls through namespaces; missing values are typed results, not empty strings |
| 2. Expression grammar | Pure, bounded, portable evaluator | No supported path uses `eval` or downloaded script |
| 3. Action protocol | Allow-listed actions with typed arguments and results | Retries cannot duplicate an idempotent contract or message operation; product actions install without changing the core runtime |
| 4. Core runtimes | TypeScript reference plus Swift and Kotlin implementations | Cancellation on mobile backgrounding leaves drafts and pending updates recoverable |
| 5. Capability and permission checks | Runtime cannot bypass the trusted shell or delegate policy | Permission denial is visible to the user and the app without leaking protected values |
| 6. Conformance suite | Shared fixture traces | Every platform produces the same typed results and semantic output for public fixtures |
