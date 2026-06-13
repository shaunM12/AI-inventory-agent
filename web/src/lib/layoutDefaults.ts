export const MAIN_LAYOUT_ID = "inventory-agent:main:v2";
export const WORKSPACE_LAYOUT_ID = "inventory-agent:workspace:v2";

type PanelSize = number | string;

export interface PanelSizeConfig {
  defaultSize: PanelSize;
  minSize: PanelSize;
  maxSize?: PanelSize;
  groupResizeBehavior?: "preserve-relative-size" | "preserve-pixel-size";
}

export function getMainPanelSizes(isMobile: boolean, isTablet: boolean): {
  dashboard: PanelSizeConfig;
  workspace: PanelSizeConfig;
} {
  if (isMobile) {
    return {
      dashboard: {
        defaultSize: "32%",
        minSize: "20%",
        maxSize: "48%",
      },
      workspace: {
        defaultSize: "68%",
        minSize: "38%",
      },
    };
  }

  if (isTablet) {
    return {
      dashboard: {
        defaultSize: "38%",
        minSize: "22%",
        maxSize: "52%",
      },
      workspace: {
        defaultSize: "62%",
        minSize: "32%",
      },
    };
  }

  // Desktop: viewport-based height keeps KPI + both store tables visible without swallowing chat.
  return {
    dashboard: {
      defaultSize: "50vh",
      minSize: 160,
      maxSize: "70vh",
      groupResizeBehavior: "preserve-relative-size",
    },
    workspace: {
      defaultSize: "50%",
      minSize: "24%",
    },
  };
}

export function getWorkspacePanelSizes(compact: boolean): {
  history: PanelSizeConfig;
  chat: PanelSizeConfig;
  metrics: PanelSizeConfig;
} {
  if (compact) {
    return {
      history: { defaultSize: "20%", minSize: "14%", maxSize: "32%" },
      chat: { defaultSize: "52%", minSize: "34%" },
      metrics: { defaultSize: "28%", minSize: "14%", maxSize: "36%" },
    };
  }

  return {
    history: { defaultSize: "16%", minSize: "12%", maxSize: "26%" },
    chat: { defaultSize: "58%", minSize: "38%" },
    metrics: { defaultSize: "26%", minSize: "14%", maxSize: "32%" },
  };
}
