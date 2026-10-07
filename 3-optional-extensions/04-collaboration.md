# 3.4 Live authoring collaboration

## Repositories

| Repository | Role | Work in this plan |
| --- | --- | --- |
| [evy](https://github.com/EVY-Platform/evy) | Modified | Shared canvas in EVY Developer (`web/`). Session contract for live edits |
| [freenet-core](https://github.com/freenet/freenet-core) | Used | Contract subscriptions and merge checks |
| [freenet-wiki](https://github.com/freenet/freenet-wiki) | Used | Shared editing example |

## Purpose

This plan is an idea note. In milestone 2 (EVY on Freenet), each contributor drafts a change in EVY Developer and submits it as a signed UI proposal ([Proposing a UI change in 2.8 Attribution](../2-evy-on-freenet/08-attribution.md#proposing-a-ui-change)). The service publisher reviews it and publishes a new UI version ([Publishing from EVY Developer in 2.5 EVY Developer on Freenet](../2-evy-on-freenet/05-developer.md#publishing-from-evy-developer)).

A live session would let Carol and a second contributor edit Marketplace's "Create item" flow at the same time. Carol reworks the "Pickup and delivery" page while the other contributor edits "Payment options", and each sees the other's changes on the canvas. The session carries edits only. The result is one signed UI proposal, which review and [attribution units in 2.8 Attribution](../2-evy-on-freenet/08-attribution.md#attribution-units) use.

## When this becomes a plan

This plan starts when EVY Developer contributors ask to edit one flow together, or when UI proposals to the same flow often overlap. Until then, EVY measures these.

| Measure | What it decides |
| --- | --- |
| Share of UI proposals that change a flow another open proposal also changes | Whether separate proposals are enough |
| Pairs of contributors who change the same flow within one day | How many contributors need live sessions |
| Time from one author's edit to the other author's canvas, and bytes per edit, through a contract subscription | Whether a Freenet contract can carry a live session, and what it costs against Core's bandwidth baseline |

The plan also decides how one UI proposal names two [contributor keys from 2.8 Attribution](../2-evy-on-freenet/08-attribution.md#contributor-keys), and how the units for the "Create item" flow split between Carol and the other contributor.

## Sources

| Source | What it shows |
| --- | --- |
| [freenet-core #5320](https://github.com/freenet/freenet-core/issues/5320) | Merge laws a session contract must follow. EVY runs `fdev verify-merge` on the session contract, as River does on its room contract in [Conflicting changes in 1.6 Application protocols, data and operations](../1-freenet-mobile-appkit/06-data-and-operations.md#conflicting-changes) |
| [freenet-wiki](https://github.com/freenet/freenet-wiki) | A wiki whose contract holds page revisions and patches. A signing delegate signs each patch, and subscriptions deliver live updates to every editor |
| [Ephemeral datagram API #4959](https://github.com/freenet/freenet-core/discussions/4959) | A proposed real-time lane in Core. It is the upstream thread if subscription latency is too slow for a live canvas |
| [freenet-core #5153](https://github.com/freenet/freenet-core/issues/5153) | Bandwidth baseline and how Core measures traffic |
