# 3.6 EVY services for Freenet apps

## Repositories

| Repository | Role | Work in this plan |
| --- | --- | --- |
| [evy](https://github.com/EVY-Platform/evy) | Modified | Payment, attribution and remuneration services open to outside apps; SDUI schemas and readers as a Swift package and a Kotlin library. Purchase contract and UI contract for outside apps |
| [freenet-appkit](https://github.com/glesage/freenet-appkit) | Used | Swift package and Kotlin library for an outside app's iOS and Android builds |
| [freenet-core](https://github.com/freenet/freenet-core) | Used | App frame rules for web apps |

## Purpose

This plan is an idea note for offering EVY services to independently hosted Freenet apps. Apps in EVY's native host use the versioned interfaces in [Shared EVY catalogue in 2.4 SDUI data and actions](../2-evy-on-freenet/04-data-and-actions.md#shared-evy-catalogue). Outside apps would use those interfaces with their own caller authorization and service policies.

After milestone 2 (EVY on Freenet), EVY could offer these services:

| Service | What outside apps would use | Plan |
| --- | --- | --- |
| Payment | Stripe payments, the 1% contributor fee and Stripe Connect seller accounts | [2.6 Payments](../2-evy-on-freenet/06-payments.md) |
| Attribution | Contributor keys, service policies and attribution units | [2.8 Attribution](../2-evy-on-freenet/08-attribution.md) |
| Remuneration | Fee splits, balances and payouts | [2.9 Remuneration and payouts](../2-evy-on-freenet/09-remuneration.md) |
| SDUI | Signed UI documents and UI contracts, rendered by SwiftUI and Compose readers on iOS and Android | [2.2 EVY UI contracts and publishing](../2-evy-on-freenet/02-ui-contracts.md), [2.3 Native SDUI readers](../2-evy-on-freenet/03-readers.md) |
| Shared resources | Purchase contracts, purchase messages, private-address projections and file interfaces. Apps sharing a purchase or file reference the same instance | [2.4 SDUI data and actions](../2-evy-on-freenet/04-data-and-actions.md#shared-evy-catalogue) |

A Freenet marketplace app could use EVY's payment service to sell Alice's skateboard to Bob for 70 dollars. Its contributors would receive the 0.70-dollar fee.

| What the app needs | What it provides | Built on |
| --- | --- | --- |
| A service policy | A policy signed by its publisher key that sets the fee rate, capability weights and payout terms | [Service policy in 2.8 Attribution](../2-evy-on-freenet/08-attribution.md#service-policy) |
| Purchase contracts | One instance of the common EVY contract per sale. Shared adapters expose purchases and messages. The payment service signs payment records into each instance; remuneration reads completed purchases | [Shared purchase interface in 2.6 Payments](../2-evy-on-freenet/06-payments.md#shared-purchase-interface), [Crediting a completed purchase in 2.9 Remuneration and payouts](../2-evy-on-freenet/09-remuneration.md#crediting-a-completed-purchase) |
| Seller accounts | Its sellers onboard with Stripe Connect through EVY's payment service | [Fees and seller accounts in 2.6 Payments](../2-evy-on-freenet/06-payments.md#fees-and-seller-accounts) |
| Contributor credit | Its repository installs the EVY GitHub App, and its contributors register contributor keys | [Code contributions in 2.8 Attribution](../2-evy-on-freenet/08-attribution.md#code-contributions) |
| Native payments | iOS and Android builds on [1.2 Embedded node and mobile SDK](../1-freenet-mobile-appkit/02-sdk.md), with Stripe's payment sheet | [Paying on a phone in 2.6 Payments](../2-evy-on-freenet/06-payments.md#paying-on-a-phone) |
| Web payments | A payment-service access path compatible with Core's app frame. Its `connect-src` permits the node's own origin ([client_api.rs](https://github.com/freenet/freenet-core/blob/main/crates/core/src/server/client_api.rs)) | [2.6 Payments](../2-evy-on-freenet/06-payments.md) |
| SDUI screens | An iOS and Android app with the SwiftUI and Compose readers built in, and UI documents authored in EVY Developer | [The UI document in 2.2 EVY UI contracts and publishing](../2-evy-on-freenet/02-ui-contracts.md#the-ui-document), [2.5 EVY Developer on Freenet](../2-evy-on-freenet/05-developer.md) |

## When this becomes a plan

Work starts after [The first paid sale in 2.10 Testing and release](../2-evy-on-freenet/10-testing-and-release.md#the-first-paid-sale), when an outside Freenet app asks to use an EVY service. This plan then decides:

- Who runs the services for outside apps, and what share of each fee pays for running them.
- How outside apps package and version the common purchase contract and shared adapters to match the format payment and remuneration support.
- How the host verifies an outside app's caller identity and grants access to a private-data delegate and namespace.
- How an outside app registers its service policy and publisher key with `services/attribution`.
- How EVY ships SDUI schemas and readers as a Swift package for iOS and a Kotlin library for Android.
- How a web app's buyer reaches the payment service from Core's app frame.

## Sources

| Source | Relevant interface or constraint |
| --- | --- |
| [evy.schema.json](https://github.com/EVY-Platform/evy/blob/dev/types/schema/sdui/evy.schema.json) and [sdui.md](https://github.com/EVY-Platform/evy/blob/dev/docs/evy/sdui.md) | The `UI_Flow` structure and row types an outside app would publish |
| [client_api.rs](https://github.com/freenet/freenet-core/blob/main/crates/core/src/server/client_api.rs) | The app frame's `connect-src`, limited to the node's own origin |
| [harvest#29](https://github.com/freenet/harvest/issues/29) | An outside payment-bridge access case that requires a path compatible with the app frame's `connect-src` rule |
| [Harvest payment.rs](https://github.com/freenet/harvest/blob/main/common/src/payment.rs) | A Freenet app that embeds payment proof in its own orders |
