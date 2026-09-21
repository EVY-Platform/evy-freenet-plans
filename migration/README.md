# Upgrades and migration

Marketplace rebuilds its offer contract. Bob's phone must find Alice's listing under the old key, carry it forward under the new rules, move her seller key into the new delegate and keep following the publisher when its signing key changes. This plan owns those four moves. [Bundles](../appkit/bundles.md) defines the container the publisher signs, [Hosts](../appkit/hosts.md) install the new bundle and run local database migrations, and [Identity and recovery](../identity/README.md) protects the keys that move.

| Section | What Freenet provides today | What AppKit proposes |
| --- | --- | --- |
| [1](#1-component-identity-and-re-keying) | BLAKE3 keys over code hash and parameters, and no upgrade protocol in Core | A predecessor registry per application and a build check that requires an entry |
| [2](#2-contract-carry-forward) | `freenet-migrate` lineage, probe driver and carry-forward gate | Host-coordinated migration with application-owned adapters and a recovery policy per domain |
| [3](#3-delegate-secret-export-and-import) | The export and import round trip in `freenet-migrate`, the FNSX bundle and the disabled node copy-forward | Every AppKit delegate implements export and import under user approval |
| [4](#4-publisher-continuity) | One verifying key per website container and whole-state replacement per version | A mutually acknowledged transfer statement between predecessor and successor containers |

## 1. Component identity and re-keying

### What Freenet provides today

A contract or delegate key is BLAKE3 over the code hash and parameter bytes, so a rebuild creates a new key and leaves state under the old one. The [whitepaper](https://github.com/freenet/paper-1/blob/main/sections/07-status.tex) states the consequence: components are content addressed, a new version is published under a new key, and Core has no upgrade protocol.

### What AppKit proposes

Record original code hashes, parameter encodings and actual instance references in the registry. Add a build check that requires a predecessor entry when component code changes. Use the resolver for successor pointers with its minimum accepted version, and handle stale, unavailable, conflicting and withdrawn results.

## 2. Contract carry-forward

### What Freenet provides today

| Library item | What it does |
| --- | --- |
| `freenet-migrate-build` | Generates the lineage registry from a TOML file at build time. River's build fails when the table is empty |
| `predecessor_ids`, `ProbeDriver` and `migrate_contract` | Rebuild predecessor IDs from code hash and parameters and probe them newest first under a `SelectionPolicy` |
| `CarryForward` and `policy_check` | Run `verify()` after `merge()`, and assert commutative, idempotent and order-invariant merges |
| `resolve_app_pointer` | Reads the frozen pointer contract from [#5194](https://github.com/freenet/freenet-core/issues/5194) and answers which code hash is current |

The [mobile plan](../freenet-mobile/README.md#0-feasibility-and-existing-evidence) records the stdlib compatibility check the library needs.

### What AppKit proposes

The host coordinates migration reads, approved imports, publication and readback. Application-owned adapters implement the contract probe I/O with domain codecs, validation and recovery rules. Atlas proves this adapter boundary. Custom applications link the library from their own code.

| Recovery policy | Use it for | Required proof |
| --- | --- | --- |
| Newest generation | Snapshot state such as a listing | The successor's validation rules accept the recovered state |
| Combined generations | Event histories with deletions and conflicts | `policy_check` assertions pass against the domain's real state model |

Preserve unresolved predecessor reads for retry. Validate recovered state with the successor's rules, publish it through authorized host operations, then read it back before recording success.

Shared-state recovery stays separate from host database migration and bundle installation. Mixed-version clients obey the domain's transition rules.

Example: the Marketplace publisher rebuilds the offer contract. The build fails until the registry gains the old code hash. Bob's phone installs the new bundle, probes the predecessor key newest first, carries Alice's listing forward, validates it under the new rules and reads it back.

## 3. Delegate secret export and import

### What Freenet provides today

Run the export and import round trip through `PredecessorSecretsIo` and `SuccessorSecretsIo` under a `MigrationAuthorization`: . [PR #5199](https://github.com/freenet/freenet-core/pull/5199) disabled Core's copy-forward of secrets, and stdlib 0.9.0 removed the predecessor-registering request.

Core encrypts delegate secrets under a node key encryption key with systemd, file and opt-in keyring backends, per [secrets at rest](https://github.com/freenet/freenet-core/blob/main/docs/secrets-at-rest.md). Its export produces an encrypted FNSX bundle and caps plaintext at 256 MiB. A CLI export and import of one delegate's secrets ([#4035](https://github.com/freenet/freenet-core/issues/4035)) and a live import into a user's own peer ([#4592](https://github.com/freenet/freenet-core/issues/4592)) are open.

### What AppKit proposes

Every AppKit delegate implements export and import, so its secrets survive re-key. Application-owned adapters implement `PredecessorSecretsIo` and `SuccessorSecretsIo`. Plaintext secrets transit the application during that round trip.

Example: Alice approves the delegate upgrade, the old delegate exports her seller key, and the new one imports it through the Marketplace adapter.

## 4. Publisher continuity

### What Freenet provides today

### What AppKit proposes

## 5. Reference recap

| Reference | Status | Names | Explained in |
| --- | --- | --- | --- |
| Contract and delegate key | Existing | One contract or delegate, from its code hash and parameters | [Section 1](#1-component-identity-and-re-keying) |
| Predecessor entry | Proposed | One earlier code hash and parameter encoding of a component | [Section 1](#1-component-identity-and-re-keying) |
| Recovery policy | Proposed | How one domain carries state across generations | [Section 2](#2-contract-carry-forward) |

## 6. Acceptance

- Migration fixtures pass for skipped versions, late predecessors, deletions, conflicts, interrupted readback and mixed-version participants.

References: [freenet-migrate](https://github.com/freenet/freenet-migrate).
