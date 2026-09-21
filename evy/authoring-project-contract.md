# Authoring-project contract

Parent: [EVY Developer platform](README.md).

This contract stores the builder's mutable authoring state. Publication exports a validated checkpoint into an ordinary application bundle with its matching declarative actions, delegate descriptors, domain artifacts and schemas. Retain the signed checkpoint and its source-to-artifact mapping for contribution review.

```text
project identity, protocol version, membership epoch
flows: Map<FlowId, Flow>
pages: Map<PageId, Page>
components: Map<ComponentId, Component>
themes: Map<ThemeId, Theme>
relationships: stable item IDs and ordered position tokens
signed operations, causal references, conflicts and tombstones
```

Each operation has a stable ID, author, membership epoch, causal parents and canonical payload. `InsertChild`, `MoveChild` and `RemoveChild` operate on stable relationship-item IDs. Operation signatures bind the full payload and project context. Conflicting bytes under one operation ID remain inspectable and block affected export.

Merge operations by ID as a set. A causally later write replaces the earlier write named in its history. Concurrent writes to the same property retain all competing values as a conflict. A resolution names every conflicting predecessor and the chosen value.

Stable order tokens determine relationship positions. Operation IDs break ties between concurrent insertions. Concurrent moves of the same item remain a conflict requiring resolution.

A concurrent deletion hides the entity, marks it as deleted and retains its edits. Restore names that deletion marker and resolves the retained values. Broken references and relationship cycles block checkpoint export.

The project owner signs the membership roster for an epoch. Each epoch has an immutable roster and base checkpoint, so every validator evaluates authors against the same authority. Membership changes produce an owner-signed successor epoch and reference. A membership epoch is a state partition inside the one authoring-project contract instance: the roster record and the operations it authorizes share the instance.

A replica at epoch N can receive operations from an epoch N+1 member before the successor roster arrives. Every delta carries the roster record together with the operations that reference it. A delta whose roster is absent is rejected in full, so the sender re-offers it with the roster attached. Discarding only the unauthorized operations would lose edits that the roster makes valid.

Publication requires the current membership epoch. The current epoch for export and certification is the highest owner-signed roster whose base checkpoint the exporting client has merged, and attribution records that roster's digest with the checkpoint. Conflicting successor rosters at one epoch number block export until the owner signs a resolution naming both. An offline client claims only the epoch its journal last merged. Keep offline edits from an earlier epoch in the local journal. An authorized current member must apply them to the current checkpoint and sign them. Preserve conflicts and evidence through this repair.

A checkpoint records the canonical entity state, operation frontier, unresolved conflicts, tombstones and membership epoch. Publication requires structural validation and resolved conflicts in included entities. Compaction verifies which operations the source checkpoint includes, then creates an owner-signed successor checkpoint and epoch. Retain predecessor references for the audit trail. Local edits only coalesce before they become shared signed operations. Shared evidence retains its identity.

Bound each submitted batch's bytes and operation count. Capacity is merge-closed: each roster member has a reserved allowance per epoch of 2,048 operations and 1 MiB, and operations beyond a member's allowance are invalid. A union of valid states from the roster's members therefore stays within the shard limit, which is the roster size times the allowance. Split a project or advance a validated checkpoint before an allowance is exhausted. The codec and merge tests establish state-size behavior under concurrent authorized batches. The authoring client and service enforce rate limits. Contract validation has no trusted wall clock. Store optional presence information in separate shard contracts that participants stop renewing when a session ends.

Authoring and collaboration contracts pass `fdev` conformance checks for the [merge properties](https://github.com/freenet/freenet-core/issues/5320) covered by the [conformance suite](https://github.com/freenet/freenet-core/pull/5344). Test associative, commutative and idempotent merge, repeated and grouped deltas, full-state/delta equivalence, malformed signatures, roster changes, stale epochs, tombstone restoration, cycles, conflicting IDs and maximum encoded size. Project-specific tests cover membership, export and capacity rules alongside the shared conformance suite.
