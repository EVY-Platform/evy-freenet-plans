# 2.10 Testing and release

## Repositories

| Repository | Role | Work in this plan |
| --- | --- | --- |
| [evy](https://github.com/EVY-Platform/evy) | Modified | Release tests. Store listings and the support page. Launch approvals and pilot results in `docs/launch/`. Moderation/admission evidence from Marketplace and shared reader actions. |
| [freenet-appkit](https://github.com/glesage/freenet-appkit) | Used | Swift package, Kotlin library, store build checks and the packaging CLI |
| [freenet-core](https://github.com/freenet/freenet-core) | Used | Pinned Core build, the EVY operator node and `fdev verify-merge` |
| [freenet-test-network](https://github.com/freenet/freenet-test-network) | Used | Isolated test network |
| [stripe-ios](https://github.com/stripe/stripe-ios), [stripe-android](https://github.com/stripe/stripe-android) | Used | Payment sheets in Stripe test mode and live mode |

## Purpose

Test milestone 2 (EVY on Freenet) on real iOS and Android phones using the thin-peer role from [1.8 Thin-peer protocol](../1-freenet-mobile-appkit/08-thin-peer.md). Deliver the pilot through TestFlight on iOS and Play internal testing on Android, verify live-payment launch approvals, then deliver production through the iOS App Store and Android Google Play. Milestone 2 (EVY on Freenet) completes at the production gate below.

Release requires every [release test](#release-tests) to pass. Run each defining suite at its declared stage/profile and retain its results. Production integration exercises Home → Hello greeting behavior and Marketplace commerce, with cross-plan recovery and evidence checks.

```mermaid
flowchart LR
    T[Release tests pass<br>on iOS and Android] --> R[Store builds in TestFlight<br>and Play internal testing]
    R --> U[One EVY application UI<br>published and authoring tools ready]
    U --> L[Launch approvals<br>recorded in evy]
    L --> S[First paid sale<br>in Stripe live mode]
```

## Test setup

Run every test on real phones with the node in network mode to exercise delegate prompts and contract notifications ([River scope in 1.9 Testing and release](../1-freenet-mobile-appkit/09-testing-and-release.md#river-scope)). Simulator and emulator runs are reported apart.

- Alice and Bob use real phones. Alice has an iPhone on iOS 17 and Bob an Android phone on Android 9 (API 28), the minimum versions in [The EVY app on iOS and Android in 2.1 Hello EVY world](01-hello-evy-world.md#the-evy-app-on-ios-and-android). A current iPhone and a current Android phone run every test too. Every phone runs in the thin-peer role.
- Use test UI contracts. A test UI contract runs the UI contract code with a test publisher key and the fixed `evy` application namespace as parameters. Its `resources` map gives static collections test parameters. EVY resource adapters derive dynamic purchase instances from those test listings and participant keys, and use the test payment service. Preview validation checks the binding dependency graph.
- Build the iOS and Android test apps with `mobile_builds.yml` from [Builds from GitHub in 2.3 Native SDUI readers](03-readers.md#builds-from-github) with `variant: test`. It installs beside the store build and opens an explicitly selected, validated EVY preview contract key from "Scan preview", as [Previewing on a phone in 2.5 EVY authoring and publishing](05-developer.md#previewing-on-a-phone) describes.

| | Isolated test network | Public network |
| --- | --- | --- |
| Network | freenet-test-network. Each node gets explicit gateways, and each run verifies that all peer connections stay in the isolated network, as River scope in 1.9 Testing and release sets | Freenet's public network through Core's gateways |
| Keys | Every contract built and signed with test keys from `evyctl key new evy-test-publisher`. `evyctl keys` writes a test `contract-keys.json` | The EVY publisher key from [The EVY publisher key in 2.1 Hello EVY world](01-hello-evy-world.md#the-evy-publisher-key) signs the complete EVY application document. Test keys sign test UI contracts |
| EVY builds | Matching iOS and Android debug builds from Xcode and Android Studio with the test `contract-keys.json` and gateway overrides for the test network | The EVY test build for test UI contracts. The EVY store build for the release |
| Nodes and services | A test EVY operator node, and test deployments of `services/payment`, `services/attribution` and `services/remuneration`, each with its own node | The EVY operator node from 2.1 Hello EVY world and the three services |
| Stripe | Test mode, with Stripe's test cards and test connected accounts | Test mode until every [launch approval](#launch-approvals) is recorded, then live mode |
| Used for | Forged states, serving-peer loss, carrier NAT, a restore drill and refunds after payout with a short payout hold | Release tests on store builds and [the first paid sale](#the-first-paid-sale) |

## Release tests

Run every test on iOS and Android in the thin-peer role. Use the same builds for tests spanning several plans and each plan's acceptance criteria.

| Release test | Passing evidence |
| --- | --- |
| Publication journal and archive | Restart the local publisher after version reservation, signing, archival, submission and readback. Its journal retains exact complete-application bytes and the archive receipt. Wrong audiences, digests, challenges and expired credentials fail. A fresh challenge resumes the same publication and independent readback confirms its exact signed bytes |
| Single-application boundary | Home, Hello and Marketplace navigate within one retained EVY document and use one EVY delegate. Independent River and EVY installs have distinct stores, installation keys and lifecycle generations. Preview and production installs have distinct IDs, stores and credentials. |
| Bounded state convergence | Run opposite-order and grouped merges at the guestbook's 1,000-ID boundary, including publisher deletion of the newest entry. Retained tombstones occupy their ranked slots. Deliver opposite-order listing admission decisions at 32 live requests and retain the same decision and separate captured-sale evidence |
| Listing admission and arbitration | Missing initial purchase bytes, forged admission and repeated scoped keys fail the admission rules. Pending requests use the verified listing decision for availability. Race two seller acceptances and their intent/capture/cancel calls, then interrupt and restore the service. One reservation fence authorizes one completed sale; uncertain Stripe results keep the fence |
| Compatible application routes | Deliver successive complete EVY documents in either arrival order. Home and Marketplace routes resolve inside the retained document. Public route names preserve arguments/action meanings. A first-page draft and internal navigation stack retain exact source document/bindings until close; idle Home activates the queued compatible document |
| Policy during a purchase | Publish a fee-policy change after admission and before pickup. Buyer authorization, seller acceptance, payment, archive snapshot, allocation, refunds and recovery retain the original policy version and digest |
| Pilot hosting | After acknowledged publication/admission, stop both phones and fetch photos and an unpaid request from a fresh reader. Repair an evicted copy from the operator inventory and verify exact bytes through a second node |
| EVY resources across internal views | On iOS and Android, create a Marketplace purchase through its flow opened from Home. Home and Marketplace display the same instance, messages and payment state through the common adapters. Two buyers requesting one item retain separate participant views and action targets. The source feature, buyer scope, UI version and digest stay bound to each purchase. Address-book records survive restore and migration; only intended recipients open shared address copies. Shared file references resolve to the same verified content. Unknown adapters, substituted contexts and unauthorized writes fail the checks in [Resource operations and permissions in 2.4 SDUI data and actions](04-data-and-actions.md#resource-operations-and-permissions) |
| Equal-version UI documents | Publish two valid signed documents at the same version and deliver them in opposite orders on iOS and Android. Contracts, native readers, preview readers and EVY Developer choose the higher `state_hash`, retain it after restart or reload, and ignore duplicate or lower tuples. An open flow keeps its exact document until exit. A winning document requiring a newer reader keeps the saved drawable document and update banner; a compatible reader update draws the winner. The publisher CLI reports a losing attempt on readback |
| UI version during a purchase | Bob asks to buy the skateboard from EVY application version 8 in Marketplace. The EVY publisher publishes version 9 while Bob is inside a flow and again before the Saturday pickup. The new version applies when Bob leaves the flow ([Reading the application UI contract in 2.3 Native SDUI readers](03-readers.md#reading-the-application-ui-contract)), and he pays in version 9. The purchase record keeps `"ui_version": 8` and its `ui_digest` from his request, and the remuneration service uses the matching archived document and snapshot |
| Archive before publication | Publish versions 8 and 9 rapidly with snapshot processing paused. Each publisher job receives a durable archive receipt before their Freenet updates. Resuming processing recovers version 8's exact bytes and snapshot. Archive outages keep publication pending; interrupted publication retries the same bytes. The recovery drill restores acknowledged entries from the immutable bucket copies, as [Archiving before publication in 2.13 Release archive and policy evidence](13-release-archive-and-policy-evidence.md#archiving-before-publication) requires |
| Newer reader during a sale | Application version 9 needs a `min_reader_version` above Bob's build while his purchase is `pickup_pending`. His phone keeps drawing the saved version 8 with the update banner ([Reader compatibility in 2.2 EVY UI contracts and publishing](02-ui-contracts.md#reader-compatibility)), and he pays and receives the skateboard. After he installs the new store build, his phone draws version 9 and shows the purchase as `sold` |
| EVY delegate update during a purchase | Alice installs an EVY build with a new EVY delegate while her purchase is `pickup_pending`. The move in [Updating the EVY delegate in 2.11 EVY delegate and private records](11-delegate-and-private-records.md#updating-the-evy-delegate) keeps her seller key, so she still reads her sealed pickup address and signs `transaction_completed`. Closing EVY during migration preserves the records; the next start completes the move |
| Offline at the pickup | Alice taps "Confirm" with no signal, and Bob closes EVY right after paying. With the purchase state retained within Core's hosting budget, Core merges Alice's message locally and sends it on reconnect ([Offline writes in 2.4 SDUI data and actions](04-data-and-actions.md#offline-writes)). The payment service captures once, and both phones show `sold` |
| Declined card and retry | On iOS and Android, Bob's first card is declined and he chooses to try again with a valid card on the same purchase and PaymentIntent. The payment record follows `failed → intent → succeeded` with increasing revisions, as [Retrying a card payment in 2.6 Payments](06-payments.md#retrying-a-card-payment) specifies. Delayed and duplicate failure events preserve the successful result, and Alice's confirmation produces one successful charge and one contributor fee |
| Seller closes before capture | Alice confirms the handover and closes EVY before capture finishes. The payment service publishes `succeeded`; Bob's reader and a third reader derive `sold` from the purchase and hide the listing from available-item search. The item record's revision stays unchanged. Retained sale references and unknown-availability cases pass [Item availability in 2.7 EVY Marketplace](07-marketplace.md#item-availability) on iOS and Android |
| Code eligibility and verified merge | Publish an EVY application UI version while Dan's attribution check passes and his PR awaits merge. His units enter the first UI snapshot published after its verified merge and committed acceptance, following [Code contributions in 2.8 Attribution](08-attribution.md#code-contributions). Changed heads renew eligibility; duplicate merge events and a restart preserve one initial acceptance |
| Cellular caps across the sale | Run the whole sale on cellular with a listing with three photos under 1 MiB each, the request, accept, payment and confirm. The node's bytes for each step fit the budgets in [Cellular budget contract in 1.11 Cellular data and resource budgets](../1-freenet-mobile-appkit/11-cellular-data-and-resource-budgets.md#cellular-budget-contract). Stripe's payment sheet talks to Stripe outside the node, so its bytes are recorded apart. A phone that reaches its cap keeps its drafts and pending records, and the sale finishes with one charge after a new allowance |
| Marketplace reader parity | EVY's "Home" flow and Marketplace's "View Item" and "Create item" flows at application versions 7 and 8, with the payment step, Report, Block and terms rows, give the same semantic snapshots and action traces on SwiftUI and Compose, as [Keeping both readers the same in 2.3 Native SDUI readers](03-readers.md#keeping-both-readers-the-same) sets. VoiceOver and TalkBack read the same names |
| Partial and repeated refunds | On iOS and Android, refund 35.00 dollars of the completed skateboard sale. The purchase stays `sold`, both phones show the partial refund and the listing stays closed. Signed totals are `refunded_cents: 3500` and `fee_refunded_cents: 35`; the ledger reverses 35 cents. Refund the remaining 35.00 dollars: totals become 7000 and 70 and the purchase becomes `refunded`. Run before and after payout, with duplicate and reordered buyer and fee-refund events, a fee-only refund, and a restart. Reversal totals match the original allocations and one full refund. First observation after refund applies allocation and reversal together before payout |
| Refund after payout | On the isolated network, a test policy sets `payout_hold_days` to 0. Carol is paid out for the sale, then the EVY operator refunds Bob with `payment_refund`. Bob gets 70.00 dollars back, Alice returns 69.30 and EVY 0.70. The payment record and the purchase show `refunded`, and the ledger holds Carol -24 cents, Dan -36, the reviewer -7 and the validator -3 ([Refunds after payout in 2.9 Remuneration and payouts](09-remuneration.md#refunds-after-payout)). The next credits pay them off |
| Core version | A test peer requires a newer Core than the store builds pin. Both phones show "Update EVY" from [Offline and before the first read in 2.1 Hello EVY world](01-hello-evy-world.md#offline-and-before-the-first-read) and keep drawing saved UI documents. The [Core version rule in 1.9 Testing and release](../1-freenet-mobile-appkit/09-testing-and-release.md#core-version-and-the-network) holds for both builds |
| [Acceptance in 1.8 Thin-peer protocol](../1-freenet-mobile-appkit/08-thin-peer.md#acceptance) | Passes with EVY's workloads on the pinned Core build |
| [Acceptance in 2.1 Hello EVY world](01-hello-evy-world.md#acceptance) | Bootstrap results pass on development fixtures. Store builds open Home, navigate Home → Hello and pass greeting GET/subscription, offline and signature-rejection integration cases |
| [Acceptance in 2.2 EVY UI contracts and publishing](02-ui-contracts.md#acceptance) | Passes for complete EVY application releases containing Home, Hello and Marketplace |
| [Acceptance in 2.3 Native SDUI readers](03-readers.md#acceptance) | Passes on builds from one `mobile_builds.yml` run |
| [Acceptance in 2.4 SDUI data and actions](04-data-and-actions.md#acceptance) | Guestbook proving results pass on development fixtures; production resource/binding/action integration passes on store builds |
| [Acceptance in 2.5 EVY authoring and publishing](05-developer.md#acceptance) | Passes with the local EVY Developer editor and protected `evyctl` workspace |
| [Acceptance in 2.6 Payments](06-payments.md#acceptance) | Passes in Stripe test mode |
| [Acceptance in 2.7 EVY Marketplace](07-marketplace.md#acceptance) | Passes on the store builds |
| [Acceptance in 2.8 Attribution](08-attribution.md#acceptance) | Passes for EVY application version 8 with the Marketplace capability snapshot |
| [Acceptance in 2.9 Remuneration and payouts](09-remuneration.md#acceptance) | Passes, including the restore drill |
| Distribution | The TestFlight and Play internal testing builds pass review, and every [store requirement](#store-requirements) holds |

### Extracted domain suites

| Suite | Release integration |
| --- | --- |
| [1.10 Backup and restore](../1-freenet-mobile-appkit/10-backup-and-restore.md#acceptance) | Manual and automatic codec parity, complete snapshot and interrupted staged activation |
| [1.11 Cellular data and resource budgets](../1-freenet-mobile-appkit/11-cellular-data-and-resource-budgets.md#acceptance) | Node cap with separate provider/Stripe traffic policy and measurements |
| [2.11 EVY delegate and private records](11-delegate-and-private-records.md#acceptance) | Ordinary/recovery authority, pending purchase through migration/lock |
| [2.12 Listings and purchases](12-listings-and-purchases.md#acceptance) | Hosted admission, seller lookup, one-sale arbitration and retained evidence |
| [2.13 Release archive and policy evidence](13-release-archive-and-policy-evidence.md#acceptance) | Base policy plus attributed publication/recovery |
| [2.14 Backend operations and recovery](14-backend-operations-and-recovery.md#acceptance) | Shared custody, compromise drill, recovery and provider reconciliation |

Record domain results once with their defining owner. Keep these interaction cases and paired iOS/Android channel evidence in the release checklist.

## Store requirements

Deliver the pilot through TestFlight on iOS and Play internal testing on Android, and production through the iOS App Store and Android Google Play. Listings and requests must meet both stores' user-generated content rules and the [store requirements in 1.9 Testing and release](../1-freenet-mobile-appkit/09-testing-and-release.md#store-requirements).

| Requirement | What the release does | App Store | Google Play |
| --- | --- | --- | --- |
| Reporting | Report coverage for every production user-written flow passes [2.7 EVY Marketplace](07-marketplace.md#moderation-and-seller-admission); the named moderator and support response time are recorded | [Guidelines](https://developer.apple.com/app-store/review/guidelines/) 1.2 | [User-generated content](https://support.google.com/googleplay/android-developer/answer/9876937) |
| Blocking | Both readers pass the scoped Block action and restore fixtures in [2.3 Native SDUI readers](03-readers.md#report-and-block-actions), with product scope from [2.7 EVY Marketplace](07-marketplace.md#moderation-and-seller-admission) | Guidelines 1.2 | User-generated content |
| Content filter | Verified admitted sellers, moderator authority and tombstones filter every Home/Marketplace projection under [2.7 EVY Marketplace](07-marketplace.md#moderation-and-seller-admission) | Guidelines 1.2 | User-generated content |
| Terms | Listing and request flows retain verified seller/buyer terms acceptance under [2.7 EVY Marketplace](07-marketplace.md#moderation-and-seller-admission) | – | User-generated content |
| Support URL | EVY publishes a support page with contact details, the report response time and the dispute deadlines. Both store listings link to it | Guidelines 1.2 | User-generated content |
| Privacy details | Declare the card and contact details Stripe's payment sheet collects, the device data Stripe collects against fraud ([Stripe mobile SDK privacy details](https://support.stripe.com/questions/stripe-ios-sdk-privacy-details)), the seller identity and bank details Stripe-hosted onboarding collects, the public item data (title, photos, price, pickup postcode and map point), and the EVY public keys and IP addresses the node sends to peers | [App privacy details](https://developer.apple.com/app-store/app-privacy-details/) | [Data safety](https://support.google.com/googleplay/android-developer/answer/10787469) |
| Physical goods | Bob pays for Alice's skateboard in Stripe's payment sheet, as [Store payment rules in 2.6 Payments](06-payments.md#store-payment-rules) sets | Guidelines 3.1.3(e) | [Payments policy](https://support.google.com/googleplay/android-developer/answer/9858738) section 3 |
| Financial features | Declare in Play Console that EVY takes card payments for physical goods through Stripe | – | [Financial features declaration](https://support.google.com/googleplay/android-developer/answer/13849271) |
| Downloaded code | `contract-keys.json` pins the hello data contract key, the `ui.evy` application key and its UI contract code hash, and the app carries the EVY delegate's Wasm. The readers verify UI documents against the pinned publisher keys. UI documents supply screen data to compiled native readers. Preview scanning and preview keys are restricted to test builds | Guidelines 2.5.2; [DPLA](https://developer.apple.com/support/terms/apple-developer-program-license-agreement/) 3.3.1(B) | [Device and network abuse](https://support.google.com/googleplay/android-developer/answer/16559646) |
| Review notes | The notes explain the embedded node in the thin-peer role and the Pulley interpreter, citing Guideline 2.5.2 and DPLA 3.3.1(B) for EVY's contracts and delegate. They say the readers draw signed screen data, that payments are for physical goods picked up in person, and which test listing to open | Guidelines 2.5.2 and 3.1.3(e); DPLA 3.3.1(B) | – |

- `mobile_builds.yml` runs every [store build check in 1.9 Testing and release](../1-freenet-mobile-appkit/09-testing-and-release.md#store-build-checks) on the store variant, with the iOS 17 deployment target and Android `minSdk` 28 from 2.1 Hello EVY world, and `fdev verify-merge` on each contract in `freenet/contracts/`.
- The EVY delegate seals with X25519, HKDF-SHA256 and ChaCha20-Poly1305, which the encryption requirement in 1.9 Testing and release already declares.

## Launch approvals

The EVY operator records each approval in `docs/launch/approvals.md` in evy, with the approver, the date and a link to the evidence. `services/payment` and `services/remuneration` switch to Stripe live mode keys only when every row is approved.

| Approval | Approver | Evidence |
| --- | --- | --- |
| Operators | EVY operator | A named primary and backup operator for the EVY operator node, `services/payment`, `services/attribution` and `services/remuneration`, plus the purchase/photo hosting inventory. Storage quotas, repair alerts and listing/dispute retention periods are set and tested |
| Stripe account and country | Financial operations lead | EVY's Australian platform account approved for Connect in live mode, charging in AUD, and test-mode onboarding of a seller like Alice and a contributor like Carol ([Fees and seller accounts in 2.6 Payments](06-payments.md#fees-and-seller-accounts)) |
| Store payment rules | Financial operations lead | A physical-goods sale paid in Stripe's payment sheet on iOS and Android, under Store payment rules in 2.6 Payments, and both store reviews passed |
| Money rules | Financial operations lead | EVY's signed application policy with `fee_rate_bp` 100 ([Application policy in 2.8 Attribution](08-attribution.md#application-policy)). EVY pays Stripe's fees, refunds and chargebacks from its own budget (Fees and seller accounts in 2.6 Payments). Negative balances after a refund after payout, and EVY carrying any that later earnings never pay off (Refunds after payout in 2.9 Remuneration and payouts) |
| Payouts | Financial operations lead | Values for `payout_minimum_cents` and `payout_schedule`, which [Balances and payouts in 2.9 Remuneration and payouts](09-remuneration.md#balances-and-payouts) leaves to the EVY publisher, signed in an EVY application policy version with Stripe's Connect fees in mind |
| Retention and recovery | EVY operator | The retention period for the monthly full backups, and a passing restore drill that meets every recovery point and time in [Operating the services in 2.14 Backend operations and recovery](14-backend-operations-and-recovery.md#operating-the-services) |
| Key custody | EVY operator | A named holder and tested backup for the EVY publisher key, the payment and attribution service keys, the Stripe restricted keys and webhook secret, the backup key, and the `mobile-builds` secrets from [Builds from GitHub in 2.3 Native SDUI readers](03-readers.md#builds-from-github) |
| Moderation and disputes | Marketplace product owner | A named Marketplace moderator, the report response time, the dispute deadlines (Bob raises a dispute within 14 days of the pickup, and the moderator decides within 7 days) and the moderator's refund access through `payment_refund` or the Stripe Dashboard ([Refunds in 2.6 Payments](06-payments.md#refunds)). Card chargebacks follow [Stripe's dispute flow](https://docs.stripe.com/disputes) |
| Participant terms and privacy notices | Marketplace product owner | The seller and buyer terms. A privacy notice that lists what anyone can read in the items and purchase contracts, the pickup address only Alice and Bob read, and what Stripe holds |

## Production completion

Record the accepted upstream decisions and implementation/fixture evidence for applicable [decision gates in README.md](../README.md#decision-gates), including inherited AppKit requirements. Production on iOS and Android requires those upstream changes in the packaged Core and passing reader, contract and backend tests.

| Stage | iOS evidence | Android evidence | Shared gate |
| --- | --- | --- | --- |
| Pilot | TestFlight beta approval, delivery receipt, installed build and test results | Play internal-testing delivery receipt, installed build and test results | Named operators/moderator, signed policy, durable archive, admission/hosting quotas and launch approvals |
| Production | App Store approval, production listing URL and fresh install/update of the approved build | Google Play production approval, production listing URL and fresh install/update of the approved build | Production acceptance below; matching source commit, execution policy, UI identity and reader version |

Milestone 2 (EVY on Freenet) completes when both production channels are approved and installable, production reader/recovery/moderation suites pass, authoring tools are released, and the paired first-sale evidence and recovery drill are recorded. Payment signing-key revocation and attribution-capacity completion evidence are production release dependencies. Set store-policy/SDK requirements from a dated review of the actual submission builds.

Promote tested signed artifacts through the build/delivery owner in [2.3 Native SDUI readers](03-readers.md#build-and-channel-evidence). Production startup opens `routes.entry` Home; preview scanning uses test builds. Publish a document requiring a higher reader only after compatible production builds are installable on both platforms.

## The first paid sale

The first live sale is a pilot:

- Run the pilot in Sydney, Australia, using AUD. Sydney is the city of Marketplace's fixture addresses in [service_data.json](https://github.com/EVY-Platform/evy/blob/d0fb7e6475f1dfc5c74325e37d4e92aed88d84ed/scripts/fixtures/services/service_data.json), and AUD is the one currency of EVY's Stripe code.
- The EVY publisher verifies seller admission and publishes the `sellers` lookup defined in [2.7 EVY Marketplace](07-marketplace.md#moderation-and-seller-admission) ([What is cloned in 2.7 EVY Marketplace](07-marketplace.md#what-is-cloned)). Search in the "Home" flow shows only their items. Every listed seller has finished Stripe onboarding.
- The operator enrolls pilot buyers and issues the admission credentials and quotas from [Listing admission and one sale in 2.12 Listings and purchases](12-listings-and-purchases.md#listing-admission-and-one-sale). Seller-signed listings authorize the certified service to admit requests and reserve one sale.
- Invite pilot users to install the store builds from TestFlight and Play internal testing. [TestFlight](https://developer.apple.com/testflight/) takes up to 10,000 external testers after Apple's beta review, and [Play internal testing](https://support.google.com/googleplay/android-developer/answer/9845334) up to 100 testers.

Alice on her iPhone sells her skateboard for 70 dollars to Bob on his Android phone, with Saturday pickup:

| Step | Who | What happens | Owning plan | What is checked |
| --- | --- | --- | --- | --- |
| 1 | Alice | Taps "Get paid" and links her Stripe account | [Fees and seller accounts in 2.6 Payments](06-payments.md#fees-and-seller-accounts) | `account.updated` shows transfers enabled. Her key is on the seller list |
| 2 | Alice | Accepts the seller terms and lists the skateboard in "Create item" for 70 dollars, with photos and Saturday pickup times | [The skateboard sale in 2.7 EVY Marketplace](07-marketplace.md#the-skateboard-sale) | The item is `available` on Bob's phone and on an independent peer |
| 3 | Bob | Accepts the buyer terms and taps "Request 10:00" for Saturday | The skateboard sale in 2.7 EVY Marketplace, with `ui_version` and `ui_digest` from [Purpose in 2.9 Remuneration and payouts](09-remuneration.md#purpose) | The purchase record is signed by Bob's buyer key, with `amount_cents` 7000, `fee_cents` 70 and the version and digest of the UI document his reader drew, the accepted policy version and digest, and a verified admission receipt |
| 4 | Alice | Taps "Accept" in "For you" | The skateboard sale in 2.7 EVY Marketplace | The payment service confirms Bob's reservation fence and `pickup_pending`. Alice's and Bob's phones open the sealed pickup address |
| 5 | Bob | At the pickup on Saturday, taps "Item received" and pays in Stripe's payment sheet | [Paying on a phone in 2.6 Payments](06-payments.md#paying-on-a-phone) | One PaymentIntent of 7,000 cents AUD with a 70-cent application fee. The payment record is `intent` |
| 6 | Alice | Taps "Confirm" in "Item given" | Paying on a phone in 2.6 Payments | The payment record is `succeeded` and the purchase `sold`. Alice's account receives 69.30 dollars and EVY holds 0.70 |
| 7 | Remuneration service | Credits the 0.70 dollars | [Crediting a completed purchase in 2.9 Remuneration and payouts](09-remuneration.md#crediting-a-completed-purchase) | One allocation per capability and recipient. With EVY application version 8's Marketplace snapshot: Carol 24 cents, Dan 36, the reviewer 7 and the validator 3 |
| 8 | Remuneration service | Pays each balance after `payout_hold_days`, once it reaches `payout_minimum_cents`, on `payout_schedule` | Balances and payouts in 2.9 Remuneration and payouts | One Stripe transfer per payout. Carol sees it on her payouts page |

The sale then runs again with the seller on an Android phone and the buyer on an iPhone, with the same checks at each step. The EVY operator writes both runs to `docs/launch/first-sale.md` in evy, with the build numbers, the EVY application UI version and the purchase contract keys.

## Releasing from GitHub

A maintainer releases EVY from one evy commit. Readers reach the stores before any UI version that needs them, as [Reader compatibility in 2.2 EVY UI contracts and publishing](02-ui-contracts.md#reader-compatibility) requires.

```mermaid
flowchart TD
    K[evyctl keys writes<br>contract-keys.json] --> B[mobile_builds.yml<br>variant: store and test]
    B --> T{Release tests pass<br>on iOS and Android?}
    T -- no, fix and rebuild --> B
    T -- yes --> S[Builds live in TestFlight<br>and Play internal testing]
    S --> R[Tag reader-v N]
    R --> U[evyctl ui publish<br>one complete EVY application]
    U --> D[Verify archived bytes<br>and independent network readback]
```

| Step | What happens | Check |
| --- | --- | --- |
| 1. Pin keys | `evyctl keys --out types/freenet/contract-keys.json` runs on the release commit, as [Pinned keys in 2.1 Hello EVY world](01-hello-evy-world.md#pinned-keys) describes, and the file is committed with it | CI in evy passed, including the `legacy.toml` check. Each pinned key reads back on the public network; payment journals and attribution archive recovery have passed their owning plans' setup gates |
| 2. Build | The maintainer runs `mobile_builds.yml` on the commit with `variant: store`, then with `variant: test`<br>Publishes each variant to TestFlight and Play internal testing | The build number and the `versionCode` are the workflow run number. The run summary lists the commit, both build numbers, the freenet-appkit release and the hash of `contract-keys.json`. The release checklist records the pinned Core version and the network's `min-compatible-version` |
| 3. Test | The [release tests](#release-tests) run on these builds. UI versions that need the new reader run as test UI contracts in the EVY test build | Every row passes |
| 4. Tag | Once both pilot builds are installable, evy tags the commit `reader-v<N>`, where N is its `reader_version` | The tag names the verified reader build; production promotion retains its exact source/artifact identity |
| 5. Publish the application | `evyctl ui publish --key evy-publisher freenet/ui/evy.json --min-reader-version <N>` reserves one application version and publishes the complete document, following [Publishing a UI version in 2.2 EVY UI contracts and publishing](02-ui-contracts.md#publishing-a-ui-version) and [Publishing the application in 2.5 EVY authoring and publishing](05-developer.md#publishing-the-application) | The archive receipt and independent second-node readback identify the exact signed application bytes. Home, Hello and Marketplace routes resolve within that document. |
| 6. Deliver authoring tools | Release the local EVY Developer editor and `evyctl` from the same commit, with the matching schema, publisher journal format and preview fixtures | A contributor exports a full application draft, validates and previews it on iOS and Android, then the authorized publisher confirms one publication. |

A compatible application UI version publishes with step 5 when the required reader is available in both stores. Adding an internal feature updates the complete application document. A change to `ui.evy`, permitted executable hashes or component roles ships in matching iOS and Android builds.
