# 3.7 Bitcoin payments

## Purpose

Research Bitcoin payments for EVY physical-goods purchases. Owner: EVY payments lead.

## When this becomes a plan

Define custody, trusted bridges, confirmations, refunds and contributor-fee handling. Verifiable payment evidence gives peers a defined way to establish settlement and respond to chain reorganizations. Release requires the evidence model and matching iOS and Android payment/recovery fixtures.

Bitcoin has a separate start decision: buyers or sellers request it, and EVY selects a supported custody and payment-evidence model. Its implementation can proceed independently of saved cards.

[freenet-bitcoin](https://github.com/freenet/freenet-bitcoin) publishes SPV payment evidence for peers to check. Evaluate its proof/bridge authority against the EVY purchase evidence model in [2.12 Listings and purchases](../2-evy-on-freenet/12-listings-and-purchases.md). Before this becomes implementation work, define real-chain anchoring, trusted bridges, confirmation and reorganization handling, refund behavior, and how a 70-dollar purchase supplies the 0.70-dollar contributor fee. Add matching iOS and Android payment and recovery acceptance cases to that implementation plan.

## Sources

- [freenet-bitcoin #27](https://github.com/freenet/freenet-bitcoin/issues/27): Real-chain anchoring before payment-proof acceptance
- [Delegated watch keys #30](https://github.com/freenet/freenet-bitcoin/pull/30): Bridge address-watch authority and recovery
