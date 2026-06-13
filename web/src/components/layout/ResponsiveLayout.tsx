"use client";

import {
  Group,
  Panel,
  Separator,
  useDefaultLayout,
} from "react-resizable-panels";

import { ActiveChat } from "@/components/chat/ActiveChat";
import { ConversationHistory } from "@/components/chat/ConversationHistory";
import { InventoryDashboard } from "@/components/dashboard/InventoryDashboard";
import { MetricsSidebar } from "@/components/metrics/MetricsSidebar";
import { useBreakpoint } from "@/hooks/useMediaQuery";
import {
  getMainPanelSizes,
  getWorkspacePanelSizes,
  MAIN_LAYOUT_ID,
  WORKSPACE_LAYOUT_ID,
} from "@/lib/layoutDefaults";
import {
  clearPanelLayouts,
  panelStorage,
  panelTouchTargets,
} from "@/lib/panelStorage";

import { ResizeHandle } from "./ResizeHandle";
import {
  MobileWorkspaceTabs,
  type WorkspacePanelProps,
} from "./WorkspacePanels";

export type ResponsiveLayoutProps = WorkspacePanelProps & {
  refreshToken: number;
};

function HorizontalWorkspace({
  props,
  compact,
}: {
  props: ResponsiveLayoutProps;
  compact: boolean;
}) {
  const sizes = getWorkspacePanelSizes(compact);
  const workspaceLayout = useDefaultLayout({
    id: WORKSPACE_LAYOUT_ID,
    panelIds: ["history", "chat", "metrics"],
    storage: panelStorage,
  });

  return (
    <Group
      id="workspace-horizontal"
      orientation="horizontal"
      className="h-full min-h-0 px-1.5 py-1.5 sm:px-2 sm:py-2"
      defaultLayout={workspaceLayout.defaultLayout}
      onLayoutChanged={workspaceLayout.onLayoutChanged}
      resizeTargetMinimumSize={panelTouchTargets}
    >
      <Panel
        id="history"
        defaultSize={sizes.history.defaultSize}
        minSize={sizes.history.minSize}
        maxSize={sizes.history.maxSize}
        className="min-w-0"
      >
        <ConversationHistory
          conversations={props.conversations}
          activeId={props.activeId}
          searchQuery={props.searchQuery}
          onSearchChange={props.onSearchChange}
          onSelect={props.onSelectConversation}
          onNewChat={props.onNewChat}
          onClear={props.onClearConversation}
        />
      </Panel>

      <Separator>
        <ResizeHandle direction="vertical" label="Resize history panel" />
      </Separator>

      <Panel
        id="chat"
        defaultSize={sizes.chat.defaultSize}
        minSize={sizes.chat.minSize}
        className="min-w-0"
      >
        <ActiveChat
          conversation={props.activeConversation}
          loading={props.chatLoading}
          error={props.chatError}
          onSend={props.onSend}
          onDismissError={props.onDismissError}
        />
      </Panel>

      <Separator>
        <ResizeHandle direction="vertical" label="Resize metrics panel" />
      </Separator>

      <Panel
        id="metrics"
        defaultSize={sizes.metrics.defaultSize}
        minSize={sizes.metrics.minSize}
        maxSize={sizes.metrics.maxSize}
        className="min-w-0"
      >
        <MetricsSidebar
          config={props.config}
          conversation={props.activeConversation}
          apiOnline={props.apiOnline}
          lastTurn={props.lastTurn}
        />
      </Panel>
    </Group>
  );
}

export function ResponsiveLayout(props: ResponsiveLayoutProps) {
  const { isMobile, isTablet } = useBreakpoint();
  const compact = isTablet;
  const mainSizes = getMainPanelSizes(isMobile, isTablet);

  const mainLayout = useDefaultLayout({
    id: MAIN_LAYOUT_ID,
    panelIds: ["dashboard", "workspace"],
    storage: panelStorage,
  });

  return (
    <div className="mx-auto flex min-h-0 w-full max-w-[1680px] flex-1 flex-col">
      <Group
        id="main-vertical"
        orientation="vertical"
        className="min-h-0 flex-1"
        defaultLayout={mainLayout.defaultLayout}
        onLayoutChanged={mainLayout.onLayoutChanged}
        resizeTargetMinimumSize={panelTouchTargets}
      >
        <Panel
          id="dashboard"
          defaultSize={mainSizes.dashboard.defaultSize}
          minSize={mainSizes.dashboard.minSize}
          maxSize={mainSizes.dashboard.maxSize}
          groupResizeBehavior={mainSizes.dashboard.groupResizeBehavior}
          className="min-h-0"
        >
          <InventoryDashboard
            config={props.config}
            refreshToken={props.refreshToken}
            compact={!isMobile}
          />
        </Panel>

        <Separator>
          <ResizeHandle
            direction="horizontal"
            label="Drag to resize inventory and chat areas"
          />
        </Separator>

        <Panel
          id="workspace"
          defaultSize={mainSizes.workspace.defaultSize}
          minSize={mainSizes.workspace.minSize}
          className="min-h-0"
        >
          {isMobile ? (
            <MobileWorkspaceTabs {...props} />
          ) : (
            <HorizontalWorkspace props={props} compact={compact} />
          )}
        </Panel>
      </Group>
    </div>
  );
}

export function resetPanelLayout(): void {
  clearPanelLayouts();
}
