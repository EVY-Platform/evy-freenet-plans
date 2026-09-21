# Fulfillment requests

Parent: [Neighborhood marketplace](README.md).

Bob proposes Saturday pickup for Alice's skateboard. This plan defines how that request gets its identity, how it reaches Alice through bounded public and granted contracts, and how its encrypted content stays private. The [Marketplace plan](README.md#5-structured-fulfillment-requests) lists the actions and the end-to-end flow.

## 1. Record identity

Each domain record carries its schema version, application identity, logical request ID, author, recipient, order and listing reference, terms revision and causal predecessor. Four rules give it an identity:

1. Derive the record ID from a domain-separated canonical encoding of every unsigned field, excluding the record ID and the signature.
2. Sign the content together with that derived ID.
3. After encryption and envelope signing, derive the storage entry digest from the complete final envelope bytes.
4. Validators recompute each identity at the boundary where it applies.

A retry preserves the logical operation ID and the original signed bytes. A counterproposal creates a new record. Participant journals retain observed conflicting variants within their disclosed evidence limits.

## 2. Public first contact and bounded transport

Each listing advertises a seller-signed current request generation. V1 permits public first contact through a bounded admission contract, then moves the conversation to a continuation page the seller grants. Both contracts merge by deterministic set union followed by their selection rule. These constants form the v1 wire profile, and the maximum canonical state size is tested from the codec.

| Contract | Record limit | Capacity | Selection rule |
| --- | --- | --- | --- |
| Public admission | 4 KiB including signed envelope and padded ciphertext | 64 records | Keep the lowest full content digests |
| Granted continuation | 4 KiB per record | 16 slots per participant | Keep the two lowest storage digests per slot |

This bounds storage and makes replicas converge. Admission remains vulnerable to competition for the available slots. A sender can grind digests or fill the area and displace an honest request. The reader reports `Awaiting seller receipt`, `Request absent from current set`, or `Admission saturated` according to observed evidence. The host keeps the original signed request locally and retries within budgets. Delivery status requires a signed seller receipt. The seller can open a new request generation so clients can retry. A sustained attack can fill that generation too.

Once the seller admits a request, it issues a signed grant bound to the application, page identity and generation, permitted participant writer, order and request ID, slot range, schema version and maximum record size.

A replica can receive continuation records before the grant that authorizes them. Every delta carries the grant record together with the operations that reference it. A delta whose grant is absent is rejected in full, so the sender re-offers it with the grant attached. Discarding only the unauthorized part would lose records that a later grant makes valid.

Two distinct records in one slot prove that its writer signed competing records. Set the slot to `Conflicted` and block the corresponding domain transition. Every retained conflict witness passes the same writer, grant and signature checks as an ordinary record. Extra observed variants can survive in participant journals within disclosed local limits.

Both participants sign a successor-page reference and agreed checkpoint when capacity is exhausted. Recovery and dispute access depend on retained network copies and recovery-covered participant journals.

Full-state and delta validation apply the same encoding, signature, grant, digest and size rules. Property tests must prove associativity, commutativity, idempotence, batch invariance and maximum encoded size for both admission and continuation contracts. Empty bootstrap state has explicit handling. Eviction follows the digest selection rule. Contract expiry requires explicit time evidence or signed participant action.

## 3. Encryption, acceptance and recovery

Use one reviewed, versioned cryptographic profile. Bind routing and context fields to authenticated encryption, derive keys separately by direction, and independently sign domain records. Participant signatures establish authorship. Keep encryption/signing keys in delegates or platform-protected storage.

Limits apply before expensive decoding and decryption. Encrypt permitted attachments separately and address them by ciphertext digest. Keep names, previews and sensitive metadata encrypted. Enforce count, byte and decode limits in the trusted host. Describe ciphertext retention, compromised-key handling and forward-secrecy expectations in the profile.

A signed admission receipt means the recipient verified and persisted the record locally. It differs from accepting the proposed terms, making payment, dispatching goods or confirming delivery. Update the processed-operation marker and resulting local state atomically. Retrying a previously processed record returns the same result. Side effects use their own stable operation IDs.

Sender queues survive restart and uncertain submission. The host re-fetches records, obtains delegate reconciliation results and republishes eligible pending records within its budgets, including a bounded previous-generation window. A local retry deadline stops local attempts. Appointment times express the participants' agreed schedule. Contract expiry requires explicit time evidence or signed participant action.

Recovery, cross-device transfer and the [forget operation](../identity/README.md#2-protected-keys-and-records) follow the identity plan. Confirm persistence of private order evidence before payment. Forgetting an active order warns that its keys or evidence may be needed for fulfillment or a claim. The domain delegate filters records from blocked keys before presentation and acknowledgment. Cache deterministic malformed-record refusals so repeated updates cannot trigger endless key derivation. Per-session CPU, download and storage budgets remain effective during a flood.
