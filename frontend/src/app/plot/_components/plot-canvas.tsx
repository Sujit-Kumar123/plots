"use client";
import { useState } from "react";
import { usePlotScene } from "./_use-plot-scene";
import { SidePanel } from "./side-panel";
import { SheetConfig } from "./sheet-config";
import { TipBar } from "./tip-bar";
import { TextInputOverlay } from "./text-input-overlay";
import { DivEditOverlay } from "./div-edit-overlay";
import { CatalogPanel } from "./catalog-panel";
import type { CatalogItem } from "@/lib/services/plot-catalog";

export default function PlotCanvas({
  initialSheetId,
  catalogPromise,
}: {
  initialSheetId?: string;
  catalogPromise: Promise<CatalogItem[]>;
}) {
  const scene = usePlotScene(initialSheetId);
  const [showCatalog, setShowCatalog] = useState(false);
  return (
    <div className="relative w-screen h-screen overflow-hidden font-sans">
      <div ref={scene.mountRef} className="absolute inset-0" />
      {showCatalog && (
        <CatalogPanel
          catalogPromise={catalogPromise}
          selectedId={scene.selectedCatalogItem?.id}
          onSelect={scene.doSelectCatalogItem}
        />
      )}
      {scene.showSheetCfg && (
        <SheetConfig
          sheetW={scene.sheetW}
          sheetD={scene.sheetD}
          draftW={scene.draftW}
          draftD={scene.draftD}
          setDraftW={scene.setDraftW}
          setDraftD={scene.setDraftD}
          onClose={() => scene.setShowSheetCfg(false)}
          buildGrid={scene.buildGrid}
          doApplySheet={scene.doApplySheet}
        />
      )}
      <SidePanel
        curTool={scene.curTool}
        curColor={scene.curColor}
        curH={scene.curH}
        selCount={scene.selCount}
        rotLocked={scene.rotLocked}
        canUndo={scene.canUndo}
        canRedo={scene.canRedo}
        sheetW={scene.sheetW}
        sheetD={scene.sheetD}
        showSheetCfg={scene.showSheetCfg}
        doTool={scene.doTool}
        curW={scene.curW}
        curD={scene.curD}
        doColor={scene.doColor}
        doHeight={scene.doHeight}
        doWidth={scene.doWidth}
        doDepth={scene.doDepth}
        doUndo={scene.doUndo}
        doRedo={scene.doRedo}
        doFill={scene.doFill}
        doClear={scene.doClear}
        doToggleRotation={scene.doToggleRotation}
        doPrint={scene.doPrint}
        onToggleSheetCfg={() => scene.setShowSheetCfg(v => !v)}
        viewMode={scene.viewMode}
        doViewMode={scene.doViewMode}
        sheetId={scene.sheetId}
        sheetName={scene.sheetName}
        isSaving={scene.isSaving}
        doSave={scene.doSave}
        doSetSheetName={scene.doSetSheetName}
        gridStep={scene.gridStep}
        doGridStep={scene.doGridStep}
        curBorderW={scene.curBorderW}
        curBorderR={scene.curBorderR}
        doBorderW={scene.doBorderW}
        doBorderR={scene.doBorderR}
        showCatalog={showCatalog}
        onToggleCatalog={() => setShowCatalog(v => !v)}
        selectedFurnitureName={scene.selectedCatalogItem?.name ?? null}
      />
      <TipBar curTool={scene.curTool} />
      {scene.showTextInput && (
        <TextInputOverlay
          pos={scene.textInputPos}
          color={scene.curColor}
          onCommit={scene.commitText}
          onCancel={scene.cancelText}
        />
      )}
      {scene.showDivInput && (
        <DivEditOverlay
          rect={scene.divEditRect}
          color={scene.curColor}
          onCommit={scene.commitDiv}
          onCancel={scene.cancelDiv}
        />
      )}
    </div>
  );
}
