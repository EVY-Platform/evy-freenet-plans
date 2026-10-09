# 3.7 Bitcoin payments

## Purpose

Research Bitcoin payments for EVY physical-goods purchases. Owner: EVY payments lead.

## When this becomes a plan

Define custody, trusted bridges, confirmations, refunds and contributor-fee handling. Relevant Freenet maintainers agree changes to Bitcoin bridge/proof interfaces before their feature PRs. Verifiable payment evidence gives peers a defined way to establish settlement and respond to chain reorganizations. Release requires the agreed evidence model and matching iOS and Android payment/recovery fixtures.

Bitcoin has a separate start decision: buyers or sellers request it, and EVY selects a supported custody and payment-evidence model. Its implementation can proceed independently of saved cards.

[freenet-bitcoin](https://github.com/freenet/freenet-bitcoin) publishes SPV payment evidence for peers to check. Harvest embeds this evidence in each order and lets the seller name trusted bridges ([payment.rs](https://github.com/freenet/harvest/blob/9eb4a04ed30e75c478df0b89f38f68044bbd947c/common/src/payment.rs)). Before this becomes implementation work, define real-chain anchoring, trusted bridges, confirmation and reorganization handling, refund behavior, and how a 70-dollar purchase supplies the 0.70-dollar contributor fee. Add matching iOS and Android payment and recovery acceptance cases to that implementation plan.

## Sources

- [freenet-bitcoin #27](https://github.com/freenet/freenet-bitcoin/issues/27): Real-chain anchoring before payment-proof acceptance
- [Delegated watch keys #30](https://github.com/freenet/freenet-bitcoin/pull/30): Bridge address-watch authority and recovery
- [Harvest payment.rs](https://github.com/freenet/harvest/blob/9eb4a04ed30e75c478df0b89f38f68044bbd947c/common/src/payment.rs): Order proof verification against seller-selected bridges
