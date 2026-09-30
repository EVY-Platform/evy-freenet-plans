# 5.6 Shared identity and payment

## Repositories

| Repository | Role | Work in this plan |
| --- | --- | --- |
| [ghostkeys](https://github.com/freenet/ghostkeys) | Used | A delegate that signs for any app after the user allows it, as the model for a shared identity delegate |
| [freenet-core](https://github.com/freenet/freenet-core) | Used | Core attests which app calls a delegate, so a shared delegate knows who asks |
| [evy](https://github.com/EVY-Platform/evy) | Used | `services/payment` and the Stripe payment sheet in the `ios/` and `android/` apps |

## Purpose

This plan is an idea note. EVY's vision is one identity and one payment setup across every app. The plans build neither yet:

- Each app has its own keys and its own secret scope under [2.2 Two apps on one node](../2-evy-mobile-app/02-shared-node.md#forgetting-one-app). Bob in River and Bob in Marketplace are two unlinked identities, and forgetting one app leaves the other untouched.
- Bob enters his card in Stripe's payment sheet for each sale under [3.4 Payments and checkout](../3-attribution-remuneration-payment/04-payment.md#checking-out-on-a-phone).

A shared identity would be a delegate in its own secret scope that signs for any app Bob allows, as the [Ghostkeys delegate](https://github.com/freenet/ghostkeys#scoped-signatures) does. Each signature names the calling app, so one app cannot replay it in another. A shared payment setup would let Stripe's payment sheet [show Bob's saved cards](https://docs.stripe.com/payments/mobile/save-during-payment).

## When this becomes a plan

This plan starts when a second app in EVY needs one of these.

| Need | What the plan must decide |
| --- | --- |
| Marketplace shows that the buyer Bob is the Bob from Alice's "Skate club" room | How Bob allows each app to link to the shared identity, and how he unlinks it. By default apps stay unlinked |
| Bob buys from a second paid app and expects his saved card | Which key identifies Bob to Stripe, since EVY has no sign-in. How forgetting EVY removes the saved card |
| Bob restores EVY on a new phone | How [5.1 Automated backup](01-backup.md) carries the shared identity's scope beside each app's scope |

## Sources

| Source | What it offers |
| --- | --- |
| [Ghostkeys scoped signatures](https://github.com/freenet/ghostkeys#scoped-signatures) | A signature bound to the runtime-attested identity of the calling app |
| [Stripe saved payment details on mobile](https://docs.stripe.com/payments/mobile/save-during-payment) | The payment sheet saves a card to a Stripe customer and shows it on the next payment |
| [2.2 Two apps on one node](../2-evy-mobile-app/02-shared-node.md#forgetting-one-app) | The per-app secret scope a shared identity would sit beside |
