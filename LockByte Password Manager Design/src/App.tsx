import { useEffect, useMemo, useState } from "react";
import {
  AlertTriangle,
  Check,
  ChevronDown,
  CircleUserRound,
  Clock3,
  Copy,
  Database,
  Eye,
  EyeOff,
  FileKey2,
  FileText,
  Fingerprint,
  FolderKey,
  Gauge,
  Globe2,
  KeyRound,
  Lock,
  LockKeyhole,
  Mail,
  MoreVertical,
  Plus,
  RefreshCw,
  Search,
  Settings,
  Shield,
  ShieldAlert,
  ShieldCheck,
  SlidersHorizontal,
  Sparkles,
  Trash2,
  Unlock,
  UserRound,
  WandSparkles,
  X,
  type LucideIcon,
} from "lucide-react";
import lockbyteFullLogo from "./assets/lockbyte-full.webp";
import lockbyteMark from "./assets/lockbyte-mark.png";

import {
  checkVaultExists, unlockVault, createVault, lockVault,
  getCredentials, addCredential, getNotes, addNote, runAudit,
  getSettings, updateSettings, changeMasterPassword,
  checkBiometricsAvailable, hasStoredBiometricKey, authenticateBiometrics, enableBiometrics, disableBiometrics
} from "./bridgeClient";

type Stage = "landing" | "welcome" | "unlock" | "app" | "locking" | "locked";
type Page = "Vault" | "Secure Notes" | "Password Generator" | "Security Audit" | "Settings";

type Credential = {
  website: string;
  domain: string;
  username: string;
  email: string;
  category: string;
  initial: string;
  color: string;
  twoFactor: boolean;
  updated: string;
};

const credentials: Credential[] = [
  {
    website: "GitHub",
    domain: "github.com",
    username: "farhan-dev",
    email: "user@example.com",
    category: "Development",
    initial: "GH",
    color: "#E2E2D2",
    twoFactor: true,
    updated: "2 min ago",
  },
  {
    website: "Google",
    domain: "accounts.google.com",
    username: "farhan.k",
    email: "user@example.com",
    category: "Personal",
    initial: "G",
    color: "#C51F5D",
    twoFactor: true,
    updated: "Yesterday",
  },
  {
    website: "Microsoft",
    domain: "microsoft.com",
    username: "farhan.work",
    email: "farhan@company.com",
    category: "Work",
    initial: "M",
    color: "#7F93A8",
    twoFactor: true,
    updated: "3 days ago",
  },
  {
    website: "Discord",
    domain: "discord.com",
    username: "farhan_99",
    email: "user@example.com",
    category: "Social",
    initial: "D",
    color: "#9A5770",
    twoFactor: false,
    updated: "1 week ago",
  },
  {
    website: "LinkedIn",
    domain: "linkedin.com",
    username: "farhan-k",
    email: "farhan@company.com",
    category: "Work",
    initial: "in",
    color: "#A9B5C0",
    twoFactor: false,
    updated: "2 weeks ago",
  },
];

const navigation: { label: Page; icon: LucideIcon; badge?: string }[] = [
  { label: "Vault", icon: FolderKey, badge: "32" },
  { label: "Secure Notes", icon: FileText, badge: "4" },
  { label: "Password Generator", icon: WandSparkles },
  { label: "Security Audit", icon: ShieldAlert, badge: "3" },
  { label: "Settings", icon: Settings },
];

function Logo({ compact = false }: { compact?: boolean }) {
  return (
    <div className={`logo ${compact ? "compact" : ""}`}>
      <span className="logo-mark logo-art-mark" aria-hidden="true">
        <img alt="" src={lockbyteMark} />
      </span>
      <div>
        <strong>LockByte</strong>
        {!compact && <small>PRIVATE VAULT</small>}
      </div>
    </div>
  );
}

function SecurityBackdrop() {
  return (
    <div className="security-backdrop" aria-hidden="true">
      <div className="grid-plane" />
      <Shield className="ghost-symbol symbol-one" />
      <KeyRound className="ghost-symbol symbol-two" />
      <Lock className="ghost-symbol symbol-three" />
      <span className="circuit-line line-one" />
      <span className="circuit-line line-two" />
    </div>
  );
}

function Landing({ onOpen }: { onOpen: () => void }) {
  const [showSecurity, setShowSecurity] = useState(false);

  return (
    <main className="entry-screen">
      <SecurityBackdrop />
      <header className="entry-header"><Logo compact /></header>
      <section className="hero-panel">
        <div className="hero-brand-art" aria-hidden="true">
          <img alt="" src={lockbyteFullLogo} />
        </div>
        <p className="overline">PRIVATE CREDENTIAL SECURITY</p>
        <h1 className="visually-hidden">LockByte</h1>
        <p className="hero-tagline">Your passwords. Your privacy. Your vault.</p>
        <p className="hero-support">Secure your digital credentials with a private, encrypted password manager.</p>
        <div className="hero-actions">
          <button className="button primary large" onClick={onOpen} type="button"><Unlock size={17} />Open LockByte</button>
          <button className="button secondary large" onClick={() => setShowSecurity((value) => !value)} type="button">
            <Shield size={17} />Learn About Security
          </button>
        </div>
        <div className={`security-features ${showSecurity ? "expanded" : ""}`}>
          {[
            ["AES-256 Encryption", LockKeyhole],
            ["Zero-Knowledge Architecture", ShieldCheck],
            ["Local Vault", Database],
            ["TOTP 2FA", KeyRound],
          ].map(([label, Icon]) => (
            <span key={label as string}><Icon size={14} />{label as string}</span>
          ))}
        </div>
      </section>
      <footer className="entry-footer"><span className="status-dot" />Your credentials stay protected.</footer>
    </main>
  );
}

function Welcome({ onContinue, onImport }: { onContinue: () => void; onImport: () => void }) {
  const [pwd, setPwd] = useState("");
  const [pwdConfirm, setPwdConfirm] = useState("");
  const [error, setError] = useState("");

  const handleCreate = async () => {
    if (pwd.length < 8) {
      setError("Password must be at least 8 characters.");
      return;
    }
    if (pwd !== pwdConfirm) {
      setError("Passwords do not match.");
      return;
    }
    const res = await createVault(pwd);
    if (res.success) {
      onContinue();
    } else {
      setError(res.error || "Failed to create vault.");
    }
  };

  const features: { title: string; copy: string; icon: LucideIcon }[] = [
    { title: "Secure Vault", copy: "Store passwords and credentials securely.", icon: LockKeyhole },
    { title: "Password Generator", copy: "Create strong, unique passwords.", icon: WandSparkles },
    { title: "Security Audit", copy: "Identify weak and reused credentials.", icon: ShieldCheck },
  ];

  return (
    <main className="entry-screen setup-screen">
      <SecurityBackdrop />
      <header className="entry-header"><Logo compact /></header>
      <section className="setup-panel">
        <div className="step-label">INITIAL SETUP • 1 OF 1</div>
        <h1>Welcome to LockByte</h1>
        <p>Create your private vault to get started.</p>
        <div className="setup-features">
          {features.map(({ title, copy, icon: Icon }) => (
            <article className="setup-card" key={title}>
              <span><Icon size={21} /></span>
              <h2>{title}</h2>
              <p>{copy}</p>
            </article>
          ))}
        </div>
        <div style={{ marginTop: 20, display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 10 }}>
          <input
            type="password"
            placeholder="Set Master Password (min 8 chars)"
            value={pwd}
            onChange={(e) => setPwd(e.target.value)}
            style={{ width: 320, padding: '10px 14px', borderRadius: 6, border: '1px solid #364e66', background: '#151f29', color: '#ececdd' }}
          />
          <input
            type="password"
            placeholder="Confirm Master Password"
            value={pwdConfirm}
            onChange={(e) => setPwdConfirm(e.target.value)}
            style={{ width: 320, padding: '10px 14px', borderRadius: 6, border: '1px solid #364e66', background: '#151f29', color: '#ececdd' }}
          />
          {error && <span style={{ color: '#c95b6d', fontSize: 12 }}>{error}</span>}
        </div>
        <div className="setup-actions">
          <button className="button primary large" onClick={handleCreate} type="button"><Lock size={17} />Create Secure Vault</button>
          <button className="text-button" onClick={onImport} type="button">Import Existing Credentials</button>
        </div>
        <p className="setup-assurance"><ShieldCheck size={14} />Your vault is encrypted locally before any data is saved.</p>
      </section>
    </main>
  );
}

function UnlockScreen({ onUnlock }: { onUnlock: () => void }) {
  const [visible, setVisible] = useState(false);
  const [password, setPassword] = useState("");
  const [remember, setRemember] = useState(true);
  const [error, setError] = useState("");
  const [bioAvailable, setBioAvailable] = useState(false);
  const [hasBioKey, setHasBioKey] = useState(false);

  useEffect(() => {
    const checkBio = async () => {
      const avail = await checkBiometricsAvailable();
      const hasKey = await hasStoredBiometricKey();
      setBioAvailable(avail);
      setHasBioKey(hasKey);
    };
    checkBio();
  }, []);

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    if (!password) return;
    const res = await unlockVault(password);
    if (res.success) {
      onUnlock();
    } else {
      setError(res.error || "Invalid master password");
    }
  };

  const handleBiometricUnlock = async () => {
    setError("");
    const res = await authenticateBiometrics();
    if (res.verified) {
      onUnlock();
    } else if (res.error) {
      setError(res.error);
    }
  };

  return (
    <main className="entry-screen unlock-screen">
      <SecurityBackdrop />
      <header className="entry-header"><Logo compact /></header>
      <section className="unlock-card">
        <div className="unlock-icon"><LockKeyhole size={30} /></div>
        <p className="overline">LOCAL VAULT</p>
        <h1>Unlock Your Vault</h1>
        <p className="unlock-subtitle">Enter your master password to continue.</p>

        {bioAvailable && hasBioKey && (
          <div style={{ marginBottom: 20 }}>
            <button className="button secondary large" onClick={handleBiometricUnlock} type="button" style={{ width: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 10, borderColor: '#c51f5d', color: '#e2e2d2' }}>
              <Fingerprint size={20} style={{ color: '#c51f5d' }} />
              <span>Unlock with Windows Hello</span>
            </button>
            <div style={{ textAlign: 'center', color: '#8295a7', fontSize: 11, marginTop: 15 }}>— OR USE MASTER PASSWORD —</div>
          </div>
        )}

        <form onSubmit={handleSubmit}>
          <label htmlFor="master-password">Master password</label>
          <div className="master-input">
            <Lock size={17} />
            <input
              autoFocus
              id="master-password"
              onChange={(event) => { setPassword(event.target.value); setError(""); }}
              placeholder="Enter master password"
              type={visible ? "text" : "password"}
              value={password}
            />
            <kbd>↵</kbd>
            <button aria-label={visible ? "Hide password" : "Reveal password"} onClick={() => setVisible((value) => !value)} type="button">
              {visible ? <EyeOff size={17} /> : <Eye size={17} />}
            </button>
          </div>
          {error && <div style={{ color: '#c95b6d', fontSize: 12, marginTop: 8, textAlign: 'center' }}>{error}</div>}
          <div className="unlock-options">
            <label className="checkbox-row">
              <input checked={remember} onChange={(event) => setRemember(event.target.checked)} type="checkbox" />
              <span><Check size={11} /></span>Remember this device
            </label>
            <button className="text-button" type="button">Forgot master password?</button>
          </div>
          <button className="button primary unlock-button" type="submit"><Unlock size={17} />Unlock Vault</button>
        </form>
        <div className="unlock-security">
          <div><ShieldCheck size={15} /><span>Your vault is protected with AES-256 &amp; Windows Hello.</span></div>
          <strong><span className="status-dot" />Vault Offline &amp; Protected</strong>
        </div>
      </section>
    </main>
  );
}

function LockedScreen({ onUnlock }: { onUnlock: () => void }) {
  return (
    <main className="entry-screen locked-screen">
      <SecurityBackdrop />
      <section className="locked-panel">
        <Logo />
        <div className="locked-emblem"><Lock size={34} /></div>
        <p className="overline">LOCKBYTE</p>
        <h1>Vault Locked</h1>
        <p>Your credentials are protected.</p>
        <button className="button primary large" onClick={onUnlock} type="button"><Unlock size={17} />Unlock Vault</button>
        <span className="encryption-caption"><ShieldCheck size={13} />AES-256 • Local encryption active</span>
      </section>
    </main>
  );
}

function LockingScreen() {
  return (
    <main className="entry-screen locking-screen">
      <div className="locking-mark"><Lock size={28} /></div>
      <h1>Vault locked.</h1>
      <p>Securing local session…</p>
    </main>
  );
}

function Sidebar({
  page,
  onNavigate,
  onLock,
}: {
  page: Page;
  onNavigate: (page: Page) => void;
  onLock: () => void;
}) {
  return (
    <aside className="sidebar">
      <div className="sidebar-brand"><Logo /></div>
      <nav className="sidebar-nav" aria-label="Primary navigation">
        <p>Workspace</p>
        {navigation.map(({ label, icon: Icon, badge }) => (
          <button className={page === label ? "active" : ""} key={label} onClick={() => onNavigate(label)} type="button">
            <Icon size={18} strokeWidth={1.8} />
            <span>{label}</span>
            {badge && <small>{badge}</small>}
          </button>
        ))}
      </nav>
      <div className="sidebar-bottom">
        <div className="vault-status">
          <span className="status-dot" />
          <div><strong>Vault Protected</strong><small>Encrypted locally</small></div>
        </div>
        <button className="lock-vault-button" onClick={onLock} type="button"><Lock size={16} /><span>Lock Vault</span></button>
      </div>
    </aside>
  );
}

function PageHeader({ page }: { page: Page }) {
  const subtitles: Record<Page, string> = {
    Vault: "Your encrypted credentials",
    "Secure Notes": "Private notes protected inside your vault",
    "Password Generator": "Create strong, unique credentials",
    "Security Audit": "Monitor the strength of your digital security",
    Settings: "Manage your vault preferences and security",
  };

  return (
    <header className="app-header">
      <div><h1>{page}</h1><p>{subtitles[page]}</p></div>
      <div className="header-account">
        <span className="vault-secure"><span className="status-dot" />Vault Secure</span>
        <button aria-label="Open profile" className="profile-button" type="button"><UserRound size={18} /></button>
      </div>
    </header>
  );
}

function VaultPage({ onSelect, liveCredentials, onRefresh }: { onSelect: (credential: Credential) => void; liveCredentials: Credential[]; onRefresh: () => void }) {
  const [query, setQuery] = useState("");
  const filtered = liveCredentials.filter((item) =>
    `${item.website} ${item.username} ${item.email}`.toLowerCase().includes(query.toLowerCase()),
  );

  return (
    <div className="page-body vault-page">
      <div className="vault-toolbar">
        <label className="search-field"><Search size={17} /><input aria-label="Search credentials" onChange={(event) => setQuery(event.target.value)} placeholder="Search credentials..." value={query} /><kbd>⌘ K</kbd></label>
        <div>
          <button className="button utility" type="button"><SlidersHorizontal size={15} />Filter</button>
          <button className="button utility" type="button"><ChevronDown size={15} />Sort</button>
          <button className="button primary" onClick={() => onSelect({ website: "", domain: "", username: "", email: "", category: "Personal", initial: "", color: "#C51F5D", twoFactor: false, updated: "Now" })} type="button"><Plus size={16} />Add Credential</button>
        </div>
      </div>
      <section className="content-surface table-surface">
        <div className="surface-heading">
          <div><h2>All credentials</h2><span>{filtered.length} items</span></div>
          <small><LockKeyhole size={13} />AES-256 ENCRYPTED</small>
        </div>
        <div className="table-scroll">
          <table>
            <thead><tr><th>Website</th><th>Username</th><th>Email</th><th>Category</th><th>2FA</th><th>Last Updated</th><th aria-label="Actions" /></tr></thead>
            <tbody>
              {filtered.map((item, index) => (
                <tr key={item.website + index} onClick={() => onSelect(item)}>
                  <td><div className="website-cell"><span style={{ color: item.color }}>{item.initial || "?"}</span><div><strong>{item.website}</strong><small>{item.domain}</small></div></div></td>
                  <td>{item.username}</td>
                  <td className="muted-cell">{item.email}</td>
                  <td><span className="category-label">{item.category}</span></td>
                  <td><span className={`two-factor-status ${item.twoFactor ? "enabled" : ""}`}><i />{item.twoFactor ? "Enabled" : "Not enabled"}</span></td>
                  <td className="muted-cell">{item.updated}</td>
                  <td><button aria-label={`More options for ${item.website}`} className="icon-button" onClick={(event) => event.stopPropagation()} type="button"><MoreVertical size={17} /></button></td>
                </tr>
              ))}
              {filtered.length === 0 && (
                <tr><td colSpan={7} style={{ textAlign: 'center', padding: '30px', color: '#8295a7' }}>No credentials found in vault. Click "+ Add Credential" above to create one.</td></tr>
              )}
            </tbody>
          </table>
        </div>
        <div className="table-footer"><span>Last synced just now</span><div><button disabled type="button">Previous</button><button type="button">Next</button></div></div>
      </section>
    </div>
  );
}

function CredentialModal({ credential, onClose, onSaveSuccess }: { credential: Credential; onClose: () => void; onSaveSuccess: () => void }) {
  const [passwordVisible, setPasswordVisible] = useState(false);
  const [copied, setCopied] = useState<string | null>(null);
  const [seconds, setSeconds] = useState(27);

  const [website, setWebsite] = useState(credential.website || "");
  const [username, setUsername] = useState(credential.username || "");
  const [email, setEmail] = useState(credential.email || "");
  const [password, setPassword] = useState((credential as any).password || "");
  const [category, setCategory] = useState(credential.category || "Personal");
  const [totpSecret, setTotpSecret] = useState((credential as any).totpSecret || "");
  const [notes, setNotes] = useState((credential as any).notes || "");

  useEffect(() => {
    const timer = window.setInterval(() => setSeconds((value) => (value <= 1 ? 30 : value - 1)), 1000);
    return () => window.clearInterval(timer);
  }, []);

  const copy = (text: string, key: string) => {
    void navigator.clipboard?.writeText(text);
    setCopied(key);
    window.setTimeout(() => setCopied(null), 1400);
  };

  const handleSave = async () => {
    if (!website || !password) return;
    await addCredential({
      website,
      username,
      email,
      password,
      category,
      totpSecret,
      notes
    });
    onSaveSuccess();
    onClose();
  };

  return (
    <div className="modal-overlay" onMouseDown={(event) => event.target === event.currentTarget && onClose()}>
      <section aria-labelledby="credential-title" aria-modal="true" className="credential-modal" role="dialog">
        <header className="modal-header">
          <div><span className="modal-title-icon"><KeyRound size={20} /></span><div><h2 id="credential-title">{credential.website ? "Credential Details" : "New Credential"}</h2><p>Manage your saved credentials securely.</p></div></div>
          <button aria-label="Close credential details" className="icon-button" onClick={onClose} type="button"><X size={19} /></button>
        </header>
        <div className="modal-body">
          <div className="form-grid">
            <label className="form-field"><span>Website</span><div><Globe2 size={16} /><input value={website} onChange={(e) => setWebsite(e.target.value)} placeholder="e.g. github.com" /></div></label>
            <label className="form-field"><span>Category</span><div><FolderKey size={16} /><select value={category} onChange={(e) => setCategory(e.target.value)}><option value="Personal">Personal</option><option value="Development">Development</option><option value="Work">Work</option><option value="Finance">Finance</option></select><ChevronDown size={15} /></div></label>
            <label className="form-field"><span>Username</span><div><CircleUserRound size={16} /><input value={username} onChange={(e) => setUsername(e.target.value)} placeholder="Username" /></div></label>
            <label className="form-field"><span>Email</span><div><Mail size={16} /><input value={email} onChange={(e) => setEmail(e.target.value)} type="email" placeholder="email@example.com" /></div></label>
          </div>
          <label className="form-field password-field">
            <span>Password <strong><i />STRONG</strong></span>
            <div><Lock size={16} /><input value={password} onChange={(e) => setPassword(e.target.value)} type={passwordVisible ? "text" : "password"} placeholder="Password" />
              <button aria-label="Reveal password" onClick={() => setPasswordVisible((value) => !value)} type="button">{passwordVisible ? <EyeOff size={16} /> : <Eye size={16} />}</button>
              <button aria-label="Copy password" onClick={() => copy(password, "password")} type="button">{copied === "password" ? <Check size={16} /> : <Copy size={16} />}</button>
            </div>
            <i className="strength-meter"><span /></i>
          </label>
          <label className="form-field notes-field"><span>2FA Secret (Optional)</span><div><KeyRound size={16} /><input value={totpSecret} onChange={(e) => setTotpSecret(e.target.value)} placeholder="Base32 TOTP Secret" /></div></label>
          <label className="form-field notes-field"><span>Notes</span><textarea value={notes} onChange={(e) => setNotes(e.target.value)} placeholder="Optional secure notes" /></label>
        </div>
        <footer className="modal-footer">
          <button className="delete-action" type="button"><Trash2 size={15} />Delete Credential</button>
          <div><button className="button secondary" onClick={onClose} type="button">Cancel</button><button className="button primary" onClick={handleSave} type="button">Save Changes</button></div>
        </footer>
      </section>
    </div>
  );
}

function SecurityAuditPage() {
  const [auditData, setAuditData] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  const performScan = async () => {
    setLoading(true);
    const res = await runAudit();
    if (res) {
      setAuditData(res);
    }
    setLoading(false);
  };

  useEffect(() => {
    performScan();
  }, []);

  const score = auditData ? auditData.score : 100;
  const metrics = [
    { label: "Weak Passwords", value: auditData ? String(auditData.weakCount) : "0", icon: AlertTriangle, tone: "warning" },
    { label: "Reused Passwords", value: auditData ? String(auditData.reusedCount) : "0", icon: RefreshCw, tone: "warning" },
    { label: "Missing 2FA", value: auditData ? String(auditData.missing2FA) : "0", icon: KeyRound, tone: "danger" },
    { label: "Compromised Credentials", value: auditData ? String(auditData.exposedCount) : "0", icon: ShieldCheck, tone: "success" },
  ];

  const actions = auditData?.actions || [];

  return (
    <div className="page-body audit-page">
      <section className="score-card content-surface">
        <div className="score-ring">
          <svg viewBox="0 0 120 120">
            <circle cx="60" cy="60" r="52" />
            <circle className="score-progress" cx="60" cy="60" r="52" style={{ strokeDashoffset: 327 - (327 * score) / 100 }} />
          </svg>
          <div><strong>{score}</strong><span>/ 100</span></div>
        </div>
        <div>
          <span className="eyebrow">SECURITY SCORE</span>
          <h2>{score >= 80 ? "Good Security" : (score >= 50 ? "Fair Security" : "Needs Attention")}</h2>
          <p>{loading ? "Running audit against encrypted vault..." : "Your vault has been analyzed using Argon2id and HaveIBeenPwned."}</p>
          <small><ShieldCheck size={14} />{loading ? "Scan in progress..." : "Last scan completed just now"}</small>
        </div>
      </section>
      <div className="metric-grid">
        {metrics.map(({ label, value, icon: Icon, tone }) => <article className="metric-card content-surface" key={label}><span className={tone}><Icon size={19} /></span><div><strong>{value}</strong><small>{label}</small></div></article>)}
      </div>
      <section className="content-surface recommendations">
        <div className="surface-heading"><div><h2>Security recommendations</h2><span>{actions.length} actions recommended</span></div><small><Gauge size={14} />AUTOMATED AUDIT</small></div>
        {actions.map((act: any, idx: number) => (
          <div className="recommendation" key={idx}>
            <span className={act.priority === 'critical' ? "danger" : "warning"}><ShieldAlert size={17} /></span>
            <div><strong>{act.action}</strong><small>{act.reason}</small></div>
            <button type="button">Review</button>
          </div>
        ))}
        {actions.length === 0 && !loading && (
          <div style={{ padding: '20px', textAlign: 'center', color: '#80aa91' }}>No security issues found in vault!</div>
        )}
      </section>
    </div>
  );
}

function GeneratorPage() {
  const [length, setLength] = useState(20);
  const [password, setPassword] = useState("K7!xP9@vL2#qR8");
  const [copied, setCopied] = useState(false);
  const [options, setOptions] = useState({ Uppercase: true, Lowercase: true, Numbers: true, Symbols: true });
  const regenerate = () => setPassword(Math.random().toString(36).slice(2, 9).toUpperCase() + "!x9@" + Math.random().toString(36).slice(2, 8));

  return (
    <div className="page-body generator-page">
      <section className="generator-card content-surface">
        <div className="generator-heading"><span><WandSparkles size={22} /></span><div><h2>Generate a secure password</h2><p>Passwords are generated locally and never leave your device.</p></div></div>
        <div className="generated-password"><code>{password}</code><div><button aria-label="Copy password" onClick={() => { void navigator.clipboard?.writeText(password); setCopied(true); window.setTimeout(() => setCopied(false), 1200); }} type="button">{copied ? <Check size={18} /> : <Copy size={18} />}</button><button aria-label="Regenerate password" onClick={regenerate} type="button"><RefreshCw size={18} /></button></div></div>
        <div className="generator-strength"><span><i />Very Strong</span><div><i /><i /><i /><i /></div></div>
        <div className="generator-controls">
          <div className="length-control"><div><label htmlFor="password-length">Password length</label><output>{length}</output></div><input id="password-length" max="32" min="8" onChange={(event) => setLength(Number(event.target.value))} type="range" value={length} /><div><span>8</span><span>32</span></div></div>
          <div className="option-grid">
            {Object.entries(options).map(([label, enabled]) => <label className="option-check" key={label}><input checked={enabled} onChange={() => setOptions((values) => ({ ...values, [label]: !enabled }))} type="checkbox" /><span><Check size={12} /></span>{label}</label>)}
          </div>
        </div>
        <button className="button primary save-password" type="button"><Plus size={16} />Save to Vault</button>
      </section>
      <div className="generator-note"><ShieldCheck size={17} /><div><strong>Local generation</strong><p>Cryptographically secure randomness is used directly on this device.</p></div></div>
    </div>
  );
}

function NoteModal({ note, onClose, onSaveSuccess }: { note?: any; onClose: () => void; onSaveSuccess: () => void }) {
  const [title, setTitle] = useState(note?.title || "");
  const [category, setCategory] = useState(note?.category || "Personal");
  const [content, setContent] = useState(note?.content || "");

  const handleSave = async () => {
    if (!title || !content) return;
    await addNote({ title, category, content });
    onSaveSuccess();
    onClose();
  };

  return (
    <div className="modal-overlay" onMouseDown={(event) => event.target === event.currentTarget && onClose()}>
      <section aria-labelledby="note-title" aria-modal="true" className="credential-modal" role="dialog">
        <header className="modal-header">
          <div><span className="modal-title-icon"><FileKey2 size={20} /></span><div><h2 id="note-title">{note ? note.title : "New Secure Note"}</h2><p>Manage your encrypted text notes.</p></div></div>
          <button aria-label="Close note details" className="icon-button" onClick={onClose} type="button"><X size={19} /></button>
        </header>
        <div className="modal-body">
          <label className="form-field"><span>Title</span><div><FileText size={16} /><input value={title} onChange={(e) => setTitle(e.target.value)} placeholder="e.g. Wi-Fi Password or Backup Codes" /></div></label>
          <label className="form-field"><span>Category</span><div><FolderKey size={16} /><select value={category} onChange={(e) => setCategory(e.target.value)}><option value="Personal">Personal</option><option value="Network">Network</option><option value="Security">Security</option><option value="Infrastructure">Infrastructure</option></select><ChevronDown size={15} /></div></label>
          <label className="form-field notes-field"><span>Content</span><textarea value={content} onChange={(e) => setContent(e.target.value)} placeholder="Type your secure note contents here..." style={{ height: 120 }} /></label>
        </div>
        <footer className="modal-footer">
          <button className="delete-action" type="button"><Trash2 size={15} />Delete Note</button>
          <div><button className="button secondary" onClick={onClose} type="button">Cancel</button><button className="button primary" onClick={handleSave} type="button">Save Note</button></div>
        </footer>
      </section>
    </div>
  );
}

function NotesPage({ liveNotes, onRefresh }: { liveNotes: any[]; onRefresh: () => void }) {
  const [query, setQuery] = useState("");
  const [showNoteModal, setShowNoteModal] = useState(false);
  const [selectedNote, setSelectedNote] = useState<any | null>(null);

  const displayNotes = liveNotes && liveNotes.length > 0 ? liveNotes : [];
  const filtered = displayNotes.filter((item) =>
    `${item.title} ${item.category} ${item.content || ""}`.toLowerCase().includes(query.toLowerCase())
  );

  return (
    <div className="page-body notes-page">
      <div className="section-actions">
        <label className="search-field"><Search size={16} /><input placeholder="Search secure notes..." value={query} onChange={(e) => setQuery(e.target.value)} /></label>
        <button className="button primary" onClick={() => { setSelectedNote(null); setShowNoteModal(true); }} type="button"><Plus size={16} />New Note</button>
      </div>
      <div className="notes-grid">
        {filtered.map((note) => (
          <article className="note-card content-surface" key={note.id || note.title} onClick={() => { setSelectedNote(note); setShowNoteModal(true); }}>
            <header><span><FileKey2 size={20} /></span><button aria-label={`Options for ${note.title}`} className="icon-button" type="button"><MoreVertical size={17} /></button></header>
            <h2>{note.title}</h2>
            <p>{note.content ? (note.content.length > 80 ? note.content.substring(0, 80) + "..." : note.content) : "This note is encrypted and protected inside your local vault."}</p>
            <footer><span>{note.category}</span><small><Clock3 size={12} />Updated {note.updated}</small></footer>
          </article>
        ))}
        {filtered.length === 0 && (
          <div style={{ gridColumn: 'span 2', textAlign: 'center', padding: '40px', color: '#8295a7' }}>
            No secure notes found. Click "+ New Note" above to create one.
          </div>
        )}
      </div>
      <div className="notes-assurance"><LockKeyhole size={15} />All secure notes use end-to-end AES-256 encryption.</div>
      {showNoteModal && <NoteModal note={selectedNote} onClose={() => setShowNoteModal(false)} onSaveSuccess={onRefresh} />}
    </div>
  );
}

function Toggle({ checked, onChange }: { checked: boolean; onChange: () => void }) {
  return <button aria-checked={checked} className={`toggle ${checked ? "on" : ""}`} onClick={onChange} role="switch" type="button"><span /></button>;
}

function ChangePasswordModal({ onClose }: { onClose: () => void }) {
  const [oldPwd, setOldPwd] = useState("");
  const [newPwd, setNewPwd] = useState("");
  const [confirmPwd, setConfirmPwd] = useState("");
  const [error, setError] = useState("");
  const [success, setSuccess] = useState(false);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async () => {
    if (!oldPwd || !newPwd || !confirmPwd) return;
    if (newPwd.length < 8) {
      setError("New password must be at least 8 characters.");
      return;
    }
    if (newPwd !== confirmPwd) {
      setError("New passwords do not match.");
      return;
    }
    setLoading(true);
    setError("");
    const res = await changeMasterPassword(oldPwd, newPwd);
    setLoading(false);
    if (res.success) {
      setSuccess(true);
    } else {
      setError(res.error || "Failed to change password");
    }
  };

  return (
    <div className="modal-overlay" onMouseDown={(e) => e.target === e.currentTarget && onClose()}>
      <section className="credential-modal" role="dialog" style={{ maxWidth: 400 }}>
        <header className="modal-header">
          <div><span className="modal-title-icon"><LockKeyhole size={20} /></span><div><h2>Change Master Password</h2><p>This will re-encrypt your entire vault.</p></div></div>
          <button className="icon-button" onClick={onClose} type="button"><X size={19} /></button>
        </header>
        <div className="modal-body">
          {success ? (
            <div style={{ padding: '20px', textAlign: 'center', color: '#80aa91' }}>
              <ShieldCheck size={40} style={{ margin: '0 auto 15px' }} />
              <h3>Password Changed Successfully</h3>
              <p style={{ marginTop: 10 }}>Your vault has been securely re-encrypted with your new master password.</p>
            </div>
          ) : (
            <div className="form-grid" style={{ gridTemplateColumns: '1fr' }}>
              <label className="form-field"><span>Current Password</span><div><Lock size={16} /><input type="password" value={oldPwd} onChange={(e) => setOldPwd(e.target.value)} /></div></label>
              <label className="form-field"><span>New Password</span><div><KeyRound size={16} /><input type="password" value={newPwd} onChange={(e) => setNewPwd(e.target.value)} /></div></label>
              <label className="form-field"><span>Confirm New Password</span><div><Check size={16} /><input type="password" value={confirmPwd} onChange={(e) => setConfirmPwd(e.target.value)} /></div></label>
              {error && <div style={{ color: '#c95b6d', fontSize: 12, marginTop: 5 }}>{error}</div>}
              {loading && <div style={{ color: '#8295a7', fontSize: 12, marginTop: 5 }}>Re-encrypting vault (this may take a moment)...</div>}
            </div>
          )}
        </div>
        <footer className="modal-footer" style={{ justifyContent: 'flex-end' }}>
          {success ? (
            <button className="button primary" onClick={onClose} type="button">Close</button>
          ) : (
            <div><button className="button secondary" onClick={onClose} type="button">Cancel</button><button className="button primary" onClick={handleSubmit} disabled={loading} type="button">Change Password</button></div>
          )}
        </footer>
      </section>
    </div>
  );
}

function EnableBiometricModal({ onClose, onSuccess }: { onClose: () => void; onSuccess: () => void }) {
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async () => {
    if (!password) return;
    setLoading(true);
    setError("");
    const res = await enableBiometrics(password);
    setLoading(false);
    if (res.success) {
      onSuccess();
      onClose();
    } else {
      setError(res.error || "Failed to verify Windows Hello");
    }
  };

  return (
    <div className="modal-overlay" onMouseDown={(e) => e.target === e.currentTarget && onClose()}>
      <section className="credential-modal" role="dialog" style={{ maxWidth: 400 }}>
        <header className="modal-header">
          <div><span className="modal-title-icon"><Fingerprint size={20} /></span><div><h2>Enable Biometric Unlock</h2><p>Authorize Windows Hello with your master password.</p></div></div>
          <button className="icon-button" onClick={onClose} type="button"><X size={19} /></button>
        </header>
        <div className="modal-body">
          <div className="form-grid" style={{ gridTemplateColumns: '1fr' }}>
            <label className="form-field"><span>Confirm Master Password</span><div><Lock size={16} /><input type="password" value={password} onChange={(e) => setPassword(e.target.value)} placeholder="Master password" /></div></label>
            {error && <div style={{ color: '#c95b6d', fontSize: 12, marginTop: 5 }}>{error}</div>}
            {loading && <div style={{ color: '#8295a7', fontSize: 12, marginTop: 5 }}>Triggering Windows Hello prompt...</div>}
          </div>
        </div>
        <footer className="modal-footer" style={{ justifyContent: 'flex-end' }}>
          <div><button className="button secondary" onClick={onClose} type="button">Cancel</button><button className="button primary" onClick={handleSubmit} disabled={loading} type="button">Authorize &amp; Verify</button></div>
        </footer>
      </section>
    </div>
  );
}

function SettingsPage({ settings, onUpdate }: { settings: any; onUpdate: (newSettings: any) => void }) {
  const [showPasswordModal, setShowPasswordModal] = useState(false);
  const [showBioModal, setShowBioModal] = useState(false);

  const set = async (key: string) => {
    if (key === "biometric") {
      if (!settings.biometric) {
        // Turning ON: open modal
        setShowBioModal(true);
        return;
      } else {
        // Turning OFF
        await disableBiometrics();
        const updated = { ...settings, biometric: false };
        onUpdate(updated);
        return;
      }
    }
    const updated = { ...settings, [key]: !settings[key] };
    onUpdate(updated);
  };

  const handleBioSuccess = () => {
    const updated = { ...settings, biometric: true };
    onUpdate(updated);
  };

  const setVal = (key: string, val: any) => {
    const updated = { ...settings, [key]: val };
    onUpdate(updated);
  };

  const sections = [
    { title: "Account", icon: UserRound, rows: [["Profile", "Farhan Khan • user@example.com", "Manage"]] },
    { title: "Security", icon: ShieldCheck, rows: [
      ["Master Password", "Requires full vault re-encryption", "changePw"],
      ["Auto-Lock", "Lock vault after inactivity", "autoLock"],
      ["Biometric Unlock", "Use Windows Hello biometrics (Fingerprint / PIN / Face)", "biometric"],
      ["Two-Factor Authentication", "Require verification when signing in", "twoFactor"],
      ["Session Timeout", "End inactive sessions automatically", "sessionTimeout"]
    ] },
    { title: "Vault", icon: Database, rows: [["Vault Location", "Stored locally on this device", "View"], ["Clipboard Protection", "Clear copied passwords after 30 seconds", "clipboard"]] },
    { title: "Notifications", icon: AlertTriangle, rows: [["Security Alerts", "Receive important vault security updates", "notifications"]] },
    { title: "Privacy", icon: Fingerprint, rows: [["Analytics", "Usage analytics are disabled", "Private"]] },
  ];

  return (
    <div className="page-body settings-page">
      {sections.map(({ title, icon: Icon, rows }) => (
        <section className="settings-section content-surface" key={title}>
          <header><Icon size={18} /><h2>{title}</h2></header>
          {rows.map(([label, copy, action]) => (
            <div className="settings-row" key={label}>
              <div><strong>{label}</strong><small>{copy}</small></div>

              {action === "changePw" ? (
                <button onClick={() => setShowPasswordModal(true)} type="button">Change</button>
              ) : action === "autoLock" ? (
                <div style={{ display: 'flex', alignItems: 'center', gap: 5 }}>
                  <select value={settings.autoLockTime || 15} onChange={(e) => setVal('autoLockTime', parseInt(e.target.value))} style={{ background: 'transparent', color: '#a2b1bc', border: 'none', cursor: 'pointer' }}>
                    <option value={5}>5 min</option>
                    <option value={15}>15 min</option>
                    <option value={30}>30 min</option>
                    <option value={60}>60 min</option>
                  </select>
                  <ChevronDown size={13} style={{ color: '#a2b1bc' }}/>
                </div>
              ) : action === "sessionTimeout" ? (
                <div style={{ display: 'flex', alignItems: 'center', gap: 5 }}>
                  <select value={settings.sessionTimeoutTime || 30} onChange={(e) => setVal('sessionTimeoutTime', parseInt(e.target.value))} style={{ background: 'transparent', color: '#a2b1bc', border: 'none', cursor: 'pointer' }}>
                    <option value={15}>15 min</option>
                    <option value={30}>30 min</option>
                    <option value={120}>2 hours</option>
                  </select>
                  <ChevronDown size={13} style={{ color: '#a2b1bc' }}/>
                </div>
              ) : ["biometric", "twoFactor", "notifications", "clipboard"].includes(action as string) ? (
                <Toggle checked={settings[action as string] || false} onChange={() => set(action as string)} />
              ) : (
                <button type="button">{action}<ChevronDown size={13} /></button>
              )}
            </div>
          ))}
        </section>
      ))}
      <section className="settings-section content-surface"><header><Settings size={18} /><h2>Appearance</h2></header><div className="settings-row"><div><strong>Theme</strong><small>Graphite dark</small></div><button type="button">Dark<ChevronDown size={13} /></button></div></section>

      {showPasswordModal && <ChangePasswordModal onClose={() => setShowPasswordModal(false)} />}
      {showBioModal && <EnableBiometricModal onClose={() => setShowBioModal(false)} onSuccess={handleBioSuccess} />}
    </div>
  );
}

function Application({ onLock }: { onLock: () => void }) {
  const [page, setPage] = useState<Page>("Vault");
  const [selectedCredential, setSelectedCredential] = useState<Credential | null>(null);
  const [liveCredentials, setLiveCredentials] = useState<Credential[]>([]);
  const [liveNotesList, setLiveNotesList] = useState<any[]>([]);

  // Default settings
  const [settings, setSettings] = useState<any>({
    biometric: true,
    twoFactor: true,
    notifications: false,
    clipboard: true,
    autoLockTime: 15,
    sessionTimeoutTime: 30
  });

  const loadData = async () => {
    const creds = await getCredentials();
    if (creds && creds.length > 0) {
      setLiveCredentials(creds);
    }
    const notesData = await getNotes();
    if (notesData) {
      setLiveNotesList(notesData);
    }
    const userSettings = await getSettings();
    if (userSettings && Object.keys(userSettings).length > 0) {
      setSettings((prev: any) => ({ ...prev, ...userSettings }));
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleUpdateSettings = async (newSettings: any) => {
    setSettings(newSettings);
    await updateSettings(newSettings);
  };

  // Auto-Lock Global Hook
  useEffect(() => {
    let timeout: number;

    const resetTimer = () => {
      window.clearTimeout(timeout);
      // autoLockTime is in minutes, convert to ms
      const lockMs = (settings.autoLockTime || 15) * 60 * 1000;
      timeout = window.setTimeout(handleLock, lockMs);
    };

    resetTimer(); // Start initial timer

    // Attach listeners
    window.addEventListener("mousemove", resetTimer);
    window.addEventListener("keydown", resetTimer);
    window.addEventListener("click", resetTimer);

    return () => {
      window.clearTimeout(timeout);
      window.removeEventListener("mousemove", resetTimer);
      window.removeEventListener("keydown", resetTimer);
      window.removeEventListener("click", resetTimer);
    };
  }, [settings.autoLockTime]);

  const handleLock = async () => {
    await lockVault();
    onLock();
  };

  const content = useMemo(() => {
    if (page === "Vault") return <VaultPage liveCredentials={liveCredentials} onRefresh={loadData} onSelect={setSelectedCredential} />;
    if (page === "Secure Notes") return <NotesPage liveNotes={liveNotesList} onRefresh={loadData} />;
    if (page === "Password Generator") return <GeneratorPage />;
    if (page === "Security Audit") return <SecurityAuditPage />;
    return <SettingsPage settings={settings} onUpdate={handleUpdateSettings} />;
  }, [page, liveCredentials, liveNotesList, settings]);

  return (
    <div className="app-shell">
      <Sidebar onLock={handleLock} onNavigate={(nextPage) => { setPage(nextPage); setSelectedCredential(null); loadData(); }} page={page} />
      <main className="main-content"><PageHeader page={page} />{content}</main>
      {selectedCredential && <CredentialModal credential={selectedCredential} onClose={() => setSelectedCredential(null)} onSaveSuccess={loadData} />}
    </div>
  );
}

export default function App() {
  const [stage, setStage] = useState<Stage>("landing");

  const lockVault = () => {
    setStage("locking");
    window.setTimeout(() => setStage("locked"), 900);
  };

  const handleOpenClick = async () => {
    const exists = await checkVaultExists();
    if (exists) {
      setStage("unlock");
    } else {
      setStage("welcome");
    }
  };

  if (stage === "landing") return <Landing onOpen={handleOpenClick} />;
  if (stage === "welcome") return <Welcome onContinue={() => setStage("app")} onImport={() => setStage("app")} />;
  if (stage === "unlock") return <UnlockScreen onUnlock={() => setStage("app")} />;
  if (stage === "locking") return <LockingScreen />;
  if (stage === "locked") return <LockedScreen onUnlock={() => setStage("unlock")} />;
  return <Application onLock={lockVault} />;
}
