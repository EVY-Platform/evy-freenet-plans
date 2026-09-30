# 5.4 Peer reputation

## Repositories

| Repository | Role | Work in this plan |
| --- | --- | --- |
| [ghostkeys](https://github.com/freenet/ghostkeys) | Used | Ghost key delegate that signs requests for apps after the user allows them |
| [harvest](https://github.com/freenet/harvest) | Used | Seller standing design and its privacy analysis |
| `evy-marketplace` | Used | Handovers signed by both buyer and seller in the order contract, as the evidence a proof would count |

## Purpose

This plan is an idea note. It waits until an app needs a private reputation proof. Until then, an app that needs spam limits or seller trust calls the [Ghostkeys delegate](https://github.com/freenet/ghostkeys#integrating-with-ghostkeys). The delegate asks Bob to allow the request. It then returns a [signature over the message and the calling app's attested identity](https://github.com/freenet/ghostkeys#scoped-signatures), with Bob's ghost key certificate. The certificate proves a donation to Freenet and records its amount and date. [Harvest](https://github.com/freenet/harvest/issues/8) builds seller standing on that certificate.

## When this becomes a plan

This plan starts when an app needs a claim that a ghost key signature cannot give. When Bob asks to pick up Alice's 70-dollar skateboard in [3.3 Marketplace pickup protocol](../3-attribution-remuneration-payment/03-marketplace-protocol.md#the-skateboard-sale), Alice's Marketplace might ask for one of these claims.

| Claim | Why a ghost key signature cannot give it |
| --- | --- |
| Bob completed 5 pickups in the last 90 days, without showing which sellers, orders or dates | The evidence is past handovers that both buyer and seller signed in order contracts. A signature proves only that Bob holds a key. Harvest publishes each order commitment so buyers can count it, and names [zero-knowledge proofs](https://github.com/freenet/harvest/blob/main/docs/design/incentive-mechanism.md#part-8--what-this-publishes-to-the-world) as the way to hide them |
| Bob holds a ghost key, without showing which one | Every signature carries the same certificate, so two apps can link Bob's requests |

The plan then picks a proof system and measures it on the iPhone 13 mini that [1.1 Mobile feasibility and supported profiles](../1-freenet-mobile-appkit/01-feasibility.md#device-limits) measured, and on an Android phone. Bob's delegate builds each proof within the 5-second Wasm limit and 256 MiB per instance under Pulley ([Running Wasm in 1.2 Embedded node and mobile SDK](../1-freenet-mobile-appkit/02-sdk.md#running-wasm)). The delegate limits how often one app can ask, so repeated threshold requests cannot narrow down Bob's count.

## Sources

| Source | What it offers |
| --- | --- |
| [Unlinkable ghost key presentation, web #25](https://github.com/freenet/web/issues/25) | Anonymous credentials that hide which certificate signed, with benchmarks |
| [Mail inbound policy #70](https://github.com/freenet/mail/issues/70) | Ghost key attestation bound to one sender and one message, and a recipient policy |
| [Harvest seller standing #8](https://github.com/freenet/harvest/issues/8), [purchase flow PR #21](https://github.com/freenet/harvest/pull/21) and [messaging PR #23](https://github.com/freenet/harvest/pull/23) | Standing as a donation bound to a ghost key, complaints that withdraw from it, and checks on a remote seller's certificate |
| [Rate-limiting nullifiers #601](https://github.com/freenet/freenet-core/discussions/601) | Hidden membership bound to one action, with per-receiver quotas |
| [Anonymous reputation #882](https://github.com/freenet/freenet-core/discussions/882) | Zero-knowledge proofs over private receipts, and manufactured activity |
