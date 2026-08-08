from fastapi import APIRouter, Depends, Request
from fastapi.responses import Response

from app.common.dependencies import require_permission
from app.config import settings
from app.proxy import proxy

router = APIRouter(tags=["catalog"])

# Furniture catalog is reference data managed by plot-service — reuses the
# same "sheets" permissions since it's a sub-resource of the plot domain.


@router.get("")
async def list_catalog_items(request: Request, _: None = Depends(require_permission("sheets:read"))) -> Response:
    return await proxy(request, settings.plot_command_url, "/catalog")


@router.get("/{item_id}")
async def get_catalog_item(item_id: str, request: Request, _: None = Depends(require_permission("sheets:read"))) -> Response:
    return await proxy(request, settings.plot_command_url, f"/catalog/{item_id}")


@router.post("", status_code=201)
async def create_catalog_item(request: Request, _: None = Depends(require_permission("sheets:write"))) -> Response:
    return await proxy(request, settings.plot_command_url, "/catalog")


@router.put("/{item_id}")
async def update_catalog_item(item_id: str, request: Request, _: None = Depends(require_permission("sheets:write"))) -> Response:
    return await proxy(request, settings.plot_command_url, f"/catalog/{item_id}")


@router.delete("/{item_id}")
async def delete_catalog_item(item_id: str, request: Request, _: None = Depends(require_permission("sheets:write"))) -> Response:
    return await proxy(request, settings.plot_command_url, f"/catalog/{item_id}")
