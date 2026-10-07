# 3.3 Peer reputation

## Repositories

| Repository | Role | Work in this plan |
| --- | --- | --- |
| [evy](https://github.com/EVY-Platform/evy) | Used | Completed purchases in purchase contracts |
| [ghostkeys](https://github.com/freenet/ghostkeys) | Used | Scoped ghost key signatures |
| [harvest](https://github.com/freenet/harvest) | Used | Seller complaints and standing |
| [web](https://github.com/freenet/web) | Used | Ghost key research |

## Purpose

This plan is an idea note for a private reputation proof in EVY Marketplace.

Freenet apps use the [Ghostkeys delegate](https://github.com/freenet/ghostkeys#integrating-with-ghostkeys) for spam limits and seller trust:

1. The app reads the delegate's current key from `delegate-key.json` in the Ghostkeys vault's website container. Each delegate Wasm build changes the key ([ghostkeys#21](https://github.com/freenet/ghostkeys/issues/21)).
2. The delegate asks Bob to allow the request.
3. It returns a [signature over the message and the caller's identity](https://github.com/freenet/ghostkeys#scoped-signatures), with Bob's ghost key certificate.
4. The certificate proves a card donation to Freenet through Stripe and records its amount and date ([D1189](https://github.com/freenet/freenet-core/discussions/1189)).

Harvest accepts complaints from paying buyers. The order's receipt key signs each complaint. This identifies the order and keeps the buyer's ghost key private. Harvest's planned seller-standing system uses a donation bond that complaints withdraw from ([harvest#8](https://github.com/freenet/harvest/issues/8)).

## When this becomes a plan

Work starts when EVY Marketplace needs evidence of completed purchases or an unlinkable ghost key proof. For example, Alice may request either claim when Bob asks to buy her 70-dollar skateboard in [The skateboard sale in 2.7 EVY Marketplace](../2-evy-on-freenet/07-marketplace.md#the-skateboard-sale).

| Claim | Evidence and privacy requirements |
| --- | --- |
| Bob completed 5 pickups in the last 90 days while keeping sellers, items and dates private | Each completed purchase has statuses and a payment-service-signed payment record in a [purchase contract from 2.6 Payments](../2-evy-on-freenet/06-payments.md#the-purchase-contract). The proof must verify those purchases and hide their details. A ghost key signature proves key possession. Harvest publishes order commitments for counting and proposes [zero-knowledge proofs](https://github.com/freenet/harvest/blob/main/docs/design/incentive-mechanism.md#part-8--what-this-publishes-to-the-world) to hide them |
| Bob holds a ghost key while keeping its identity private | The proof must hide the certificate. Ghost key signatures carry the same certificate, which lets services link requests. An "always allow" grant lasts indefinitely; expiry and revocation controls remain open work ([ghostkeys#49](https://github.com/freenet/ghostkeys/issues/49)) |

Zero-knowledge proofs can take seconds to minutes to build ([D882](https://github.com/freenet/freenet-core/discussions/882)). This plan selects a proof system and measures it on both iOS and Android. The iOS test device is the iPhone 13 mini used in [1.1 Mobile feasibility and supported profiles](../1-freenet-mobile-appkit/01-feasibility.md#device-limits).

The EVY delegate must build each proof within the 5-second Wasm limit and 256 MiB per instance under Pulley ([Running Wasm in 1.2 Embedded node and mobile SDK](../1-freenet-mobile-appkit/02-sdk.md#running-wasm)). Request limits must prevent a service from narrowing down Bob's count through repeated threshold requests.

A scoped signature identifies its caller by a web app contract or delegate key. This plan defines requests from the native EVY app through the EVY delegate. That path requires the replies between delegates proposed in [RFC #5587](https://github.com/freenet/freenet-core/issues/5587).

## Sources

| Source | Relevant research |
| --- | --- |
| [Unlinkable ghost key presentation, web #25](https://github.com/freenet/web/issues/25) | Anonymous credentials (BBS+) hide the signing certificate. Benchmarks show verification exceeds the 5-second Wasm limit above about 13 members. Each service would need a voucher to use this method |
| [One-time ghost key bundles, ghostkeys #2](https://github.com/freenet/ghostkeys/issues/2) | One key per action hides the signing ghost key at a lower cost. Closed proposal |
| [Ghost key library, web `rust/gklib`](https://github.com/freenet/web/tree/main/rust/gklib) | Ghost key certificates issued with blind RSA signatures (`blind-rsa-signatures`) |
| [Harvest seller standing #8](https://github.com/freenet/harvest/issues/8), [purchase flow PR #21](https://github.com/freenet/harvest/pull/21) and [messaging PR #23](https://github.com/freenet/harvest/pull/23) | A proposed donation bond bound to a ghost key, with complaints that withdraw from it. Certificate checks for remote sellers |
| [Rate-limiting nullifiers #601](https://github.com/freenet/freenet-core/discussions/601) | The receiving contract enforces per-epoch action limits while hiding membership. Exceeding the limit reveals the key |
| [Anonymous reputation #882](https://github.com/freenet/freenet-core/discussions/882) | Anonymous feedback receipts that prove buyer and seller are different people. Proofs take seconds to minutes with RISC Zero |
