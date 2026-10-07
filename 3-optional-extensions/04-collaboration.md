# 3.4 Live authoring collaboration

## Repositories

| Repository | Role | Work in this plan |
| --- | --- | --- |
| [evy](https://github.com/EVY-Platform/evy) | Modified | Shared canvas in EVY Developer (`web/`). Session contract for live edits |
| [freenet-core](https://github.com/freenet/freenet-core) | Used | Contract subscriptions and merge checks |
| [freenet-wiki](https://github.com/freenet/freenet-wiki) | Used | Shared editing example |

## Purpose

This plan is an idea note for editing a flow together in EVY Developer. In milestone 2 (EVY on Freenet), contributors submit signed UI proposals ([Proposing a UI change in 2.8 Attribution](../2-evy-on-freenet/08-attribution.md#proposing-a-ui-change)). The service publisher reviews each proposal and publishes a new UI version ([Publishing from EVY Developer in 2.5 EVY Developer on Freenet](../2-evy-on-freenet/05-developer.md#publishing-from-evy-developer)).

In a live session, Carol and a second contributor would edit Marketplace's "Create item" flow together:

- Carol changes the "Pickup and delivery" page.
- The other contributor changes "Payment options".
- Each sees the other's edits on the canvas.
- The session carries draft edits. The contributors submit one signed UI proposal for review and [attribution units in 2.8 Attribution](../2-evy-on-freenet/08-attribution.md#attribution-units).

## When this becomes a plan

Work starts when contributors ask to edit a flow together or frequently submit overlapping UI proposals. EVY measures demand and tests contract delivery before starting the work.

| Measure | What it decides |
| --- | --- |
| Share of UI proposals that change a flow another open proposal also changes | Whether contributors need to edit together |
| Pairs of contributors who change the same flow within one day | How many contributors need live sessions |
| Contract-subscription delay between an edit and its appearance on the other canvas, and bytes per edit | Whether contract subscriptions meet the session's latency and bandwidth needs, using Core's bandwidth baseline |

This plan also decides how one UI proposal names two [contributor keys from 2.8 Attribution](../2-evy-on-freenet/08-attribution.md#contributor-keys), and how the units for the "Create item" flow split between Carol and the other contributor.

## Sources

| Source | Relevant design |
| --- | --- |
| [freenet-core #5320](https://github.com/freenet/freenet-core/issues/5320) | Merge laws for the session contract. EVY runs `fdev verify-merge` on the session contract, as River does on its room contract in [Conflicting changes in 1.6 Application protocols, data and operations](../1-freenet-mobile-appkit/06-data-and-operations.md#conflicting-changes) |
| [freenet-wiki](https://github.com/freenet/freenet-wiki) | A wiki whose contract holds page revisions and patches. A signing delegate signs each patch, and subscriptions deliver live updates to every editor |
| [Ephemeral datagram API #4959](https://github.com/freenet/freenet-core/discussions/4959) | A proposed real-time transport in Core to assess if subscription latency exceeds the live canvas's needs |
| [freenet-core #5153](https://github.com/freenet/freenet-core/issues/5153) | Bandwidth baseline and how Core measures traffic |
