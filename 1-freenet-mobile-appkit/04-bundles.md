# Plan 1.4: Application bundles

## Purpose

Plan 1.4 packages and publishes a defined application's web UI, contract and delegate artifacts, and host metadata. River's first mobile release opens its web UI in a WebView. Custom native builds use the SDK and their platform distribution process.

## Prerequisites

The supported versions and application profile in [1.1](01-feasibility.md) and [1.2](02-sdk.md), the [host](03-host.md) interface, and the component identity rules in [migration](07-migration.md). Mobile release acceptance includes the required [thin-peer gate in 1.10](10-thin-peer.md).

This plan owns archive metadata, signing, release validation and canonical publication references. [Certification 3.3](../3-attribution-remuneration-payment/03-certification.md) owns certification. [SDUI bundles 4.2](../4-sdui/02-bundles.md) adds optional reader and screen artifacts.

## The archive and its definition

The source material for this plan describes `fdev build` writing `contracts/<code_hash>.wasm` and `dependencies.json`. `fdev website publish` requires `index.html`, creates a tar.xz archive, signs its version and archive, and submits it to the website container. Confirm these details against the versions selected in 1.1. Source links here are plan evidence, rather than a verified report of current upstream status.

```text
index.html
application code and assets
contracts/
  <code_hash>.wasm
  dependencies.json
delegates/
  <delegate>.wasm
app_definition.json
```

The selected profile uses the stock website container packaged as `crates/fdev/resources/website_contract.wasm`. River's [container source](https://github.com/freenet/river/blob/main/contracts/web-container-contract/src/lib.rs) records a single 32-byte Ed25519 verifying key as parameters, CBOR metadata containing version and signature, then the tar.xz archive. Its recorded caps are 100 MB for state and 1 KB for metadata. Enforce the effective lower limit when Core's state cap also applies.

Application code loads its assets from `index.html` and coordinates concrete application requests. `app_definition.json` supplies the metadata the selected host needs.

| Field | Purpose |
| --- | --- |
| Format version | Select the supported metadata encoding |
| Name and description | Identify the application in trusted install and application-management screens |
| Host requirements | Name compatible host APIs and concrete application protocol versions |
| Contract/delegate references | Identify artifacts, exact parameters or their application-defined encoding, setup requirements and predecessors |
| Permissions | Declare required and optional capabilities under the [base authorization rules](03-host.md#base-authorization-and-device-access) |
| Native links | Identify publisher-endorsed platform builds and distribution links |
| Publisher transfer | Carry a transfer statement or acknowledgement under [migration 1.7](07-migration.md) |

Container version orders publications. Format version selects the metadata layout. Application protocol versions select concrete codecs. Each has a separate encoding and purpose. Native executable changes arrive through an installed-app release.

## Contracts, delegates and initialization

Each component entry records `alias`, `kind`, artifact path or verified reference, parameter encoding, protocol versions, setup requirement and predecessor rows. An alias is an application-local name. [Migration](07-migration.md#component-identity-and-re-keying) owns key derivation, predecessor encodings and the build check for changed component code.

| River component | Parameters and protocol | Setup |
| --- | --- | --- |
| `river.room` contract | `ChatRoomParametersV1 { owner }`, `ChatRoomStateV1` | `none` at installation. Application code and its delegate create each room |
| `river.chat` delegate | Empty parameters, the chat delegate's concrete message protocol | `register` under user-approved installation |

`setup` records `create` with an initial-state rule, `register`, or `none`. The application's bootstrap code performs these steps through authorized host/SDK calls. It supplies the cipher and nonce required by `RegisterDelegate`. Setup is retry-safe and records completion before opening dependent features.

River sources include the [chat delegate protocol](https://github.com/freenet/river/blob/main/delegates/chat-delegate/README.md) and [invite parameter handling](https://github.com/freenet/river/blob/main/ui/src/components/members.rs). Packaging copies the application's predecessor registry into release metadata where the host needs it. The migration owner defines how those rows select and recover components.

## Publishing and evidence

Plan 1.4 adds a retention hook inside `fdev website publish` and a retained-envelope submission path for retries. These are planned tooling changes.

1. Validate metadata, component hashes, parameter fixtures, compatibility, declared permissions and archive limits.
2. Within one publishing invocation, build the archive, stamp its version and sign it. Before submission, the retention hook durably saves the exact signed envelope and archive, container key, version, hash algorithm and digest. Submission waits for that save to succeed.
3. Submit those retained bytes from the same invocation. Read back the stored state, verify its signature and compare its version and archive digest with the retained attempt.
4. After an uncertain submission, reconcile the retained attempt first. A retry uses the retained-envelope path with the original signed bytes and version. A fresh build, version stamp or signature starts a separate publication attempt.

Verified locally stored bytes and their envelope can go directly to [certification 3.3](../3-attribution-remuneration-payment/03-certification.md) for certification. Tooling also provides an independent-node fetch that verifies the signature, version and digest and retains the observing node and time. Local readback proves local acceptance. Independent readback proves retrievability at that observation time. Attribution owns the certification sequence and the independent-observation gate for paid eligibility.

| Reference | Required fields |
| --- | --- |
| `publication_ref` | Full container `ContractKey`, signed container version, hash algorithm and digest of the exact archive read back |
| `application_content_ref` with `kind: publication` | A `publication_ref` |
| `application_content_ref` with `kind: native` | Platform identity, build identity, hash algorithm and build digest |

River's source fixture identifies its container as `raAqMhMG7KUpXBU2SxgCQ3Vh4PYjttxdSWd9ftV7RLv`, per [FREENET.md](https://github.com/freenet/river/blob/main/FREENET.md). Validate deployed identities when selecting release fixtures.

These references have fixed, versioned encodings. Routine website releases retain the container identity while advancing its signed version. A rebuild may change archive bytes and therefore its digest. A native build's relationship to a container requires publisher endorsement. Attribution verifies certification claims and the product-to-container mapping. [Remuneration](../3-attribution-remuneration-payment/05-remuneration.md) verifies usage evidence against those records.

## Installing a copy

The packaging tool validates these conditions before publishing. The [single-app host](03-host.md#single-app-installation-interface) repeats applicable checks before executing archive content.

| Check | Requirement |
| --- | --- |
| Container identity, signature and version | Match the selected application and verify the signed snapshot |
| Paths | Reject absolute paths, parent traversal, symlinks, hardlinks and duplicate paths |
| Executable content | Match the supported application profile and declared artifacts |
| Resource use | Enforce measured download, decompression, file-count and memory caps |
| Metadata and components | Verify artifact hashes, supported formats, parameter encodings and application protocols |
| Setup and access | Match approved setup and declared capabilities |

The source snapshot records a 50 MiB Core contract-state limit. Release tooling checks the pinned node and container limits together. Plan 1.1 sets measured host caps, and 1.10 supplies cellular budgets. Each publication sends the whole archive, including assets. A separate blob-store proposal can use the [hash-keyed contract discussion #3985](https://github.com/freenet/freenet-core/issues/3985) as evidence.

The [single-app installation interface in 1.3](03-host.md#single-app-installation-interface) owns installation/session identifiers and foundational activation, rollback and same-version conflict handling. [Plan 2.3](../2-evy-mobile-app/03-installation-and-updates.md) composes staged installation per app. Component re-keying and publisher transfer follow migration 1.7.

## Retention and recovery

The publisher retains exact archives and signed envelopes, including supported predecessor releases. The website container holds its latest state, and network availability depends on hosting demand, as described in the [whitepaper status](https://github.com/freenet/paper-1/blob/main/sections/07-status.tex). Restoring an archived release requires retained bytes and a compatible host.

[Identity 1.5](05-identity.md) owns the app-specific customer export/import baseline. [Recovery 5.2](../5-optional-extensions/02-recovery.md) adds automated and broader customer recovery. Publisher-key backup and transfer belong to [migration](07-migration.md).

## Reference definitions

| Term owned here | Meaning |
| --- | --- |
| Application container identity | The full container `ContractKey` followed across routine releases |
| Container version | The signed order of publications under that identity |
| Definition format version | The encoding of host metadata |
| `publication_ref` | One exact signed web archive |
| `application_content_ref` | The web publication or native build used by an operation |

## Acceptance

- River's web archive builds, signs, publishes and opens in the supported iOS and Android WebViews. The release passes 1.10's thin-peer and cellular tests.
- CLI/CI rejects unsafe paths, hash mismatches, unsupported metadata, invalid parameter fixtures and releases that exceed the selected profile's limits.
- A failed retention hook stops submission. Termination and uncertain-publication fixtures resume with the exact retained signed bytes and version through the retry path.
- Verified local readback supplies certification input. Independent-node observations retain their own provenance for Attribution's eligibility checks.
- A consumer verifies a `publication_ref` against retained bytes after the live container advances. A native build reference verifies against its endorsed build artifact.
- Setup can resume after termination. Changed delegates and new access pass the host's consent checks before activation.
- Certification fixtures in 3.3 consume these references and exact bytes through their own acceptance gate.

Sources: [website publication manual](https://freenet.org/build/manual/publish-a-website/), [container implementation](https://github.com/freenet/freenet-core/tree/main/crates/website-contract), [fdev website subcommand](https://github.com/freenet/freenet-core/blob/main/crates/fdev/src/website.rs). Host security evidence is collected in [1.3](03-host.md#host-admission-and-permission-dependencies).
