# 3.3 Peer reputation

## Repositories

| Repository | Role | Work in this plan |
| --- | --- | --- |
| [evy](https://github.com/EVY-Platform/evy) | Used | Completed purchases in purchase contracts |
| [ghostkeys](https://github.com/freenet/ghostkeys) | Used | Scoped ghost key signatures |
| [harvest](https://github.com/freenet/harvest) | Used | Seller complaints and standing |
| [web](https://github.com/freenet/web) | Used | Ghost key research |

## Purpose

This plan is an idea note. It waits until EVY Marketplace needs a private reputation proof. Freenet apps that need spam limits or seller trust call the [Ghostkeys delegate](https://github.com/freenet/ghostkeys#integrating-with-ghostkeys) today. The app reads the delegate's current key from `delegate-key.json` in the Ghostkeys vault's website container, because the key changes with every delegate Wasm build ([ghostkeys#21](https://github.com/freenet/ghostkeys/issues/21)). The delegate asks Bob to allow the request. It then returns a [signature over the message and the caller's identity](https://github.com/freenet/ghostkeys#scoped-signatures), with Bob's ghost key certificate. The certificate proves a card donation to Freenet through Stripe and records its amount and date ([D1189](https://github.com/freenet/freenet-core/discussions/1189)).

Harvest, a Freenet marketplace, keeps complaints that only a paying buyer can make, each signed by the order's receipt key. They carry no ghost key. Seller standing as a donation bond that complaints withdraw from is Harvest's planned next phase ([harvest#8](https://github.com/freenet/harvest/issues/8)).

## When this becomes a plan

This plan starts when EVY Marketplace needs a claim that a ghost key signature cannot give. When Bob asks to buy Alice's 70-dollar skateboard in [The skateboard sale in 2.7 EVY Marketplace](../2-evy-on-freenet/07-marketplace.md#the-skateboard-sale), Alice might ask for one of these claims.

| Claim | Why a ghost key signature cannot give it |
| --- | --- |
| Bob completed 5 pickups in the last 90 days, without showing which sellers, items or dates | The evidence is Bob's completed purchases, each in a [purchase contract from 2.6 Payments](../2-evy-on-freenet/06-payments.md#the-purchase-contract) with its statuses and a payment record signed by the payment service key. A signature proves only that Bob holds a key. Harvest publishes each order commitment so buyers can count it, and names [zero-knowledge proofs](https://github.com/freenet/harvest/blob/main/docs/design/incentive-mechanism.md#part-8--what-this-publishes-to-the-world) as the way to hide them |
| Bob holds a ghost key, without showing which one | Every signature carries the same certificate, so two services can link Bob's requests. Once Bob allows a caller with "always allow", the grant has no expiry and no screen revokes it ([ghostkeys#49](https://github.com/freenet/ghostkeys/issues/49)) |

Zero-knowledge proofs can take seconds to minutes to build ([D882](https://github.com/freenet/freenet-core/discussions/882)). The plan then picks a proof system and measures it on the iPhone 13 mini that [1.1 Mobile feasibility and supported profiles](../1-freenet-mobile-appkit/01-feasibility.md#device-limits) measured, and on an Android phone. The EVY delegate builds each proof within the 5-second Wasm limit and 256 MiB per instance under Pulley ([Running Wasm in 1.2 Embedded node and mobile SDK](../1-freenet-mobile-appkit/02-sdk.md#running-wasm)). It limits how often one service can ask, so repeated threshold requests cannot narrow down Bob's count.

A scoped signature names its caller as a web app's contract or a delegate key. The native EVY app is neither, so the plan also decides how EVY asks: through the EVY delegate, once delegates can answer each other as [RFC #5587](https://github.com/freenet/freenet-core/issues/5587) proposes.

## Sources

| Source | What it offers |
| --- | --- |
| [Unlinkable ghost key presentation, web #25](https://github.com/freenet/web/issues/25) | Anonymous credentials (BBS+) that hide which certificate signed, with benchmarks. Past about 13 members a contract cannot check them inside the 5-second Wasm limit, so each service would need a voucher. We track it, because it would change how EVY checks ghost keys |
| [One-time ghost key bundles, ghostkeys #2](https://github.com/freenet/ghostkeys/issues/2) | A cheaper way to hide which ghost key signed, by spending one key per action. Its author closed it as not planned |
| [Ghost key library, web `rust/gklib`](https://github.com/freenet/web/tree/main/rust/gklib) | Ghost key certificates issued with blind RSA signatures (`blind-rsa-signatures`) |
| [Harvest seller standing #8](https://github.com/freenet/harvest/issues/8), [purchase flow PR #21](https://github.com/freenet/harvest/pull/21) and [messaging PR #23](https://github.com/freenet/harvest/pull/23) | The planned bond design (standing as a donation bound to a ghost key, with complaints that withdraw from it), and the shipped checks on a remote seller's certificate |
| [Rate-limiting nullifiers #601](https://github.com/freenet/freenet-core/discussions/601) | Hidden membership with per-epoch action limits that the receiving contract enforces. Going over the limit reveals the key |
| [Anonymous reputation #882](https://github.com/freenet/freenet-core/discussions/882) | Anonymous feedback receipts that prove buyer and seller are different people. Proofs take seconds to minutes with RISC Zero |
