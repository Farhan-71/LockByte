"""Security audit engine for credential hygiene."""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from security.password_analyzer import PasswordStrengthAnalyzer
from vault.models import PasswordAnalysis, SecurityAuditResult, CredentialCategory


@dataclass
class AuditFinding:
    """Represents a security audit finding."""
    finding_type: str  # weak_password, reused_password, old_password, missing_2fa, exposed
    credential_id: str
    website: str
    username: str
    severity: str  # critical, high, medium, low
    description: str
    recommendation: str
    details: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        from dataclasses import asdict
        return asdict(self)


class SecurityAuditEngine:
    """Performs security audits on vault credentials."""

    # Password age thresholds (in days)
    OLD_PASSWORD_THRESHOLD = 90  # 3 months
    VERY_OLD_PASSWORD_THRESHOLD = 180  # 6 months

    # Score weights
    WEAK_PASSWORD_PENALTY = 10
    REUSED_PASSWORD_PENALTY = 15
    MISSING_2FA_PENALTY = 5
    OLD_PASSWORD_PENALTY = 5
    EXPOSED_CREDENTIAL_PENALTY = 20

    def __init__(self, old_password_days: int = None, reuse_threshold: int = 2):
        """Initialize audit engine.

        Args:
            old_password_days: Days after which a password is considered old
            reuse_threshold: Minimum reuse count to flag
        """
        self.old_password_days = old_password_days or self.OLD_PASSWORD_THRESHOLD
        self.reuse_threshold = reuse_threshold

    def audit_credentials(self, credentials: List, exposed_credentials: set = None) -> SecurityAuditResult:
        """Perform a complete security audit of all credentials.

        Args:
            credentials: List of credential objects
            exposed_credentials: Set of credential IDs that may be exposed

        Returns:
            SecurityAuditResult with findings
        """
        if exposed_credentials is None:
            exposed_credentials = set()

        findings = []
        weak_passwords = 0
        reused_passwords = 0
        old_passwords = 0
        missing_2fa = 0
        exposed = 0

        # Check for password reuse
        reuse_map = self._find_reused_passwords(credentials)

        for cred in credentials:
            # Analyze password
            analysis = PasswordStrengthAnalyzer.analyze(
                cred.password,
                password_id=cred.id,
                check_reuse=True,
                reuse_count=reuse_map.get(cred.password, 0)
            )

            # Check for weak passwords
            if analysis.strength_level.value in ['very_weak', 'weak']:
                weak_passwords += 1
                findings.append(AuditFinding(
                    finding_type='weak_password',
                    credential_id=cred.id,
                    website=cred.website,
                    username=cred.username,
                    severity='high',
                    description=f"Password strength is {analysis.strength_level.value}",
                    recommendation='Consider using a stronger password',
                    details={
                        'strength_level': analysis.strength_level.value,
                        'entropy': analysis.entropy,
                        'length': analysis.length,
                        'recommendations': analysis.recommendations
                    }
                ))

            # Check for reused passwords
            if cred.password in reuse_map and reuse_map[cred.password] > 1:
                reused_passwords += 1
                findings.append(AuditFinding(
                    finding_type='reused_password',
                    credential_id=cred.id,
                    website=cred.website,
                    username=cred.username,
                    severity='critical',
                    description=f"Password is reused {reuse_map[cred.password]} times",
                    recommendation='Use unique passwords for each account',
                    details={
                        'reuse_count': reuse_map[cred.password],
                        'other_sites': [c['website'] for c in reuse_map[cred.password] if c['credential_id'] != cred.id]
                    }
                ))

            # Check for old passwords
            if cred.password_changed_date:
                age_days = (datetime.utcnow() - cred.password_changed_date).days
                if age_days >= self.VERY_OLD_PASSWORD_THRESHOLD:
                    old_passwords += 1
                    findings.append(AuditFinding(
                        finding_type='old_password',
                        credential_id=cred.id,
                        website=cred.website,
                        username=cred.username,
                        severity='medium',
                        description=f"Password is {age_days} days old (>180 days)",
                        recommendation='Consider changing this password',
                        details={'age_days': age_days}
                    ))
                elif age_days >= self.old_password_days:
                    old_passwords += 1
                    findings.append(AuditFinding(
                        finding_type='old_password',
                        credential_id=cred.id,
                        website=cred.website,
                        username=cred.username,
                        severity='low',
                        description=f"Password is {age_days} days old (>90 days)",
                        recommendation='Consider changing this password soon',
                        details={'age_days': age_days}
                    ))

            # Check for missing 2FA
            if not cred.has_2fa:
                missing_2fa += 1
                # Only flag as finding for important categories
                if cred.category in [CredentialCategory.FINANCE, CredentialCategory.WORK]:
                    findings.append(AuditFinding(
                        finding_type='missing_2fa',
                        credential_id=cred.id,
                        website=cred.website,
                        username=cred.username,
                        severity='medium',
                        description='Account does not have 2FA enabled',
                        recommendation='Enable two-factor authentication',
                        details={'category': cred.category.value}
                    ))

            # Check for exposed credentials
            if cred.id in exposed_credentials:
                exposed += 1
                findings.append(AuditFinding(
                    finding_type='exposed_credential',
                    credential_id=cred.id,
                    website=cred.website,
                    username=cred.username,
                    severity='critical',
                    description='This credential may have been exposed in a data breach',
                    recommendation='Change this password immediately',
                    details={'exposure_source': 'breach_check'}
                ))

        # Calculate overall score (0-100)
        total_issues = weak_passwords + reused_passwords + old_passwords + missing_2fa + exposed
        overall_score = self._calculate_score(
            len(credentials),
            weak_passwords,
            reused_passwords,
            missing_2fa,
            old_passwords,
            exposed
        )

        return SecurityAuditResult(
            vault_id='current',
            total_credentials=len(credentials),
            weak_passwords=weak_passwords,
            reused_passwords=reused_passwords,
            exposed_credentials=exposed,
            missing_2fa=missing_2fa,
            old_passwords=old_passwords,
            overall_score=overall_score,
            issues=[f.to_dict() for f in findings]
        )

    def _find_reused_passwords(self, credentials: List) -> Dict[str, int]:
        """Count password reuse across credentials.

        Args:
            credentials: List of credentials

        Returns:
            Dictionary mapping password to usage count
        """
        password_counts = {}
        for cred in credentials:
            # Use hash to avoid storing plain passwords
            password_hash = hash(cred.password)
            password_counts[password_hash] = password_counts.get(password_hash, 0) + 1
        return password_counts

    def _calculate_score(self, total: int, weak: int, reused: int,
                        missing_2fa: int, old: int, exposed: int) -> int:
        """Calculate overall security score (0-100).

        Args:
            total: Total number of credentials
            weak: Number of weak passwords
            reused: Number of reused passwords
            missing_2fa: Number without 2FA
            old: Number of old passwords
            exposed: Number potentially exposed

        Returns:
            Score from 0-100
        """
        if total == 0:
            return 100

        # Start with perfect score and subtract penalties
        score = 100

        # Weighted penalties
        score -= weak * self.WEAK_PASSWORD_PENALTY
        score -= reused * self.REUSED_PASSWORD_PENALTY
        score -= missing_2fa * self.MISSING_2FA_PENALTY
        score -= old * self.OLD_PASSWORD_PENALTY
        score -= exposed * self.EXPOSED_CREDENTIAL_PENALTY

        # Clamp to 0-100
        return max(0, min(100, score))

    def get_priority_actions(self, result: SecurityAuditResult) -> List[Dict[str, str]]:
        """Get prioritized remediation actions.

        Args:
            result: Security audit result

        Returns:
            List of prioritized actions
        """
        actions = []

        # Critical actions first
        if result.reused_passwords > 0:
            actions.append({
                'priority': 'critical',
                'action': 'Change reused passwords',
                'reason': f'{result.reused_passwords} passwords are reused across multiple accounts',
                'impact': 'High - one breach exposes multiple accounts'
            })

        if result.exposed_credentials > 0:
            actions.append({
                'priority': 'critical',
                'action': 'Review breach alerts',
                'reason': f'{result.exposed_credentials} credentials may be exposed',
                'impact': 'High - credentials may already be compromised'
            })

        if result.weak_passwords > 0:
            actions.append({
                'priority': 'high',
                'action': 'Strengthen weak passwords',
                'reason': f'{result.weak_passwords} passwords are weak',
                'impact': 'Medium - vulnerable to guessing attacks'
            })

        # Medium priority
        if result.old_passwords > 0:
            actions.append({
                'priority': 'medium',
                'action': 'Update old passwords',
                'reason': f'{result.old_passwords} passwords are over 90 days old',
                'impact': 'Low - good security practice'
            })

        if result.missing_2fa > 0:
            # Only report for important accounts
            actions.append({
                'priority': 'medium',
                'action': 'Enable 2FA on important accounts',
                'reason': f'{result.missing_2fa} important accounts lack 2FA',
                'impact': 'Medium - significantly improves account security'
            })

        return actions