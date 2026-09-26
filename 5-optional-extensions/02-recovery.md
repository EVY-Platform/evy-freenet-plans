# Extended customer backup and recovery

Plan ID: 5.2. This optional extension adds automated backups, additional storage destinations and recovery across a user's selected applications. It builds on the tested app-specific encrypted export/import baseline in [identity 1.5](../1-freenet-mobile-appkit/05-identity.md).

Prerequisites: protected keys and package validation in 1.5, [host admission 1.3](../1-freenet-mobile-appkit/03-host.md), [multi-app sessions 2.2](../2-evy-mobile-app/02-sessions.md), [permissions 2.4](../2-evy-mobile-app/04-permissions.md), [durable operations 1.6](../1-freenet-mobile-appkit/06-data-and-operations.md), and [migration 1.7](../1-freenet-mobile-appkit/07-migration.md) for records spanning component versions. Mobile use inherits [1.10's thin-peer and cellular budget gate](../1-freenet-mobile-appkit/10-thin-peer.md).

## Scope

| Addition | Owned behavior |
| --- | --- |
| Automated backup | Schedule bounded exports, record successful checkpoints and expose incomplete or stale coverage |
| Storage destinations | Add user-selected destinations with authentication, retention, deletion and availability checks |
| Coverage reporting | List covered apps, key purposes, delegate identities, private records, pending work and unavailable dependencies |
| Broader recovery | Restore selected apps onto an authorized device, including supported lineage and component migrations |
| Recovery drills | Prove retained packages and their keys can restore the declared coverage after device loss |

Customer recovery uses the package cryptography, same-key FNSX rule, session renewal and privacy disclosures owned by [1.5](../1-freenet-mobile-appkit/05-identity.md). Application adapters declare their export/import support and recovery prerequisites. Cross-key delegate imports and publisher continuity follow [migration](../1-freenet-mobile-appkit/07-migration.md).

The user selects applications, records and destinations. Each destination states who can read metadata, who holds decryption authority, any service cost, and who retains copies. Automatic backups follow user-approved network, byte, retry and retention limits. On mobile, backup traffic shares the application's budget under [EVY 2.5](../2-evy-mobile-app/05-lifecycle.md).

## Recovery coverage

A coverage checkpoint records the package version, creation time, application/content references, component parameters, protocol versions and the last verified export for each selected app. References to network records include their availability assumptions. The [bundle retention rules](../1-freenet-mobile-appkit/04-bundles.md) provide publisher artifacts needed by supported restores.

Coverage must distinguish:

- Recoverable keys and records included in the package.
- Hardware-bound keys with a supported successor-authorization path.
- Records that require another device, a retained archive or a service.
- Interrupted exports and data changed since the last completed backup.
- Service-managed contributor or financial accounts whose authority requires the service's checks.

Keep a verified recoverable copy while a replacement package or destination is being validated. Reconcile restored operations through [1.6](../1-freenet-mobile-appkit/06-data-and-operations.md) before retries. [Device sync 5.3](03-sync-and-collaboration.md#consumer-device-sync) supplies continuous synchronization under its own gate. Financial service queues, backups and restore drills belong to [commercial operations 3.7](../3-attribution-remuneration-payment/07-operations.md).

## Acceptance

- Restore selected applications on a fresh device after loss of the source device. Report exactly which keys, records and pending operations recovered.
- Interrupt export, upload, destination changes and restore at each durable boundary. Resume safely and retain the last verified recovery copy.
- Test an unavailable destination, expired credentials, stale package, lost hardware-bound key, corrupt data and exhausted storage.
- Revoke a destination and stop subsequent uploads. Report which retained copies remain under that destination's policy.
- Recovery drills exercise supported component migrations and obtain fresh host sessions. Services apply their own contributor and financial recovery checks.
- Automated backups stay within approved mobile lifecycle and traffic budgets. Incomplete coverage remains visible until a verified checkpoint replaces it.
