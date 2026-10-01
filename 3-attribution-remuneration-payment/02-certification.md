# 3.2 Release certification

## Repositories

| Repository | Role | Work in this plan |
| --- | --- | --- |
| [evy](https://github.com/EVY-Platform/evy) | Modified | `services/attribution` gains the second-node read, the source check, contribution records, snapshots, saved evidence, paid eligibility and record lookup |
| `freenet-appkit` | Modified | Packaging CLI validates the `capabilities` field in `app_definition.json` and sends the certification request after readback |
| [river](https://github.com/freenet/river) | Modified | `app_definition.json` declares `river.member.invite`. The release build uses the pinned toolchain, `--locked` and path remapping, and rebuilds to the same file digests |
| [freenet-core](https://github.com/freenet/freenet-core) | Used | `fdev --node-url <url> execute get <key>` and the website container's signature check |

## Purpose

This plan ties each published release to the accepted work inside it. The attribution service certifies one version of a website container at a time. It signs a contribution record with a snapshot of contributor units, and decides whether that version can take paid operations. Accepted work and the signed product policy come from [3.1 Contributor registration and attribution](01-attribution.md). The release comes from the [packaging CLI in 1.4 Application bundles](../1-freenet-mobile-appkit/04-bundles.md#publishing-and-evidence).

For example, the River publisher publishes River version 1790640000 with Carol's merged "Invite member" screen. The service certifies it, and Carol's `river.member.invite` work counts as units only, because River has no paid operations.

## Declaring capabilities

A release lists its credited capabilities in a `capabilities` field in [`app_definition.json`](../1-freenet-mobile-appkit/04-bundles.md#the-archive-and-its-definition), for example `["river.member.invite"]`. River defines no capability names, so this plan assigns `river.member.invite`. The packaging CLI checks the field's format in its validate step. The service refuses a release that lists an ID missing from the product policy.

## Certifying a version

| Step | Who | What happens |
| --- | --- | --- |
| 1. Request | Packaging CLI | After readback closes the attempt, sends the container key, the version and the release commit to the service. |
| 2. Read from a second node | Service | Reads the container from a node the service runs, with the same call as the readback in [1.4 Application bundles](../1-freenet-mobile-appkit/04-bundles.md#publishing-and-evidence). Checks the publisher's signature over version and archive, as the [website container's `validate_state`](https://github.com/freenet/freenet-core/blob/main/crates/website-contract/src/lib.rs) does. |
| 3. Check source | Service | Rebuilds the release folder from the release commit in an isolated runner. The runner uses the toolchain pinned at that commit, builds with `--locked`, and maps the workspace, `$CARGO_HOME` and `$RUSTUP_HOME` paths to fixed names with `--remap-path-prefix`. Delta, Ghostkeys and freenet-delegates build their Wasm this way ([delta#4](https://github.com/freenet/delta/pull/4), [ghostkeys#9](https://github.com/freenet/ghostkeys/issues/9), [freenet-delegates#4](https://github.com/freenet/freenet-delegates/pull/4)). Compares every file's digest with the files in the archive it read. |
| 4. Collect work | Service | Includes each acceptance from 3.1 Contributor registration and attribution whose merge commit is in the release commit's history and whose capability the release lists. Refuses while an included acceptance has an open challenge. |
| 5. Sign | Service | Signs the record and snapshot and saves the archive bytes, the signed version, the node URL and the read time.<br>--> Produces the contribution record below. |

The website container keeps only its latest version. The service saves the archive bytes it read, because it can't read version 1790640000 again after River publishes a newer one. If a newer version is already current at step 2, the publisher certifies that one instead.

River publishes with its pinned container Wasm through `--contract-wasm`, as set in [1.4 Application bundles](../1-freenet-mobile-appkit/04-bundles.md#the-archive-and-its-definition). Every River version therefore keeps the container key `raAqMhMG7KUpXBU2SxgCQ3Vh4PYjttxdSWd9ftV7RLv`, and all its records name the same registered product.

River commits its `Cargo.lock` so that its contract and delegate Wasm can be rebuilt ([river#393](https://github.com/freenet/river/pull/393)). No River CI job rebuilds the Wasm, so a committed Wasm that differs from the build of its source passes every check ([river#678](https://github.com/freenet/river/issues/678)). A comment-only edit changes the room contract key, because panic `Location` records carry file and line. Step 3 closes this gap for each release.

[River's publish rules](https://github.com/freenet/river/blob/main/.claude/rules/river-publish.md) record a rebuild that differed byte for byte. River's first certification therefore checks that its build rebuilds to the same file digests.

Code that no acceptance covers, such as River code from before River registered, earns no units. A change to any file makes a new version with its own record. A repeated request for the same version returns the existing record.

## The contribution record

```jsonc
{
  "format_version": "1",                                          // record format the service signs
  "container_key": "raAqMhMG7KUpXBU2SxgCQ3Vh4PYjttxdSWd9ftV7RLv", // River's website container, the registered product
  "version": 1790640000,                                          // container version this record certifies
  "hash_algorithm": "blake3",                                     // algorithm for every digest below
  "archive_digest": "<digest>",                                   // digest of the archive read in step 2
  "release_commit": "<commit>",                                   // source rebuilt in step 3
  "capabilities": ["river.member.invite"],                        // copied from app_definition.json
  "acceptances": ["<acceptance ID>"],                             // Carol's "Invite member" acceptance, included in step 4
  "snapshot": {                                                   // units frozen at certification
    "river.member.invite": {                                      // one entry per listed capability
      "carol": 6.8,                                               // Carol's units, stored under her ActorId
      "reviewer": 0.8,                                            // the accepted reviewer's units
      "validator": 0.4                                            // the first validator's units
    }
  },
  "policy_version": 1,                                            // product policy version in force
  "signature": "<signature>"                                      // attribution service signature over every field above
}
```

The container key, version, hash algorithm and archive digest together form the `publication_ref` from 1.4 Application bundles. A later policy version or a new acceptance from a challenge in 3.1 Contributor registration and attribution never alters a certified snapshot. If a later River version drops `river.member.invite` and a newer one restores it, Carol's acceptance counts again in the newer record.

## Paid eligibility and lookup

A version is paid eligible when the service has certified it and has not suspended its product. River has no paid operations, so its eligibility changes nothing for Carol. On Marketplace, Bob's 70-dollar payment for Alice's skateboard runs only on a paid-eligible version.

- A suspended product returns `paid_eligible: false` for new paid operations and keeps its records and snapshots.
- A lookup takes a container key, version and capability ID. It returns the signed record, whether the record lists that capability, the snapshot, and whether the version can take new paid operations today.
- Older versions keep the units frozen at their certification.

## Acceptance

- Certifying River version 1790640000 twice returns the same record, which lists `river.member.invite` and Carol's acceptance.
- The service refuses a release when one rebuilt file digest differs, when it lists a capability missing from the product policy, when the read has a bad signature or a newer version, or while an included acceptance has an open challenge.
- A lookup for a capability the record doesn't list returns absent. After the service suspends a product, lookups return `paid_eligible: false` and the original snapshot units.
- The service returns the saved archive bytes for version 1790640000 after River publishes a newer version.
