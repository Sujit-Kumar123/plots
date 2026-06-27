"use client";

import { useEffect, useRef, useCallback, useState } from "react";
import * as THREE from "three";
import { TrackballControls } from "three/examples/jsm/controls/TrackballControls.js";
import type { Tool, BlockInfo, UndoCmd, ShapeAnchor, WallInfo, DivPanelInfo, TextInfo } from "./_types";
import { CURSORS } from "./_constants";
import { cssColorToInt, cssColorToStr, getSceneBg } from "./_colors";
import { circlePts, ellipsePts, planeRight, vCirclePts, vEllipsePts } from "./_geometry";
import { apiCreateSheet, apiGetSheet, apiUpdateSheet, type SheetElements } from "@/lib/services/plot-sheets";

// ── canvas-based text sprite ──────────────────────────────────────────────────
function makeTextSprite(text: string, color: string): THREE.Sprite {
  const fontSize = 48;
  const pad = 14;
  const canvas = document.createElement("canvas");
  const ctx = canvas.getContext("2d")!;
  ctx.font = `bold ${fontSize}px sans-serif`;
  const tw = Math.max(ctx.measureText(text).width, 8);
  canvas.width  = Math.ceil(tw) + pad * 2;
  canvas.height = fontSize + pad * 2;
  ctx.font = `bold ${fontSize}px sans-serif`;
  ctx.fillStyle = color;
  ctx.textBaseline = "middle";
  ctx.fillText(text, pad, canvas.height / 2);
  const tex = new THREE.CanvasTexture(canvas);
  const mat = new THREE.SpriteMaterial({ map: tex, transparent: true, depthTest: false });
  const spr = new THREE.Sprite(mat);
  spr.scale.set((canvas.width / canvas.height) * 2, 2, 1);
  return spr;
}

function roundedRect(ctx: CanvasRenderingContext2D, x: number, y: number, w: number, h: number, r: number) {
  const rr = Math.min(r, w / 2, h / 2);
  ctx.beginPath();
  ctx.moveTo(x + rr, y);
  ctx.lineTo(x + w - rr, y);
  ctx.arcTo(x + w, y,     x + w, y + rr,     rr);
  ctx.lineTo(x + w, y + h - rr);
  ctx.arcTo(x + w, y + h, x + w - rr, y + h, rr);
  ctx.lineTo(x + rr, y + h);
  ctx.arcTo(x,       y + h, x, y + h - rr,   rr);
  ctx.lineTo(x, y + rr);
  ctx.arcTo(x,       y,     x + rr, y,        rr);
  ctx.closePath();
}

function makeDivTexture(text: string, color: string, w: number, h: number, borderWidth = 3, borderRadius = 0): THREE.CanvasTexture {
  const RES = 512;
  const cw = Math.round(RES * (w >= h ? 1 : w / h));
  const ch = Math.round(RES * (h >= w ? 1 : h / w));
  const cv = document.createElement("canvas");
  cv.width = cw; cv.height = ch;
  const ctx = cv.getContext("2d")!;
  const lw = Math.round(borderWidth * (RES / 100));
  const r  = Math.round(Math.min(cw, ch) * (borderRadius / 200));
  const pad = lw / 2 + 1;
  // background fill
  ctx.fillStyle = color;
  ctx.globalAlpha = 0.18;
  roundedRect(ctx, 0, 0, cw, ch, r);
  ctx.fill();
  ctx.globalAlpha = 1;
  // border stroke
  ctx.strokeStyle = color;
  ctx.lineWidth = lw;
  roundedRect(ctx, pad, pad, cw - pad * 2, ch - pad * 2, Math.max(0, r - pad));
  ctx.stroke();
  // text
  const fs = Math.min(cw, ch) * 0.15;
  ctx.font = `bold ${fs}px sans-serif`;
  ctx.fillStyle = color;
  ctx.textAlign = "center";
  ctx.textBaseline = "middle";
  const maxW = cw - 24;
  const words = text.split(" ");
  const lines: string[] = [];
  let cur = "";
  for (const word of words) {
    const test = cur ? `${cur} ${word}` : word;
    if (ctx.measureText(test).width > maxW && cur) { lines.push(cur); cur = word; }
    else cur = test;
  }
  if (cur) lines.push(cur);
  const lh = fs * 1.4;
  const startY = ch / 2 - ((lines.length - 1) * lh) / 2;
  lines.forEach((line, i) => ctx.fillText(line, cw / 2, startY + i * lh, maxW));
  const tex = new THREE.CanvasTexture(cv);
  tex.needsUpdate = true;
  return tex;
}

export function usePlotScene(initialSheetId?: string) {
  const mountRef = useRef<HTMLDivElement>(null);
  const sceneRef = useRef<THREE.Scene | null>(null);

  const stateRef = useRef({
    curTool:   "block" as Tool,
    curColor:  "#3b82f6",
    curH:      3,
    curW:      1,
    curD:      1,
    rotLocked: false,
    blockMeshes: [] as THREE.Mesh[],
    meshInfo:    new Map<THREE.Mesh, BlockInfo>(),
    penLines:    [] as THREE.Line[],
    penPts:      [] as THREE.Vector3[],
    penLine:     null as THREE.Line | null,
    penOn:       false,
    wallMeshes:   [] as THREE.Mesh[],
    wallInfo:     new Map<THREE.Mesh, WallInfo>(),
    divPanels:    [] as THREE.Mesh[],
    divPanelInfo: new Map<THREE.Mesh, DivPanelInfo>(),
    textSprites: [] as THREE.Sprite[],
    textInfo:    new Map<THREE.Sprite, TextInfo>(),
    shapeAnchor:  null as ShapeAnchor | null,
    shapePreview: null as THREE.Group | null,
    vertPlane:    null as THREE.Plane | null,
    selected:    new Set<THREE.Mesh | THREE.Line>(),
    selHelpers:  new Map<THREE.Mesh | THREE.Line, THREE.BoxHelper | true>(),
    undoStack:   [] as UndoCmd[],
    redoStack:   [] as UndoCmd[],
    pdx: 0, pdz: 0, dragged: false,
    viewMode: "3d" as "2d" | "3d",
    sheetW: 50,
    sheetD: 20,
    gridStep: 1,
    curBorderW: 3,
    curBorderR: 0,
  });

  // React state (drives re-renders)
  const [curTool,       setCurTool]       = useState<Tool>("block");
  const [curColor,      setCurColor]      = useState("#3b82f6");
  const [curH,          setCurH]          = useState(3);
  const [showTextInput, setShowTextInput] = useState(false);
  const [textInputPos,  setTextInputPos]  = useState({ x: 0, y: 0 });
  const pendingTextRef = useRef<{ wx: number; wy: number; wz: number } | null>(null);
  const [showDivInput,  setShowDivInput]  = useState(false);
  const [divEditRect,   setDivEditRect]   = useState({ x: 0, y: 0, w: 0, h: 0 });
  const pendingDivRef = useRef<{ cx: number; cz: number; rx: number; rz: number } | null>(null);
  const activeDivMeshRef = useRef<THREE.Mesh | null>(null);
  const [curW,          setCurW]          = useState(1);
  const [curD,          setCurD]          = useState(1);
  const [selCount,      setSelCount]      = useState(0);
  const [rotLocked,     setRotLocked]     = useState(false);
  const [viewMode,      setViewMode]      = useState<"2d" | "3d">("3d");
  const [gridStep,      setGridStep]      = useState(1);
  const [curBorderW,    setCurBorderW]    = useState(3);
  const [curBorderR,    setCurBorderR]    = useState(0);
  const [canUndo,       setCanUndo]       = useState(false);
  const [canRedo,       setCanRedo]       = useState(false);
  const [sheetId,       setSheetId]       = useState<string | null>(null);
  const [sheetName,     setSheetName]     = useState("Untitled Sheet");
  const [isSaving,      setIsSaving]      = useState(false);
  const sheetIdRef    = useRef<string | null>(null);
  const sheetNameRef  = useRef("Untitled Sheet");
  const saveTimerRef  = useRef<ReturnType<typeof setTimeout> | undefined>(undefined);
  const scheduleAutoSaveRef = useRef<() => void>(() => {});
  // Sheet size
  const [sheetW,        setSheetW]        = useState(20);
  const [sheetD,        setSheetD]        = useState(20);
  const [showSheetCfg,  setShowSheetCfg]  = useState(false);
  const [draftW,        setDraftW]        = useState("20");
  const [draftD,        setDraftD]        = useState("20");

  // Three.js object refs
  const ctrlRef      = useRef<InstanceType<typeof TrackballControls> | null>(null);
  const cameraRef    = useRef<THREE.PerspectiveCamera | null>(null);
  const rendererRef  = useRef<THREE.WebGLRenderer | null>(null);
  const groundRef    = useRef<THREE.Mesh | null>(null);
  const ghostRef     = useRef<THREE.Mesh | null>(null);
  const ghostMatRef  = useRef<THREE.MeshBasicMaterial | null>(null);
  const gridRef      = useRef<THREE.LineSegments | null>(null);
  const boundaryRef  = useRef<THREE.Line | null>(null);
  const centerRef    = useRef<THREE.LineSegments | null>(null);
  const sheetFloorRef = useRef<THREE.Mesh | null>(null);
  const rayRef       = useRef(new THREE.Raycaster());
  const mpRef        = useRef(new THREE.Vector2());

  // ── helpers ──────────────────────────────────────────────────────────────
  const syncUI = useCallback(() => {
    const s = stateRef.current;
    setCanUndo(s.undoStack.length > 0);
    setCanRedo(s.redoStack.length > 0);
    setSelCount(s.selected.size);
  }, []);

  const record = useCallback((cmd: UndoCmd) => {
    const s = stateRef.current;
    s.undoStack.push(cmd);
    s.redoStack.length = 0;
    syncUI();
    scheduleAutoSaveRef.current();
  }, [syncUI]);

  // ── sheet grid builder ────────────────────────────────────────────────────
  const buildGrid = useCallback((W: number, D: number) => {
    const scene = sceneRef.current;
    if (!scene) return;

    // Fixed gray grid colors — independent of accent theme
    const dark        = document.documentElement.classList.contains("dark");
    const gridColor   = dark ? 0x555555 : 0xa0a0a0;
    const centerColor = dark ? 0x6b6b6b : 0x808080;
    const boundaryColor = dark ? 0x888888 : 0x606060;

    // Dispose & remove old sheet floor
    if (sheetFloorRef.current) {
      sheetFloorRef.current.geometry.dispose();
      (sheetFloorRef.current.material as THREE.Material).dispose();
      scene.remove(sheetFloorRef.current);
      sheetFloorRef.current = null;
    }

    // Dispose & remove old grid
    if (gridRef.current) {
      gridRef.current.geometry.dispose();
      (gridRef.current.material as THREE.Material).dispose();
      scene.remove(gridRef.current);
      gridRef.current = null;
    }
    // Dispose & remove old boundary
    if (boundaryRef.current) {
      boundaryRef.current.geometry.dispose();
      (boundaryRef.current.material as THREE.Material).dispose();
      scene.remove(boundaryRef.current);
      boundaryRef.current = null;
    }

    // Dispose & remove old centre lines
    if (centerRef.current) {
      centerRef.current.geometry.dispose();
      (centerRef.current.material as THREE.Material).dispose();
      scene.remove(centerRef.current);
      centerRef.current = null;
    }

    const halfW = W / 2, halfD = D / 2;
    const step = stateRef.current.gridStep;

    // Build rectangular grid lines
    const pts: THREE.Vector3[] = [];
    for (let z = 0; z <= D; z += step) {
      pts.push(
        new THREE.Vector3(-halfW, 0, -halfD + z),
        new THREE.Vector3( halfW, 0, -halfD + z),
      );
    }
    if (D % step !== 0) {
      pts.push(new THREE.Vector3(-halfW, 0, halfD), new THREE.Vector3(halfW, 0, halfD));
    }
    for (let x = 0; x <= W; x += step) {
      pts.push(
        new THREE.Vector3(-halfW + x, 0, -halfD),
        new THREE.Vector3(-halfW + x, 0,  halfD),
      );
    }
    if (W % step !== 0) {
      pts.push(new THREE.Vector3(halfW, 0, -halfD), new THREE.Vector3(halfW, 0, halfD));
    }
    const gridGeo = new THREE.BufferGeometry().setFromPoints(pts);
    const gridMat = new THREE.LineBasicMaterial({ color: gridColor });
    const grid = new THREE.LineSegments(gridGeo, gridMat);
    scene.add(grid);
    gridRef.current = grid;

    // Centre-axis lines — full width/depth, slightly elevated, darker colour
    const cPts: THREE.Vector3[] = [
      new THREE.Vector3(-halfW, 0.012, 0),
      new THREE.Vector3( halfW, 0.012, 0),
      new THREE.Vector3(0, 0.012, -halfD),
      new THREE.Vector3(0, 0.012,  halfD),
    ];
    const centerLines = new THREE.LineSegments(
      new THREE.BufferGeometry().setFromPoints(cPts),
      new THREE.LineBasicMaterial({ color: centerColor }),
    );
    scene.add(centerLines);
    centerRef.current = centerLines;

    // Boundary frame
    const bPts = [
      new THREE.Vector3(-halfW, 0.018, -halfD),
      new THREE.Vector3( halfW, 0.018, -halfD),
      new THREE.Vector3( halfW, 0.018,  halfD),
      new THREE.Vector3(-halfW, 0.018,  halfD),
      new THREE.Vector3(-halfW, 0.018, -halfD),
    ];
    const boundary = new THREE.Line(
      new THREE.BufferGeometry().setFromPoints(bPts),
      new THREE.LineBasicMaterial({ color: boundaryColor }),
    );
    scene.add(boundary);
    boundaryRef.current = boundary;

    // Visible sheet floor — gray plane sitting just below the grid lines
    const isDark = document.documentElement.classList.contains("dark");
    const floorColor = isDark ? 0x3a3a3a : 0xd1d5db;
    const floor = new THREE.Mesh(
      new THREE.PlaneGeometry(W, D),
      new THREE.MeshBasicMaterial({ color: floorColor, side: THREE.DoubleSide }),
    );
    floor.rotation.x = -Math.PI / 2;
    floor.position.y = -0.002;
    scene.add(floor);
    sheetFloorRef.current = floor;

    // Expand camera max zoom for large sheets
    if (ctrlRef.current) {
      ctrlRef.current.maxDistance = Math.max(W, D) * 4;
    }

    stateRef.current.sheetW = W;
    stateRef.current.sheetD = D;
    setSheetW(W);
    setSheetD(D);
    setDraftW(String(W));
    setDraftD(String(D));
  }, []);

  // ── raycasting helpers ────────────────────────────────────────────────────
  const setMP = useCallback((e: PointerEvent | MouseEvent) => {
    const dom = rendererRef.current?.domElement;
    if (!dom) return;
    const r = dom.getBoundingClientRect();
    mpRef.current.x =  ((e.clientX - r.left) / r.width)  * 2 - 1;
    mpRef.current.y = -((e.clientY - r.top)  / r.height) * 2 + 1;
  }, []);

  const groundPt = useCallback((e: PointerEvent | MouseEvent) => {
    if (!cameraRef.current || !groundRef.current) return null;
    setMP(e);
    rayRef.current.setFromCamera(mpRef.current, cameraRef.current);
    const hits = rayRef.current.intersectObject(groundRef.current);
    return hits.length ? hits[0].point : null;
  }, [setMP]);

  const defaultVertPlane = useCallback(() => {
    const cam = cameraRef.current!;
    const tgt = ctrlRef.current!.target as THREE.Vector3;
    const N = new THREE.Vector3(cam.position.x - tgt.x, 0, cam.position.z - tgt.z);
    if (N.length() < 0.001) N.set(0, 0, 1);
    N.normalize();
    return new THREE.Plane(N, -N.dot(new THREE.Vector3(tgt.x, tgt.y, tgt.z)));
  }, []);

  const hitVPlane = useCallback((e: PointerEvent | MouseEvent) => {
    if (!cameraRef.current) return null;
    const s = stateRef.current;
    const plane = s.vertPlane || defaultVertPlane();
    setMP(e);
    rayRef.current.setFromCamera(mpRef.current, cameraRef.current);
    const t = new THREE.Vector3();
    return rayRef.current.ray.intersectPlane(plane, t) ? t : null;
  }, [setMP, defaultVertPlane]);

  const getPlacement = useCallback((e: PointerEvent | MouseEvent) => {
    if (!cameraRef.current || !groundRef.current) return null;
    const s = stateRef.current;
    setMP(e);
    rayRef.current.setFromCamera(mpRef.current, cameraRef.current);

    if (s.blockMeshes.length) {
      const bHits = rayRef.current.intersectObjects(s.blockMeshes);
      if (bHits.length) {
        const hit  = bHits[0];
        const info = s.meshInfo.get(hit.object as THREE.Mesh)!;
        const ny = hit.face!.normal.y;
        if (ny > 0.9)  return { gx: info.gx, gz: info.gz, bottomY: info.topY };
        if (ny < -0.9) return { gx: info.gx, gz: info.gz, bottomY: info.bottomY - s.curH };
        // Side faces — place adjacent block at the same vertical level
        const nx = hit.face!.normal.x;
        const nz = hit.face!.normal.z;
        if (nx > 0.9)  return { gx: info.gx + info.width,  gz: info.gz,             bottomY: info.bottomY };
        if (nx < -0.9) return { gx: info.gx - s.curW,      gz: info.gz,             bottomY: info.bottomY };
        if (nz > 0.9)  return { gx: info.gx,               gz: info.gz + info.depth, bottomY: info.bottomY };
        if (nz < -0.9) return { gx: info.gx,               gz: info.gz - s.curD,    bottomY: info.bottomY };
        return null;
      }
    }
    const gHits = rayRef.current.intersectObject(groundRef.current);
    if (gHits.length) {
      const pt = gHits[0].point;
      return { gx: Math.floor(pt.x), gz: Math.floor(pt.z), bottomY: 0 };
    }
    return null;
  }, [setMP]);

  // ── block helpers ─────────────────────────────────────────────────────────
  const addBlock = useCallback((m: THREE.Mesh, info: BlockInfo) => {
    sceneRef.current!.add(m);
    stateRef.current.blockMeshes.push(m);
    stateRef.current.meshInfo.set(m, info);
  }, []);

  const removeBlock = useCallback((m: THREE.Mesh) => {
    sceneRef.current!.remove(m);
    const s = stateRef.current;
    s.blockMeshes.splice(s.blockMeshes.indexOf(m), 1);
    s.meshInfo.delete(m);
  }, []);

  const addWall = useCallback((m: THREE.Mesh, info: WallInfo) => {
    sceneRef.current!.add(m);
    stateRef.current.wallMeshes.push(m);
    stateRef.current.wallInfo.set(m, info);
  }, []);

  const removeWall = useCallback((m: THREE.Mesh) => {
    sceneRef.current!.remove(m);
    const s = stateRef.current;
    s.wallMeshes.splice(s.wallMeshes.indexOf(m), 1);
    s.wallInfo.delete(m);
  }, []);

  const addDivPanel = useCallback((m: THREE.Mesh, info: DivPanelInfo) => {
    sceneRef.current!.add(m);
    stateRef.current.divPanels.push(m);
    stateRef.current.divPanelInfo.set(m, info);
  }, []);

  const removeDivPanel = useCallback((m: THREE.Mesh) => {
    sceneRef.current!.remove(m);
    const s = stateRef.current;
    s.divPanels.splice(s.divPanels.indexOf(m), 1);
    s.divPanelInfo.delete(m);
  }, []);

  const addTextSprite = useCallback((spr: THREE.Sprite, info: TextInfo) => {
    sceneRef.current!.add(spr);
    stateRef.current.textSprites.push(spr);
    stateRef.current.textInfo.set(spr, info);
  }, []);

  const removeTextSprite = useCallback((spr: THREE.Sprite) => {
    sceneRef.current!.remove(spr);
    const s = stateRef.current;
    s.textSprites.splice(s.textSprites.indexOf(spr), 1);
    s.textInfo.delete(spr);
  }, []);

  const commitText = useCallback((text: string) => {
    const anchor = pendingTextRef.current;
    if (!anchor || !text.trim()) { setShowTextInput(false); return; }
    const s = stateRef.current;
    const spr = makeTextSprite(text, s.curColor);
    spr.position.set(anchor.wx, anchor.wy, anchor.wz);
    const info: TextInfo = { ...anchor, text, color: s.curColor };
    addTextSprite(spr, info);
    record({ undo: () => removeTextSprite(spr), redo: () => addTextSprite(spr, info) });
    pendingTextRef.current = null;
    setShowTextInput(false);
  }, [addTextSprite, removeTextSprite, record]);

  const cancelText = useCallback(() => {
    pendingTextRef.current = null;
    setShowTextInput(false);
  }, []);

  const commitDiv = useCallback((text: string) => {
    const mesh = activeDivMeshRef.current;
    const pending = pendingDivRef.current;
    if (!mesh || !pending) { setShowDivInput(false); return; }
    const s = stateRef.current;
    const { rx, rz } = pending;
    if (!text.trim()) {
      removeDivPanel(mesh);
    } else {
      const mat = mesh.material as THREE.MeshLambertMaterial;
      mat.map?.dispose();
      mat.map = makeDivTexture(text, s.curColor, rx * 2, rz * 2, s.curBorderW, s.curBorderR);
      mat.needsUpdate = true;
      const info = s.divPanelInfo.get(mesh);
      if (info) { info.text = text; info.borderWidth = s.curBorderW; info.borderRadius = s.curBorderR; }
    }
    activeDivMeshRef.current = null;
    pendingDivRef.current = null;
    setShowDivInput(false);
  }, [removeDivPanel]);

  const cancelDiv = useCallback(() => {
    if (activeDivMeshRef.current) {
      removeDivPanel(activeDivMeshRef.current);
      activeDivMeshRef.current = null;
    }
    pendingDivRef.current = null;
    setShowDivInput(false);
  }, [removeDivPanel]);

  const placeBlock = useCallback((pl: { gx: number; gz: number; bottomY: number }) => {
    const s = stateRef.current;
    const { gx, gz, bottomY } = pl;
    const info: BlockInfo = { gx, gz, bottomY, height: s.curH, topY: bottomY + s.curH, width: s.curW, depth: s.curD };
    const m = new THREE.Mesh(
      new THREE.BoxGeometry(s.curW - 0.05, s.curH, s.curD - 0.05),
      new THREE.MeshLambertMaterial({ color: s.curColor }),
    );
    m.position.set(gx + s.curW / 2, bottomY + s.curH / 2, gz + s.curD / 2);
    m.castShadow = true; m.receiveShadow = true;
    addBlock(m, info);
    record({ undo: () => removeBlock(m), redo: () => addBlock(m, info) });
  }, [addBlock, removeBlock, record]);

  // ── selection helpers ─────────────────────────────────────────────────────
  const addSel = useCallback((obj: THREE.Mesh | THREE.Line) => {
    const s = stateRef.current;
    if (s.selected.has(obj)) return;
    s.selected.add(obj);
    if ((obj as THREE.Mesh).isMesh) {
      const mesh = obj as THREE.Mesh;
      const h = new THREE.BoxHelper(mesh, 0xffd700);
      sceneRef.current!.add(h);
      s.selHelpers.set(obj, h);
      (mesh.material as THREE.MeshLambertMaterial).emissive.setHex(0x443300);
    } else {
      const line = obj as THREE.Line;
      (line.material as THREE.LineBasicMaterial).color.setHex(0xffd700);
      s.selHelpers.set(obj, true);
    }
    setSelCount(s.selected.size);
  }, []);

  const removeSel = useCallback((obj: THREE.Mesh | THREE.Line) => {
    const s = stateRef.current;
    if (!s.selected.has(obj)) return;
    s.selected.delete(obj);
    if ((obj as THREE.Mesh).isMesh) {
      const h = s.selHelpers.get(obj);
      if (h && h !== true) sceneRef.current!.remove(h as THREE.BoxHelper);
      s.selHelpers.delete(obj);
      (obj as THREE.Mesh & { material: THREE.MeshLambertMaterial }).material.emissive.setHex(0);
    } else {
      const line = obj as THREE.Line;
      (line.material as THREE.LineBasicMaterial).color.set(
        (line.userData.origColor as string) || "#ffffff",
      );
      s.selHelpers.delete(obj);
    }
    setSelCount(s.selected.size);
  }, []);

  const clearSel = useCallback(() => {
    Array.from(stateRef.current.selected).forEach(removeSel);
  }, [removeSel]);

  // ── line creation ─────────────────────────────────────────────────────────
  const createPenLine = useCallback((pts: THREE.Vector3[]) => {
    const s = stateRef.current;
    const l = new THREE.Line(
      new THREE.BufferGeometry().setFromPoints(pts),
      new THREE.LineBasicMaterial({ color: s.curColor }),
    );
    sceneRef.current!.add(l);
    s.penLines.push(l);
    record({
      undo: () => { sceneRef.current!.remove(l); s.penLines.splice(s.penLines.indexOf(l), 1); },
      redo: () => { sceneRef.current!.add(l); s.penLines.push(l); },
    });
  }, [record]);

  // ── shape preview ─────────────────────────────────────────────────────────
  const clearShapePreview = useCallback(() => {
    const s = stateRef.current;
    if (!s.shapePreview) return;
    s.shapePreview.traverse((o) => {
      if ((o as THREE.Mesh).geometry) (o as THREE.Mesh).geometry.dispose();
      if ((o as THREE.Mesh).material) ((o as THREE.Mesh).material as THREE.Material).dispose();
    });
    sceneRef.current?.remove(s.shapePreview);
    s.shapePreview = null;
  }, []);

  const updateShapePreview = useCallback((e: PointerEvent | MouseEvent) => {
    const s = stateRef.current;
    if (!s.shapeAnchor) return;
    clearShapePreview();
    s.shapePreview = new THREE.Group();
    sceneRef.current!.add(s.shapePreview);

    const isVert = s.curTool === "vline" || s.curTool === "vcircle" || s.curTool === "vellipse";
    const pt = isVert ? hitVPlane(e) : groundPt(e);
    if (!pt) return;

    const anch = s.shapeAnchor;
    const aC = new THREE.Vector3(anch.wx, anch.wy, anch.wz);
    let pts: THREE.Vector3[] | null = null;

    if (s.curTool === "line") {
      pts = [new THREE.Vector3(anch.wx, 0.06, anch.wz), new THREE.Vector3(pt.x, 0.06, pt.z)];
    } else if (s.curTool === "circle") {
      const r = Math.sqrt((pt.x - anch.wx) ** 2 + (pt.z - anch.wz) ** 2);
      if (r > 0.1) pts = circlePts(anch.wx, anch.wz, r);
    } else if (s.curTool === "ellipse") {
      const rx = Math.abs(pt.x - anch.wx), rz = Math.abs(pt.z - anch.wz);
      if (rx > 0.1 && rz > 0.1) pts = ellipsePts(anch.wx, anch.wz, rx, rz);
    } else if (s.curTool === "vline") {
      pts = [aC, pt.clone()];
    } else if (s.curTool === "vcircle") {
      const r = aC.distanceTo(pt);
      if (r > 0.1) pts = vCirclePts(aC, r, s.vertPlane!.normal);
    } else if (s.curTool === "vellipse") {
      const right = planeRight(s.vertPlane!.normal);
      const diff = pt.clone().sub(aC);
      const rx = Math.abs(diff.dot(right)), ry = Math.abs(diff.y);
      if (rx > 0.1 && ry > 0.1) pts = vEllipsePts(aC, rx, ry, s.vertPlane!.normal);
    }

    if (pts) {
      s.shapePreview.add(new THREE.Line(
        new THREE.BufferGeometry().setFromPoints(pts),
        new THREE.LineBasicMaterial({ color: s.curColor }),
      ));
    }

    if (s.curTool === "wall") {
      const gPt = groundPt(e);
      if (!gPt) return;
      const dx = gPt.x - anch.wx, dz = gPt.z - anch.wz;
      const len = Math.sqrt(dx * dx + dz * dz);
      if (len < 0.1) return;
      const prev = new THREE.Mesh(
        new THREE.BoxGeometry(len, s.curH, 0.1),
        new THREE.MeshBasicMaterial({ color: s.curColor, transparent: true, opacity: 0.45, depthWrite: false }),
      );
      prev.position.set((anch.wx + gPt.x) / 2, s.curH / 2, (anch.wz + gPt.z) / 2);
      prev.rotation.y = -Math.atan2(dz, dx);
      s.shapePreview.add(prev);
    }

    if (s.curTool === "div") {
      const gPt = groundPt(e);
      if (!gPt) return;
      const rx = Math.abs(gPt.x - anch.wx);
      const rz = Math.abs(gPt.z - anch.wz);
      if (rx < 0.1 || rz < 0.1) return;
      const fill = new THREE.Mesh(
        new THREE.PlaneGeometry(rx * 2, rz * 2),
        new THREE.MeshBasicMaterial({ color: s.curColor, transparent: true, opacity: 0.2, side: THREE.DoubleSide, depthWrite: false }),
      );
      fill.rotation.x = -Math.PI / 2;
      fill.position.set(anch.wx, 0.015, anch.wz);
      const edges = new THREE.LineSegments(
        new THREE.EdgesGeometry(new THREE.BoxGeometry(rx * 2, 0.01, rz * 2)),
        new THREE.LineBasicMaterial({ color: s.curColor }),
      );
      edges.position.set(anch.wx, 0.015, anch.wz);
      s.shapePreview.add(fill);
      s.shapePreview.add(edges);
    }
  }, [clearShapePreview, groundPt, hitVPlane]);

  const finalizeShape = useCallback((e: PointerEvent | MouseEvent) => {
    const s = stateRef.current;
    const isVert = s.curTool === "vline" || s.curTool === "vcircle" || s.curTool === "vellipse";
    const pt = isVert ? hitVPlane(e) : groundPt(e);
    if (!pt) return;

    const anch = s.shapeAnchor!;
    const aC = new THREE.Vector3(anch.wx, anch.wy, anch.wz);

    if (s.curTool === "line") {
      createPenLine([new THREE.Vector3(anch.wx, 0.06, anch.wz), new THREE.Vector3(pt.x, 0.06, pt.z)]);
    } else if (s.curTool === "circle") {
      const r = Math.sqrt((pt.x - anch.wx) ** 2 + (pt.z - anch.wz) ** 2);
      if (r > 0.1) createPenLine(circlePts(anch.wx, anch.wz, r));
    } else if (s.curTool === "ellipse") {
      const rx = Math.abs(pt.x - anch.wx), rz = Math.abs(pt.z - anch.wz);
      if (rx > 0.1 && rz > 0.1) createPenLine(ellipsePts(anch.wx, anch.wz, rx, rz));
    } else if (s.curTool === "vline") {
      createPenLine([aC, pt.clone()]);
    } else if (s.curTool === "vcircle") {
      const r = aC.distanceTo(pt);
      if (r > 0.1) createPenLine(vCirclePts(aC, r, s.vertPlane!.normal));
    } else if (s.curTool === "vellipse") {
      const right = planeRight(s.vertPlane!.normal);
      const diff = pt.clone().sub(aC);
      const rx = Math.abs(diff.dot(right)), ry = Math.abs(diff.y);
      if (rx > 0.1 && ry > 0.1) createPenLine(vEllipsePts(aC, rx, ry, s.vertPlane!.normal));
    } else if (s.curTool === "wall") {
      const gPt = groundPt(e);
      if (!gPt) return;
      const dx = gPt.x - anch.wx, dz = gPt.z - anch.wz;
      const len = Math.sqrt(dx * dx + dz * dz);
      if (len < 0.1) return;
      const info: WallInfo = { x1: anch.wx, z1: anch.wz, x2: gPt.x, z2: gPt.z, bottomY: 0, height: s.curH };
      const mesh = new THREE.Mesh(
        new THREE.BoxGeometry(len, s.curH, 0.1),
        new THREE.MeshLambertMaterial({ color: s.curColor }),
      );
      mesh.position.set((anch.wx + gPt.x) / 2, s.curH / 2, (anch.wz + gPt.z) / 2);
      mesh.rotation.y = -Math.atan2(dz, dx);
      mesh.castShadow = true; mesh.receiveShadow = true;
      addWall(mesh, info);
      record({ undo: () => removeWall(mesh), redo: () => addWall(mesh, info) });
    }
  }, [createPenLine, groundPt, hitVPlane, addWall, removeWall, record]);

  // ── erase ─────────────────────────────────────────────────────────────────
  const eraseAt = useCallback((e: PointerEvent | MouseEvent) => {
    const s = stateRef.current;
    if (!cameraRef.current) return;
    setMP(e);
    rayRef.current.setFromCamera(mpRef.current, cameraRef.current);

    if (s.blockMeshes.length) {
      const bHits = rayRef.current.intersectObjects(s.blockMeshes);
      if (bHits.length) {
        const m    = bHits[0].object as THREE.Mesh;
        const info = s.meshInfo.get(m)!;
        removeBlock(m);
        record({ undo: () => addBlock(m, info), redo: () => removeBlock(m) });
        return;
      }
    }
    if (s.wallMeshes.length) {
      const dHits = rayRef.current.intersectObjects(s.wallMeshes);
      if (dHits.length) {
        const m    = dHits[0].object as THREE.Mesh;
        const info = s.wallInfo.get(m)!;
        removeWall(m);
        record({ undo: () => addWall(m, info), redo: () => removeWall(m) });
        return;
      }
    }
    if (s.divPanels.length) {
      const pHits = rayRef.current.intersectObjects(s.divPanels);
      if (pHits.length) {
        const m    = pHits[0].object as THREE.Mesh;
        const info = s.divPanelInfo.get(m)!;
        removeDivPanel(m);
        record({ undo: () => addDivPanel(m, info), redo: () => removeDivPanel(m) });
        return;
      }
    }
    if (s.textSprites.length) {
      const tHits = rayRef.current.intersectObjects(s.textSprites);
      if (tHits.length) {
        const spr  = tHits[0].object as THREE.Sprite;
        const info = s.textInfo.get(spr)!;
        removeTextSprite(spr);
        record({ undo: () => addTextSprite(spr, info), redo: () => removeTextSprite(spr) });
        return;
      }
    }
    if (s.penLines.length) {
      (rayRef.current.params as { Line?: { threshold: number } }).Line = { threshold: 0.8 };
      const lHits = rayRef.current.intersectObjects(s.penLines);
      if (lHits.length) {
        const line = lHits[0].object as THREE.Line;
        sceneRef.current!.remove(line);
        s.penLines.splice(s.penLines.indexOf(line), 1);
        record({
          undo: () => { sceneRef.current!.add(line); s.penLines.push(line); },
          redo: () => {
            sceneRef.current!.remove(line);
            const i = s.penLines.indexOf(line);
            if (i >= 0) s.penLines.splice(i, 1);
          },
        });
      }
    }
  }, [addBlock, removeBlock, addWall, removeWall, addDivPanel, removeDivPanel, addTextSprite, removeTextSprite, record, setMP]);

  // ── toolbar actions ───────────────────────────────────────────────────────
  const doTool = useCallback((t: Tool) => {
    const s = stateRef.current;
    s.curTool = t;
    s.shapeAnchor = null; clearShapePreview(); s.vertPlane = null;
    if (t !== "select") clearSel();
    ctrlRef.current!.noRotate = s.rotLocked || t === "pencil" || t === "erase" || s.viewMode === "2d";
    if (rendererRef.current) rendererRef.current.domElement.style.cursor = CURSORS[t] ?? "crosshair";
    setCurTool(t);
  }, [clearShapePreview, clearSel]);

  const doColor = useCallback((c: string) => {
    stateRef.current.curColor = c;
    if (ghostMatRef.current) ghostMatRef.current.color.set(c);
    setCurColor(c);
  }, []);

  const doHeight = useCallback((h: number) => {
    const s = stateRef.current;
    s.curH = h;
    if (ghostRef.current) {
      ghostRef.current.geometry.dispose();
      ghostRef.current.geometry = new THREE.BoxGeometry(s.curW - 0.05, h, s.curD - 0.05);
    }
    setCurH(h);
  }, []);

  const doWidth = useCallback((w: number) => {
    const s = stateRef.current;
    s.curW = w;
    if (ghostRef.current) {
      ghostRef.current.geometry.dispose();
      ghostRef.current.geometry = new THREE.BoxGeometry(w - 0.05, s.curH, s.curD - 0.05);
    }
    setCurW(w);
  }, []);

  const doDepth = useCallback((d: number) => {
    const s = stateRef.current;
    s.curD = d;
    if (ghostRef.current) {
      ghostRef.current.geometry.dispose();
      ghostRef.current.geometry = new THREE.BoxGeometry(s.curW - 0.05, s.curH, d - 0.05);
    }
    setCurD(d);
  }, []);

  function doUndo() {
    const s = stateRef.current;
    if (!s.undoStack.length) return;
    const cmd = s.undoStack.pop()!;
    cmd.undo(); s.redoStack.push(cmd);
    setCanUndo(s.undoStack.length > 0); setCanRedo(true);
  }

  function doRedo() {
    const s = stateRef.current;
    if (!s.redoStack.length) return;
    const cmd = s.redoStack.pop()!;
    cmd.redo(); s.undoStack.push(cmd);
    setCanUndo(true); setCanRedo(s.redoStack.length > 0);
  }

  const doFill = useCallback(() => {
    const s = stateRef.current;
    if (!s.selected.size) return;
    const changes: { obj: THREE.Mesh | THREE.Line; type: "mesh" | "line"; old: string; nw: string }[] = [];
    s.selected.forEach((obj) => {
      if ((obj as THREE.Mesh).isMesh) {
        const mesh = obj as THREE.Mesh & { material: THREE.MeshLambertMaterial };
        const old = "#" + mesh.material.color.getHexString();
        mesh.material.color.set(s.curColor);
        changes.push({ obj, type: "mesh", old, nw: s.curColor });
      } else {
        const old = (obj.userData.origColor as string) || "#ffffff";
        obj.userData.origColor = s.curColor;
        changes.push({ obj, type: "line", old, nw: s.curColor });
      }
    });
    if (!changes.length) return;
    record({
      undo: () => changes.forEach((c) => {
        if (c.type === "mesh") (c.obj as THREE.Mesh & { material: THREE.MeshLambertMaterial }).material.color.set(c.old);
        else if (s.selected.has(c.obj)) c.obj.userData.origColor = c.old;
        else (c.obj as THREE.Line & { material: THREE.LineBasicMaterial }).material.color.set(c.old);
      }),
      redo: () => changes.forEach((c) => {
        if (c.type === "mesh") (c.obj as THREE.Mesh & { material: THREE.MeshLambertMaterial }).material.color.set(c.nw);
        else if (s.selected.has(c.obj)) c.obj.userData.origColor = c.nw;
        else (c.obj as THREE.Line & { material: THREE.LineBasicMaterial }).material.color.set(c.nw);
      }),
    });
  }, [record]);

  const doClear = useCallback(() => {
    const s = stateRef.current;
    clearSel();
    s.blockMeshes.slice().forEach((m) => { sceneRef.current!.remove(m); m.geometry.dispose(); (m.material as THREE.Material).dispose(); });
    s.blockMeshes.length = 0; s.meshInfo.clear();
    s.wallMeshes.slice().forEach((m) => { sceneRef.current!.remove(m); m.geometry.dispose(); (m.material as THREE.Material).dispose(); });
    s.wallMeshes.length = 0; s.wallInfo.clear();
    s.divPanels.slice().forEach((m) => { sceneRef.current!.remove(m); m.geometry.dispose(); (m.material as THREE.Material).dispose(); });
    s.divPanels.length = 0; s.divPanelInfo.clear();
    s.textSprites.slice().forEach((spr) => {
      sceneRef.current!.remove(spr);
      (spr.material as THREE.SpriteMaterial).map?.dispose();
      spr.material.dispose();
    });
    s.textSprites.length = 0; s.textInfo.clear();
    s.penLines.slice().forEach((l) => { sceneRef.current!.remove(l); l.geometry.dispose(); (l.material as THREE.Material).dispose(); });
    s.penLines.length = 0;
    s.undoStack.length = 0; s.redoStack.length = 0;
    setCanUndo(false); setCanRedo(false);
  }, [clearSel]);

  const doToggleRotation = useCallback(() => {
    const s = stateRef.current;
    s.rotLocked = !s.rotLocked;
    ctrlRef.current!.noRotate = s.rotLocked || s.curTool === "pencil" || s.curTool === "erase" || s.viewMode === "2d";
    setRotLocked(s.rotLocked);
  }, []);

  const doViewMode = useCallback((mode: "2d" | "3d") => {
    const s = stateRef.current;
    s.viewMode = mode;
    setViewMode(mode);
    const ctrl = ctrlRef.current;
    const cam  = cameraRef.current;
    if (!ctrl || !cam) return;
    ctrl.reset();
    if (mode === "2d") {
      const h = Math.max(s.sheetW, s.sheetD) * 0.5 + 10;
      cam.position.set(0, h, 0.001);
      cam.up.set(0, 1, 0);
      ctrl.target.set(0, 0, 0);
      ctrl.noRotate = true;
      ctrl.maxDistance = h * 4;
      ctrl.minDistance = 1;
    } else {
      cam.position.set(14, 17, 14);
      cam.up.set(0, 1, 0);
      ctrl.target.set(0, 0, 0);
      ctrl.noRotate = s.rotLocked || s.curTool === "pencil" || s.curTool === "erase";
      ctrl.maxDistance = Math.max(s.sheetW, s.sheetD) * 4;
    }
    ctrl.update();
  }, []);

  const doGridStep = useCallback((dir: 1 | -1) => {
    const s = stateRef.current;
    const next = Math.round(Math.min(10, Math.max(0.1, s.gridStep + dir * 0.1)) * 10) / 10;
    if (next === s.gridStep) return;
    s.gridStep = next;
    setGridStep(next);
    buildGrid(s.sheetW, s.sheetD);
  }, [buildGrid]);

  const doBorderW = useCallback((v: number) => {
    stateRef.current.curBorderW = v;
    setCurBorderW(v);
  }, []);

  const doBorderR = useCallback((v: number) => {
    stateRef.current.curBorderR = v;
    setCurBorderR(v);
  }, []);

  // ── sheet persistence ─────────────────────────────────────────────────────

  const serializeScene = useCallback((): SheetElements => {
    const s = stateRef.current;
    return {
      blocks: s.blockMeshes.map(m => ({
        ...s.meshInfo.get(m)!,
        color: "#" + (m.material as THREE.MeshLambertMaterial).color.getHexString(),
      })),
      penLines: s.penLines.map(l => {
        const pos = l.geometry.attributes.position as THREE.BufferAttribute;
        const points: { x: number; y: number; z: number }[] = [];
        for (let i = 0; i < pos.count; i++)
          points.push({ x: +pos.getX(i).toFixed(4), y: +pos.getY(i).toFixed(4), z: +pos.getZ(i).toFixed(4) });
        return { color: "#" + (l.material as THREE.LineBasicMaterial).color.getHexString(), points };
      }),
      walls: s.wallMeshes.map(m => ({
        ...s.wallInfo.get(m)!,
        color: "#" + (m.material as THREE.MeshLambertMaterial).color.getHexString(),
      })),
      divPanels: s.divPanels.map(m => ({ ...s.divPanelInfo.get(m)! })),
      textSprites: s.textSprites.map(spr => ({ ...s.textInfo.get(spr)! })),
    };
  }, []);

  const performSave = useCallback(async () => {
    const s = stateRef.current;
    const elements = serializeScene();
    const payload = {
      name: sheetNameRef.current,
      sheet_w: s.sheetW,
      sheet_d: s.sheetD,
      grid_step: s.gridStep,
      elements,
    };
    try {
      setIsSaving(true);
      if (sheetIdRef.current) {
        await apiUpdateSheet(sheetIdRef.current, payload);
      } else {
        const result = await apiCreateSheet(payload);
        if (result?.id) {
          sheetIdRef.current = result.id;
          setSheetId(result.id);
          window.history.pushState({}, "", `?sheet=${result.id}`);
        }
      }
    } catch (e) {
      console.error("Sheet save failed:", e);
    } finally {
      setIsSaving(false);
    }
  }, [serializeScene]);

  useEffect(() => {
    scheduleAutoSaveRef.current = () => {
      clearTimeout(saveTimerRef.current);
      saveTimerRef.current = setTimeout(performSave, 2000);
    };
  }, [performSave]);

  const loadScene = useCallback(async (id: string) => {
    const data = await apiGetSheet(id);
    if (!data) return;

    doClear();
    buildGrid(data.sheet_w, data.sheet_d);

    const s = stateRef.current;
    const scene = sceneRef.current!;
    s.gridStep = data.grid_step;
    setGridStep(data.grid_step);

    for (const b of (data.elements.blocks ?? [])) {
      const mesh = new THREE.Mesh(
        new THREE.BoxGeometry(b.width - 0.05, b.height, b.depth - 0.05),
        new THREE.MeshLambertMaterial({ color: b.color }),
      );
      mesh.position.set(b.gx + b.width / 2, b.bottomY + b.height / 2, b.gz + b.depth / 2);
      mesh.castShadow = true; mesh.receiveShadow = true;
      scene.add(mesh);
      s.blockMeshes.push(mesh);
      s.meshInfo.set(mesh, { gx: b.gx, gz: b.gz, bottomY: b.bottomY, height: b.height, topY: b.topY, width: b.width, depth: b.depth });
    }

    for (const l of (data.elements.penLines ?? [])) {
      const pts = l.points.map((p: { x: number; y: number; z: number }) => new THREE.Vector3(p.x, p.y, p.z));
      const line = new THREE.Line(
        new THREE.BufferGeometry().setFromPoints(pts),
        new THREE.LineBasicMaterial({ color: l.color }),
      );
      scene.add(line);
      s.penLines.push(line);
    }

    for (const w of (data.elements.walls ?? [])) {
      const dx = w.x2 - w.x1, dz = w.z2 - w.z1;
      const len = Math.sqrt(dx * dx + dz * dz);
      if (len < 0.1) continue;
      const mesh = new THREE.Mesh(
        new THREE.BoxGeometry(len, w.height, 0.1),
        new THREE.MeshLambertMaterial({ color: w.color }),
      );
      mesh.position.set((w.x1 + w.x2) / 2, w.height / 2, (w.z1 + w.z2) / 2);
      mesh.rotation.y = -Math.atan2(dz, dx);
      mesh.castShadow = true; mesh.receiveShadow = true;
      scene.add(mesh);
      s.wallMeshes.push(mesh);
      s.wallInfo.set(mesh, { x1: w.x1, z1: w.z1, x2: w.x2, z2: w.z2, bottomY: w.bottomY, height: w.height });
    }

    for (const d of (data.elements.divPanels ?? [])) {
      const tex = makeDivTexture(d.text, d.color, d.rx * 2, d.rz * 2, d.borderWidth, d.borderRadius);
      const mesh = new THREE.Mesh(
        new THREE.PlaneGeometry(d.rx * 2, d.rz * 2),
        new THREE.MeshLambertMaterial({ map: tex, transparent: true, side: THREE.DoubleSide }),
      );
      mesh.rotation.x = -Math.PI / 2;
      mesh.position.set(d.cx, 0.02, d.cz);
      scene.add(mesh);
      s.divPanels.push(mesh);
      s.divPanelInfo.set(mesh, d);
    }

    for (const t of (data.elements.textSprites ?? [])) {
      const spr = makeTextSprite(t.text, t.color);
      spr.position.set(t.wx, t.wy, t.wz);
      scene.add(spr);
      s.textSprites.push(spr);
      s.textInfo.set(spr, t);
    }

    sheetIdRef.current = id;
    setSheetId(id);
    setSheetName(data.name);
    sheetNameRef.current = data.name;
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [doClear, buildGrid]);

  const doSave = useCallback(() => {
    clearTimeout(saveTimerRef.current);
    performSave();
  }, [performSave]);

  const doSetSheetName = useCallback((name: string) => {
    sheetNameRef.current = name;
    setSheetName(name);
  }, []);

  const doApplySheet = useCallback(() => {
    const w = Math.min(200, Math.max(2, parseInt(draftW) || 20));
    const d = Math.min(200, Math.max(2, parseInt(draftD) || 20));
    buildGrid(w, d);
    setShowSheetCfg(false);
  }, [buildGrid, draftW, draftD]);

  const doPrint = useCallback(() => {
    const s = stateRef.current;
    const blockData: object[] = [];
    s.meshInfo.forEach((info, mesh) => {
      blockData.push({ ...info, color: "#" + (mesh.material as THREE.MeshLambertMaterial).color.getHexString() });
    });
    const lineData = s.penLines.map((line, i) => {
      const pos = line.geometry.attributes.position as THREE.BufferAttribute;
      const pts: object[] = [];
      if (pos) for (let j = 0; j < pos.count; j++)
        pts.push({ x: +pos.getX(j).toFixed(3), y: +pos.getY(j).toFixed(3), z: +pos.getZ(j).toFixed(3) });
      return { strokeIndex: i, color: "#" + (line.material as THREE.LineBasicMaterial).color.getHexString(), points: pts };
    });
    console.group("=== 3D Plot Data ===");
    console.log(`Sheet: ${sheetW}×${sheetD}`);
    console.log(`Blocks (${blockData.length}):`, blockData);
    console.log(`Lines (${lineData.length}):`, lineData);
    console.groupEnd();
    console.log(JSON.stringify({ sheet: { w: sheetW, d: sheetD }, blocks: blockData, lines: lineData }, null, 2));
  }, [sheetW, sheetD]);

  // ── init Three.js scene ───────────────────────────────────────────────────
  useEffect(() => {
    const container = mountRef.current!;

    // Read theme colors once at mount time
    const primaryInt  = cssColorToInt("var(--primary)");
    const primaryStr  = cssColorToStr("var(--primary)");

    // Seed the draw color to the current theme primary
    stateRef.current.curColor = primaryStr;
    setCurColor(primaryStr);

    const scene = new THREE.Scene();
    scene.background = new THREE.Color(getSceneBg());
    sceneRef.current = scene;

    const camera = new THREE.PerspectiveCamera(55, container.clientWidth / container.clientHeight, 0.1, 500);
    camera.position.set(14, 17, 14);
    cameraRef.current = camera;

    const renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
    renderer.setSize(container.clientWidth, container.clientHeight);
    renderer.shadowMap.enabled = true;
    renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    renderer.domElement.style.cursor = CURSORS["block"];
    container.appendChild(renderer.domElement);
    rendererRef.current = renderer;

    const ctrl = new TrackballControls(camera, renderer.domElement) as InstanceType<typeof TrackballControls>;
    ctrl.rotateSpeed = 3.0; ctrl.zoomSpeed = 1.2; ctrl.panSpeed = 0.8;
    ctrl.staticMoving = false; ctrl.dynamicDampingFactor = 0.15;
    ctrl.minDistance = 3; ctrl.maxDistance = 80;
    ctrlRef.current = ctrl;

    scene.add(new THREE.AmbientLight(0xffffff, 0.80));
    const sun = new THREE.DirectionalLight(0xffffff, 0.90);
    sun.position.set(10, 20, 10); sun.castShadow = true;
    sun.shadow.mapSize.width = sun.shadow.mapSize.height = 2048;
    scene.add(sun);

    // Large invisible ground for raycasting (never shown)
    const ground = new THREE.Mesh(
      new THREE.PlaneGeometry(500, 500),
      new THREE.MeshBasicMaterial({ visible: false, side: THREE.DoubleSide }),
    );
    ground.rotation.x = -Math.PI / 2;
    scene.add(ground);
    groundRef.current = ground;

    const ghostMat = new THREE.MeshBasicMaterial({ color: primaryInt, transparent: true, opacity: 0.38, depthWrite: false });
    const ghost = new THREE.Mesh(new THREE.BoxGeometry(0.95, 3, 0.95), ghostMat);
    ghost.visible = false;
    scene.add(ghost);
    ghostRef.current = ghost;
    ghostMatRef.current = ghostMat;

    // Build initial 20×20 grid
    buildGrid(20, 20);

    // ── Keep Three.js colors in sync with dark/light + theme switches ────
    const syncSceneColors = () => {
      scene.background = new THREE.Color(getSceneBg());
      const isDark = document.documentElement.classList.contains("dark");
      if (gridRef.current)
        (gridRef.current.material as THREE.LineBasicMaterial).color.setHex(isDark ? 0x555555 : 0xa0a0a0);
      if (centerRef.current)
        (centerRef.current.material as THREE.LineBasicMaterial).color.setHex(isDark ? 0x6b6b6b : 0x808080);
      if (boundaryRef.current)
        (boundaryRef.current.material as THREE.LineBasicMaterial).color.setHex(isDark ? 0x888888 : 0x606060);
      if (ghostMatRef.current)
        ghostMatRef.current.color.setHex(cssColorToInt("var(--primary)"));
      if (sheetFloorRef.current) {
        const dark = document.documentElement.classList.contains("dark");
        (sheetFloorRef.current.material as THREE.MeshBasicMaterial).color.setHex(dark ? 0x3a3a3a : 0xd1d5db);
      }
    };
    const themeObserver = new MutationObserver(syncSceneColors);
    themeObserver.observe(document.documentElement, {
      attributes: true,
      attributeFilter: ["class", "data-theme"],
    });

    // Animate
    let animId: number;
    const s = stateRef.current;
    function loop() {
      animId = requestAnimationFrame(loop);
      ctrl.update();
      s.selHelpers.forEach((h) => { if (h && (h as THREE.BoxHelper).update) (h as THREE.BoxHelper).update(); });
      renderer.render(scene, camera);
    }
    loop();

    const onResize = () => {
      camera.aspect = container.clientWidth / container.clientHeight;
      camera.updateProjectionMatrix();
      renderer.setSize(container.clientWidth, container.clientHeight);
      ctrl.handleResize();
    };
    window.addEventListener("resize", onResize);

    const onKey = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key === "z") { e.preventDefault(); doUndo(); }
      if ((e.ctrlKey || e.metaKey) && (e.key === "y" || (e.shiftKey && e.key === "z"))) { e.preventDefault(); doRedo(); }
      if (e.key === "Escape") { s.shapeAnchor = null; clearShapePreview(); }
    };
    window.addEventListener("keydown", onKey);

    return () => {
      cancelAnimationFrame(animId);
      window.removeEventListener("resize", onResize);
      window.removeEventListener("keydown", onKey);
      themeObserver.disconnect();
      ctrl.dispose();
      renderer.dispose();
      container.removeChild(renderer.domElement);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // ── pointer events ────────────────────────────────────────────────────────
  useEffect(() => {
    const dom = rendererRef.current?.domElement;
    if (!dom) return;
    const s = stateRef.current;

    const onDown = (e: PointerEvent) => {
      s.pdx = e.clientX; s.pdz = e.clientY; s.dragged = false;

      if (e.button === 0) {
        if (s.curTool === "pencil") {
          const pt = groundPt(e);
          if (pt) {
            e.stopImmediatePropagation();
            s.penOn = true;
            s.penPts = [new THREE.Vector3(pt.x, 0.06, pt.z)];
            s.penLine = new THREE.Line(
              new THREE.BufferGeometry().setFromPoints(s.penPts),
              new THREE.LineBasicMaterial({ color: s.curColor }),
            );
            sceneRef.current!.add(s.penLine);
            s.penLines.push(s.penLine);
            dom.setPointerCapture(e.pointerId);
          }
        } else if (s.curTool === "erase") {
          e.stopImmediatePropagation();
          dom.setPointerCapture(e.pointerId);
          eraseAt(e);
        }
      }
    };

    const onMove = (e: PointerEvent) => {
      if (Math.abs(e.clientX - s.pdx) > 6 || Math.abs(e.clientY - s.pdz) > 6) s.dragged = true;

      if (s.penOn) e.stopImmediatePropagation();

      const isShape = ["line","circle","ellipse","vline","vcircle","vellipse","wall","div"].includes(s.curTool);

      if (s.curTool === "block" && ghostRef.current) {
        const pl = getPlacement(e);
        if (pl) { ghostRef.current.position.set(pl.gx + s.curW / 2, pl.bottomY + s.curH / 2, pl.gz + s.curD / 2); ghostRef.current.visible = true; }
        else ghostRef.current.visible = false;
      } else if (ghostRef.current) {
        ghostRef.current.visible = false;
      }

      if (isShape) updateShapePreview(e);

      if (s.curTool === "pencil" && s.penOn && s.penLine) {
        const pt = groundPt(e);
        if (pt) {
          s.penPts.push(new THREE.Vector3(pt.x, 0.06, pt.z));
          const prevGeo = s.penLine.geometry;
          s.penLine.geometry = new THREE.BufferGeometry().setFromPoints(s.penPts);
          s.penLine.geometry.computeBoundingSphere();
          prevGeo.dispose();
        }
      }
      if (s.curTool === "erase" && (e.buttons & 1)) {
        e.stopImmediatePropagation();
        eraseAt(e);
      }
    };

    const onUp = (e: PointerEvent) => {
      const wasPen   = s.penOn;
      const wasErase = s.curTool === "erase" && e.button === 0;
      if (wasPen || wasErase) e.stopImmediatePropagation();

      s.penOn = false;
      const finishedLine = s.penLine; s.penLine = null;

      if (wasPen && finishedLine) {
        const l = finishedLine;
        record({
          undo: () => { sceneRef.current!.remove(l); s.penLines.splice(s.penLines.indexOf(l), 1); },
          redo: () => { sceneRef.current!.add(l); s.penLines.push(l); },
        });
      }

      if (e.button === 2 && !s.dragged) { eraseAt(e); return; }
      if (e.button !== 0 || s.dragged || wasPen) return;

      if (s.curTool === "block") {
        const pl = getPlacement(e); if (pl) placeBlock(pl);
      } else if (s.curTool === "select") {
        setMP(e);
        rayRef.current.setFromCamera(mpRef.current, cameraRef.current!);
        let hit: THREE.Mesh | THREE.Line | null = null;
        if (s.blockMeshes.length) {
          const bh = rayRef.current.intersectObjects(s.blockMeshes);
          if (bh.length) hit = bh[0].object as THREE.Mesh;
        }
        if (!hit && s.wallMeshes.length) {
          const dh = rayRef.current.intersectObjects(s.wallMeshes);
          if (dh.length) hit = dh[0].object as THREE.Mesh;
        }
        if (!hit && s.divPanels.length) {
          const ph = rayRef.current.intersectObjects(s.divPanels);
          if (ph.length) hit = ph[0].object as THREE.Mesh;
        }
        if (!hit && s.penLines.length) {
          (rayRef.current.params as { Line?: { threshold: number } }).Line = { threshold: 0.8 };
          const lh = rayRef.current.intersectObjects(s.penLines);
          if (lh.length) hit = lh[0].object as THREE.Line;
        }
        if (!e.shiftKey) clearSel();
        if (hit) { if (s.selected.has(hit)) removeSel(hit); else addSel(hit); }
      } else if (["line","circle","ellipse"].includes(s.curTool)) {
        if (!s.shapeAnchor) {
          const pt = groundPt(e);
          if (pt) s.shapeAnchor = { wx: pt.x, wy: 0.06, wz: pt.z, gx: Math.floor(pt.x), gz: Math.floor(pt.z) };
        } else {
          finalizeShape(e); clearShapePreview(); s.shapeAnchor = null;
        }
      } else if (["vline","vcircle","vellipse"].includes(s.curTool)) {
        if (!s.shapeAnchor) {
          s.vertPlane = defaultVertPlane();
          const vpt = hitVPlane(e);
          if (vpt) s.shapeAnchor = { wx: vpt.x, wy: vpt.y, wz: vpt.z, gx: 0, gz: 0 };
        } else {
          finalizeShape(e); clearShapePreview(); s.shapeAnchor = null; s.vertPlane = null;
        }
      } else if (s.curTool === "wall") {
        if (!s.shapeAnchor) {
          const pt = groundPt(e);
          if (pt) s.shapeAnchor = { wx: pt.x, wy: 0, wz: pt.z, gx: Math.floor(pt.x), gz: Math.floor(pt.z) };
        } else {
          finalizeShape(e); clearShapePreview(); s.shapeAnchor = null;
        }
      } else if (s.curTool === "div") {
        if (!s.shapeAnchor) {
          const pt = groundPt(e);
          if (pt) s.shapeAnchor = { wx: pt.x, wy: 0, wz: pt.z, gx: Math.floor(pt.x), gz: Math.floor(pt.z) };
        } else {
          const pt = groundPt(e);
          if (pt) {
            const anch = s.shapeAnchor;
            const rx = Math.abs(pt.x - anch.wx);
            const rz = Math.abs(pt.z - anch.wz);
            const cx = anch.wx, cz = anch.wz;
            if (rx > 0.1 && rz > 0.1) {
              // Place the div immediately with empty text
              const mesh = new THREE.Mesh(
                new THREE.PlaneGeometry(rx * 2, rz * 2),
                new THREE.MeshLambertMaterial({ transparent: true, side: THREE.DoubleSide, opacity: 0.15 }),
              );
              mesh.rotation.x = -Math.PI / 2;
              mesh.position.set(cx, 0.02, cz);
              mesh.receiveShadow = true;
              const info: DivPanelInfo = { cx, cz, rx, rz, text: "", color: s.curColor, borderWidth: s.curBorderW, borderRadius: s.curBorderR };
              addDivPanel(mesh, info);
              record({ undo: () => removeDivPanel(mesh), redo: () => addDivPanel(mesh, info) });
              activeDivMeshRef.current = mesh;
              pendingDivRef.current = { cx, cz, rx, rz };
              // Compute screen-space rect from projected corners
              if (rendererRef.current && cameraRef.current) {
                const cam = cameraRef.current;
                const domRect = rendererRef.current.domElement.getBoundingClientRect();
                const corners = [
                  new THREE.Vector3(cx - rx, 0.02, cz - rz),
                  new THREE.Vector3(cx + rx, 0.02, cz - rz),
                  new THREE.Vector3(cx + rx, 0.02, cz + rz),
                  new THREE.Vector3(cx - rx, 0.02, cz + rz),
                ].map(v => { v.project(cam); return { x: (v.x * 0.5 + 0.5) * domRect.width, y: (-v.y * 0.5 + 0.5) * domRect.height }; });
                const xs = corners.map(p => p.x), ys = corners.map(p => p.y);
                setDivEditRect({ x: Math.min(...xs), y: Math.min(...ys), w: Math.max(...xs) - Math.min(...xs), h: Math.max(...ys) - Math.min(...ys) });
              }
              setShowDivInput(true);
            }
          }
          clearShapePreview();
          s.shapeAnchor = null;
        }
      } else if (s.curTool === "text") {
        const pt = groundPt(e);
        if (pt && rendererRef.current && cameraRef.current) {
          pendingTextRef.current = { wx: pt.x, wy: 0.6, wz: pt.z };
          // project world pos → canvas-relative screen pos for the overlay
          const v = new THREE.Vector3(pt.x, 0.6, pt.z).project(cameraRef.current);
          const rect = rendererRef.current.domElement.getBoundingClientRect();
          setTextInputPos({
            x: (v.x * 0.5 + 0.5) * rect.width,
            y: (-v.y * 0.5 + 0.5) * rect.height,
          });
          setShowTextInput(true);
        }
      }
    };

    const onLeave = () => {
      if (ghostRef.current) ghostRef.current.visible = false;
      s.penOn = false; s.penLine = null;
      ctrlRef.current!.enabled = true;
    };

    dom.addEventListener("pointerdown", onDown, true);
    dom.addEventListener("pointermove", onMove, true);
    dom.addEventListener("pointerup",   onUp,   true);
    dom.addEventListener("mouseleave",  onLeave);
    dom.addEventListener("contextmenu", (e) => e.preventDefault());

    return () => {
      dom.removeEventListener("pointerdown", onDown, true);
      dom.removeEventListener("pointermove", onMove, true);
      dom.removeEventListener("pointerup",   onUp,   true);
      dom.removeEventListener("mouseleave",  onLeave);
    };
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [addSel, removeSel, clearSel, eraseAt, finalizeShape, getPlacement, groundPt,
      hitVPlane, placeBlock, record, setMP, updateShapePreview, clearShapePreview, defaultVertPlane,
      addDivPanel, removeDivPanel]);

  // Load sheet from URL on mount
  useEffect(() => {
    if (initialSheetId) {
      loadScene(initialSheetId);
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return {
    mountRef,
    curTool,
    curColor,
    curH,
    showTextInput,
    textInputPos,
    commitText,
    cancelText,
    showDivInput,
    divEditRect,
    commitDiv,
    cancelDiv,
    selCount,
    rotLocked,
    viewMode,
    doViewMode,
    canUndo,
    canRedo,
    sheetW,
    sheetD,
    showSheetCfg,
    draftW,
    draftD,
    setShowSheetCfg,
    setDraftW,
    setDraftD,
    curW,
    curD,
    doTool,
    doColor,
    doHeight,
    doWidth,
    doDepth,
    doUndo,
    doRedo,
    doFill,
    doClear,
    doToggleRotation,
    doApplySheet,
    doPrint,
    buildGrid,
    gridStep,
    doGridStep,
    curBorderW,
    curBorderR,
    doBorderW,
    doBorderR,
    sheetId,
    sheetName,
    isSaving,
    doSave,
    doSetSheetName,
    loadScene,
  };
}
