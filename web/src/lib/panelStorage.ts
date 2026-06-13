import type { LayoutStorage } from "react-resizable-panels";

export const panelStorage: LayoutStorage = {
  getItem(key: string) {
    if (typeof window === "undefined") {
      return null;
    }
    return window.localStorage.getItem(key);
  },
  setItem(key: string, value: string) {
    if (typeof window === "undefined") {
      return;
    }
    window.localStorage.setItem(key, value);
  },
};

export function clearPanelLayouts(): void {
  if (typeof window === "undefined") {
    return;
  }
  for (const key of Object.keys(window.localStorage)) {
    if (
      key.startsWith("react-resizable-panels:inventory-agent:") ||
      key.includes("inventory-agent:main") ||
      key.includes("inventory-agent:workspace") ||
      key.includes("inventory-agent:stores")
    ) {
      window.localStorage.removeItem(key);
    }
  }
}

/** Larger hit targets on touch screens for drag handles. */
export const panelTouchTargets = {
  coarse: 36,
  fine: 10,
};
