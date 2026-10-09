# LockByte Security Architecture

## Overview

LockByte is a local-first cybersecurity password manager built around encrypted vault storage, password analysis, secure generation, security auditing, and privacy-preserving breach awareness.

## Cryptographic Design

### Key Derivation (KDF)
- **Algorithm**: Argon2id
- **Memory Cost**: 64 MB (65536 KiB)
- **Time Cost**: 3 iterations
- **Parallelism**: 4 threads
- **Salt Length**: 32 bytes (256 bits)
- **Output Length**: 32 bytes (256 bits)

The master password is never stored. Instead, a verification key is derived and stored to allow password verification without storing plaintext.

### Encryption
- **Algorithm**: AES-256-GCM (Galois/Counter Mode)
- **Key Length**: 256 bits
- **Nonce Length**: 96 bits (12 bytes)
- **Authentication Tag**: 128 bits (16 bytes)
- **Mode**: Authenticated Encryption with Associated Data (AEAD)

AES-GCM provides both confidentiality and authenticity, protecting against tampering.

### Storage Format
```
Nonce (12 bytes) || Ciphertext || Authentication Tag (16 bytes)
```

## Threat Model

### Threats Addressed

1. **Attacker obtains a copy of the local database**
   - Mitigation: All credential passwords are encrypted with AES-256-GCM
   - Without the master password, encrypted data is computationally infeasible to decrypt

2. **Repeated master-password guessing**
   - Mitigation: Argon2id with high memory cost (64MB) makes each guess expensive
   - Guessing 1 million passwords would require ~64TB of RAM per password hash

3. **Malware/local process memory inspection**
   - Mitigation: Vault locks automatically on inactivity
   - Sensitive data is encrypted when stored in memory
   - Master password is never stored in plaintext

4. **Clipboard observation**
   - Mitigation: Copied passwords are cleared after a configurable timeout
   - User is warned about clipboard exposure

5. **Compromised breach-check service**
   - Mitigation: Privacy-preserving k-anonymity method
   - Only first 5 characters of password hash are sent to breach checker
   - Full password never transmitted

6. **Accidental plaintext export**
   - Mitigation: Export requires vault authentication
   - Clear warnings before creating unencrypted exports

### Threats Not Addressed

1. **Fully compromised operating system** - Desktop manager cannot protect against OS-level malware with kernel access
2. **Physical memory acquisition** - If attacker gains physical access to running system, decrypted memory could be inspected
3. **Cloud synchronization** - Not implemented to maintain local-first security model
4. **Passkeys/WebAuthn** - Future enhancement, not in current scope

## Security Assumptions

1. The user's operating system is not compromised
2. The user's master password is strong (≥8 characters, ideally 12+)
3. The user's computer is physically secure
4. The user has backup of the vault or uses a strong master password for recovery
5. TLS/HTTPS is used for any remote services (breach checking)

## Component Security

### Vault Repository
- Requires unlock before any operations
- All credential data returned to caller is **decrypted**
- Database always stores encrypted data
- Audit events logged for all modifications

### Password Analyzer
- Checks entropy, character diversity, patterns
- Detects common passwords and keyboard patterns
- Identifies password reuse across the vault
- Generates actionable recommendations (not crack-time estimates)

### Password Generator
- Uses `secrets` module for cryptographic randomness
- Ensures character type diversity
- Can exclude ambiguous characters (I, l, O, 0, 1)
- Supports passphrases for memorability

### Security Audit Engine
- Scores credentials on multiple dimensions
- Identifies weak, reused, old, and exposed passwords
- Flags accounts missing 2FA
- Generates priority-ordered remediation actions

### TOTP/2FA
- Secrets stored encrypted in vault
- Time-based generation (HMAC-SHA1)
- Uses standard 30-second time window
- Supports verification window for clock skew

### Breach Checking
- Uses k-anonymity: only sends first 5 chars of SHA-1 hash
- Queries Have I Been Pwned (HIBP) API
- Local verification of returned hashes
- Full password never transmitted over the network
- Email checking also supported

## Auto-Lock Security

- Vault automatically locks after configurable inactivity period (default: 15 minutes)
- Sensitive UI state is cleared when locked
- Vault must be unlocked with master password to access credentials

## Backup Security

- Encrypted backups strongly recommended
- Plaintext exports require explicit authentication and warning
- Backups inherit encryption properties of vault

## Future Security Considerations

1. **Passkeys/WebAuthn** - Hardware-backed authentication
2. **Multi-device sync** - Would require server and increase attack surface
3. **Browser integration** - Risk/benefit analysis needed
4. **Secure deletion** - Overwriting deleted records on disk
5. **Memory encryption** - Full encryption of sensitive data in memory