# 3.5 Saved payment methods

## Repositories

| Repository | Role | Work in this plan |
| --- | --- | --- |
| [evy](https://github.com/EVY-Platform/evy) | Modified | Stripe customers in `services/payment`; saved cards in the iOS and Android payment sheet. A bitcoin payment record in the purchase contract |
| [stripe-ios](https://github.com/stripe/stripe-ios), [stripe-android](https://github.com/stripe/stripe-android) | Used | Payment sheet with saved cards |
| [freenet-bitcoin](https://github.com/freenet/freenet-bitcoin) | Used | Bitcoin payment evidence |
| [harvest](https://github.com/freenet/harvest) | Used | Bitcoin payment proof in orders |

## Purpose

This plan is an idea note. Bob enters his card in Stripe's payment sheet for each purchase, as [Paying on a phone in 2.6 Payments](../2-evy-on-freenet/06-payments.md#paying-on-a-phone) describes. The EVY delegate gives Bob one identity across EVY's services, so one saved card could serve every service.

Stripe's payment sheet on iOS and Android shows saved cards when the server names a Stripe Customer, passes the sheet a CustomerSession client secret and sets `setup_future_usage` on the PaymentIntent ([save during payment](https://docs.stripe.com/payments/mobile/save-during-payment)). EVY's payment code creates PaymentIntents with no Customer today ([stripeGateway.ts](https://github.com/EVY-Platform/evy/blob/dev/api/src/procedures/stripeGateway.ts)).

A second payment method could use [freenet-bitcoin](https://github.com/freenet/freenet-bitcoin), whose bridge publishes SPV evidence of a payment that any peer can check. Harvest embeds this evidence in each order, and the seller names the bridges it trusts ([payment.rs](https://github.com/freenet/harvest/blob/main/common/src/payment.rs)).

## When this becomes a plan

This plan starts when buyers ask EVY to keep their card, for example when Bob buys from Marketplace a second time and types his card again.

| Need | What the plan must decide |
| --- | --- |
| Bob buys again and expects his card | Which key names Bob's Stripe Customer in `services/payment`. EVY has no sign-in, so the EVY delegate signs each request with Bob's EVY key |
| Bob removes a card or forgets EVY | How EVY detaches the card in Stripe and deletes the Customer once no key names it |
| Bob restores on a new phone or links his tablet | A check that [3.1 Automated backup](01-backup.md) and [3.2 Device sync](02-sync.md) bring back the EVY key that names his Customer |
| Bob pays Alice in bitcoin | How EVY collects the 1% contributor fee of 0.70 dollars without Stripe, and which bridges the purchase contract trusts |

## Sources

| Source | What it offers |
| --- | --- |
| [Stripe: save payment details during an in-app payment](https://docs.stripe.com/payments/mobile/save-during-payment) | Customer, CustomerSession client secret and `setup_future_usage` for the iOS and Android payment sheet |
| [freenet-bitcoin](https://github.com/freenet/freenet-bitcoin), [#27](https://github.com/freenet/freenet-bitcoin/issues/27) and [delegated watch keys #30](https://github.com/freenet/freenet-bitcoin/pull/30) | Bridge-signed payment claims with SPV evidence. Proofs are not yet anchored to the real chain. A background process can ask the bridge to watch an address |
| [Harvest payment.rs](https://github.com/freenet/harvest/blob/main/common/src/payment.rs) | Bitcoin payment proof embedded in each order, checked against the bridges the seller names |
