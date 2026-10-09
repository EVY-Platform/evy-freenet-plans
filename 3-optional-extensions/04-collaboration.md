# 3.4 Live authoring collaboration

## Repositories

| Repository | Role | Work in this plan |
| --- | --- | --- |
| [evy](https://github.com/EVY-Platform/evy) | Modified | Shared canvas in EVY Developer (`web/`). Session contract for live edits |
| [freenet-core](https://github.com/freenet/freenet-core) | Used | Contract subscriptions and merge checks |
| [freenet-wiki](https://github.com/freenet/freenet-wiki) | Used | Shared editing example |

## Purpose

This plan is an idea note for editing flows together in the local EVY Developer editor. Each session edits a draft of the complete EVY application document. The session contract carries draft data and contributor confirmations. In milestone 2 (EVY on Freenet), contributors submit signed UI proposals ([Proposing a UI change in 2.8 Attribution](../2-evy-on-freenet/08-attribution.md#proposing-a-ui-change)). The EVY publisher reviews each proposal and publishes a new complete EVY application UI version ([Publishing the application in 2.5 EVY authoring and publishing](../2-evy-on-freenet/05-developer.md#publishing-the-application)).

In a live session, Carol and a second contributor would edit Marketplace's "Create item" flow together:

- Carol changes the "Pickup and delivery" page.
- The other contributor changes "Payment options".
- Each sees the other's edits on the canvas.
- The session carries draft edits. The contributors submit one signed UI proposal for review and [attribution units in 2.8 Attribution](../2-evy-on-freenet/08-attribution.md#attribution-units).

## When this becomes a plan

Define session latency, bandwidth and contributor-confirmation requirements. If measurements lead to a new Core transport, obtain Freenet approach approval for that interface before its feature PR. A live session lets contributors reconcile overlapping edits and confirm one draft and contribution split before publication.

Work starts when contributors ask to edit a flow together or frequently submit overlapping UI proposals. EVY measures demand and tests contract delivery before starting the work.

| Measure | What it decides |
| --- | --- |
| Share of UI proposals that change a flow another open proposal also changes | Whether contributors need to edit together |
| Pairs of contributors who change the same flow within one day | How many contributors need live sessions |
| Contract-subscription delay between an edit and its appearance on the other canvas, and bytes per edit | Whether contract subscriptions meet the session's latency and bandwidth needs, using Core's traffic measurements |

The session produces the complete application draft, the signed proposal and contributor-share format from [Proposing a UI change in 2.8 Attribution](../2-evy-on-freenet/08-attribution.md#proposing-a-ui-change). Its contributor shares total 10,000. This plan defines how both contributors confirm the final document and their shares, and how attribution records those confirmations before review and publication.

## Sources

- [freenet-core #5320](https://github.com/freenet/freenet-core/issues/5320): Merge laws for the session contract. EVY runs `fdev verify-merge` on the session contract, as River does on its room contract in [Conflicting changes in 1.6 Application protocols, data and operations](../1-freenet-mobile-appkit/06-data-and-operations.md#conflicting-changes)
- [freenet-wiki](https://github.com/freenet/freenet-wiki): A wiki whose contract holds page revisions and patches. A signing delegate signs each patch, and subscriptions deliver live updates to every editor
- [Ephemeral datagram API #4959](https://github.com/freenet/freenet-core/discussions/4959): A proposed real-time transport in Core to assess if subscription latency exceeds the live canvas's needs
- [freenet-core #5153](https://github.com/freenet/freenet-core/issues/5153): How Core measures traffic
