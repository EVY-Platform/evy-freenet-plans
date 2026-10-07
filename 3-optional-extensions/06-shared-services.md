# 3.6 EVY services for Freenet apps

## Repositories

| Repository | Role | Work in this plan |
| --- | --- | --- |
| [evy](https://github.com/EVY-Platform/evy) | Modified | Payment, attribution and remuneration services open to outside apps; SDUI schemas and readers as a Swift package and a Kotlin library. Purchase contract and UI contract for outside apps |
| [freenet-appkit](https://github.com/glesage/freenet-appkit) | Used | Swift package and Kotlin library for an outside app's iOS and Android builds |
| [freenet-core](https://github.com/freenet/freenet-core) | Used | App frame rules for web apps |

## Purpose

This plan is an idea note.

EVY applications within the native host already use the versioned interfaces in [Shared EVY catalogue in 2.4 SDUI data and actions](../2-evy-on-freenet/04-data-and-actions.md#shared-evy-catalogue). This plan extends that catalogue to independently hosted applications, with their own caller authorization and service policies.

Once milestone 2 (EVY on Freenet) works, EVY can offer these services to Freenet apps outside EVY:

- **Payment:** Stripe payments, the 1% contributor fee and Stripe Connect seller accounts from [2.6 Payments](../2-evy-on-freenet/06-payments.md).
- **Attribution:** contributor keys, service policies and attribution units from [2.8 Attribution](../2-evy-on-freenet/08-attribution.md).
- **Remuneration:** fee splits, balances and payouts from [2.9 Remuneration and payouts](../2-evy-on-freenet/09-remuneration.md).
- **SDUI:** the signed UI document and UI contract from [2.2 EVY UI contracts and publishing](../2-evy-on-freenet/02-ui-contracts.md), drawn by the SwiftUI and Compose readers from [2.3 Native SDUI readers](../2-evy-on-freenet/03-readers.md).
- **Shared resources:** the common purchase contract, purchase-message protocol, private-address projection and file interfaces from the shared EVY catalogue. Applications reference the same instances when they share a purchase or file.

For example, a Freenet marketplace app could sell Alice's skateboard to Bob for 70 dollars through EVY's payment service and pay the 0.70-dollar fee to the contributors of its own code.

| What the app needs | What it provides | Built on |
| --- | --- | --- |
| A service policy | Its own policy with fee rate, capability weights and payout terms, signed with its publisher key | [Service policy in 2.8 Attribution](../2-evy-on-freenet/08-attribution.md#service-policy) |
| Purchase contracts | The common EVY implementation, one instance per sale. Shared resource adapters project purchases and messages. The payment service signs payment records into the instance, and remuneration reads completed purchases from it | [Shared purchase interface in 2.6 Payments](../2-evy-on-freenet/06-payments.md#shared-purchase-interface), [Crediting a completed purchase in 2.9 Remuneration and payouts](../2-evy-on-freenet/09-remuneration.md#crediting-a-completed-purchase) |
| Seller accounts | Its sellers onboard with Stripe Connect through EVY's payment service | [Fees and seller accounts in 2.6 Payments](../2-evy-on-freenet/06-payments.md#fees-and-seller-accounts) |
| Contributor credit | Its repository installs the EVY GitHub App, and its contributors register contributor keys | [Code contributions in 2.8 Attribution](../2-evy-on-freenet/08-attribution.md#code-contributions) |
| A way to pay | An iOS and Android app built on [1.2 Embedded node and mobile SDK](../1-freenet-mobile-appkit/02-sdk.md) shows Stripe's payment sheet as EVY does. A web app runs in Core's app frame, which connects only to the node's own origin ([client_api.rs](https://github.com/freenet/freenet-core/blob/main/crates/core/src/server/client_api.rs)), so it needs another path to the payment service | [Paying on a phone in 2.6 Payments](../2-evy-on-freenet/06-payments.md#paying-on-a-phone) |
| SDUI screens | An iOS and Android app with the SwiftUI and Compose readers built in, and UI documents authored in EVY Developer | [The UI document in 2.2 EVY UI contracts and publishing](../2-evy-on-freenet/02-ui-contracts.md#the-ui-document), [2.5 EVY Developer on Freenet](../2-evy-on-freenet/05-developer.md) |

## When this becomes a plan

This plan starts after [The first paid sale in 2.10 Testing and release](../2-evy-on-freenet/10-testing-and-release.md#the-first-paid-sale), when a Freenet app outside EVY asks to use one of these services. The plan then decides:

- Who runs the services for outside apps, and what share of each fee pays for running them.
- How outside apps package and version the common purchase contract and shared resource adapters, so payment and remuneration read the catalogue's supported format.
- How an independently hosted app obtains permission to use a private-data delegate and its namespace, through the host's attested caller and grant rules.
- How an outside app registers its service policy and publisher key with `services/attribution`.
- How EVY ships the SDUI schemas and the SwiftUI and Compose readers as a Swift package and a Kotlin library.
- How a web app's buyer reaches the payment service from Core's app frame.

## Sources

| Source | What it shows |
| --- | --- |
| [evy.schema.json](https://github.com/EVY-Platform/evy/blob/dev/types/schema/sdui/evy.schema.json) and [sdui.md](https://github.com/EVY-Platform/evy/blob/dev/docs/evy/sdui.md) | The `UI_Flow` shape and row types an outside app would publish |
| [client_api.rs](https://github.com/freenet/freenet-core/blob/main/crates/core/src/server/client_api.rs) | The app frame's `connect-src`, limited to the node's own origin |
| [harvest#29](https://github.com/freenet/harvest/issues/29) | A published Freenet app that could not reach an outside payment bridge because of that rule |
| [Harvest payment.rs](https://github.com/freenet/harvest/blob/main/common/src/payment.rs) | A Freenet app that embeds payment proof in its own orders |
