# 4.6 SDUI testing and release

## Repositories

| Repository | Role | Work in this plan |
| --- | --- | --- |
| `freenet-sdui` | Modified | River screen fixtures for the four screens, the cross-target suite, the upgrade tests and published results |
| [evy](https://github.com/EVY-Platform/evy) | Modified | Test builds of the `ios/` and `android/` apps with the native readers, App Review notes, TestFlight and Play internal-testing builds |
| `freenet-appkit` | Used | Scenario harness from [1.9 Testing and release](../1-freenet-mobile-appkit/09-testing-and-release.md#release-tests) for iOS and Android runs, and the packaging CLI for the test releases |
| [river](https://github.com/freenet/river) | Used | Room contract and chat delegate with `CreateInvitation`, run for real in every test |
| [freenet-core](https://github.com/freenet/freenet-core) | Used | One pinned build for every run |

## Purpose

This plan tests milestone 4 (SDUI) in a browser and on real iOS and Android phones, then releases it. The tests run River's four screens as SDUI in the web reader in the release bundle, the SwiftUI reader in EVY on iOS and the Compose reader in EVY on Android. Alice owns "Skate club", invites Bob from the "Invite member" screen that Carol built in [4.5 EVY Developer visual authoring](05-developer.md), and Bob sends "Skate session Saturday?".

The [release tests](#release-tests) add cross-target, upgrade and store tests to the acceptance of each earlier plan in milestone 4 (SDUI). Milestone 4 (SDUI) ships when every row passes.

## Test releases

River's publisher owns River's website container, so the suite never publishes to it. The packaging CLI from [1.4 Application bundles](../1-freenet-mobile-appkit/04-bundles.md#publishing-and-evidence) builds River's web app and the fixture `ui/sdui/` files into a test container signed with a test key, as 1.9 Testing and release does with the Atlas test index. Each publication passes River's pinned container Wasm with `--contract-wasm`, so every test release keeps one test container key. A test build of EVY on iOS and Android lists that container in its catalogue. Rooms keep their keys, because River's room contract and chat delegate keys come from their code and parameters alone.

## River's four screens

Each case runs in a browser, in EVY on iOS and in EVY on Android, with the fixed locale, time zone and clock from 4.1 SDUI format.

| Screen | River source | Test | Passing result |
| --- | --- | --- | --- |
| Room list | [room_list.rs](https://github.com/freenet/river/blob/main/ui/src/components/room_list.rs) | Alice opens River and taps "Skate club" | The list shows her rooms from the chat delegate, and the tap opens the conversation |
| Invite member | [invite_member_modal.rs](https://github.com/freenet/river/blob/main/ui/src/components/members/invite_member_modal.rs) | Alice opens "Invite member" and copies the link | The action calls `CreateInvitation`. On iOS and Android the host asks for `clipboard` at first use, and the link is copied. Bob joins "Skate club" from it. A denied `clipboard` on iOS and Android, and from a test host in a browser, leaves the link as selectable text, as [Showing permission results in 4.2 SDUI readers](02-readers.md#showing-permission-results) sets |
| Members | [members.rs](https://github.com/freenet/river/blob/main/ui/src/components/members.rs) | Alice opens the member list after Bob joins | Bob appears as a member with his nickname |
| Conversation | [conversation.rs](https://github.com/freenet/river/blob/main/ui/src/components/conversation.rs) | Bob types "Skate session Saturday?" and sends it | The message shows as "Sending" from the tap, then as sent. `PrepareMessage` signs it in the chat delegate, as [Forms, drafts and send state in 4.3 SDUI actions and data](03-actions-and-data.md#forms-drafts-and-send-state) sets. While the node merges updates for "Skate club", `PrepareMessage` meets the reply-time targets in that section, and the results report its reply time. Alice sees the message in the room |

Across the three targets, the tests compare room state, delegate request bytes, send states, navigation events and typed errors. Layout may differ. A screen-reader case walks each screen with a browser screen reader, VoiceOver on iOS and TalkBack on Android. Every control exposes the same name, role and focus order on all three.

## Drafts across upgrades

In version 12 of the test release, Bob types "Skate session Saturday?" and leaves it unsent. The draft sits in the chat delegate's store, as in [Reads and local data in 1.6 Application protocols, data and operations](../1-freenet-mobile-appkit/06-data-and-operations.md#reads-and-local-data). Each upgrade below runs on iOS and Android for the current and previous EVY build against River versions 12 and 13. The reader upgrade also runs in a browser.

| Upgrade | Test | Passing result |
| --- | --- | --- |
| Screen | Version 13 of the test release moves the conversation's send button | The host activates version 13 at the next session boundary, as in [Activating a release in 1.3 Single-application host](../1-freenet-mobile-appkit/03-host.md#activating-a-release), and the reader shows the draft |
| Reader | A new EVY build ships newer native readers, and a new release carries a newer `ui/sdui/web/` | Each reader reads the draft saved by the older reader |
| Delegate key | Version 13 carries a new chat delegate Wasm, and Bob opens it first in the native reader | EVY runs River's web UI once in a hidden WebView to move the secrets, as [Migration in native readers in 4.4 SDUI bundles and publication](04-bundles.md#migration-in-native-readers) sets, and the draft moves with them. River's start code stores the signing key again, as [Calling a delegate in 4.3 SDUI actions and data](03-actions-and-data.md#calling-a-delegate) sets, and Bob sends the draft through `PrepareMessage` |
| Interrupted | Kill EVY during activation and during the secret move | The next start keeps or finishes the upgrade, and the draft is still there |
| Newer screen | Version 13 needs a component the installed native reader lacks | EVY opens River's `index.html` in the WebView, as [4.2 SDUI readers](02-readers.md#native-readers-in-evy) sets. Version 13's web reader follows the compatibility rules in [4.1 SDUI format](01-format.md#compatibility), and the draft stays |

## Release tests

| Release test | Passing evidence |
| --- | --- |
| Plan acceptance | The acceptance of 4.1 SDUI format, 4.2 SDUI readers, 4.3 SDUI actions and data, 4.4 SDUI bundles and publication and 4.5 EVY Developer visual authoring passes on the pinned builds |
| River screens | Every case in [River's four screens](#rivers-four-screens) passes in a browser and on real iOS and Android devices |
| Drafts | Every case in [Drafts across upgrades](#drafts-across-upgrades) passes on real iOS and Android devices |
| Publication | Each test release publishes through the packaging CLI with the pinned container Wasm and keeps its test container key. Readback through an independent node matches every file under `ui/sdui/`, as [Publication in 4.4 SDUI bundles and publication](04-bundles.md#publication) sets |
| Browser refresh | A browser open on version 12 loads version 13's `ui/sdui/ui.json` on its next fetch, and its CSS, fonts and icons come from version 13's content-hashed names, under the cache rules in [Web reader in 4.2 SDUI readers](02-readers.md#web-reader) |
| Web UI unchanged | The [River acceptance cases in 1.9 Testing and release](../1-freenet-mobile-appkit/09-testing-and-release.md#river-acceptance-cases) still pass through River's own web UI, and the two-app cases in [2.3 Testing and release](../2-evy-mobile-app/03-testing-and-release.md) still pass |
| Cellular data | With reader traffic included, the [acceptance in 1.8 Thin-peer role and cellular data budgets](../1-freenet-mobile-appkit/08-thin-peer.md#acceptance) passes on iOS and Android |
| Distribution | The EVY builds with native readers pass TestFlight on iOS and Play internal testing on Android. App Review notes say the readers render screen data and run no publisher code. The [store requirements](../1-freenet-mobile-appkit/09-testing-and-release.md#store-requirements) and [store build checks in 1.9 Testing and release](../1-freenet-mobile-appkit/09-testing-and-release.md#store-build-checks) still hold |

## Acceptance

- Alice and Bob complete the room list, "Invite member", members and conversation cases in a browser and on real iOS and Android devices, with matching room state and send states.
- Each of River's four screens exposes the same control names, roles and focus order to a browser screen reader, to VoiceOver on iOS and to TalkBack on Android.
- In a browser and on iOS and Android, Bob's message shows as "Sending" from the tap, and `PrepareMessage` meets the reply-time targets in [Forms, drafts and send state in 4.3 SDUI actions and data](03-actions-and-data.md#forms-drafts-and-send-state) while the node merges updates.
- On iOS and Android, Bob's unsent "Skate session Saturday?" draft survives a screen upgrade, a reader upgrade and a chat delegate key change, including when EVY is killed mid-upgrade, for each supported pair of EVY build and River version. After the chat delegate key change, Bob sends the draft.
- Each test release reads back through an independent node, and a browser open on version 12 shows version 13's screens.
- The EVY iOS build passes TestFlight and the EVY Android build passes Play internal testing with native readers.
- Published results list the exact revisions of Core, `freenet-sdui` schemas and readers, the test release versions and the EVY builds, with devices, OS versions and redacted logs. Simulator and emulator runs are reported apart from real-device runs.
