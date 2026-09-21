# Reorganization plan: reading order and one topic per plan

Status: executed on 2026-09-22 in [PR #2](https://github.com/EVY-Platform/evy-freenet-plans/pull/2), after [PR #1](https://github.com/EVY-Platform/evy-freenet-plans/pull/1) merged. Section numbers below refer to the restructured `appkit/data-actions.md` as it stood before the split. The optional move in [6.8](#68-optional-bundles-section-4-into-hosts) was declined in favor of the pointer sentence in hosts section 6.

Reorder the roadmap so a reader meets generic and customer-visible concepts first and granular mechanics later. Split the plans that carry more than two topics. Give each cross-cutting topic one home. Every move in this plan is a move or a split. No sentence is deleted unless another plan already states it, and each such case is named.

The audit behind this plan covered all 17 markdown files, the link graph between them, freenet-core `ios` branch commit 0e9ced57, paper-1 commit 981978e3 and the upstream issue tracker on 2026-09-22.

## 1. What the audit found

| # | Plan | Lines | Topics today | Verdict |
| --- | --- | --- | --- | --- |
| 1 | Bundles | 217 | Packaging and publication. Section 4 describes host behavior | Keep. Section 4 move is optional, see [6.8](#68-optional-bundles-section-4-into-hosts) |
| 2 | Data and actions | 331 | Actions, delegate convention, views, storage, operation lifecycle, adapters, limits, migrations | Split into two plans, move adapters to hosts and migrations to the new migration plan |
| 3 | SDUI | 193 | Screen description and readers | Keep |
| 4 | Hosts | 262 | Execution and permissions, installation and updates, device adapters, diagnostics | Keep. Absorb the adapter text from data-actions |
| 5 | Mobile SDK | 219 | Embedding Core with bindings, plus a thin-peer network proposal aimed at Core maintainers | Move the proposal to a sub-plan |
| 6 | Identity | 169 | Keys and recovery, delegate upgrades, device sync, publisher continuity | Keep keys and recovery. Move the other three |
| 7 | Attribution | 194 | Contribution review and certification | Keep |
| 8 | Payments | 142 | Checkout and signed status | Keep |
| 9 | Remuneration | 137 | Allocation and payouts | Keep |
| 10 | EVY Developer | 221 | Visual builder, publishing, contributor workspace | Keep |
| 11 | Atlas sample | 84 | Proof project | Keep |
| 12 | Mobile app | 98 | Consumer app | Keep, move up |
| 13 | Marketplace | 260 | The product, plus a 78 line contract transport design in section 5 | Move section 5's transport design to a sub-plan |
| opt | Peer reputation | 156 | Research | Keep last |

Five topics have more than one home:

| Topic | Homes today | Home after this plan |
| --- | --- | --- |
| Device and service adapters | Hosts 7, data-actions 7 | Hosts 7 |
| Migration | Data-actions 9, identity 4 and 7, bundles 3, hosts 6, Marketplace 8 | `migration/README.md`. Hosts 6 keeps local database migration and Marketplace 8 links |
| Installation | Bundles 4, hosts 6, mobile app 3 | Hosts 6, with bundles 4 optional |
| Permissions and limits | Hosts 2 and 3, data-actions 8 | Hosts for grants and gates, the actions plan for executor limits |
| Lifecycle | Mobile SDK 5 for the node, hosts 5 for the session, data-actions 6 for the operation | Unchanged. Three layers, each linked to the next |

Three plans carry a `Dependencies:` line, and hosts and SDUI point at each other. The README order plus each intro paragraph carries the reading order instead.

Inbound link counts, from the audit script: hosts 26, mobile SDK 23, identity 21, bundles 17, data-actions 16, SDUI 13, attribution 13, payment 13, EVY 11, remuneration 10, Marketplace 5, Atlas 4, mobile app 3, reputation 3. The four most-linked plans sit at positions 4, 5, 6 and 1 today.

## 2. Rules the work follows

| Rule set | Where | What it means here |
| --- | --- | --- |
| Plain language | [AGENTS.md](../AGENTS.md) | State what will happen. Sentence case headings, straight quotes, no em dashes, no mid-sentence semicolons |
| Wording | The `unslop` skill | Tables and diagrams over prose. Alice, Bob and Carol examples. Active voice |
| Plan conventions | [The data-actions refactor plan](2026-09-22-data-actions-refactor.md) section 1 | Two subheadings per section in AppKit plans, "What Freenet provides today" and "What AppKit proposes". Identifiers introduced where first needed. Recap table at the end |
| One canonical home | This plan, section 1 | Move text, then link to it. Delete a sentence only when the table in [section 6](#6-change-specifications) names the plan that already states it |
| Checker | `python3 maintenance/check-plans.py --strict` | Exit 0 before every commit |
| Anchors | The plan-writing memory | Keep heading text where inbound links exist. Where a heading must go, retarget every link in [section 7](#7-inbound-link-retargets) |

## 3. Target reading order

Replace the README roadmap table with this one. The Group column carries the reading order rationale. Link each plan name to the file in its File column, as the current table does. Keep the "What for" sentences that exist today and add the two new ones and the migration one.

| Group | Plan | File | What for |
| --- | --- | --- | --- |
| Generic concepts | Application bundles | `appkit/bundles.md` | Bob opens a signed Freenet container holding definitions, screens and domain artifacts. |
| Generic concepts | Hosts | `appkit/hosts.md` | The host verifies bundles, manages installed copies and asks for access in a trusted screen. |
| Generic concepts | Identity and recovery | `identity/README.md` | Alice recovers the keys and private records needed to finish her sale. |
| Customer journey | Freenet mobile app | `freenet-mobile-app/README.md` | People discover and open compatible Freenet applications in one mobile app. |
| Customer journey | Marketplace | `marketplace/README.md` | People buy and sell nearby, arrange fulfillment and pay through the shared platform. |
| Customer journey | SDUI | `appkit/sdui.md` | A publisher describes screens once. Readers display them using browser, iPhone and Android controls. |
| Customer journey | Actions and delegates | `appkit/actions-and-delegates.md` | A tap on a declared action runs bounded steps and asks the application's delegate to prepare the result. |
| Customer journey | Data and pending operations | `appkit/data-and-operations.md` | Screens read verified views, keep drafts offline and track each submitted update to its outcome. |
| Customer journey | Payments | `payment/README.md` | The payment service signs the payment result for the agreed order. |
| Contributor journey | EVY Developer platform | `evy/README.md` | Developers build SDUI screens, publish bundles and manage contributions and earnings. |
| Contributor journey | Attribution | `attribution/README.md` | Accepted contributions have recorded authors, reviews and allocation weights. |
| Contributor journey | Remuneration | `remuneration/README.md` | The service allocates funded contributor fees once and accounts for refunds. |
| Platform internals | Freenet mobile SDK | `freenet-mobile/README.md` | A phone embeds Freenet, reconnects and follows the contracts its apps use. |
| Platform internals | Upgrades and migration | `migration/README.md` | Contracts, delegate secrets and publisher keys survive code and key changes. |
| Delivery | Atlas sample | `atlas-sample/README.md` | Atlas search and publication work through web, SDUI and custom native interfaces. |
| Research | Peer reputation | `reputation-proofs/README.md` | A person proves a supported application claim while limiting disclosure. |

Add one sentence above the table: "The table is the reading order. The build order starts with the SDK feasibility stage below and ends with Marketplace." The existing paragraph that begins "Start with the SDK feasibility stage" is the build order and stays. The whitepaper follows the same shape, from problem and thesis through primitives to status, so the README's approach section and this table agree with it.

Sub-plans stay out of the table and are reached from their parent, as `evy/authoring-project-contract.md` and `marketplace/harvest-comparison.md` are today.

## 4. Files

| File | Change | Owns after this plan |
| --- | --- | --- |
| `appkit/actions-and-delegates.md` | Create from data-actions sections 1, 2, 3 and 8 | How a declared action runs and how it talks to a delegate |
| `appkit/data-and-operations.md` | Create from data-actions sections 4, 5 and 6 | Reads, freshness, local values and storage, submitting updates offline |
| `appkit/data-actions.md` | Delete after the two files above exist | Nothing |
| `appkit/hosts.md` | Section 7 absorbs data-actions section 7. Delete the `Dependencies:` line | Device and service adapters, plus everything it owns today |
| `migration/README.md` | Create from data-actions section 9, identity sections 4 and 7, and two paragraphs of bundles section 3 | Component re-keying, contract carry-forward, delegate secret export and import, publisher continuity |
| `identity/README.md` | Retitle "Identity and recovery". Remove sections 4, 5 and 7. Renumber section 6 to 4 | Identities, protected keys, customer recovery |
| `identity/device-sync.md` | Create from identity section 5, the phase 4 row and the Core dependency paragraph | Opt-in device synchronization |
| `freenet-mobile/README.md` | Section 4 becomes a one-paragraph pointer | Embedding Core, bindings, lifecycle, storage |
| `freenet-mobile/thin-peer-proposal.md` | Create from mobile section 4 | The proposed Core network role |
| `marketplace/README.md` | Section 5 keeps its heading, intro, action table and sequence diagram | The product |
| `marketplace/fulfillment-requests.md` | Create from the rest of Marketplace section 5 | Admission and continuation contracts, record identity, encryption profile |
| `appkit/bundles.md` | Retarget two links. Section 4 move is optional | Packaging and publication |
| `appkit/sdui.md`, `evy/README.md` | Delete the `Dependencies:` line. Retarget links | Unchanged |
| `README.md` | Replace the roadmap table. Add the reading versus build order sentence | Index |
| `maintenance/check-plans.py` | Add this plan and the data-actions refactor plan to `SKIP` | Unchanged |
| `attribution/README.md`, `atlas-sample/README.md`, `freenet-mobile-app/README.md`, `payment/README.md`, `remuneration/README.md`, `reputation-proofs/README.md` | Retarget links only | Unchanged |

## 5. Alignment with Freenet Core, the whitepaper and upstream issues

Checked on 2026-09-22. Each row names what a plan says, what the source shows and what the executor does about it.

| Plan statement | Source | Finding | Action |
| --- | --- | --- | --- |
| A new contract or delegate version has a new key and Core has no upgrade protocol (migration plan premise) | paper-1 `sections/07-status.tex` line 14: content-addressed components, "a new version is published under a new key" | Agrees. The paper also lists no upgrade mechanism among open problems | Cite the paper in migration plan section 1 today |
| Key derivation is BLAKE3 over code hash and parameters | paper-1 `sections/03-primitives.tex` line 20 gives the two-stage hash. stdlib 0.10.0 `contract_interface/key.rs` | Agrees | Keep the sentence from data-actions section 9 |
| Delegate secrets sit under a node key encryption key with systemd, file and opt-in keyring backends | freenet-core `docs/secrets-at-rest.md` | Agrees. The auto-resolver omits the keyring backend on purpose | Cite the doc from migration plan section 3 and identity section 2 |
| An encrypted FNSX export bundle exists and import is a node-stopped CLI step | [#4592](https://github.com/freenet/freenet-core/issues/4592) body, [#4035](https://github.com/freenet/freenet-core/issues/4035) open | Agrees. Both issues are open as of 2026-08-31 | Cite both in migration plan section 3 today |
| Core-mediated provenance is separately gated | [RFC #5255](https://github.com/freenet/freenet-core/issues/5255) open | Agrees | Keep the path table from identity section 4 |
| Cross-device delegate sync uses an encrypted shared-secret contract | paper-1 `sections/06-trust.tex` line 60 and `07-status.tex` line 37 mark the pattern partial. [RFC #5587](https://github.com/freenet/freenet-core/issues/5587) and [RFC #4560](https://github.com/freenet/freenet-core/issues/4560) open | Agrees | State the partial status in the device-sync sub-plan |
| The thin-peer role is AppKit's proposal | paper-1 `sections/03-primitives.tex` defines one peer role. No freenet-core issue or discussion names a thin or light peer. [Discussion 811](https://github.com/freenet/freenet-core/discussions/811) on mobile platforms is the closest thread | Agrees that nothing upstream exists yet | The sub-plan's first task files the proposal and links discussion 811 |
| The client API has no per-connection authentication | freenet-core `docs/client-api-exposure.md`, [#5264](https://github.com/freenet/freenet-core/issues/5264) open | Agrees. The embedded node binds an ephemeral loopback port and reports it through `FreenetNode::api_port()` | No change. Hosts section 3 already states it |
| The in-app web view talks to the embedded node through a WebView protocol | freenet-core `docs/mobile-web-runtime-protocol.md`, 469 lines, describing the `atlas-discover-ios` bridge | Agrees with mobile app section 2 | Add the doc as a source link in mobile app section 2 |
| Responses carry no request ID, cited as [#5048](https://github.com/freenet/freenet-core/issues/5048) | Issue closed as completed on 2026-08-31. stdlib 0.10.0 `ContractRequest` still has no request id field | The wire fact stands. The issue citation reads as open | In `data-and-operations.md` sections 1 and 3 and mobile section 2, cite the stdlib type for the fact and mark #5048 as closed for the TypeScript SDK's own matching |
| Delegate-side unsubscribe traces to [#5600](https://github.com/freenet/freenet-core/issues/5600) | Issue closed as completed on 2026-09-10, referencing PR 5623. Core `ios` still comments that it produces no `UnsubscribeContractResponse` | Partly stale | In `data-and-operations.md` section 1, say the delegate handler landed under #5600 and the client `ContractRequest::Unsubscribe` remains upcoming |
| The website container caps the archive | `crates/website-contract/src/lib.rs` sets `MAX_WEB_SIZE` to 100 MiB and notes the node's 50 MiB `MAX_STATE_SIZE` binds first | Bundles section 5 says 50 MiB, which is the effective cap | No change |
| Changing the container Wasm changes every site's key | `crates/website-contract/README.md` | Agrees with bundles section 1 | No change |
| Guest execution has a wall-clock deadline, cited as [#4864](https://github.com/freenet/freenet-core/pull/4864) | Merged PR on 2026-07-20 | Agrees | No change |
| `MessageOrigin::Delegate` attests delegate callers | [#3860](https://github.com/freenet/freenet-core/issues/3860) closed 2026-04-14. stdlib 0.10.0 has the variant. Core `user_input.rs` still reserves its prompt variant | Agrees for the API. Prompts lag | No change |

## 6. Change specifications

### 6.1 Split data-actions into two plans

`appkit/actions-and-delegates.md` keeps the intro paragraph on scope and Bob's Make offer walk-through. Its intro table:

```markdown
| Section | What Freenet provides today | What AppKit proposes |
| --- | --- | --- |
| [1](#1-who-does-what) | Core's contract and delegate runtimes and delegate secret namespaces | The action executor, the host broker and the application delegate convention |
| [2](#2-declared-actions) | Application code that calls the client API directly | Versioned action definitions with bounded steps, run by the installed executor |
| [3](#3-delegate-requests-and-results) | `ApplicationMessages` with opaque payload bytes and a runtime-attested `MessageOrigin` | A typed request and result protocol inside the payload, with fixtures and correlation |
| [4](#4-limits-and-security) | Core's Wasm state, context and deadline limits | Host limits for actions, views, subscriptions and storage, plus session authority |
```

Its headings:

```text
## 1. Who does what
## 2. Declared actions
## 3. Delegate requests and results
## 4. Limits and security
## 5. Reference recap
## 6. Acceptance
```

`appkit/data-and-operations.md` opens with Alice's train example from data-actions section 4 and her offline price change from section 6. Its intro table:

```markdown
| Section | What Freenet provides today | What AppKit proposes |
| --- | --- | --- |
| [1](#1-reads-views-and-freshness) | `Get`, `Subscribe`, `GetResponse` and `UpdateNotification` keyed by contract, with no timestamps | Logical resources, declared views, value states and host-recorded freshness |
| [2](#2-values-and-local-storage) | Opaque state bytes in Core and the browser storage gates | A shared value model, storage namespaces and cache keys |
| [3](#3-submitting-updates-and-pending-operations) | `Update`, total merge in `update_state` and an `UpdateResponse` summary from the local node | Operation IDs, a durable journal and the lifecycle from Queued to Accepted or Superseded |
```

Its headings:

```text
## 1. Reads, views and freshness
## 2. Values and local storage
## 3. Submitting updates and pending operations
## 4. Reference recap
## 5. Acceptance
```

| Data-actions text | Destination |
| --- | --- |
| Intro lines 3 to 5 | Actions plan intro. The data plan gets its own two-sentence intro naming the actions plan |
| Section 1 Who does what, lines 19 to 61 | Actions plan section 1, unchanged |
| Section 2 Declared actions, lines 62 to 87 | Actions plan section 2. Retarget the step table's "Detailed in" column: read or observe to `data-and-operations.md#1-reads-views-and-freshness`, submit and cancel to `data-and-operations.md#3-submitting-updates-and-pending-operations`, local read and time to `data-and-operations.md#2-values-and-local-storage`, blob and device rows to `hosts.md#7-photos-files-and-external-services`, call delegate to `#3-delegate-requests-and-results` |
| Section 3 Delegate requests and results, lines 88 to 117 | Actions plan section 3, unchanged |
| Section 4 Reads, views and freshness, lines 118 to 144 | Data plan section 1. Apply the #5048 and #5600 wording from [section 5](#5-alignment-with-freenet-core-the-whitepaper-and-upstream-issues) |
| Section 5 Values and local storage, lines 145 to 175 | Data plan section 2, unchanged |
| Section 6 Submitting updates and pending operations, lines 176 to 218 | Data plan section 3. Apply the #5048 wording |
| Section 7 Device and service adapters, lines 219 to 243 | Hosts section 7, see [6.6](#66-hosts-absorbs-the-device-and-service-adapters) |
| Section 8 Limits and security, lines 244 to 266 | Actions plan section 4, unchanged |
| Section 9 Application migrations, lines 267 to 301 | Migration plan sections 1 to 3, see [6.2](#62-the-upgrades-and-migration-plan) |
| Section 10 Reference recap rows | `MessageOrigin`, action definition and step version, delegate protocol version and request ID go to the actions plan recap. `UpdateResponse` summary, logical resource and view, storage namespace and operation ID go to the data plan recap. Contract and delegate key and recovery policy go to the migration plan recap. Verified content reference and completion evidence are introduced in hosts section 7 after the move and leave the recap |
| Section 10 closing line on `app_ref` and `publication_ref` | Both new recaps |
| Section 11 Acceptance bullets | Atlas action, new action without an executor update, real delegate integration tests, and hosts reject forged caller IDs and malformed results go to the actions plan. Request correlation and subscription repair, the fixtures bullet, and force termination go to the data plan. Migration fixtures go to the migration plan |
| Section 11 references line | Client API and delegate interface links to the actions plan. Client API link to the data plan. freenet-migrate link to the migration plan |

The two new plans link each other in their intros. The actions plan's example in section 2 already names the `listingDetails` view, so it links `data-and-operations.md#1-reads-views-and-freshness` there.

### 6.2 The upgrades and migration plan

`migration/README.md`, top-level like `identity/`. Intro: Marketplace rebuilds its offer contract, so Bob's phone must find Alice's listing under the old key, carry it forward, move her seller key into the new delegate and keep following the publisher after a key change. Intro table:

```markdown
| Section | What Freenet provides today | What AppKit proposes |
| --- | --- | --- |
| [1](#1-component-identity-and-re-keying) | BLAKE3 keys over code hash and parameters, and no upgrade protocol in Core | A predecessor registry per application and a build check that requires an entry |
| [2](#2-contract-carry-forward) | `freenet-migrate` lineage, probe driver and carry-forward gate | Host-coordinated migration with application-owned adapters and a recovery policy per domain |
| [3](#3-delegate-secret-export-and-import) | The export and import round trip in `freenet-migrate`, the FNSX bundle and the disabled node copy-forward | Every AppKit delegate implements export and import under user approval |
| [4](#4-publisher-continuity) | One verifying key per website container and whole-state replacement per version | A mutually acknowledged transfer statement between predecessor and successor containers |
```

Its headings:

```text
## 1. Component identity and re-keying
## 2. Contract carry-forward
## 3. Delegate secret export and import
## 4. Publisher continuity
## 5. Reference recap
## 6. Acceptance
```

| Source text | Destination |
| --- | --- |
| Data-actions section 9 today, first sentence on BLAKE3 keys | Section 1 today, with the paper-1 citation from [section 5](#5-alignment-with-freenet-core-the-whitepaper-and-upstream-issues) |
| Bundles section 3 today, the paragraph "Contract and delegate identity uses the same derivation" and the sentence on successor pointers from `freenet-migrate` | Section 1 today. Bundles section 3 keeps its `fdev build` sentence and links here |
| Bundles section 3 proposes, the fixtures paragraph and the paragraph beginning "Hosts link `freenet-migrate`" | Section 1 proposes and section 2 proposes. Bundles section 3 keeps the definition field sentence and the example, and links here |
| Data-actions section 9 today, the library table rows for `freenet-migrate-build`, `predecessor_ids`, `CarryForward` and `resolve_app_pointer` | Section 2 today |
| Data-actions section 9 today, the `migrate_delegate_secrets` row, the PR #5199 sentence and the 256 MiB export cap | Section 3 today, plus the `docs/secrets-at-rest.md`, #4035 and #4592 citations |
| Data-actions section 9 proposes, paragraphs 1 to 5 and the recovery policy table | Section 1 proposes for the registry paragraph, section 2 proposes for the rest |
| Data-actions section 9 proposes, the sentence "Every AppKit delegate implements export and import" through "handle stale, unavailable, conflicting and withdrawn results" | Section 3 proposes for the delegate sentences, section 1 proposes for the resolver sentence |
| Data-actions section 9 example | Section 2 example, with the delegate sentence moved to section 3's example |
| Identity section 4 Delegate upgrades, lines 80 to 110 | Section 3. The first two paragraphs and the path table are today. The sequence diagram, the migration record paragraph and the test paragraph are proposes. The PR #5199 paragraph is today |
| Identity section 7 Publisher continuity, lines 144 to 169 | Section 4. The paragraph on routine updates and the container property table are today. The numbered transfer steps, the divergence paragraph, the transfer link paragraph and the test paragraph are proposes |
| Identity section 6, phase 3 row "Delegate migration" | Section 6 acceptance |
| Data-actions section 11, migration fixtures bullet | Section 6 acceptance |

Relative links change when text moves from `appkit/` to `migration/`. `bundles.md` becomes `../appkit/bundles.md`, `hosts.md` becomes `../appkit/hosts.md`, and `../identity/README.md#4-delegate-upgrades` becomes the internal `#3-delegate-secret-export-and-import`. Links to `../freenet-mobile/` and `../identity/` keep their form.

Recap table rows: contract and delegate key (existing, section 1), predecessor entry (proposed, section 1), recovery policy (proposed, section 2), migration record (proposed, section 3), transfer statement (proposed, section 4).

### 6.3 Identity keeps keys and recovery

Retitle the file "Identity and recovery". Rewrite the second intro paragraph so the plan owns user key protection and recovery coverage, and links the migration plan for delegate upgrades and publisher transfers and the device-sync sub-plan for synchronization. Remove sections 4, 5 and 7. Renumber section 6 to 4. Its phase table keeps phases 1 and 2, and the paragraph "Phases 1 through 3 apply to the Marketplace launch profile" becomes "Both phases apply to the Marketplace launch profile."

`identity/device-sync.md` starts with a Parent line that links "Identity and recovery" to its `README.md`, and contains identity section 5 lines 111 to 128, the phase 4 row from section 6 as its own delivery line, the Core dependency paragraph from section 6 under a heading "Core dependencies", and one today paragraph: the whitepaper describes the shared-secret contract pattern and marks the delegate-to-delegate flow partial, per `sections/06-trust.tex` and `sections/07-status.tex`. Headings: 1 Enrollment and encryption, 2 Core dependencies, 3 Delivery and acceptance.

### 6.4 The thin-peer proposal sub-plan

`freenet-mobile/thin-peer-proposal.md` starts with a Parent line that links "Freenet mobile SDK" to its `README.md`, and contains mobile section 4 lines 118 to 147 in full: the description, the flowchart, the negotiation paragraph, the Core area table and the proposal paragraph. Add one today paragraph: the whitepaper's primitives section defines a single peer role, and no freenet-core issue or discussion names a thin or light peer as of 2026-09-22, with [discussion 811](https://github.com/freenet/freenet-core/discussions/811) as the nearest thread. Add one task line: file the role-design proposal in freenet-core and record its number here.

Mobile section 4 keeps its heading and becomes one paragraph with three sentences. A thin peer opens a terminal connection to a serving full peer that routes, hosts and distributes updates for it. This is AppKit's proposed Core extension, specified in the thin-peer proposal, linked as `thin-peer-proposal.md`. The full-peer profile stays the production role until the proposal lands. Sections 5 to 8 keep their numbers, so no inbound anchor changes.

### 6.5 The fulfillment requests sub-plan

Marketplace section 5 keeps its heading, its first paragraph, the action table, the fulfillment modes paragraph and the sequence diagram. It gains one sentence that names the fulfillment requests plan, linked as `fulfillment-requests.md`, as the owner of record identity, the admission and continuation contracts and the encryption profile.

`marketplace/fulfillment-requests.md` starts with a Parent line that links "Neighborhood marketplace" to its `README.md`, and contains, from section 5, the record identity paragraph with its four rules and the retry paragraph (lines 138 to 145), the subsection "Public first contact and bounded transport" (lines 167 to 186) and the subsection "Encryption, acceptance and recovery" (lines 188 to 198). Promote the two subsections to `##` headings and add "## 1. Record identity" for the rules. Remuneration section 3 links the admission contract table, so its link moves to `../marketplace/fulfillment-requests.md#2-public-first-contact-and-bounded-transport`.

### 6.6 Hosts absorbs the device and service adapters

Hosts section 7 already holds the picker outcome table and the network policy table. Insert after the network policy table, in this order:

1. The attachments paragraph from data-actions section 7: validate size and media policy, encrypt when required, store content-addressed bytes, return a verified content reference, publish only after upload evidence.
2. The pickers paragraph: scoped handles bounded by grants, session and lifetime.
3. The completion evidence paragraph with its remuneration link.
4. The example: Alice's photo becomes a blob the node serves, Bob pays through a popup, the host forwards completion evidence with his operation ID.

Leave out the adapter table and the checkout paragraph from data-actions section 7. The network policy table in hosts section 7 already states popups, in-app browser sessions and media loading per target, and the payment sentence duplicates hosts section 7's last paragraph. Hosts section 7 has no today and proposes split, so the moved text drops those subheadings.

### 6.7 README and dependency lines

Replace the roadmap table with the one in [section 3](#3-target-reading-order). Add the reading versus build order sentence above it. Check the risks list: item 2 mentions typed delegate interfaces and stays correct.

Delete line 3 of `appkit/hosts.md`, `appkit/sdui.md` and `evy/README.md`. Each intro already names its neighbors in prose. SDUI loses its only link to the actions plan with that line, so section 2 of SDUI gains a link on "The action definition names bounded steps" to `actions-and-delegates.md#2-declared-actions`.

### 6.8 Optional: bundles section 4 into hosts

Bundles section 4 describes what the host runs from the definition and the installation and session identifiers. Moving it into hosts section 6 puts installation in one place but drops its today and proposes split, because hosts has none, and renumbers bundles sections 5 to 8, which retargets three links. Do it last, or leave it and add one sentence in hosts section 6 that links `bundles.md#4-host-execution-from-the-definition`. The rest of this plan does not depend on the choice.

## 7. Inbound link retargets

Every link that changes, by source. Line numbers are from the branch state on 2026-09-22.

| Source | Today | New target |
| --- | --- | --- |
| `README.md:127` | Row for data-actions | Two rows in the new table |
| `appkit/bundles.md:3` | `data-actions.md` | `actions-and-delegates.md` |
| `appkit/bundles.md:42` | `../identity/README.md#7-publisher-continuity` | `../migration/README.md#4-publisher-continuity` |
| `appkit/bundles.md:127` | `data-actions.md#9-application-migrations` | `../migration/README.md#2-contract-carry-forward` |
| `appkit/hosts.md:3` | `Dependencies:` line | Deleted |
| `appkit/hosts.md:26` | `data-actions.md` | `actions-and-delegates.md` and `data-and-operations.md`, one link each |
| `appkit/hosts.md:149` | `data-actions.md#6-submitting-updates-and-pending-operations` | `data-and-operations.md#3-submitting-updates-and-pending-operations` |
| `appkit/hosts.md:157` | `../identity/README.md#4-delegate-upgrades` | `../migration/README.md#3-delegate-secret-export-and-import` |
| `appkit/hosts.md:187` | `data-actions.md#9-application-migrations` and `../identity/README.md#4-delegate-upgrades` | `../migration/README.md#2-contract-carry-forward` and `#3-delegate-secret-export-and-import` |
| `appkit/hosts.md:201` | `../identity/README.md#7-publisher-continuity` | `../migration/README.md#4-publisher-continuity` |
| `appkit/sdui.md:3` | `Dependencies:` line | Deleted, with the new link in SDUI section 2 |
| `evy/README.md:3` | `Dependencies:` line | Deleted |
| `evy/README.md:102` | `../appkit/data-actions.md` | `../appkit/data-and-operations.md#1-reads-views-and-freshness` |
| `freenet-mobile/README.md:53` | `../appkit/data-actions.md` | `../appkit/actions-and-delegates.md` and `../appkit/data-and-operations.md` |
| `freenet-mobile/README.md:116` | `../appkit/data-actions.md` | `../appkit/actions-and-delegates.md` |
| `freenet-mobile/README.md:189` | `../identity/README.md#6-delivery-and-acceptance` | `../identity/device-sync.md#2-core-dependencies` |
| `marketplace/README.md:5` | `../appkit/data-actions.md` | Both new plans |
| `marketplace/README.md:230` | `../appkit/data-actions.md#9-application-migrations` | `../migration/README.md#2-contract-carry-forward` |
| `atlas-sample/README.md:29` | `../appkit/data-actions.md#3-delegate-requests-and-results` | `../appkit/actions-and-delegates.md#3-delegate-requests-and-results` |
| `attribution/README.md:9` | `../identity/README.md#7-publisher-continuity` | `../migration/README.md#4-publisher-continuity` |
| `remuneration/README.md:51` | `../marketplace/README.md#5-structured-fulfillment-requests` | `../marketplace/fulfillment-requests.md#2-public-first-contact-and-bounded-transport` |
| `reputation-proofs/README.md:5` | `../appkit/data-actions.md` | `../appkit/actions-and-delegates.md` |
| Moved text in the migration plan | `bundles.md#…`, `hosts.md#…`, `../identity/README.md#4-delegate-upgrades` | `../appkit/bundles.md#…`, `../appkit/hosts.md#…`, `#3-delegate-secret-export-and-import` |

Links into `appkit/hosts.md`, `appkit/sdui.md`, `payment/`, `remuneration/`, `attribution/` and `freenet-mobile/README.md` sections 0 to 3 and 5 to 8 keep working, because those headings stay.

## 8. Tasks

Each step is one action. Run the checker before every commit. Work on a branch from `main` after PR #1 merges.

### 8.1 Prepare

1. Read [AGENTS.md](../AGENTS.md) and load the `unslop` skill.
2. Read this plan and the [data-actions refactor plan](2026-09-22-data-actions-refactor.md) section 1.
3. Run `python3 maintenance/check-plans.py --strict` and confirm exit 0.
4. Create the branch `plan-reorganization`.
5. Add `maintenance/2026-09-22-data-actions-refactor.md` and `maintenance/2026-09-22-plan-reorganization.md` to the `SKIP` set in `maintenance/check-plans.py`, because both describe files this plan deletes or creates.
6. Run the checker and commit as "Exempt maintenance plans from the link checker".

### 8.2 Split data-actions, absorb adapters, seed the migration plan

1. Create `appkit/actions-and-delegates.md` with the intro, the table and the six headings from [6.1](#61-split-data-actions-into-two-plans).
2. Move data-actions sections 1, 2, 3 and 8 into it as sections 1 to 4.
3. Retarget the step table's "Detailed in" column as [6.1](#61-split-data-actions-into-two-plans) lists.
4. Write its recap and acceptance from the split in [6.1](#61-split-data-actions-into-two-plans).
5. Create `appkit/data-and-operations.md` with its intro, table and five headings.
6. Move data-actions sections 4, 5 and 6 into it as sections 1 to 3.
7. Apply the #5048 and #5600 wording from [section 5](#5-alignment-with-freenet-core-the-whitepaper-and-upstream-issues) in its sections 1 and 3.
8. Write its recap and acceptance.
9. Insert the four items from [6.6](#66-hosts-absorbs-the-device-and-service-adapters) into hosts section 7.
10. Create `migration/README.md` with the intro, the table and the six headings from [6.2](#62-the-upgrades-and-migration-plan).
11. Move data-actions section 9 into migration sections 1 to 3 as the mapping table assigns, fixing relative links.
12. Delete `appkit/data-actions.md`.
13. Retarget every `data-actions` link in [section 7](#7-inbound-link-retargets).
14. Replace the README row for data-actions with the two new rows, keeping the current table shape for now.
15. Run the checker and confirm 0 errors.
16. Commit as "Split data-actions into actions and data plans".

### 8.3 Complete the migration plan and trim identity

1. Move identity section 4 into migration section 3, splitting today and proposes as [6.2](#62-the-upgrades-and-migration-plan) assigns.
2. Move identity section 7 into migration section 4 the same way.
3. Move the two bundles section 3 paragraphs into migration section 1 and leave a link in bundles section 3.
4. Add the `docs/secrets-at-rest.md`, #4035, #4592 and paper-1 citations to migration sections 1 and 3.
5. Write the migration recap table and the acceptance list, including identity's phase 3 row and the migration fixtures bullet.
6. Create `identity/device-sync.md` from identity section 5, the phase 4 row and the Core dependency paragraph, with the whitepaper status paragraph.
7. Retitle identity, rewrite its second intro paragraph, remove sections 4, 5 and 7, and renumber section 6 to 4.
8. Retarget every `identity` link in [section 7](#7-inbound-link-retargets).
9. Run the checker and confirm 0 errors.
10. Commit as "Add the upgrades and migration plan and trim identity".

### 8.4 Sub-plans for the thin peer and fulfillment requests

1. Create `freenet-mobile/thin-peer-proposal.md` from mobile section 4 with the today paragraph and the filing task from [6.4](#64-the-thin-peer-proposal-sub-plan).
2. Replace mobile section 4's body with the pointer paragraph.
3. Run the checker.
4. Commit as "Move the thin-peer role to a sub-plan".
5. Create `marketplace/fulfillment-requests.md` from the parts of Marketplace section 5 listed in [6.5](#65-the-fulfillment-requests-sub-plan).
6. Trim Marketplace section 5 to its heading, intro, action table, modes paragraph, sequence diagram and the new pointer sentence.
7. Retarget `remuneration/README.md:51`.
8. Run the checker.
9. Commit as "Move fulfillment request transport to a sub-plan".

### 8.5 README, dependency lines and alignment wording

1. Replace the README roadmap table with the one in [section 3](#3-target-reading-order) and add the reading versus build order sentence.
2. Delete the `Dependencies:` lines in hosts, SDUI and EVY.
3. Add the SDUI section 2 link to `actions-and-delegates.md#2-declared-actions`.
4. Add the `docs/mobile-web-runtime-protocol.md` source link to mobile app section 2.
5. Reword the #5048 citation in mobile section 2 per [section 5](#5-alignment-with-freenet-core-the-whitepaper-and-upstream-issues).
6. Run this scan on every changed file and rewrite each hit:

```bash
grep -nE "\b(utilize|leverage|robust|seamless|crucial|delve|enhance|foster|showcase|underscore|pivotal|landscape|additionally|in order to|due to the fact|it is important|won't|can't|cannot|no longer|used to|previously|old approach|rather than|instead of)\b" README.md appkit/*.md identity/*.md migration/*.md freenet-mobile/*.md marketplace/*.md
```

7. Run the checker and confirm 0 errors and 0 warnings.
8. Commit as "Regroup the roadmap into a reading order".
9. Decide on [6.8](#68-optional-bundles-section-4-into-hosts). If yes, move bundles section 4 into hosts section 6, renumber bundles, retarget `payment/README.md:37` and the two recap links to `bundles.md#6-reference-recap`, run the checker and commit as "Move host execution from bundles to hosts".
10. Open a pull request against `main` with the new roadmap table in the description.

## 9. Acceptance

- The README table lists 16 plans in four groups, and every group reads from generic to granular.
- No plan carries more than two topics by the table in [section 1](#1-what-the-audit-found), and every moved sentence appears in exactly one plan.
- `appkit/data-actions.md` is gone and every former link resolves to one of the two new plans or the migration plan.
- Migration has one home. Bundles section 3, hosts section 6, identity and Marketplace section 8 link to it and hold no migration rules of their own except local database migration in hosts.
- The three `Dependencies:` lines are gone and every intro names its neighbors in prose.
- The checker exits 0 with 0 warnings on every commit.
- Each alignment row in [section 5](#5-alignment-with-freenet-core-the-whitepaper-and-upstream-issues) marked with an action is applied, and the #5048 and #5600 citations state the closed status.
