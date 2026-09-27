# 5.1 Peer reputation

This optional research and application-integration track lets an application request evidence about a peer while the peer keeps its credentials and activity receipts private. A claim proves the source's stated activity, such as participation on 20 distinct days.

Prerequisites: [protected identity in 1.5 Identity, keys and local protection](../1-freenet-mobile-appkit/05-identity.md), [authenticated host access in 1.3 Single-application host](../1-freenet-mobile-appkit/03-host.md) and an application that defines qualifying events and receipt issuance. Mobile implementations inherit the [resource and cellular limits in 1.10 Thin-peer role and cellular data budgets](../1-freenet-mobile-appkit/10-thin-peer.md). Ordinary application use and commercial release have their own gates.

This plan owns claims, private witnesses, verification and disclosure policy. Application code requests a scoped proof through its authorized host/SDK interface. [3.8 Paid application pilot and commercial acceptance](../3-attribution-remuneration-payment/08-marketplace.md) owns seller checks, orders, refunds and disputes.

## Repositories

| Repository | Role | Work in this plan |
| --- | --- | --- |
| `freenet-reputation` | Created | Claim and source protocol, trust-graph contract, receipts delegate, proof system, contract verifier and host adapter |
| `evy-marketplace` | Modified | Positive-event receipts and purpose-bound claim checks under its policy |
| `freenet-appkit` | Modified | Proof grants, protected witnesses, session cancellation and persistent request history |
| [river](https://github.com/freenet/river) | Used | Qualified activity events in the worked example |
| [mail](https://github.com/freenet/mail) | Used | Recipient policy in the worked example and policy issue #70 |
| [freenet-core](https://github.com/freenet/freenet-core), [paper-1](https://github.com/freenet/paper-1), [web](https://github.com/freenet/web), [harvest](https://github.com/freenet/harvest) and [atlas](https://github.com/freenet/atlas) | Used | Research sources listed at the end of this plan |

## Claims and evidence

| Candidate claim | Evidence source | Meaning |
| --- | --- | --- |
| Pass registered at least 30 days ago | Accepted trust-graph records and time evidence | Registration age |
| Pass holds a Ghost Key | [Ghost Key issuer](https://freenet.org/ghostkey/) | Donation evidence under the accepted issuer policy |
| Peer sponsored by another peer | Signed sponsorship under source rules | The named sponsor's endorsement |
| Activity on 20 distinct days | Qualified River, Mail or other application events | Participation under that application's event and time rules |
| Relay or hosting contribution | Verified delivery or hosting receipts | The measured service described by the receipt policy |

Sources specify admission, deduplication, time evidence and issuer authority. Evaluate freely created identities, shared credentials and colluding issuers. A claim's UI states what its evidence supports.

## Passes, receipts and snapshots

A pass is a membership commitment in a trust-graph contract. A node's delegate holds its private credential. Explicitly enrolled nodes may share that credential, with the sharing authority and recovery policy recorded. Several nodes sharing a pass contribute one distinct pass to the anonymity pool.

The proposed hosted profile assigns one pass to the hosted node. Its users' activity accrues to that pass while private receipts remain in their authorized namespaces. Hosted operators process private evidence and belong in the trust boundary. Each application/user pair grants proof access explicitly.

Prototype a Merkle DAG for membership commitments, separate source-event trees and private receipts. A source admits a qualified event once. The delegate retains a receipt that binds the event to its pass while hiding that link from public readers.

Use a shared graph by default. A snapshot is identified by its cryptographic state digest and accepted freshness evidence. The verifier checks the source's time rules and maximum age. Rotation and retirement use permanent observed-remove tombstones. Tests reject replayed commitments against a snapshot containing the retirement.

Verifier-specific or custom pools require explicit approval because smaller pools make peers easier to distinguish. The production profile sets minimum distinct-pass counts, allowed thresholds and request limits per recipient. The delegate persists request history and enforces those limits across restarts.

## Purpose-bound proof flow

Bob's peer accumulates River receipts, then Bob sends Alice a Mail message. Alice's Mail policy accepts a claim of activity on 20 distinct days.

1. The host authenticates the application, user and session and checks the grant's claims, sources and recipients.
2. The delegate selects an accepted graph snapshot and qualified source records. It proves control of an active pass and distinct receipts belonging to that pass.
3. It binds the proof to the intended action using a canonical encoding:

   `hash(encode(protocol version, Mail contract ID, Alice's inbox ID, Bob's signing public key, canonical message and attachments, random nonce))`

4. Bob sends the message, nonce and proof through Mail's private channel. A fresh random nonce limits guessing attacks against short messages.
5. Alice's peer checks Bob's signature, recomputes the action hash and verifies the claim against accepted graph/source snapshots. Her application applies its own policy to the result.

The same purpose binding applies when a source requires a membership proof before admitting an event. Credit that event once and apply receiver-owned limits to repeated actions.

## Privacy and authority

| Audience | Visible information |
| --- | --- |
| Contract readers | Membership commitments, state digests and source records under each application's visibility rules |
| Proof recipient | Claim, accepted sources, threshold, snapshot digests, intended action and verification result |
| Credential holders | The shared credential and receipts they hold |
| Hosted operator | Private evidence processed on its Core |

The privacy target covers pass identifiers, credentials, receipts, exact totals and links between source events and the pass. Public source records, network addresses, timing and information already held by recipients remain part of the threat model.

[1.3 Single-application host](../1-freenet-mobile-appkit/03-host.md) owns caller authentication and response isolation. [2.2 Multi-application sessions and authority](../2-evy-mobile-app/02-sessions.md) and [2.4 Identity, permissions and device access](../2-evy-mobile-app/04-permissions.md) own sharing and grants. [1.7 Upgrades and migration](../1-freenet-mobile-appkit/07-migration.md) owns publisher continuity. Proof grants name accepted claims, source contracts and recipients. Grant transfer requires verified continuity and user approval. Treat a declined proof as an unanswered request.

## Implementation and acceptance

| Deliverable | Required evidence |
| --- | --- |
| Claim/source protocol | Versioned encodings, source contract identities, accepted schema versions, digests, thresholds, action binding and distinct refusal/error results |
| Private receipts | Event qualification, source signatures or contract witnesses, pass binding, deduplication and authorized recovery |
| Selected proof system | Complete-flow privacy analysis and measured generation, memory, proof-size and verification limits |
| Contract verifier | Update and full-state validation within the selected Core runtime budget for proofs entering public contracts |
| Host adapter | Grants, protected witnesses, session cancellation, recipient limits and persistent request history |
| Application integration | A source issues qualified receipts and a recipient checks a purpose-bound claim under its own policy |

Compare candidate credential and membership systems across the complete flow, using the [Ghost Key benchmarks](https://github.com/freenet/web/issues/25#issuecomment-5162479374) as one input. If the selected profile uses external signed attestations, specify the issuer's authority, availability and private-data exposure.

Acceptance covers:

- Changed sender, recipient, message or attachment, replayed challenges and duplicate source credit.
- Fabricated activity, related sponsors, shared credentials, stale snapshots and retired passes.
- Narrowed pools, repeated threshold probes and restored request histories.
- Missing, declined, stale and invalid proofs as separate results.
- Proof generation and verification on target mobile devices, hosted concurrency, exhausted budgets and full-state validation cost.
- Normal River and commercial flows with the optional adapter disabled.

Select and publish the numeric privacy and cost profile before enabling the application integration. Record source revisions, devices, workloads and measured results with the decision.

## Research sources

These references supply research questions and implementation evidence. Their issue state alone establishes neither cryptographic safety nor production support.

| Source | Question or constraint |
| --- | --- |
| [Security architecture #5380](https://github.com/freenet/freenet-core/discussions/5380) and [client identity #5264](https://github.com/freenet/freenet-core/issues/5264) | Authenticated proof requests and private delegate evidence under the host's authority rules |
| [Rate limiting #601](https://github.com/freenet/freenet-core/discussions/601) and [contract sketch](https://github.com/freenet/freenet-core/discussions/601#discussioncomment-5714500) | Hidden membership bound to exact actions and receiver quotas |
| [Multi-Purpose Trust Network #458](https://github.com/freenet/freenet-core/issues/458) | Separate claim types and application-selected sources |
| [DRIP #443](https://github.com/freenet/freenet-core/discussions/443) and [circular-trust critique](https://github.com/freenet/freenet-core/discussions/443#discussioncomment-4504162) | Sponsorship discovery, cooldowns, collusion and related sponsors |
| [Proof-of-Trust #799](https://github.com/freenet/freenet-core/discussions/799) | Participation, sponsorship and the wealth bias of donation evidence |
| [Web of trust and anonymity #133](https://github.com/freenet/freenet-core/discussions/133) | Hidden membership, rotation, retirement and narrow-pool privacy |
| [Anonymous reputation #882](https://github.com/freenet/freenet-core/discussions/882) | Private receipts and manufactured activity |
| [Karma #11](https://github.com/freenet/freenet-core/issues/11) | Relay and hosting evidence, delivery checks and disputes |
| [Symmetric NAT relays #2925](https://github.com/freenet/freenet-core/issues/2925) and [contract hardening](https://github.com/freenet/freenet-core/blob/08798042093a24d2e0c9d2dc744e570500747aa5/docs/design/contract-hardening.md) | Verifiable relay receipts and collusion. Thin mobile peers' network role remains owned by 1.10 Thin-peer role and cellular data budgets |
| [Ghost Key research](https://github.com/freenet/web/issues/25) and [Mail policy #70](https://github.com/freenet/mail/issues/70) | Certificate-hiding proofs, attestation encryption and recipient/message binding |
| [Harvest incentive mechanism](https://github.com/freenet/harvest/blob/main/docs/design/incentive-mechanism.md) and [design notes](https://github.com/freenet/harvest/blob/main/docs/design/README.md) | Signed order evidence and receiver policy, assessed in the [Harvest source appendix in 3.8 Paid application pilot and commercial acceptance](../3-attribution-remuneration-payment/08-marketplace.md) |
| [Anonymous keypairs and blind donation verification #602](https://github.com/freenet/freenet-core/issues/602) | Donation-backed identity with a hidden donation link |
| [Atlas reputation proposal](https://github.com/freenet/atlas/blob/main/PROPOSAL.md#ghostkeys-integration) | Discovery trust weights, signed feedback and analyzer reputation |
| [Whitepaper trust boundaries](https://github.com/freenet/paper-1/blob/main/sections/06-trust.tex) and [open problems](https://github.com/freenet/paper-1/blob/main/sections/07-status.tex) | Sybil-exposed routing, revocation and consistency of accumulating and decreasing claims |
