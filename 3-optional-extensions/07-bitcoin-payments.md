# 3.7 Bitcoin payments

## Repositories

| Repository | Role | Work in this plan |
| --- | --- | --- |
| [evy](https://github.com/EVY-Platform/evy) | Modified | Bitcoin payment option in `api/src/modules/payment` and in the iOS and Android readers |
| [freenet-bitcoin](https://github.com/freenet/freenet-bitcoin) | Used | SPV payment evidence that peers can check |

## Purpose

This plan is an idea note for Bitcoin payments in EVY physical-goods purchases, such as Bob paying Alice for her 70-dollar skateboard.

## When this becomes a plan

Work starts when buyers or sellers ask to pay with Bitcoin and EVY picks a custody and payment-evidence model.

[freenet-bitcoin](https://github.com/freenet/freenet-bitcoin) publishes SPV payment evidence for peers to check. Compare its proof and bridge authority with the purchase evidence in [The purchase contract in 2.7 EVY Marketplace](../2-evy-on-freenet/07-marketplace.md#the-purchase-contract). The plan must then define:

- custody and trusted bridges
- anchoring to the real chain
- confirmations and chain reorganizations
- refunds
- how a 70-dollar purchase supplies the 0.70-dollar contributor fee

Release needs matching iOS and Android payment and recovery tests.

## Sources

- [freenet-bitcoin #27](https://github.com/freenet/freenet-bitcoin/issues/27): Real-chain anchoring before payment-proof acceptance
- [Delegated watch keys #30](https://github.com/freenet/freenet-bitcoin/pull/30): Bridge address-watch authority and recovery
