# 5.2 Catalogue updates and Atlas search

## Repositories

| Repository | Role | Work in this plan |
| --- | --- | --- |
| [evy](https://github.com/EVY-Platform/evy) | Modified | The `ios/` and `android/` apps read the signed catalogue container, save the accepted version, rebuild home, the store index and the age check from it, and add the home search box |
| [atlas](https://github.com/freenet/atlas) | Modified | Atlas's UI reads a starting query from `#q=` in its URL |
| `freenet-appkit` | Used | Installation interface from 1.4 Application bundles |
| [freenet-core](https://github.com/freenet/freenet-core) | Used | Stock [website container contract](https://github.com/freenet/freenet-core/blob/main/crates/website-contract/src/lib.rs) and the unchanged `fdev website publish` for the catalogue. The shell passes the URL fragment to Atlas |

## Purpose

This plan lets the EVY curator add or remove apps without an EVY store release, and adds Atlas search to EVY home. [2.1 EVY shell and curated catalogue](../2-evy-mobile-app/01-catalogue.md#the-catalogue) bundles `catalogue.json` in each EVY build. This plan publishes the same file in a signed catalogue container that EVY reads from the network. EVY keeps the last accepted catalogue until a newer signed one verifies.

Alice types "river" in EVY home, and EVY opens Atlas with that query. She taps the River result and River opens in its own WebView. Later the curator adds Delta, a Freenet website builder, and Delta appears on Alice's home.

## Updating the catalogue

The curator publishes the catalogue as a website container with the unchanged `fdev website publish`. Its `index.html` lists the apps for browsers, and its `catalogue.json` has the shape and entry fields from 2.1 EVY shell and curated catalogue. Core's website container contract checks the curator's signature and rejects any update whose version is not higher. EVY's release configuration pins the catalogue container key, and the bundled `catalogue.json` is the starting catalogue. `store_age_rating` stays the value in EVY's store build.

| Step | Who | Rule |
| --- | --- | --- |
| 1. Check the app | Curator | Add Delta only after Delta's own UI takes reports and blocks abusive users on iOS and Android, as guideline 4.7.1 in [2.3 Testing and release](../2-evy-mobile-app/03-testing-and-release.md#store-requirements) requires |
| 2. Publish | Curator | Add Delta's entry to `catalogue.json` and publish. fdev sets the new version |
| 3. Accept | EVY | Read the container on each start and while in the foreground. Apply the container version rules of the [installation interface in 1.4 Application bundles](../1-freenet-mobile-appkit/04-bundles.md#installing-a-copy). An older copy from a stale peer keeps the saved catalogue. A same-version copy with different bytes keeps the accepted bytes |
| 4. Show | EVY | Show Delta on home once its own website container verifies through the same installation interface. The store index lists it, and the [age check in 2.1 EVY shell and curated catalogue](../2-evy-mobile-app/01-catalogue.md#store-index-and-age-check) applies to its rating |
| 5. Remove | Curator, then EVY | A version without Delta hides it from home and the store index and stops it opening. Delta's data stays until Alice removes it on its settings page |

Catalogue reads count toward the [cellular budget in 1.8 Thin-peer role and cellular data budgets](../1-freenet-mobile-appkit/08-thin-peer.md#cellular-budget-contract).

## Searching from EVY home

Atlas's UI loads its whole index and filters it on the phone ([ui/src/main.rs](https://github.com/freenet/atlas/blob/main/ui/src/main.rs)). A peer fetches and verifies a contract's whole state before it reads any part ([D678](https://github.com/freenet/freenet-core/discussions/678)), so each Atlas search on cellular costs the full index.

EVY home opens Atlas with the typed query at `#q=river`. Core's shell already passes the URL fragment into the app frame and follows `hashchange` ([shell_bridge.js](https://github.com/freenet/freenet-core/blob/main/crates/core/src/server/path_handlers/assets/shell_bridge.js)), so Atlas only reads `#q=` at startup. A tap on a result follows Atlas's Open link, which EVY routes as in [Opening links and alerts in 2.1 EVY shell and curated catalogue](../2-evy-mobile-app/01-catalogue.md#opening-links-and-alerts). River opens in its own WebView. A result for a website container key outside the catalogue shows the not-in-EVY message and keeps Atlas on screen. An external web link opens the system browser.

The index limits in [Atlas fixture scope and acceptance in 1.9 Testing and release](../1-freenet-mobile-appkit/09-testing-and-release.md#atlas-fixture-scope-and-acceptance) apply to search, and the index holds at most 20,000 entries (`MAX_ENTRIES`, [atlas#10](https://github.com/freenet/atlas/issues/10)). River rooms open only through a one-time invite, so Atlas lists no rooms ([river#513](https://github.com/freenet/river/issues/513), [river#515](https://github.com/freenet/river/issues/515)).

## Acceptance

- On iOS and Android, typing "river" in EVY home opens Atlas at `#q=river`, and the River result from the [1.9 Testing and release](../1-freenet-mobile-appkit/09-testing-and-release.md#atlas-fixture-scope-and-acceptance) test index opens River in its own WebView.
- On iOS and Android, a search result outside the catalogue shows the not-in-EVY message and loads nothing, and an external result opens the system browser.
- On iOS and Android, publishing a catalogue version that adds Delta shows Delta on home and in the store index without an EVY store release. A test entry rated above `store_age_rating` opens only after the age question.
- On iOS and Android, a container under another key, an older version, a same-version copy with different bytes, an invalid `catalogue.json` or no network leaves the last accepted catalogue in place.
- On iOS and Android, a version that drops Delta stops Delta opening and keeps its data until the user removes it.
