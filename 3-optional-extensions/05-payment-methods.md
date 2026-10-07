# 3.5 Saved payment methods

## Repositories

| Repository | Role | Work in this plan |
| --- | --- | --- |
| [evy](https://github.com/EVY-Platform/evy) | Modified | Stripe customers in `services/payment`; saved cards in the iOS and Android payment sheet. A bitcoin payment record in the purchase contract |
| [stripe-ios](https://github.com/stripe/stripe-ios), [stripe-android](https://github.com/stripe/stripe-android) | Used | Payment sheet with saved cards |
| [freenet-bitcoin](https://github.com/freenet/freenet-bitcoin) | Used | Bitcoin payment evidence |
| [harvest](https://github.com/freenet/harvest) | Used | Bitcoin payment proof in orders |

## Purpose

This plan is an idea note for saved cards and bitcoin payments. [Paying on a phone in 2.6 Payments](../2-evy-on-freenet/06-payments.md#paying-on-a-phone) has Bob enter his card for each purchase. His EVY delegate key identifies him across services, so those services could share a saved card.

Saving a card during payment on iOS and Android requires three additions to EVY's [PaymentIntent creation](https://github.com/EVY-Platform/evy/blob/dev/api/src/procedures/stripeGateway.ts):

- Name a Stripe Customer.
- Pass a CustomerSession client secret to the payment sheet.
- Set `setup_future_usage` on the PaymentIntent.

Stripe's [save-during-payment flow](https://docs.stripe.com/payments/mobile/save-during-payment) then shows the saved cards in the payment sheet.

Bitcoin payments could use [freenet-bitcoin](https://github.com/freenet/freenet-bitcoin). Its bridge publishes SPV payment evidence for peers to check. Harvest embeds this evidence in each order and lets the seller name trusted bridges ([payment.rs](https://github.com/freenet/harvest/blob/main/common/src/payment.rs)).

## When this becomes a plan

Work starts when buyers ask EVY to save a card. For example, Bob may want to reuse his card for a second Marketplace purchase.

| Need | What the plan must decide |
| --- | --- |
| Bob buys again and expects his card | Which EVY key identifies Bob's Stripe Customer in `services/payment`. The EVY delegate signs each request with Bob's key as proof of identity |
| Bob removes a card or forgets EVY | How EVY detaches the card in Stripe and deletes the Customer after the last key association is removed |
| Bob restores on a new phone or links his tablet | How [3.1 Automated backup](01-backup.md) and [3.2 Device sync](02-sync.md) restore the EVY key that identifies his Customer |
| Bob pays Alice in bitcoin | How EVY collects the 1% contributor fee of 0.70 dollars in a bitcoin purchase, and which bridges the purchase contract trusts |

## Sources

| Source | Relevant design |
| --- | --- |
| [Stripe: save payment details during an in-app payment](https://docs.stripe.com/payments/mobile/save-during-payment) | Customer, CustomerSession client secret and `setup_future_usage` for the iOS and Android payment sheet |
| [freenet-bitcoin](https://github.com/freenet/freenet-bitcoin), [#27](https://github.com/freenet/freenet-bitcoin/issues/27) and [delegated watch keys #30](https://github.com/freenet/freenet-bitcoin/pull/30) | Bridge-signed payment claims with SPV evidence. Real-chain anchoring is required before using these proofs for payments. A background process can ask the bridge to watch an address |
| [Harvest payment.rs](https://github.com/freenet/harvest/blob/main/common/src/payment.rs) | Bitcoin payment proof embedded in each order, checked against the bridges the seller names |
