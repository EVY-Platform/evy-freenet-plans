# 5.5 Live authoring collaboration

## Repositories

| Repository | Role | Work in this plan |
| --- | --- | --- |
| [evy](https://github.com/EVY-Platform/evy) | Modified | The `web/` editor gains live sessions that share edits and show which component each author has selected |
| [freenet-core](https://github.com/freenet/freenet-core) | Used | Contract subscriptions deliver each author's edits to the others. `fdev verify-merge` tests the session contract's merge |
| [freenet-wiki](https://github.com/freenet/freenet-wiki) | Used | Worked example of shared editing through one contract |
| [river](https://github.com/freenet/river) | Used | Worked example. Two contributors edit the "Invite member" sheet under `ui/sdui/` |

## Purpose

This plan is an idea note. In [4.5 EVY Developer visual authoring](../4-sdui/05-developer.md#editing-a-screen), two authors already work on one app on separate branches, and git merges their pull requests. A live session would let Carol and a second contributor edit River's "Invite member" sheet at the same time, each seeing the other's changes on the canvas. The session carries edits only. The pull request stays the result that review and credit use under [3.1 Contributor registration and attribution](../3-attribution-remuneration-payment/01-attribution.md).

## When this becomes a plan

This plan starts when EVY Developer contributors ask to edit one screen together, or when pull requests that change the same `ui/sdui/` file often conflict. Until then, EVY measures these.

| Measure | What it decides |
| --- | --- |
| Share of `ui/sdui/` pull requests with merge conflicts | Whether branches are enough |
| Pairs of contributors who change the same screen within one day | How many users need live sessions |
| Time from one author's edit to the other author's canvas, and bytes per edit, through a contract subscription | Whether a Freenet contract can carry a live session, and what it costs against Core's bandwidth baseline |

## Sources

| Source | What it shows |
| --- | --- |
| [freenet-core #5320](https://github.com/freenet/freenet-core/issues/5320) | Merge laws a session contract must follow. EVY runs `fdev verify-merge` on the session contract, as River does on its room contract in [Sending updates in 1.6 Application protocols, data and operations](../1-freenet-mobile-appkit/06-data-and-operations.md#sending-updates) |
| [freenet-wiki](https://github.com/freenet/freenet-wiki) | A wiki whose contract holds page revisions and patches. A signing delegate signs each patch, and subscriptions deliver live updates to every editor |
| [Ephemeral datagram API #4959](https://github.com/freenet/freenet-core/discussions/4959) | A proposed real-time lane in Core. It is the upstream thread if subscription latency is too slow for a live canvas |
| [freenet-core #5153](https://github.com/freenet/freenet-core/issues/5153) | Bandwidth baseline and how Core measures traffic |
