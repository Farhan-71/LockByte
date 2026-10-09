# 🔒 LockByte - Secure Credential Management & Password Security Platform

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.8%2B-blue)
![Security](https://img.shields.io/badge/security-Cybersecurity-red)

LockByte is a **defensive cybersecurity portfolio project** combining a secure local password manager with password analysis, credential-security auditing, privacy-preserving breach awareness, secure password generation, optional TOTP/2FA support, and encrypted local storage.

## 🎯 Project Overview

LockByte demonstrates real-world authentication, key derivation, encryption, secure storage, threat modeling, privacy, and secure software engineering. It's designed as a portfolio piece that showcases comprehensive cybersecurity knowledge.

## ✨ Key Features

### 🔐 Secure Vault
- **Encrypted Credential Storage**: AES-256-GCM authenticated encryption
- **Master Password Authentication**: Never stored in plaintext
- **Argon2id Key Derivation**: Memory-hard PBKDF with configurable parameters
- **Auto-Lock**: Automatic vault locking after inactivity

### 📊 Password Analysis & Security
- **Strength Assessment**: Analyzes length, patterns, entropy, character diversity
- **Reuse Detection**: Identifies password reuse across accounts
- **Pattern Recognition**: Detects keyboard patterns, sequences, common passwords
- **Actionable Recommendations**: Security improvement suggestions

### 🔄 Password Generation
- **Cryptographically Secure**: Uses system CSPRNG
- **Configurable Generation**: Length, character sets, ambiguous character exclusion
- **Passphrase Support**: Diceware-style memorable passphrases
- **Entropy Estimation**: Calculates and displays password strength

### 🛡️ Security Auditing
- **Comprehensive Analysis**: Checks for weak, reused, old, exposed passwords
- **Security Dashboard**: Overall security score and priority actions
- **Vulnerability Reports**: Detailed findings with remediation steps

### 🌐 Privacy-Preserving Breach Checking
- **k-Anonymity Method**: Only sends first 5 characters of SHA-1 hash
- **Have I Been Pwned API**: Checks against known data breaches
- **Email & Password Checks**: Identifies compromised credentials

### ⏰ TOTP/2FA Support (Optional)
- **Secure Storage**: TOTP secrets stored encrypted in vault
- **Time-Based Generation**: Standard 30-second windows
- **QR Code Support**: Generate TOTP setup URIs

## 🏗️ Architecture

```
User → LockByte Desktop UI → Authentication/Vault Controller
                         ↓
            Argon2id Key Derivation
                         ↓
               Encryption Layer (AES-256-GCM)
                         ↓
            Encrypted Local Database (SQLite)
```

### Supporting Modules:
- Password Analyzer & Generator
- Security Audit Engine
- TOTP/2FA Module
- Breach-Check Module
- Import/Export
- Auto-Lock Controller

## 🔧 Installation

### Prerequisites
- Python 3.8+
- pip package manager

### Quick Start
```bash
# Clone the repository
git clone https://github.com/yourusername/lockbyte.git
cd lockbyte

# Install dependencies
pip install -r requirements.txt

# Run LockByte
python -m app.main
```

### Dependencies
All dependencies are listed in `requirements.txt`:
- **PySide6**: Desktop GUI framework
- **argon2-cffi**: Argon2id password hashing
- **cryptography**: AES-256-GCM encryption
- **zxcvbn**: Password strength estimation
- **pyotp**: TOTP generation
- **pytest**: Testing framework

## 🚀 Usage

### First Run
```bash
python -m app.main
```
- Follow prompts to create a new vault
- Set a strong master password (minimum 8 characters)

### Adding Credentials
```
Website: github.com
Username: yourusername
Password: ****************
Email: user@example.com
```

### Generating Passwords
```
Select option: 3
Password length (default 16): 20
Generated: H8@kQ7sV#nP!xZ2mW9rY3
Strength: very_strong
Entropy: 131.5 bits
```

### Running Security Audit
```
Select option: 5
🔍 Running security audit...

╔══ LOCKBYTE SECURITY CENTER ══╗
║ Overall Security Score: 82/100
╚════════════════════════════════╝

Credentials: 15
Weak passwords: 2
Reused passwords: 1
Exposed credentials: 0
Missing 2FA: 4
Old passwords: 3
```

## 🧪 Testing

Run the comprehensive test suite:
```bash
python -m pytest tests/ -v
```

## 🔒 Security Design

### Cryptography
- **KDF**: Argon2id with 64MB memory, 3 iterations
- **Encryption**: AES-256-GCM authenticated encryption
- **Key Management**: Never store master password, only derived verification key

### Threat Model
LockByte addresses:
- Local database theft (encrypted at rest)
- Password guessing attacks (Argon2id memory-hard)
- Memory inspection (auto-lock and memory clearing)
- Clipboard exposure (automatic clearing)
- Network surveillance (k-anonymity for breach checks)

## 📁 Project Structure
```
lockbyte/
├── app/                 # Main application
├── crypto/              # Cryptographic core
│   ├── kdf.py           # Argon2id key derivation
│   ├── encryption.py    # AES-256-GCM encryption
│   ├── key_management.py# Key management
│   └── secure_random.py # Cryptographic random generation
├── vault/               # Vault management
│   ├── models.py        # Data models
│   ├── database.py      # SQLite database
│   └── repository.py    # High-level vault interface
├── security/            # Security features
│   ├── password_analyzer.py
│   ├── password_generator.py
│   ├── audit.py         # Security auditing
│   ├── totp.py          # TOTP/2FA support
│   └── breach_check.py  # Privacy-preserving breach checks
├── tests/               # Comprehensive test suite
├── docs/                # Documentation
└── requirements.txt     # Python dependencies
```

## 🎓 What This Project Demonstrates

LockByte showcases:
- **Authentication & Credential Security**: Secure password management
- **Key Derivation**: Password-based key derivation with Argon2id
- **Encryption & Secure Storage**: AES-256-GCM authenticated encryption
- **Threat Modeling**: Security analysis and defensive controls
- **Privacy-Aware Design**: k-anonymity for breach checking
- **Desktop Application Development**: Python GUI with PySide6
- **Secure Software Development**: Security-first design patterns

## 🚧 Limitations & Considerations

### Security Limitations
1. **Compromised OS**: Cannot protect against kernel-level malware
2. **Physical Memory**: If attacker gains physical access to running system
3. **Browser Integration**: Currently desktop-only, no browser plugin
4. **Cloud Sync**: Not implemented (intentional local-first design)

### Platform Limitations
- **Desktop Only**: No mobile or web interface
- **No Synchronization**: Single device, no multi-device sync
- **No Auto-Fill**: Does not integrate with browser password managers

## 🔄 Development Roadmap

### Phase 1 (Current) - Core Security
- ✓ Cryptographic foundation (Argon2id, AES-256-GCM)
- ✓ Secure vault with master password authentication
- ✓ Password analysis and generation
- ✓ Security auditing dashboard

### Phase 2 (Next) - Enhanced Features
- [ ] TOTP/2FA support with QR code generation
- [ ] Advanced password analysis with zxcvbn
- [ ] Encrypted backup and import/export
- [ ] Secure notes with rich text support

### Phase 3 (Future) - Platform Expansion
- [ ] Browser extension for autofill
- [ ] Mobile app with encrypted sync
- [ ] Passkeys/WebAuthn support
- [ ] Sharing features with end-to-end encryption

## 🤝 Contributing

This is primarily a portfolio project demonstrating cybersecurity concepts. However, contributions that improve security or fix bugs are welcome.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📜 License

MIT License - See LICENSE file for details.

## 🛡️ Responsible Security

This project is for educational and portfolio purposes. If you discover a security vulnerability, please report it responsibly.

**Note**: This is not intended for production use without thorough security review and additional hardening. Use at your own risk.

## 📊 Screenshots

*(Add screenshots here demonstrating the interface)*

- Security Dashboard
- Credential Management
- Password Generation
- Security Audit Results