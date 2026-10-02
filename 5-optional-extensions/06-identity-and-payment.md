# 5.6 Shared identity and payment

## Repositories

| Repository | Role | Work in this plan |
| --- | --- | --- |
| [ghostkeys](https://github.com/freenet/ghostkeys) | Used | Shared identity delegate model |
| [freenet-core](https://github.com/freenet/freenet-core) | Used | Calling-app attestation |
| [freenet-bitcoin](https://github.com/freenet/freenet-bitcoin) | Used | Bitcoin payment evidence |
| [evy](https://github.com/EVY-Platform/evy) | Used | iOS and Android payment setup |
| [raven](https://github.com/freenet/raven) | Used | Single-app identity example |

## Purpose

This plan is an idea note. EVY's vision is one identity and one payment setup across every app. Each app keeps its own identity and payment step:

- Each app has its own keys and its own secret scope under [2.1 EVY catalogue and app hosting](../2-evy-mobile-app/01-catalogue-and-hosting.md#secret-scopes). Bob in River and Bob in Marketplace are two unlinked identities, and forgetting one app leaves the other untouched.
- Bob enters his card in Stripe's payment sheet for each sale under [3.4 Payments and checkout](../3-attribution-remuneration-payment/04-payment.md#checking-out-on-a-phone).

A shared identity would be a delegate in its own secret scope that signs for any app Bob allows, as the [Ghostkeys delegate](https://github.com/freenet/ghostkeys#scoped-signatures) does. Each signature names the calling app, so one app cannot replay it in another. Apps would find the delegate through a published `delegate-key.json`, as they find the Ghostkeys delegate, because a delegate key changes with every Wasm build ([ghostkeys#21](https://github.com/freenet/ghostkeys/issues/21)). A passkey brokered by the shell is another way to hold the shared identity ([#5764](https://github.com/freenet/freenet-core/issues/5764)). It syncs across Bob's devices through iCloud Keychain on iOS or Google Password Manager on Android, with the origin limit that [Recovery code in 1.5 Identity, keys and local protection](../1-freenet-mobile-appkit/05-identity.md#recovery-code) notes.

A shared payment setup would let Stripe's payment sheet [show Bob's saved cards](https://docs.stripe.com/payments/mobile/save-during-payment). A payment path beside Stripe could use [freenet-bitcoin](https://github.com/freenet/freenet-bitcoin), whose bridge publishes signed claims with SPV evidence that any peer can re-check. Trust in those claims rests on a bridge the reader's app recognises ([freenet-bitcoin#27](https://github.com/freenet/freenet-bitcoin/issues/27)).

## When this becomes a plan

This plan starts when a second app in EVY needs one of these.

| Need | What the plan must decide |
| --- | --- |
| Marketplace shows that the buyer Bob is the Bob from Alice's "Skate club" room | How Bob allows each app to link to the shared identity, and how he unlinks it. By default apps stay unlinked. The Ghostkeys delegate has `RevokePermission`, and no screen calls it yet ([ghostkeys#49](https://github.com/freenet/ghostkeys/issues/49)) |
| Bob buys from a second paid app and expects his saved card | Which key identifies Bob to Stripe, since EVY has no sign-in. How forgetting EVY removes the saved card |
| Bob restores EVY on a new phone | How [5.1 Automated backup](01-backup.md) carries the shared identity's scope beside each app's scope |

## Sources

| Source | What it offers |
| --- | --- |
| [freenet-bitcoin](https://github.com/freenet/freenet-bitcoin), [#27](https://github.com/freenet/freenet-bitcoin/issues/27) and [delegated watch keys #30](https://github.com/freenet/freenet-bitcoin/pull/30) | Bridge-signed payment claims with SPV evidence. Proofs are not yet anchored to the real chain. A background process can ask the bridge to watch an address |
| [raven](https://github.com/freenet/raven) | An ML-DSA-65 identity delegate that signs for one app |
