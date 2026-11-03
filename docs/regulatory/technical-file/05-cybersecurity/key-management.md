# Key management (gap G8)

- **Status:** Draft. The owner has not reviewed it. It must be Approved before any unit leaves the owner's control.
- **Related:** ADR-0006, ADR-0007, ADR-0008, SYS-013, SYS-029, SYS-034, SYS-035, SYS-043, SYS-046, RISK-006, RISK-007, RISK-012, RISK-022
- **Scope:** every secret that the project creates, stores or uses. Values and key material are never stored in this repository.

Parts marked *(verify)* depend on the ESP32-C3 documentation or on spike 7.1 and are not yet checked.

## 1. Inventory
| Key / secret | Purpose | Lives where | Created by | Who can read it | Loss means |
|--------------|---------|-------------|------------|-----------------|------------|
| Image release key (ECDSA P-256, MCUboot) | Signs release images | Offline: hardware token or encrypted offline medium | Owner | Owner only | No more updates for released units, unless a backup key exists (RISK-006) |
| Image backup key | Replaces the release key if it is lost or leaked | Offline, stored apart from the release key | Owner | Owner only | Loss of both = units cannot be updated |
| Development image key | Signs development builds | Developer machine, marked by a distinct key ID | Build tooling | Developers | Nothing in the field (it is never in a release, RISK-007) |
| Secure-boot key (chip secure boot v2) *(verify)* | Signs the first-stage bootloader; its digest is in eFuse | Offline, like the release key | Owner | Owner only | New bootloader cannot be installed on locked units |
| Flash-encryption key | Encrypts flash content | Inside the chip (eFuse), never leaves it | The chip, at first locked boot *(verify)* | Nobody | Not recoverable by design; units must be reflashed only through the signed path (SYS-046) |
| Unit passphrase (80 bit) | Protects the provisioning access point (ADR-0006) | Secrets partition of the unit; also on the label | The unit, from its hardware random generator | Owner who holds the label; the unit; physical presence over USB | Label lost: read over USB with the button held |
| Device TLS key and certificate | Identity for HTTPS on the LAN (ADR-0008) | Secrets partition of the unit | The unit | The unit only | Factory reset creates a new key; pins change (SYS-041, RISK-016) |
| Web login password hash | Access to the web interface (SYS-039) | Settings area | User, at first setup | The unit | User resets by factory reset |
| Push token, Jenkins token | Authentication of sources | Settings area | User | The unit; the user sees them once | User creates a new token |

## 2. Which key signs what
1. **Stage 1 (internal prototypes):** the development key signs all images. No eFuse is set. These units never leave the owner.
2. **Stage 3 (units for others):** the secure-boot key signs the bootloader. The release key signs each application image. The bootloader holds the public part of the release key and, if MCUboot supports it, of the backup key *(verify)*.
3. A release build fails if it is signed with the development key ID. A development build is refused by a locked unit.
4. The first image on a new unit is flashed over USB with the production signing path (section 5). Later images come over the network.

## 3. Generation and storage
- Keys are generated on the owner's offline machine or token, never on a build server or in a pipeline.
- The release key and the secure-boot key are kept on hardware tokens *(preferred)* or on encrypted media in two places. The backup key is stored apart from the release key.
- CI signs only development builds. A release is signed by the owner on the offline machine from a tagged commit.
- Passphrase for the offline media is held by the owner; a second person holds a sealed copy once there is a second person (open: owner decision).
- The unit passphrase is created on the device (ADR-0006 item 2) and shown once over USB. The owner prints the label from that output. The value is not kept in a file, or is kept in a password manager.

## 4. Use and rotation
- Every signature is made on the offline machine and logged: date, key ID, image hash, commit.
- **Compromise or loss of the release key:**
  - Leak: stop releasing, tell users, switch to the backup key by signing a transition image with the old key if it is still trusted *(verify MCUboot multi-key support)*. If the key cannot be trusted, units need reflashing over USB.
  - Loss: switch to the backup key the same way.
- **Compromise of the secure-boot key:** units already locked cannot change this key. The risk is accepted for release 1 and recorded in the technical file. A new hardware revision is the remedy.
- Yearly review of the access list and the storage; test that the backup key can sign a build that a test unit accepts.
- The development key can be replaced at any time; it is never trusted by locked units.

## 5. Production steps per unit (stage 3)
1. Flash the signed bootloader and application over USB on a station that has no network access to the signing keys.
2. Run the self-test (SYS-023). Create the unit passphrase and read it back before the label is printed (ADR-0006 item 7).
3. Set secure boot, flash encryption and the lock of download mode and debug port *(verify the eFuse list; do this only after steps 1 and 2 pass)*.
4. Write the unit record: serial number, stage (prototype without locks, or locked), image version, date. The record holds no secret.
5. Quarantine rule: a unit that fails any step is marked and not given out. A unit in stage 1 is never given to anyone else.

The first run of this procedure is on sacrificial boards (ADR-0007 stage 2). No irreversible step is done on a unit that cannot be lost.

## 6. Recovery of locked units
A unit with a broken application is recovered over USB with a correctly signed image (SYS-046). Recovery does not erase the unit passphrase or the device key. Where the chip needs download mode for this, the exact path and its limits are written here after spike 7.1 *(verify)*.

## 7. Open points for the owner
1. Hardware token or encrypted medium for the offline keys, and where the backup is kept.
2. Whether a second person is needed to hold a backup of the passphrase of the offline media.
3. Whether the owner accepts that a leaked secure-boot key cannot be replaced on locked units.
4. Whether prototypes get eFuse steps (working default: no, ADR-0007).
