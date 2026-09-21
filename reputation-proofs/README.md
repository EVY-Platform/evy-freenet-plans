# Peer reputation

Peer reputation is an optional research project for proving application activity while protecting private evidence. An application can request a claim about an unfamiliar peer while the peer keeps its pass and receipt history private. [Marketplace](../marketplace/README.md) can use these claims alongside its seller checks.

[Identity and recovery](../identity/README.md) owns protected keys, enrollment and recovery. [Hosts](../appkit/hosts.md) authenticate the calling application and enforce grants. This plan owns claims, private witnesses, verification and privacy policy. [Declared application actions](../appkit/actions-and-delegates.md) request scoped proof operations. SDUI and custom native clients receive the same results through that interface.

The examples below describe proposed integrations. Each source application must implement rules for accepting activity and issuing receipts before a proof can verify that activity.

## 1. Candidate evidence sources

1. Ghost Keys
2. Longevity
3. Sponsorships
4. Application activity such as publishing sites in Delta or writing messages in River
5. Effort provided by the peer such as relaying data or hosting contracts

## 2. Claims and proofs

### Examples

| Claim | Source | Application use |
| --- | --- | --- |
| Peer pass registered at least 30 days ago | Trust graph contract | River: show "established peer" and apply the app's moderation policy |
| Peer pass registered 1 day ago | Trust graph contract | Mail: place messages backed by this new peer in the "risky" folder |
| Peer pass has a $20 Ghost Key | [Ghost Key issuer](https://freenet.org/ghostkey/) | Marketplace: show a donation badge alongside the app's own seller checks |
| Peer sponsored by peer X | Peer X | River: show "backed by a sponsored peer" |

Applications choose which examples to adopt. Sources define qualifying events and how they verify them. Treat registration age as evidence of registration and posting activity as evidence of participation. Assess uptime and honesty using evidence specific to those claims.

### Proof flow

A pass is a membership commitment in the trust-graph contract, held by one node's delegate. Several enrolled peers may share one pass. A pass is per node, since a device node's secret namespace is the node. A hosted node serves several application users under per-user secret namespaces, and every hosted user's activity accrues to that node's one pass while each user's receipts stay in their own namespace. The hosted operator's terms state this. Each application and user needs an explicit proof grant. The record accumulates positive events under source rules. Applications account for freely created identities and colluding event sources.

Bob uses peer B to post in River, then later sends Alice a message through Mail. Peer B already has a pass in the trust graph and keeps its credentials private. The proposed proof lets a verifier check active membership while hiding the pass identifier. Connection metadata remains governed by the network threat model.

1. Bob submits a River message. Peer B adds a proof that it controls an active pass and authorizes this exact message in this room. Changing the message or attachments makes the proof fail.

2. River checks Bob's signature, the peer's proof, and the message against its rules. It records the valid message and proof and credits the action once.

3. Peer B's delegate saves a private receipt linking that credit to its pass. River's public credit record lets others check a later proof without seeing the receipt or its link to the pass. The trust graph stores membership commitments. River stores its messages, and peer B keeps its activity totals private.

4. After accumulating receipts over time, peer B uses them for Bob's Mail message to Alice. Her Mail rules ask for evidence of River activity on at least 20 days, so peer B makes a proof for that claim. The proof is tied to Alice's inbox and Bob's exact message using:

   `hash(encode(protocol version, Mail contract ID, Alice's inbox ID, Bob's signing public key, canonical message and attachments, random nonce))`

   Bob sends the message, proof, and nonce through Mail's private channel. The nonce is a fresh random value that prevents outsiders from testing guesses about short messages.

5. Alice's peer recalculates the hash from the received message and nonce, and verifies Bob's message signature. A different sender key, inbox, message, or attachment makes the proof fail. It checks the proof against recent graph and River records under the contracts and rules her app accepts. The peer uses validated local copies or fetches the required updates.

6. Once the proof passes, Alice's Mail rules decide how to handle Bob's message based on peer B's claim.

### Structure of the trust graph

Prototype a Merkle DAG of commitments for peer membership, with separate source event trees and private receipts. Each tree has a cryptographic state digest that changes when its contents change. [Discussion #133](https://github.com/freenet/freenet-core/discussions/133) supplies the commitment-and-proof research.

A proof uses a snapshot of one of these anonymity pools:

- A verifier-selected pool is a snapshot chosen by Alice or her app.
- A shared pool is a snapshot recognized by many apps.
- A custom pool serves one app or community.

A pool snapshot is the trust-graph contract's summary digest with a maximum age. Contracts carry no version number, so the digest is the snapshot identity and the recipient rejects a digest older than its accepted age. Retirement and rotation of a pass are non-monotone changes, so the graph models them as permanent observed-remove tombstones: a retired pass cannot re-enter by replaying an earlier membership commitment.

The default is one trust graph shared across sources and applications. New snapshots record changes to that same pool over time. Verifier-specific and custom pools require explicit approval because smaller crowds make peers easier to distinguish. The anonymity pool counts distinct passes. A hosted node serving a thousand users contributes one pass, and several peers sharing it still contribute one.

## 3. What a proof reveals

The privacy target is to hide the pass identifier, credentials, receipts, exact totals, and links between source events and the pass from other applications and verifiers.

| Audience | What it can see |
| --- | --- |
| Contract readers | Pass commitments, public source records, and state digests. River messages remain public under River's rules. |
| Proof recipient | Accepted sources, claim type, requested threshold, state digests, action hash, and whether the proof passes. The recipient also sees the message sent to it. |
| Peers holding the credentials | The shared pass and any receipts they hold. |
| Hosted operator | Private evidence processed on its Core. Include the operator in the trust boundary. |

The prototype uses the shared graph by default. Custom pools require explicit approval through the peer's proof-access policy. A production proof profile must set the minimum number of distinct passes in a pool, allowed threshold values and a request limit for each recipient. The delegate persists request history and refuses requests outside that profile. Prototype measurements and privacy tests select the numeric profile before release. Enable the integration only after the profile is complete.

The host authenticates the full application container identity, user and session on each request. The production profile requires Core-authenticated app sessions, and [session admission #5264](https://github.com/freenet/freenet-core/issues/5264) remains open. Implement and test the selected admission path before enabling proof operations. Core then binds each delegate request to that admitted session. Publisher transfers require the identity plan's approval before proof grants move to a successor container. Proof grants specify accepted claims, source contracts and recipients. The peer's proof delegate keeps the private evidence used to construct proofs. A hosted Core operator that processes witnesses remains in the trust boundary.

Apply each source application's visibility rules. Public posts, connection addresses, timing and information already held by a recipient remain visible. Treat a declined proof as an unanswered request.

## 4. Proof implementation

The River-to-Mail example requires a proof of all of the following:

1. The prover controls an active pass in an accepted graph state.
2. The source records validate under the contracts and versions the recipient accepts.
3. The receipts belong to that same pass and refer to distinct credited events.
4. Those events satisfy the source-defined claim, such as activity on 20 distinct days.
5. The proof authorizes the intended application, recipient, sender key, and exact action.

Credit each event once. Apply receiver-owned limits when the resulting reputation supports repeated actions.

The proof design covers:

| Part | Required detail |
| --- | --- |
| Proof format | Versioned claim ID, source contract IDs and versions, state digests, threshold, intended application/recipient, exact action digest and fresh challenge. Define canonical encoding and verification errors. |
| Private evidence | Pass secret, membership witness, receipts, and source-event witnesses. Explain how the receipt binds an event to the pass without publishing that link. |
| Receipt creation | A peer delegate constructs private evidence against public contract records. Keep receipt secrets in the delegate. If an issuer signs receipts, specify its authority and what verifiers trust it to attest. |
| Retirement and rotation | Permanent observed-remove tombstones in the trust graph. A proof against a snapshot that contains the tombstone fails for the retired pass. |
| Source interface | A versioned way to identify and verify an application's claim. Applications own claim definitions, event qualification, and time evidence under Freenet's normal process. |
| Ghost Key event | Verify possession and the issuer chain when crediting the event. Prove the event later without showing the certificate. Treat the event as donation evidence, and account for payments separately. |
| Execution | Generate proofs privately on the peer and verify them on the recipient's peer. Public event-admission proofs also need a contract-compatible verifier. Define validation on updates and full-state receipt. |
| Cost | Measure generation time, memory, proof size, verification time, and full-state validation as passes and receipts grow. Include mobile peers and hosted concurrency. |

The research compares proof systems across this complete flow, including existing credentials, anonymous credentials and membership proofs. Product adapters require a selected cryptographic profile that meets measured resource and privacy limits. Declared actions and custom applications request proof operations through their authorized host adapters and platform SDK. They receive public results while the protected prover retains private evidence.

Compare the complete flow with [Ghost Key credential benchmarks](https://github.com/freenet/web/issues/25#issuecomment-5162479374). Proof verification must fit the contract runtime's execution budget. If verification needs an external service issuing signed attestations, document the added trust and availability dependency.

## 5. Research questions and dependencies

These sources inform the proof design and its acceptance tests.

| Source | Application in this plan |
| --- | --- |
| [Security architecture #5380](https://github.com/freenet/freenet-core/discussions/5380) and [client identity #5264](https://github.com/freenet/freenet-core/issues/5264) | Implement authenticated proof requests, explicit shared-pass grants, private delegate evidence and recovery. Include hosted operators in the trust boundary. |
| [Rate limiting #601](https://github.com/freenet/freenet-core/discussions/601) and its [contract sketch](https://github.com/freenet/freenet-core/discussions/601#discussioncomment-5714500) | Bind hidden membership proofs to exact actions. Credit each source event once and apply local receiver quotas to repeated use. |
| [Multi-Purpose Trust Network #458](https://github.com/freenet/freenet-core/issues/458) | Define separate claim types. Let applications choose sources, evidence requirements and responses. |
| [DRIP #443](https://github.com/freenet/freenet-core/discussions/443) and its [circular-trust critique](https://github.com/freenet/freenet-core/discussions/443#discussioncomment-4504162) | Specify sponsorship discovery, cooldowns and limits on related sponsors. Test collusion and shared credentials. |
| [Proof-of-Trust #799](https://github.com/freenet/freenet-core/discussions/799) | Research participation and sponsorship as free contribution paths. Assess the wealth bias of donation evidence wherever applications accept it. |
| [Web of trust and anonymity #133](https://github.com/freenet/freenet-core/discussions/133) | Implement shared hidden membership, rotation, retirement, recovery and safeguards against identifying a pass through narrow pools. |
| [Anonymous reputation #882](https://github.com/freenet/freenet-core/discussions/882) | Prototype private receipts and measure the complete proof flow. Test manufactured activity under application rules. |
| [Karma #11](https://github.com/freenet/freenet-core/issues/11) | Define evidence for relay and hosting contributions, including delivery checks and disputes. |
| [Symmetric NAT relays #2925](https://github.com/freenet/freenet-core/issues/2925) and [contract-hardening.md](https://github.com/freenet/freenet-core/blob/08798042093a24d2e0c9d2dc744e570500747aa5/docs/design/contract-hardening.md) | Research verifiable relay receipts and collusion. The [mobile SDK plan](../freenet-mobile/README.md) defines mobile participation and relay admission. |
| [Ghost Key research](https://github.com/freenet/web/issues/25) and [Mail policy #70](https://github.com/freenet/mail/issues/70) | Implement certificate-hiding proofs bound to the sender, recipient and message. Specify attestation encryption and Mail integration. |
| [Harvest incentive mechanism](https://github.com/freenet/harvest/blob/main/docs/design/incentive-mechanism.md) and [design notes](https://github.com/freenet/harvest/blob/main/docs/design/README.md) | Define signed order evidence and receiver policy. Keep seller standing, payment proofs, order exposure, refunds and complaints in the marketplace's accounting rules. |

## 6. Delivery and acceptance

| Phase | Delivers |
| --- | --- |
| Claim interfaces | Versioned claim/source/action binding, canonical encoding, public result and refusal types |
| Private receipt prototype | Distinct events bind to one hidden pass, with source validation and recovery fixtures |
| Proof-system assessment | Complete-flow benchmarks, privacy analysis, mobile memory/time limits and an explicit selected profile |
| Host integration | Application/user grants, protected witnesses, session cancellation and request-history enforcement |
| Optional product adapter | Optional Marketplace claim issuance and purpose-bound verification |

Tests cover replay to another recipient, changed actions/attachments, duplicate event credit, fabricated activity, related sponsors, shared credentials, revoked or stale membership evidence, narrowed anonymity pools, repeated thresholds, exhausted budgets and restored witness state. Verify both update admission and full-state validation when proofs enter public contracts.

Measure proof generation and verification on target mobile devices and under hosted concurrency. The selected profile sets limits for proof size, peak memory and full-state validation cost. Tests verify those limits and the behavior when they are exceeded. Missing, declined, stale and invalid proofs have distinct results. Ordinary Marketplace flows, mobile access, payment and remuneration must pass with the optional adapter disabled.

Applications own the rules for refunds, complaints, account balances and sanctions. Each reputation claim states its source-defined evidence and limits. For example, 20 days of River activity proves participation under River's rules.

## 7. Further reading

The [Harvest comparison](../marketplace/harvest-comparison.md) explains seller standing and payment-backed complaints. These sources cover the wider identity and reputation design:

| Source | Design question |
| --- | --- |
| [Anonymous keypair generation and blind donation verification](https://github.com/freenet/freenet-core/issues/602) | How can a peer prove donation-backed identity while hiding the donation link? |
| [Atlas reputation proposal](https://github.com/freenet/atlas/blob/main/PROPOSAL.md#ghostkeys-integration) | How can discovery use persistent identities, trust weights, signed feedback and analyzer reputation? |
| [Whitepaper security and trust boundaries](https://github.com/freenet/paper-1/blob/main/sections/06-trust.tex) | How can application-layer reputation establish trust when its own contracts depend on routing exposed to Sybil attacks? |
| [Whitepaper limitations and open problems](https://github.com/freenet/paper-1/blob/main/sections/07-status.tex) | Which consistency mechanisms support revocation, slashing and balance reduction alongside accumulating endorsements? |
