"""Windows Hello & DPAPI Biometric Authentication Manager."""

import ctypes
import logging
import concurrent.futures
from ctypes import wintypes
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

# Check WinRT availability
try:
    import winrt.windows.security.credentials.ui as ui
    WINRT_AVAILABLE = True
except ImportError:
    WINRT_AVAILABLE = False

# Windows DPAPI Setup
crypt32 = ctypes.windll.crypt32

class DATA_BLOB(ctypes.Structure):
    _fields_ = [
        ('cbData', wintypes.DWORD),
        ('pbData', ctypes.POINTER(ctypes.c_byte))
    ]

def _dpapi_encrypt(data: bytes) -> bytes:
    """Encrypt data using Windows DPAPI."""
    in_blob = DATA_BLOB(len(data), ctypes.cast(data, ctypes.POINTER(ctypes.c_byte)))
    out_blob = DATA_BLOB()
    if crypt32.CryptProtectData(ctypes.byref(in_blob), "LockByteBiometricKey", None, None, None, 0, ctypes.byref(out_blob)):
        res = ctypes.string_at(out_blob.pbData, out_blob.cbData)
        ctypes.windll.kernel32.LocalFree(out_blob.pbData)
        return res
    raise RuntimeError("DPAPI encryption failed")

def _dpapi_decrypt(data: bytes) -> bytes:
    """Decrypt data using Windows DPAPI."""
    in_blob = DATA_BLOB(len(data), ctypes.cast(data, ctypes.POINTER(ctypes.c_byte)))
    out_blob = DATA_BLOB()
    if crypt32.CryptUnprotectData(ctypes.byref(in_blob), None, None, None, None, 0, ctypes.byref(out_blob)):
        res = ctypes.string_at(out_blob.pbData, out_blob.cbData)
        ctypes.windll.kernel32.LocalFree(out_blob.pbData)
        return res
    raise RuntimeError("DPAPI decryption failed")


def _run_in_executor(func, *args):
    """Run WinRT async call in a clean background thread to avoid Qt GUI STA thread deadlocks."""
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(func, *args)
        return future.result(timeout=30)


class BiometricAuthManager:
    """Manager for Windows Hello biometrics and DPAPI credential protection."""

    def __init__(self, key_store_dir: Optional[Path] = None):
        self.key_store_dir = key_store_dir or (Path.home() / ".lockbyte")
        self.key_store_dir.mkdir(parents=True, exist_ok=True)
        self.key_file = self.key_store_dir / "biometric.dat"

    @staticmethod
    def is_available() -> bool:
        """Check if Windows Hello (Fingerprint / PIN / Face) is available."""
        if not WINRT_AVAILABLE:
            return False
        try:
            def _check():
                res = ui.UserConsentVerifier.check_availability_async().get()
                return int(res) == 0  # 0 = UserConsentVerifierAvailability.AVAILABLE
            return _run_in_executor(_check)
        except Exception as e:
            logger.error(f"Error checking biometric availability: {e}")
            return False

    @staticmethod
    def verify_user(message: str = "Unlock LockByte Vault") -> bool:
        """Trigger the native Windows Hello prompt."""
        if not WINRT_AVAILABLE:
            return False
        try:
            def _verify():
                res = ui.UserConsentVerifier.request_verification_async(message).get()
                return int(res) == 0  # 0 = UserConsentVerificationResult.VERIFIED
            return _run_in_executor(_verify)
        except Exception as e:
            logger.error(f"Error during Windows Hello verification: {e}")
            return False

    def store_master_password(self, master_password: str) -> bool:
        """Protect and store master password using DPAPI after biometric verification."""
        try:
            encrypted_data = _dpapi_encrypt(master_password.encode('utf-8'))
            self.key_file.write_bytes(encrypted_data)
            return True
        except Exception as e:
            logger.error(f"Failed to store biometric key: {e}")
            return False

    def retrieve_master_password(self) -> Optional[str]:
        """Retrieve and decrypt master password using DPAPI."""
        if not self.key_file.exists():
            return None
        try:
            encrypted_data = self.key_file.read_bytes()
            decrypted_data = _dpapi_decrypt(encrypted_data)
            return decrypted_data.decode('utf-8')
        except Exception as e:
            logger.error(f"Failed to retrieve biometric key: {e}")
            return None

    def clear_stored_key(self):
        """Remove stored DPAPI biometric key file."""
        if self.key_file.exists():
            try:
                self.key_file.unlink()
            except Exception:
                pass
