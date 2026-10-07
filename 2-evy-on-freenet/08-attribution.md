# 2.8 Attribution

## Repositories

| Repository | Role | Work in this plan |
| --- | --- | --- |
| [evy](https://github.com/EVY-Platform/evy) | Modified | `services/attribution` and the EVY GitHub App. EVY Developer (`web/`) from [2.5 EVY Developer on Freenet](05-developer.md) gains contributor screens, proposal mode and review screens. `services/payment` takes the fee rate from the service policy. UI proposal contract in `freenet/contracts/ui_proposal/`. Contributor keys and new messages in the EVY Developer delegate |
| [freenet-core](https://github.com/freenet/freenet-core) | Used | Node for the attribution service, delegate secret backup |
| [freenet-stdlib](https://github.com/freenet/freenet-stdlib) | Used | TypeScript client for the attribution service |

## Purpose

This plan credits the people who improve an EVY service. Two kinds of work count: a UI proposal drafted in EVY Developer, and code merged into `evy`. The attribution service (`services/attribution` in evy, TypeScript on Bun with Postgres like [`services/marketplace`](https://github.com/EVY-Platform/evy/blob/dev/services/marketplace/package.json)) turns each piece of accepted work into attribution units for one capability of the service.

- Carol moves the "Listing dimensions" row of Marketplace's "Create item" flow from the "Create listing" page to the "Describe item" page ([service_sdui.json](https://github.com/EVY-Platform/evy/blob/dev/scripts/fixtures/services/service_sdui.json)). The service publisher publishes her proposal as Marketplace UI version 2, and Carol earns 6.8 units for `marketplace.item.create`.
- Dan opens a pull request to evy that makes Marketplace's contract accept a pickup request only at a time Alice offered. It merges, and Dan earns 4.25 units for `marketplace.item.buy`.

Units decide each contributor's part of the 1% contributor fee that [Fees and seller accounts in 2.6 Payments](06-payments.md#fees-and-seller-accounts) collects on each sale.

## Contributor keys

Carol's contributor key is an Ed25519 key in the EVY Developer delegate on her own node, from [The EVY Developer bundle in 2.5 EVY Developer on Freenet](05-developer.md#the-evy-developer-bundle). The page asks the delegate to sign and never holds the private key. A web app in Core's shell reaches only its own node ([client_api.rs](https://github.com/freenet/freenet-core/blob/main/crates/core/src/server/client_api.rs)) and can open new tabs ([#5100](https://github.com/freenet/freenet-core/pull/5100)), so EVY Developer sends each signed statement to the attribution service by opening the service's contributor page in a new tab.

| Action | In EVY Developer | At the attribution service |
| --- | --- | --- |
| Register | Carol clicks "Create contributor key". The new `ContributorKey` message creates the key, and `SignContribution` signs a registration statement | Checks the signature and creates an `ActorId` for the key |
| Link GitHub | Carol signs in with GitHub on the contributor page. Only code work needs it | Stores her GitHub user ID with her `ActorId` |
| Rotate | Carol clicks "Rotate key". `RotateContributorKey` creates a new key and signs a statement with the old key that names the new one | Moves her `ActorId`, roles and units to the new key |
| Back up | Carol runs Core's [`freenet secrets export`](https://github.com/freenet/freenet-core/blob/main/docs/secrets-at-rest.md), which writes her node's delegate secrets to a file encrypted with her passphrase | Nothing |

`SignContribution { kind, record }` also signs proposals, reviews, size estimates, challenges and sign-in statements. `SignServiceRecord { service, kind, record }` signs a policy, acceptance or publication confirmation with the publisher key, after the author confirms in Core's prompt, as `SignUiVersion` does.

| Carol's situation | What the attribution service does |
| --- | --- |
| She restores her backup file | Nothing. The key and `ActorId` are unchanged |
| She lost the key and the backup | She creates a new key and signs in with her linked GitHub account. The service links the new key to her `ActorId` after a 7-day hold. A signature from the old key during the hold cancels the link |
| She lost the key, the backup and the GitHub account | The new key gets a new `ActorId`. Her earlier units stay with the old one |

## Service policy

Each EVY service has a **UI proposal contract**, built from `freenet/contracts/ui_proposal/` in evy. Its parameters are those of the service's UI contract in [The UI contract in 2.2 EVY UI contracts and publishing](02-ui-contracts.md#the-ui-contract): the service publisher's verifying key and the service ID. Its state holds the service policy, the registered contributor keys, the open UI proposals, their review records and the attribution snapshots. The EVY Developer bundle gains its Wasm as `evy.ui_proposal`, and `types/freenet/contract-keys.json` gains its code hash under `code.ui_proposal`. EVY Developer derives each service's UI proposal contract key from it, as it derives UI contract keys in [The home service in 2.2 EVY UI contracts and publishing](02-ui-contracts.md#the-home-service).

The service publisher signs each policy version in EVY Developer with `SignServiceRecord`. For Marketplace the key is the EVY publisher key from [The EVY publisher key in 2.1 Hello EVY world](01-hello-evy-world.md#the-evy-publisher-key). Policy version 1 PUTs the contract. Setup archives the service's current signed UI document and confirms its readback before enabling attribution-backed publication and payouts.

- The contract keeps the highest policy version signed by the key in its parameters.
- Each record is signed over its own prefix, such as `evy.ui-proposal/1`, and its RFC 8785 canonical JSON, as hello states are.
- A new version applies to work accepted after it, and each acceptance records the version it used.
- From this plan on, the payment service takes the fee rate from the service policy's `fee_rate_bp`, 100 basis points (1%) for Marketplace, and checks each purchase's `fee_cents` against it, rounded half up as in [Fees and seller accounts in 2.6 Payments](06-payments.md#fees-and-seller-accounts). A service with no policy, such as `hello`, keeps the 1% fee of 2.6 Payments.

```jsonc
{
  "service": "marketplace",                              // EVY service ID, as in its UI contract
  "version": 1,                                          // a new number for every change
  "fee_rate_bp": 100,                                    // contributor fee on each sale: 1%, so 0.70 of 70 dollars
  "capabilities": {                                      // credited behavior, by capability ID
    "marketplace.item.create": {                         // "Create item": "Create listing" to "Payment options"
      "weight_bp": 4000,                                 // 40% of each fee. All weights total 10,000
      "flows": ["ca47e6c5-da19-4491-8422-adb40d9e8a27"]  // flow IDs in the UI document
    },
    "marketplace.item.buy": {                            // "View Item": pickup request to "Item received"
      "weight_bp": 6000,                                 // 60% of each fee
      "flows": ["74a49d4b-2176-4925-857a-e29e2991f1bd"]  // flow IDs in the UI document
    }
  },
  "sizes": [1, 2, 3, 5, 8, 13, 21],                      // the sizes a piece of work can have
  "role_split_bp": [8500, 1000, 500],                    // units to contributors, reviewer and validators
  "reviewers": ["actor:..."],                            // ActorIds that review for the service publisher
  "validators": ["actor:..."],                           // ActorIds that size work
  "attribution_key": "ed25519:...",                      // attribution service key: snapshots and registered keys
  "archive_url": "https://attribution.example/ui-archive", // HTTPS archive page and API, signed with the policy
  "challenge_days": 30,                                  // days after acceptance to open a challenge
  "payout_hold_days": 30,                                // days after a purchase is sold before a share is payable
  "payout_minimum_cents": "...",                         // set by the service publisher before launch
  "payout_schedule": "...",                              // set by the service publisher before launch
  "signature": "ed25519:..."                             // by the service publisher key
}
```

## Archiving before publication

For a service using attribution, `evyctl ui publish` and EVY Developer archive each signed UI document before its PUT or UPDATE. The service policy supplies the HTTPS `archive_url` and `attribution_key`. The archive identity is the UI contract key, service, version and `ui_digest`: the 32-byte BLAKE3 hash of the exact complete signed bytes sent as contract state. The publisher saves those bytes and the receipt for retries.

| Step | Required behavior |
| --- | --- |
| 1. Submit | The publisher supplies the signed document and its UI contract identity. EVY Developer uses the archive service page in a separate tab; `evyctl` calls the archive API. |
| 2. Check | The attribution service checks the publisher signature against the UI contract's parameters, the service, version, document validation and size cap, then computes the digest itself. |
| 3. Save | Create a receipt signed with `attribution_key` under `evy.ui-archive/1`, covering the UI contract key, service, version, digest and policy version. Save an immutable copy of the exact signed document bytes, receipt and archive manifest in the second-region S3-compatible bucket from [Operating the services in 2.9 Remuneration and payouts](09-remuneration.md#operating-the-services), then commit the archive index and receipt in Postgres. |
| 4. Acknowledge | Return the saved receipt after the bucket objects and database commit are durable. A repeated submission returns the same receipt. |
| 5. Publish | The publisher verifies the receipt against the signed policy and pending document identity, sends those same bytes to Freenet, and performs the publishing tool's readback check. |
| 6. Confirm | The publisher signs a publication confirmation containing the archive identity and readback evidence. The attribution service verifies it, saves it with the immutable archive evidence and records the version as published. This confirmation can be retried after an interruption. |

An acknowledged archive entry is prepared for publication. UI acceptance and snapshots use entries with verified publisher publication confirmation. UI proposal acceptance records name the same version and digest. The service can process that confirmation and create a snapshot from the archived bytes after later versions replace the live UI document. Each snapshot names the service, version and digest, and the archive retains its signed snapshot with the publication evidence.

Archive failure keeps publication pending until a valid durable receipt is available. Identical retries keep one archive entry; different signed documents retain separate digest identities. The immutable copies cover acknowledged documents and signed snapshots within the database's recovery window. Recovery verifies and reindexes these copies before resuming attribution or payout calculations.

## Proposing a UI change

```mermaid
flowchart LR
    Carol[Carol in EVY Developer] -->|signed UI proposal| Prop[Marketplace UI proposal contract]
    Val[Validator] -->|size estimate| Prop
    Pub[Service publisher in EVY Developer] -->|review and acceptance| Prop
    Pub -->|signed bytes before publication| Archive[Durable UI archive]
    Archive -->|signed receipt| Pub
    Pub -->|UI version 2| UI[Marketplace UI contract]
    Prop --> Attr[Attribution service]
    Pub -->|publication confirmation| Attr
    Archive -->|version 2 bytes| Attr
    Attr -->|snapshot for version 2| Prop
```

| Step | Who | Rule |
| --- | --- | --- |
| 1. Draft | Carol | Opens Marketplace as [Opening a service in 2.5 EVY Developer on Freenet](05-developer.md#opening-a-service) describes. Without the publisher key, EVY Developer opens it in proposal mode: she edits a draft, and Publish becomes Propose. She moves the "Listing dimensions" row to the "Describe item" page |
| 2. Preview | Carol | Checks the change on the EVY test build on iOS and Android, as [Previewing on a phone in 2.5 EVY Developer on Freenet](05-developer.md#previewing-on-a-phone) describes |
| 3. Propose | Carol | Picks `marketplace.item.create` and size 8. EVY Developer assembles and validates the document as [Publishing from EVY Developer in 2.5 EVY Developer on Freenet](05-developer.md#publishing-from-evy-developer) does. `SignContribution` signs a UI proposal: each changed flow whole (here "Create item", about 17 KB), the version it starts from (1), the capabilities and contributors with shares that total 10,000, and the size. EVY Developer sends it as an UPDATE<br>--> Produces the UI proposal |
| 4. Size | Validator | Signs a size estimate in EVY Developer |
| 5. Review | Service publisher | A reviewer from the policy opens the proposal beside version 1, previews it on iOS and Android and signs an approval. A rejection closes the proposal |
| 6. Publish | Service publisher | Builds the next document from the live version with the proposal's flows in place, archives its signed bytes and waits for the receipt, then publishes Marketplace UI version 2 and confirms readback, as [Publishing a UI version in 2.2 EVY UI contracts and publishing](02-ui-contracts.md#publishing-a-ui-version) describes. Signs an acceptance record naming the proposal, version 2 and the document's digest |
| 7. Link | Attribution service | Uses version 2's archived bytes, verifies the publication confirmation and acceptance digest, and records the acceptance<br>--> Produces Carol's acceptance and units |

- The contract caps its state at 512 KiB, as the UI contract does. It accepts a proposal only from a registered contributor key, with one open proposal per key. The attribution service writes the registered keys, signed with `attribution_key`.
- It accepts an acceptance record only when the service publisher key signed it, and a [snapshot](#attribution-units) only when `attribution_key` signed it.
- A closed proposal keeps its record and drops its flows. The attribution service keeps their bytes.
- The attribution service accepts the work only when the reviewer and validators are on the policy's lists, nobody reviews or sizes their own proposal, the size is in `sizes`, shares total 10,000, every changed flow belongs to a claimed capability and no challenge is open.

### Capacity follow-up

The service's UI proposal contract keeps its 512 KiB state limit. Contributor registrations, proposal and review records, policy history and snapshots share that budget. An update that exceeds the limit leaves the accepted contract state intact; EVY Developer and the attribution service retain the draft or pending signed record and report the capacity limit.

Long-term attribution storage is a planned follow-up. That work will define how the service accommodates growing contribution history and snapshots while preserving verifiable evidence for challenges and historical payouts. The storage structure and migration rules remain open questions for that work.

## Code contributions

Code reaches attribution through the EVY GitHub App, served by `services/attribution` and installed on `evy`. Dan's pull request description names the service, the capability and the size:

```text
EVY-Service: marketplace
EVY-Capability: marketplace.item.buy
EVY-Size: 5
```

| Step | Who | Rule |
| --- | --- | --- |
| 1. Check | EVY GitHub App | Checks that the author's GitHub account is linked to a contributor key, the capability is in Marketplace's policy and the size is in `sizes`. Sets the required check "EVY attribution" to pending |
| 2. Review | Reviewer | Approves the pull request on GitHub from a linked account on the policy's `reviewers` list |
| 3. Size | Validator | Comments `/evy size 5` from a linked account on the `validators` list |
| 4. Confirm eligibility | Attribution service | Validates the review, size, contributor shares and policy. Saves an eligibility record for the exact head commit and contribution metadata, and marks the check passed<br>--> Produces eligibility to merge |
| 5. Merge | Maintainer | Merges the eligible head into the configured evy target branch. GitHub branch protection requires the passed check for that head |
| 6. Accept merged work | Attribution service | Verifies the merge through GitHub's API, matches the merged PR's head to the eligible head and checks the contribution against the policy in force at acceptance. Commits the acceptance and units together, recording repository ID, PR number, reviewed head, merge commit, merge time and acceptance time<br>--> Produces Dan's acceptance and units for the first Marketplace UI version published after this verified acceptance |

- The author holds all contributor shares. Shared work lists each contributor's share in the description, and each listed contributor confirms with a `/evy confirm` comment from their linked account.
- Reviews, size estimates and share confirmations are bound to the eligible head and contribution metadata. A new commit or a change to that metadata sets the check back to pending until the approvals cover the new values.
- A pull request with no `EVY-Capability` line passes the check at once and merges like any other change.

The EVY GitHub App verifies webhook signatures and uses pull-request events to trigger a check of the current PR through [GitHub's pull request API](https://docs.github.com/en/rest/pulls/pulls#get-a-pull-request). Acceptance requires a verified merge into the configured repository and target branch, the eligible reviewed head and complete attribution checks. GitHub's reviewed head and resulting merge commit are recorded separately, covering merge, squash and rebase workflows.

Postgres allows one initial code acceptance per repository ID and PR number. Repeated or reordered events and a service restart reconcile the PR to that same acceptance. Eligible work awaiting merge stays in the eligibility records; only committed acceptances supply units to snapshots. A merge awaiting complete verification stays pending attribution until the service finishes its checks. Challenge corrections follow [Attribution units](#attribution-units).

## Attribution units

The attribution service splits each accepted size by the policy's `role_split_bp` and stores units as integer ten-thousandths of a size point. If the first validator's estimate differs from the proposed size, a second validator picks one of the two. The validator part goes in equal parts to the validators whose estimate equals the accepted size. The same reviewer and validator sign both examples, and each first estimate matched.

| Acceptance | Capability | Size | Contributor | Reviewer | Validator |
| --- | --- | ---: | ---: | ---: | ---: |
| Carol's UI proposal | `marketplace.item.create` | 8 | Carol 6.8 (68,000) | 0.8 (8,000) | 0.4 (4,000) |
| Dan's pull request | `marketplace.item.buy` | 5 | Dan 4.25 (42,500) | 0.5 (5,000) | 0.25 (2,500) |

For each published UI document identity, the attribution service signs a **snapshot** with `attribution_key`, saves its immutable bucket copy, then writes it to the service's UI proposal contract and makes it available to remuneration. EVY Developer shows Carol her units and anyone can check them.

- A snapshot identifies the archived service, UI version and document digest. It lists the units per capability and `ActorId` of every acceptance that counts in that version, and the policy version in force when the version was published.
- A UI proposal counts from the version that published it. A pull request counts from the first UI version published after its merge is verified and its acceptance is committed. Snapshots take units from committed acceptances.
- A signed snapshot never changes. Marketplace version 2's snapshot holds both rows above, because Dan's pull request merged and its acceptance was verified and committed before version 2. A delayed merge verification contributes to a later version's snapshot.

| Challenge | Opened by | Resolved when |
| --- | --- | --- |
| Omitted author | The person left out | The claimant and every contributor on the work sign a resolution |
| Shares | A contributor on the work | Every contributor on the work signs a resolution |
| Size | A contributor or validator on the work | A validator outside the work picks one of the disputed sizes |

A challenge on a UI proposal is a signed record in the UI proposal contract. A challenge on a pull request is a `/evy challenge` comment from a linked account. An open challenge blocks acceptance. A challenge within `challenge_days` after acceptance marks the acceptance as challenged. A resolution that changes shares or size creates a new acceptance, which counts from the next UI version's snapshot. Older snapshots keep their units.

## Acceptance

- Carol registers and rotates her key in EVY Developer, and the private key stays in the EVY Developer delegate. A rotation signed by the old key keeps her `ActorId`. A GitHub recovery links a new key after the 7-day hold, and an old-key signature during the hold cancels it.
- The UI proposal contract refuses a policy with a lower version or another signer, a proposal from an unregistered key, a second open proposal from one key, a state over 512 KiB, an acceptance not signed by the service publisher key and a snapshot not signed by `attribution_key`.
- The attribution service refuses self-review, self-sizing, reviewers and validators missing from the policy, sizes outside `sizes`, share totals other than 10,000 and a proposal that changes a flow outside its capabilities.
- On iOS and Android, the Marketplace "Create item" flow shows "Listing dimensions" on the "Describe item" page after the service publisher publishes Carol's proposal as version 2.
- Dan's pull request stays pending until the review and size arrive. A changed head or contribution metadata renews the eligibility checks, and GitHub blocks the merge until they pass. A pull request with no EVY lines merges with the check passed.
- An approved PR awaiting merge and a PR closed without merging each retain zero attribution units. A verified merge of the eligible head creates one initial acceptance and the units in the table. Merge, squash and rebase fixtures preserve both the reviewed head and resulting merge commit.
- Duplicate and reordered merge events, two racing workers and a service restart produce the same initial acceptance and units. A merge with a head that differs from the eligibility record stays pending attribution until valid checks cover that head.
- Publish a UI version while Dan's PR is eligible and awaiting merge, then merge and verify it. His units appear in the first UI version published after the acceptance commits. A delayed merge verification uses a later snapshot and preserves existing signed snapshots.
- Marketplace version 2's snapshot holds exactly the units in the table, recomputing it from stored acceptances reproduces it, and units always sum to the accepted size.
- Publish versions 2 and 3 rapidly while snapshot processing is paused. Each receives a durable archive receipt before its Freenet update. After processing resumes, version 2's archived bytes and publication evidence reproduce its acceptance and signed snapshot even when the live contract holds version 3.
- Archive outages, invalid receipts, interrupted publication and retries preserve the exact pending signed bytes. Prepared entries become snapshot sources after verified publication confirmation. Digest, signature or contract-identity mismatches fail validation.
- Restore the attribution database to a point before an acknowledged archive write. Recover its document, receipt, publication evidence and signed snapshot from the immutable bucket copies, verify their identities and signatures, and rebuild the archive index before remuneration resumes.
- An open challenge blocks acceptance. A resolution after version 2 changes only the snapshots of later versions.
