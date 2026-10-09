# 3.5 Saved payment methods

## Repositories

| Repository | Role | Work in this plan |
| --- | --- | --- |
| [evy](https://github.com/EVY-Platform/evy) | Modified | Stripe customers in `services/payment`; saved cards in the iOS and Android payment sheet. |
| [stripe-ios](https://github.com/stripe/stripe-ios), [stripe-android](https://github.com/stripe/stripe-android) | Used | Payment sheet with saved cards |

## Purpose

This plan is an idea note for saved cards. [Paying on a phone in 2.6 Payments](../2-evy-on-freenet/06-payments.md#paying-on-a-phone) has Bob enter his card for each purchase. A dedicated user payment key can authenticate his Stripe Customer inside EVY for the features he enables.

Saving a card during payment on iOS and Android requires three additions to EVY's [PaymentIntent creation](https://github.com/EVY-Platform/evy/blob/d0fb7e6475f1dfc5c74325e37d4e92aed88d84ed/api/src/procedures/stripeGateway.ts):

- Name a Stripe Customer.
- Pass a CustomerSession client secret to the payment sheet.
- Set `setup_future_usage` on the PaymentIntent.

Stripe's [save-during-payment flow](https://docs.stripe.com/payments/mobile/save-during-payment) then shows the saved cards in the payment sheet.

### Customer identity

A reusable customer profile lets Bob use a saved card across selected features; consent explains the resulting link between those purchases. Define profile recovery and revocation alongside that consent, and verify them with iOS and Android identity/recovery fixtures.

When Bob opts in, the EVY delegate creates a random Ed25519 payment-customer key and stores it under `payments/customer/<profile_id>`. The payment service associates its public key with Bob's Stripe Customer. The delegate's `DelegateKey` identifies the code and parameter namespace that holds this secret; the customer key identifies Bob to the payment service. Feature and purchase-scoped keys retain their roles from [The EVY delegate in 2.11 EVY delegate and private records](../2-evy-on-freenet/11-delegate-and-private-records.md#the-evy-delegate).

The implementation plan defines `profile_id` as a random UUID created once at opt-in, with one active customer profile per EVY identity. The delegate owns its customer key and consent feature list; the payment backend maps `(application_key, profile_id, customer_public_key)` to one Stripe Customer and verifies key possession before restoring access. Backups and sync preserve the ID, key and consent version. Rotation preserves that association through signed old-to-new proof; revocation and remote cleanup name the same profile. Additional profiles require an explicit product decision and migration/consent fixtures.

A request carries a short-lived payment-service challenge, audience, requested operation, EVY application identity, originating feature and purchase context. The delegate checks the trusted caller, Bob's enabled EVY features and the verified purchase context, then signs with the customer key. The payment service verifies that signature and separately verifies the purchase's buyer authorization before returning customer-session access. Repeated or expired challenges follow the service's idempotency and expiry rules.

The opt-in screen explains that the payment service can link purchases using this customer profile across the selected EVY features. Bob controls that feature list. The feature extends `ExportRecords` and `ImportRecords`, manual backup, [3.1 Automated backup](01-backup.md) and [3.2 Device sync](02-sync.md) to preserve the customer key and feature choices. Key rotation requires a signed old-to-new association or an explicit account-recovery process; the implementation plan defines how that process verifies Bob and retires the previous key.

## When this becomes a plan

Work starts when buyers ask EVY to save a card. For example, Bob may want to reuse his card for a second Marketplace purchase.

| Need | What the plan must decide |
| --- | --- |
| Bob buys again and expects his card | A customer-key challenge proves access to his profile, and purchase-scoped authorization proves permission for this payment. Tests cover substituted customers, application identity, features and purchase contexts |
| Bob removes a card or forgets EVY | Define detaching a Stripe payment method, closing the customer profile and local Forget as distinct actions. Record remote cleanup acknowledgements and retry pending cleanup before reporting it complete |
| Bob restores on a new phone or links his tablet | Preserve the customer key and consent records through manual backup, [3.1 Automated backup](01-backup.md) and [3.2 Device sync](02-sync.md); verify that the same profile returns after restore and that retired customer keys fail authentication |

## Sources

- [Stripe: save payment details during an in-app payment](https://docs.stripe.com/payments/mobile/save-during-payment): Customer, CustomerSession client secret and `setup_future_usage` for the iOS and Android payment sheet
