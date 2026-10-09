# 3.6 EVY services for Freenet apps

## Repositories

| Repository | Role | Work in this plan |
| --- | --- | --- |
| [evy](https://github.com/EVY-Platform/evy) | Modified | Future integration research for outside applications, backend services and native reader packages |
| [freenet-appkit](https://github.com/glesage/freenet-appkit) | Used | Swift package and Kotlin library for an outside app's iOS and Android builds |
| [freenet-core](https://github.com/freenet/freenet-core) | Used | App frame rules for web apps |

## Purpose

This plan is a future idea for offering EVY backend services to independently hosted Freenet applications. Work starts after milestone 2 (EVY on Freenet), when an outside application asks for a specific integration.

The current delivery scope is defined by [2.10 Testing and release](../2-evy-on-freenet/10-testing-and-release.md): one EVY application with native readers on iOS and Android, its own data contracts and one EVY delegate per installation.

| Potential integration | Starting point |
| --- | --- |
| Payments for physical goods | [2.6 Payments](../2-evy-on-freenet/06-payments.md) |
| Contribution accounting | [2.8 Attribution](../2-evy-on-freenet/08-attribution.md) |
| Contributor payouts | [2.9 Remuneration and payouts](../2-evy-on-freenet/09-remuneration.md) |
| Reusable native readers | [2.3 Native SDUI readers](../2-evy-on-freenet/03-readers.md) |

## When this becomes a plan

The outside application's owner and EVY integration owner agree the authority and service terms below. Relevant Freenet maintainers approve changes to shared Freenet interfaces before their feature PRs. This lets an independently published application use EVY services with a verified caller, retained policy and defined recovery path.

Require a named outside application, an integration owner and a concrete operation before writing an implementation plan.

| Design decision | Required evidence |
| --- | --- |
| Application identities | Signed registrations bind each outside application's publisher, release and supported protocol. |
| Authorization | A reviewed design defines caller authentication, user consent, operation and participant scopes, expiry and revocation. |
| Data ownership | The design identifies the owner and lifetime of each referenced record, contract instance and private key. |
| Payment context | Purchases bind the outside application, its accepted policy, seller authorization and exact retained release evidence. |
| Native and browser routes | Each selected route has an authenticated transport and matching request/reply context. Native integration has matching iOS and Android fixtures. |
| Service operations | Named operators, hosting quotas, fee allocation, moderation, privacy, recovery and support are agreed for the outside application. |
| Compatibility | Versioned protocols and fixtures prove upgrades, restored sessions, refunds and historical attribution. |

An implementation plan will define these interfaces and its own release gates once the demand and owners are established.

## Sources

- [evy.schema.json](https://github.com/EVY-Platform/evy/blob/d0fb7e6475f1dfc5c74325e37d4e92aed88d84ed/types/schema/sdui/evy.schema.json) and [sdui.md](https://github.com/EVY-Platform/evy/blob/d0fb7e6475f1dfc5c74325e37d4e92aed88d84ed/docs/evy/sdui.md): The `UI_Flow` structure and row types an outside app would publish
- [client_api.rs](https://github.com/freenet/freenet-core/blob/e7d0b06c9326f377d250bf8344baaac2ba2658c6/crates/core/src/server/client_api.rs): The app frame's `connect-src`, limited to the node's own origin
- [harvest#29](https://github.com/freenet/harvest/issues/29): An outside payment-bridge access case that requires a path compatible with the app frame's `connect-src` rule
- [Harvest payment.rs](https://github.com/freenet/harvest/blob/9eb4a04ed30e75c478df0b89f38f68044bbd947c/common/src/payment.rs): A Freenet app that embeds payment proof in its own orders
