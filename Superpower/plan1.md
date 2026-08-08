# Pass 1 — Furniture Catalog + 3D Placement

## Context

The "plot" feature is currently a generic 3-D CAD editor (`services/plot-service` + `frontend/src/app/plot`): blocks, walls, pen-lines, labeled zones, and text sprites, all stored as one JSONB blob per plot row (`plot_unified.plots.elements`). To move this toward an actual interior-design tool, the first concrete capability needed is a **furniture catalog** that users can browse and place into the 3-D scene — everything else on the roadmap (rooms, materials, budget, AI layout) builds on having real furniture items instead of anonymous colored boxes.

Decisions already made with the user:
- Catalog lives inside the existing `plot-service` (not a new microservice) — reuses its DB, auth, and CQRS-lite plumbing.
- For this pass, placed furniture renders as **parametric boxes** sized to the catalog item's real-world dimensions + a text label (matches the existing `blocks` element exactly) — no GLTF asset pipeline yet.
- Placement uses **click-to-place**, matching every other tool in the editor (block/wall/div/text all work this way) — not drag-and-drop, which would require new UX and a new dependency (`dnd-kit`) inconsistent with the rest of the app.
- All new React code follows the user's standing convention: `memo` for pure list items, `useCallback` for handlers, `useTransition` for non-urgent UI updates (search filtering), `Suspense` for data fetching — matching this codebase's existing heavy use of `useCallback` throughout `_use-plot-scene.ts`.
- Catalog read/write is gated behind the existing `sheets:read` / `sheets:write` permissions (no new RBAC permission added) — catalog is a sub-resource of the plot/sheet domain, and anyone who can edit plots can browse/manage it.

## Backend — `services/plot-service`

New sibling module `app/catalog/`, mirroring the existing `app/plots/` structure (`models`, `schemas/request`, `schemas/response`, `commands`, `queries`, `routers`):

- **`app/catalog/models/catalog_models.py`** — `FurnitureCatalogItem(Base)`, table `plot_unified.furniture_catalog`: `name` (str), `category` (str, e.g. "seating", "tables", "storage", "bedroom"), `width`/`height`/`depth` (float, same units as `sheet_w`/`grid_step`), `default_color` (str hex), `price` (float, nullable), `description` (str, nullable). Inherits `id`/`created_at`/`updated_at`/`is_deleted` from `Base` (see `app/database.py`).
- **Migration** `services/plot-service/alembic/versions/0002_furniture_catalog.py` (follows `0001_initial_plot_tables.py`'s style) — creates the table and seeds ~10 starter items (sofa, armchair, dining table, dining chair, queen bed, wardrobe, bookshelf, coffee table, TV unit, kitchen island) with sensible dimensions/colors/prices, so the catalog panel isn't empty on first load.
- **Schemas**: `app/catalog/schemas/request/catalog_commands.py` (`CreateCatalogItemCommand`, `UpdateCatalogItemCommand`), `app/catalog/schemas/response/catalog_schemas.py` (`CatalogItem`, `CatalogListResponse`) — same shape as `plot_schemas.py`.
- **Queries** `app/catalog/queries/handlers.py`: `list_catalog_items(db, category=None, q=None, limit, offset)`, `get_catalog_item(id, db)` — plain SQLAlchemy, no Kafka involved (reference data, no read/write split needed).
- **Commands** `app/catalog/commands/handlers.py`: `handle_create_item`, `handle_update_item`, `handle_delete_item` (soft delete) — direct DB writes, **no Kafka event publishing** (unlike plots, this is low-frequency admin data, not a per-user event stream — avoids unnecessary complexity).
- **Router** `app/catalog/routers/catalog_router.py`: `GET /catalog`, `GET /catalog/{id}`, `POST /catalog`, `PUT /catalog/{id}`, `DELETE /catalog/{id}`. Same `X-User-ID` header dependency pattern as `plot_router.py` (auth presence check only — catalog rows aren't user-scoped).
- **`app/main.py`**: register the new router, add a `"catalog"` tag entry.

## Gateway — `services/api-gateway`

- New `app/routers/catalog.py`, mirroring `app/routers/plot.py`'s `proxy()` pattern, all routes proxying to `settings.plot_command_url` (same plot-service instance):
  - `GET/POST /` → `require_permission("sheets:read"/"sheets:write")`
  - `GET/PUT/DELETE /{item_id}` → same permission split
- **`app/main.py`**: `app.include_router(catalog.router, prefix="/api/v1/catalog", tags=["catalog"])`.

## Frontend — data layer

- New `frontend/src/lib/services/plot-catalog.ts` (`"use server"`), mirroring `plot-sheets.ts`: `CatalogItem` type + `apiListCatalogItems(params?)` using `cqrsFetch` against `/api/v1/catalog`.
- `plot-sheets.ts`: extend `SheetElements` with `furniturePlacements: SerializedFurniturePlacement[]`.

## Frontend — types & constants

- `_types.ts`: add `FurnitureInfo` (`id`, `catalogItemId`, `name`, `gx`, `gz`, `bottomY`, `rotationY`, `width`, `height`, `depth`, `color`) and add `"furniture"` to the `Tool` union.
- `_constants.ts`: add a `furniture` cursor to `CURSORS` and a tip string to `TIP_MAP` (both required — `TIP_MAP` is typed `Record<Tool, string>` so this is enforced by the compiler).

## Frontend — scene hook (`_use-plot-scene.ts`)

Following the exact pattern already used for blocks/walls/divs/text sprites in this file:
- `stateRef`: add `furnitureMeshes: THREE.Mesh[]` + `furnitureInfo: Map<THREE.Mesh, FurnitureInfo>`.
- `selectedCatalogItem` as `useState` + `doSelectCatalogItem` (`useCallback`) — the "armed" catalog item; selecting one also switches `curTool` to `"furniture"`.
- `addFurniture`/`removeFurniture` (`useCallback`, mirrors `addBlock`/`removeBlock` at lines 391-402).
- `placeFurniture(pl, item)` (`useCallback`, mirrors `placeBlock` at line 491): builds a `BoxGeometry(item.width, item.height, item.depth)` + `MeshLambertMaterial({color: item.default_color})`, adds a `makeTextSprite(item.name, ...)` label above it, positions via the grid placement (`gx`/`gz`/`bottomY`), registers undo/redo via `record()`.
- Pointer-up dispatch (~line 1314, alongside the existing `if (s.curTool === "block")` branch): add `else if (s.curTool === "furniture" && s.selectedCatalogItem) { const pl = getPlacement(e); if (pl) placeFurniture(pl, s.selectedCatalogItem); }`.
- `serializeScene()` (line 934): add `furniturePlacements: s.furnitureMeshes.map(m => ({...s.furnitureInfo.get(m)!}))`.
- `loadScene()` (line 993): reconstruct furniture meshes from `data.elements.furniturePlacements ?? []`, same loop style as the existing block/wall reconstruction.
- Hook return value: expose `catalogItems`/`selectedCatalogItem`/`doSelectCatalogItem` (the promise itself is threaded through from the page, not fetched inside the hook — see below).

## Frontend — Suspense-based catalog panel

- `app/plot/page.tsx` (Server Component): call `apiListCatalogItems()` **without awaiting**, pass the resulting `Promise<CatalogItem[]>` down as a `catalogPromise` prop to `<PlotCanvas>`.
- New `catalog-panel.tsx` (client component):
  - `CatalogPanel` wraps `<Suspense fallback={<CatalogPanelSkeleton />}>` around `<CatalogList promise={catalogPromise} .../>`.
  - `CatalogList` calls React's `use(promise)` to unwrap the data (suspends the boundary until it resolves — no client-side fetch, no new query library needed).
  - The search/filter input uses `useTransition`: `startTransition(() => setQuery(v))`, so typing while the 3-D canvas is rendering doesn't block interaction.
  - Each row renders via a `React.memo`-wrapped `CatalogItemCard`, receiving a `useCallback`-stable `onSelect` handler.
- `plot-canvas.tsx`: render `<CatalogPanel catalogPromise={catalogPromise} onSelect={scene.doSelectCatalogItem} selectedId={scene.selectedCatalogItem?.id} />` alongside the existing `SidePanel`.
- `side-panel.tsx`: add a toggle button (reusing the existing `Btn` component) to show/hide the catalog panel, and a small indicator for the currently-armed item.

## Verification

1. Start the dev stack (`docker compose -f docker-compose.dev.yml up -d` / `make dev`) and confirm `plot-service` runs its migration on boot (`_run_migrations` in `app/main.py`'s lifespan) — check `plot_unified.furniture_catalog` exists and has ~10 seeded rows via pgAdmin or `docker compose exec postgres psql`.
2. Call `GET http://localhost:8000/api/v1/catalog` (through the gateway, authenticated) → expect the seeded items back.
3. In the browser at `/plot`: open the catalog panel, type in the filter (confirm the 3-D view stays responsive — `useTransition` working), click an item (tool switches to "furniture"), click on the grid → a labeled box appears at the correct size/position.
4. Confirm undo (`◀ Back`) removes the placed furniture and redo brings it back.
5. Confirm autosave persists it — reload the page with `?sheet=<id>` and verify the furniture reappears (round-trips through `serializeScene`/`loadScene` and the backend `elements` JSONB).
