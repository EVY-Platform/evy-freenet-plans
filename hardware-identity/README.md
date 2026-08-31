# Hardware-backed identity

Every defence against a Sybil attack works the same way: make identities cost something. Proof-of-work makes them cost electricity, and Freenet's maintainers rejected it as wasteful and biased against small devices ([#456](https://github.com/freenet/freenet-core/discussions/456)). Payment works ([Ghost Keys](https://freenet.org/ghostkey/) cost a donation) but can never be the only door into a network that promises open access.

This plan adds a third cost, free to most users: proof that a private key lives inside dedicated security hardware on a genuine device. Most phones sold in the last several years ship that hardware. Copying a software process does not copy a hardware-held key, so multiplying identities means buying devices.

The deliverable is a credential format, a verification library, and platform adapters. What a credential is worth is each consumer's decision. [Duty negotiation](../duty-negotiation/README.md) counts one as evidence for a larger network allowance; a reputation system can count one as an enrolment cost; a full peer can count one as a local trust signal.

## 1. What a credential proves

A verified credential proves exactly this: a private key was created inside real hardware, cannot be exported from it, is controlled right now, and just signed a fresh challenge chosen by the verifier.

The verifier reduces each provider's vendor-specific evidence to one normalized result:

```text
provider        which platform attested (apple, android, tpm, ...)
public key      the hardware-held key's public half
credential_id   32 bytes labelling this credential
assurance tier  how strong the hardware and boot state are
```

## 2. What it cannot prove

- It binds a key to *a* genuine device, not to *this* live session. Relay attacks are bounded by challenge binding (section 4) and per-credential caps at the consumer, not prevented.
- Attested keys leak: extracted keyboxes and shared factory batch keys are documented, and revocation is reactive.
- It says nothing about behaviour. Helium's attested hotspots were gamed above the key layer (a ~25,000-device denylist resulted), and Secret Network's SGX admission fell to a hardware bug. Every serious deployment pairs attestation with budgets, behavioural detection, or a denylist.

## 3. Providers

| Platform | Proves | Limits |
| --- | --- | --- |
| iOS / iPadOS (App Attest) | Apple-attested key bound to the calling app; a fresh assertion per use with an increasing counter | Apple's service required at first enrolment; unsupported on macOS |
| Android (Keystore attestation) | Certificate chain to Google/OEM roots covering security level, verified boot, and app identity; a fresh signature per use | Needs periodic revocation refetches from Google; factory reset mints a new credential; TEE must be acceptable, since StrongBox is flagship-only |
| Windows / Linux (TPM 2.0) | A key certified by the machine's TPM (one extra round trip) | No canonical root store, so the library curates a CA bundle; measured boot is a separate tier |
| macOS | Nothing: no attestation API for ordinary apps | Consumers fall back to their no-credential path |

**Custom ROMs are eligible, deliberately.** GrapheneOS supports standard hardware attestation and publishes its verified-boot keys; the policy ships an allowlist of them and a process for extending it. Excluding de-Googled Android would exclude a core Freenet constituency for no security gain.

Anything weaker contributes nothing: software keys, virtual TPMs, or a Play Integrity verdict alone yield no credential. The library reports "no grant", and the consumer decides what happens next.

## 4. The credential interface

Consumers interact through three operations and one data shape:

```text
enrol(challenge)                  -> evidence item   (first use; may need the vendor's service)
assert(challenge)                 -> evidence item   (per use; a fresh possession proof)
verify(item, challenge, policy)   -> normalized result, or no grant
```

- **The challenge is caller-supplied bytes.** Consumers bind it to whatever they protect; duty negotiation hashes its whole connection transcript into it, so a proof cannot be replayed to another peer or repurposed. The library never invents freshness on its own.
- An **evidence item** names its kind, versions, provider, key, enrolment evidence, freshness proof, and the signed challenge, in a canonical byte encoding sized to slot into any consumer's envelope. Size caps and cheap checks run before expensive validation.
- An unknown provider yields no grant rather than an error, so old verifiers degrade quietly. A malformed item from a known provider fails closed.

## 5. Verification library

One Rust library owns all verification; platform calls live in thin Swift and Kotlin adapters that return opaque bytes to it. No validation or policy ever runs on the device being judged.

Rules:

- Parsers are audited and fuzzed; never hand-rolled ASN.1.
- Trust roots and issuer keys are pinned by digest, shipped signed in releases, and rotated through a signed update mechanism for roots and revocation metadata; rotation is tested, not assumed.
- No compile-time feature may strip verification while leaving acceptance enabled.
- Verification is bounded in bytes, CPU, and concurrency so a flood of bogus items cannot stall the caller.
- Raw credential ids never appear in logs, metrics, or storage; consumers cache normalized results under local pseudonyms of their own (duty negotiation defines one such scheme).

## 6. Limits

| Limit | Consequence |
| --- | --- |
| Issuer trust | The roots belong to Apple, Google/OEMs, and TPM vendors. Plurality of issuers is the mitigation, and every consumer must grant a usable floor without any credential, so no vendor becomes a gatekeeper to Freenet. |
| Linkability | A credential shown to several verifiers lets them correlate those sessions. Consumers should let users present per-verifier minimums; one-time-use credentials and ZK pseudonyms are future work needing an enrolment root, which this credential can become. |
| Eligibility | Old devices, VMs, and attestation-less desktops get nothing here. That is acceptable only because consumers keep other paths (a Ghost Key, a floor tier). Custom ROMs are eligible by design (section 3). |
| Vendor outage | An Apple or Google outage degrades new enrolments on that platform only; already-enrolled credentials keep working. |

## 7. Credential lifecycle

| Event | Behaviour |
| --- | --- |
| First use | Create a credential only when the user enables the consuming feature; never back up the private key; distinguish "unsupported hardware" from "provider outage" in what the user sees. |
| App update | Keep the credential where the platform permits; accept current and previous app signers during rollout so a release does not look like Sybil churn. |
| Reinstall, reset, loss | A replacement credential is a new credential; nothing merges. Consumers absorb the churn with their own rate limits. |
| Compromise, revocation | Reject revoked chains and certificates; retire roots and signers through the signed update mechanism (section 5); emergency updates fail closed for new enrolments while existing sessions finish. |

## 8. Prior work and precedent

No earlier Freenet proposal applies device attestation to admission or identity: [#4137](https://github.com/freenet/freenet-core/issues/4137) and [#4140](https://github.com/freenet/freenet-core/issues/4140) cover only at-rest key protection, and [PR #829](https://github.com/freenet/freenet-core/pull/829)'s "app attestation" means something else, a naming collision worth calling out in any RFC. The client-API passkey direction ([#5264](https://github.com/freenet/freenet-core/issues/5264)) is the same instinct at a different layer.

External precedent exists: [Acurast](https://docs.acurast.com/) admits smartphones to a decentralized compute network by exactly this mechanism, on both app stores.

## 9. Delivery

| Phase | Delivers | Done when |
| --- | --- | --- |
| 1. Verifier core | Normalized result, challenge binding, evidence-item format, a fake provider for tests, golden fixtures | A consumer integrates end to end against the fake provider; malformed-item fuzzing runs in CI |
| 2. Apple App Attest | Enrolment and assertion verification, pinned Apple roots, Swift adapter | Real-device fixtures pass; the enrolment-outage path is tested |
| 3. Android Keystore | Chain validation to Google/OEM roots, revocation refetch, GrapheneOS allowlist, Kotlin adapter | A de-Googled GrapheneOS device verifies; a factory reset yields a new credential and nothing merges |
| 4. TPM 2.0 | Key certification and the curated CA bundle | Windows and Linux fixture machines pass; a bundle update is exercised end to end |
| 5. Hardening | Fuzzed parsers, full device matrix, root-rotation and revocation drills, redaction audit | No raw credential id appears in any log or metric; rotation completes without stranding valid credentials |

Phases 2–4 are independent of each other; a stall on one platform never blocks the rest.

## 10. Open decisions

1. Android baseline: TEE or StrongBox as the minimum tier, which verified-boot states are accepted, and who maintains the custom-ROM allowlist.
2. TPM baseline: hardware key only, or measured boot as a higher tier, and who curates the CA bundle.
3. Behaviour when the vendor is unreachable at first enrolment (guidance consumers can adopt: fall to their floor, or prompt for an alternative credential).
4. The exact signed channel for shipping root and revocation updates between releases.
5. Whether assurance tiers should scale consumer grants or remain informational in v1.

## References

- [Ghost Keys](https://freenet.org/ghostkey/) (the payment-based sibling primitive)
- [Proof-of-work rejection, freenet-core#456](https://github.com/freenet/freenet-core/discussions/456)
- [At-rest key protection (not admission): #4137](https://github.com/freenet/freenet-core/issues/4137), [#4140](https://github.com/freenet/freenet-core/issues/4140)
- [Apple App Attest](https://developer.apple.com/documentation/devicecheck)
- [Android Keystore attestation](https://developer.android.com/privacy-and-security/security-key-attestation)
- [Acurast](https://docs.acurast.com/), the working precedent
