// Client bridge helper for QWebChannel with polling retry

declare global {
  interface Window {
    qt?: any;
    QWebChannel?: any;
    pybridge?: any;
  }
}

let pybridgeInstance: any = null;
let bridgePromise: Promise<any> | null = null;

export function initBridge(): Promise<any> {
  if (pybridgeInstance) {
    return Promise.resolve(pybridgeInstance);
  }

  if (bridgePromise) {
    return bridgePromise;
  }

  bridgePromise = new Promise((resolve) => {
    let attempts = 0;
    const maxAttempts = 50; // Poll for up to 5 seconds

    const check = () => {
      if (window.qt && window.QWebChannel) {
        try {
          new window.QWebChannel(window.qt.webChannelTransport, (channel: any) => {
            pybridgeInstance = channel.objects.pybridge;
            window.pybridge = pybridgeInstance;
            console.log("PyBridge Connected Successfully!");
            resolve(pybridgeInstance);
          });
          return;
        } catch (e) {
          console.error("Error initializing QWebChannel:", e);
        }
      }

      attempts++;
      if (attempts < maxAttempts) {
        setTimeout(check, 100);
      } else {
        console.warn("PyBridge not available after 5s. Falling back to mock mode.");
        resolve(null);
      }
    };

    check();
  });

  return bridgePromise;
}

// Helper to wrap old-school QWebChannel callbacks in modern Promises
function invokeBridge<T>(methodName: string, ...args: any[]): Promise<T> {
  return new Promise(async (resolve) => {
    const bridge = await initBridge();
    if (!bridge) {
      resolve(null as any);
      return;
    }

    // Call the method with all arguments, plus a callback function at the end
    bridge[methodName](...args, (result: T) => {
      resolve(result);
    });
  });
}

export async function checkVaultExists(): Promise<boolean> {
  const result = await invokeBridge<boolean>("check_vault_exists");
  return result || false;
}

export async function unlockVault(password: string): Promise<{ success: boolean; error?: string }> {
  const resStr = await invokeBridge<string>("unlock_vault", password);
  if (resStr) return JSON.parse(resStr);
  return { success: true }; // Fallback
}

export async function createVault(password: string): Promise<{ success: boolean; error?: string }> {
  const resStr = await invokeBridge<string>("create_vault", password);
  if (resStr) return JSON.parse(resStr);
  return { success: true };
}

export async function lockVault(): Promise<void> {
  await invokeBridge<void>("lock_vault");
}

export async function getCredentials(search = ""): Promise<any[]> {
  const resStr = await invokeBridge<string>("get_credentials", search);
  if (resStr) {
    const res = JSON.parse(resStr);
    if (res.success) return res.data;
  }
  return [];
}

export async function addCredential(data: any): Promise<boolean> {
  const resStr = await invokeBridge<string>("add_credential", JSON.stringify(data));
  if (resStr) {
    const res = JSON.parse(resStr);
    return res.success;
  }
  return true;
}

export async function getNotes(): Promise<any[]> {
  const resStr = await invokeBridge<string>("get_notes");
  if (resStr) {
    const res = JSON.parse(resStr);
    if (res.success) return res.data;
  }
  return [];
}

export async function addNote(data: any): Promise<boolean> {
  const resStr = await invokeBridge<string>("add_note", JSON.stringify(data));
  if (resStr) {
    const res = JSON.parse(resStr);
    return res.success;
  }
  return true;
}

export async function runAudit(): Promise<any> {
  const resStr = await invokeBridge<string>("run_audit");
  if (resStr) {
    const res = JSON.parse(resStr);
    if (res.success) return res;
  }
  return null;
}

export async function getSettings(): Promise<any> {
  const resStr = await invokeBridge<string>("get_settings");
  if (resStr) {
    const res = JSON.parse(resStr);
    if (res.success) return res.data;
  }
  return {};
}

export async function updateSettings(settings: any): Promise<boolean> {
  const resStr = await invokeBridge<string>("update_settings", JSON.stringify(settings));
  if (resStr) {
    const res = JSON.parse(resStr);
    return res.success;
  }
  return false;
}

export async function changeMasterPassword(oldPw: string, newPw: string): Promise<{ success: boolean; error?: string }> {
  const resStr = await invokeBridge<string>("change_master_password", oldPw, newPw);
  if (resStr) return JSON.parse(resStr);
  return { success: false, error: "Bridge failed" };
}

export async function checkBiometricsAvailable(): Promise<boolean> {
  const resStr = await invokeBridge<string>("check_biometrics_available");
  if (resStr) {
    const res = JSON.parse(resStr);
    return res.available || false;
  }
  return false;
}

export async function hasStoredBiometricKey(): Promise<boolean> {
  const resStr = await invokeBridge<string>("has_stored_biometric_key");
  if (resStr) {
    const res = JSON.parse(resStr);
    return res.hasKey || false;
  }
  return false;
}

export async function authenticateBiometrics(): Promise<{ success: boolean; verified: boolean; error?: string }> {
  const resStr = await invokeBridge<string>("authenticate_biometrics");
  if (resStr) return JSON.parse(resStr);
  return { success: false, verified: false, error: "Bridge failed" };
}

export async function enableBiometrics(masterPassword: string): Promise<{ success: boolean; error?: string }> {
  const resStr = await invokeBridge<string>("enable_biometrics", masterPassword);
  if (resStr) return JSON.parse(resStr);
  return { success: false, error: "Bridge failed" };
}

export async function disableBiometrics(): Promise<boolean> {
  const resStr = await invokeBridge<string>("disable_biometrics");
  if (resStr) {
    const res = JSON.parse(resStr);
    return res.success;
  }
  return false;
}
