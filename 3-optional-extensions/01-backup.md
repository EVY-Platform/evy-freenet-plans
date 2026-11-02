# 3.1 Automated backup

## Repositories

| Repository | Role | Work in this plan |
| --- | --- | --- |
| [evy](https://github.com/EVY-Platform/evy) | Modified | Automatic backup settings in the SwiftUI and Compose apps |
| [freenet-core](https://github.com/freenet/freenet-core) | Used | Export and import of delegate secrets |
| [freenet-appkit](https://github.com/glesage/freenet-appkit) | Used | Backup and restore screens from 1.10 Backup and restore |

## Purpose

This plan is an idea note for backing up EVY on iOS and Android without Alice starting each backup herself.

[1.10 Backup and restore](../1-freenet-mobile-appkit/10-backup-and-restore.md) gives Alice a manual backup: she exports a file protected by her recovery code and restores it on a new phone. [Application data inventory in 2.11 EVY delegate updates and recovery](../2-evy-on-freenet/11-delegate-updates-and-recovery.md#application-data-inventory) lists the EVY records in that file. This plan would make the same backup run by itself.

Example: Alice turns on automatic backups and picks a folder in iCloud Drive or Google Drive. She accepts Bob's skateboard purchase for a Saturday pickup, then loses her phone. On a new iOS or Android phone she installs EVY and restores the newest file with her recovery code. Her keys and saved addresses come from the file. Bob's purchase comes back from the network.

## When this becomes a plan

Work starts when many users have no recent manual backup, or users ask for automatic backups.

Ideas to design then:

| Idea | What it would do |
| --- | --- |
| Automatic export | Export once a day while EVY is open, or when Alice taps "Back up now" |
| Stored master key | Keep a key derived from the recovery code in protected storage, so Alice enters the code only at setup and restore |
| Folder grants | Keep access to the chosen folder: a security-scoped bookmark on iOS, a persistable URI permission on Android |
| Provider access | Show whether the cloud provider has uploaded the file, where the provider reports it, and keep a few older files |
| Passkey recovery | Unlock the backup with a passkey as well as the recovery code |

Each idea needs matching iOS and Android tests, and Forget must also delete the stored key and folder grants.

## Sources

- [1.10 Backup and restore](../1-freenet-mobile-appkit/10-backup-and-restore.md): the manual backup file, recovery code and restore this plan would build on
- [iCloud upload status](https://developer.apple.com/documentation/foundation/urlresourcekey/ubiquitousitemisuploadedkey): how iOS reports that a file reached iCloud
- [Android persistable URI permissions](https://developer.android.com/training/data-storage/shared/documents-files#persist-permissions): how an Android app keeps access to a folder the user picked
