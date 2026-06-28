from fastapi import APIRouter, Request
from fastapi.responses import Response

from app.config import settings
from app.proxy import proxy

router = APIRouter(tags=["plots"])

# ── Write operations → plot-command ──────────────────────────────────────────

@router.post("", status_code=201)
async def create_plot(request: Request) -> Response:
    return await proxy(request, settings.plot_command_url, "/plots")


@router.post("/bulk", status_code=202)
async def create_plots_bulk(request: Request) -> Response:
    return await proxy(request, settings.plot_command_url, "/plots/bulk")


@router.put("/{plot_id}")
async def update_plot(plot_id: str, request: Request) -> Response:
    return await proxy(request, settings.plot_command_url, f"/plots/{plot_id}")


@router.delete("/{plot_id}")
async def delete_plot(plot_id: str, request: Request) -> Response:
    return await proxy(request, settings.plot_command_url, f"/plots/{plot_id}")


# ── Read operations → plot-query ─────────────────────────────────────────────

@router.get("")
async def list_plots(request: Request) -> Response:
    return await proxy(request, settings.plot_query_url, "/plots")


@router.get("/search")
async def search_plots(request: Request) -> Response:
    return await proxy(request, settings.plot_query_url, "/plots/search")


@router.get("/{plot_id}")
async def get_plot(plot_id: str, request: Request) -> Response:
    return await proxy(request, settings.plot_query_url, f"/plots/{plot_id}")
