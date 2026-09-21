# Harvest comparison

Parent: [Neighborhood marketplace](README.md).

Marketplace draws on Harvest's purchase flow, privacy and seller-accountability designs. It uses its own code and contracts. The table identifies which Harvest ideas inform each part of the plan.

| Dimension | Harvest reference | Neighborhood marketplace plan |
| --- | --- | --- |
| Client and packaging | Rust common/contracts/delegate with a Dioxus web UI and reproducible contract builds | Per-target SDKs (TypeScript for the custom web app, the Rust-backed browser build for the web reader, native libraries for readers and native apps), declarative SDUI and domain delegates |
| Purchase interaction | Encrypted buyer/seller mailbox and purchase flow | Typed pickup, delivery and shipping requests |
| Payment | Bitcoin purchase flow with verification through a bridge | Payment-service Checkout with signed, order-bound status |
| Payment proof placement | Proof embedded in the order, and the trusted-bridge list moved from store parameters into the signed order ([integration status](https://github.com/freenet/harvest/blob/main/docs/bitcoin-integration-status.md)) | Bridge-signed record embedded in the order update. Root key in parameters, succession chain in the record |
| Economic design | Proposed donation-backed seller standing and identity-level exposure ledger | Contributor accounting with optional reputation claims |
| Discovery and fulfillment | Store-centric application | Neighborhood indexes, replaceable discovery provider and explicit local fulfillment terms |
| Privacy | Encrypted payloads alongside public order metadata | Explicit public identity/order links and encrypted precise logistics |
| Migration | Encoding and state compatibility across releases | Freenet migration helpers, application-specific selection rules and recovery tests |

Sources: [Harvest repository](https://github.com/freenet/harvest), [design index](https://github.com/freenet/harvest/blob/main/docs/design/README.md), [standing proposal #8](https://github.com/freenet/harvest/issues/8), [messaging PR #23](https://github.com/freenet/harvest/pull/23), [buy-flow PR #24](https://github.com/freenet/harvest/pull/24), and [migration notes](https://github.com/freenet/harvest/blob/main/docs/design/migratability.md).

Four purchase-flow rules apply to Marketplace:

- Bind accepted terms to the buyer's own request.
- Derive identifiers from complete terms so changing a price or destination creates a new identity.
- Verify published payment prerequisites independently of a transport response.
- Embed the payment proof in the order so a paid order validates on its own, with the bridge root key in parameters and key succession in the record.

## Seller standing and reputation

Harvest's seller-standing proposal links complaints to payment evidence. The [peer reputation](../reputation-proofs/README.md) plan explores private proofs of positive activity. Marketplace keeps those facts separate when applying its seller and dispute policies.

| Source | Design relevance |
| --- | --- |
| [Harvest v1, bonded sellers and pre-signed claims](https://github.com/freenet/harvest/issues/8) | Proposal for donation-backed seller standing, public order commitments, payment-backed complaints and refunds that restore standing. Covers exposure limits, buyer extortion, identity-level accounting and Bitcoin verification. |
| [Incentive mechanism design](https://github.com/freenet/harvest/blob/main/docs/design/incentive-mechanism.md) | Identity replacement, exit scams, false complaints, penalty multipliers and the privacy cost of publishing orders. The [design notes](https://github.com/freenet/harvest/blob/main/docs/design/README.md) explain payment-proof and timestamp constraints. |
| [Gaming the feedback system](https://github.com/freenet/harvest/issues/3) | Category-only feedback as a response to users putting positive messages inside negative categories. |
| [Feedback identity and signature coverage](https://github.com/freenet/harvest/issues/22) | Signature coverage for feedback text and categories, including competing variants and suppressed complaints. |
| [Purchase-flow security findings](https://github.com/freenet/harvest/pull/21) | Payment verification, Ghostkey identity checks and authorization for feedback-token creation. |
| [Buyer-seller messaging](https://github.com/freenet/harvest/pull/23) | Durable encrypted messaging that preserves the buyer's seller-signed claim. |
