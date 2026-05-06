from typing import Annotated

from fastapi import Depends
from fastapi import FastAPI
from fastapi import Query
from fastapi.middleware.cors import CORSMiddleware

from app.backend.db import close_pool
from app.backend.queries import get_filter_options
from app.backend.queries import get_kpis
from app.backend.queries import get_map_points
from app.backend.queries import get_ranking
from app.backend.queries import get_time_series
from app.backend.schemas import FilterOptions
from app.backend.schemas import FilterParams
from app.backend.schemas import KpiSummary
from app.backend.schemas import MapPoint
from app.backend.schemas import RankingDimension
from app.backend.schemas import RankingRow
from app.backend.schemas import TimeSeriesPoint


app = FastAPI(title="Viagens Gov BR Dashboard API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def parse_filters(
    orgao: Annotated[list[str] | None, Query()] = None,
    beneficiario: str | None = None,
    cargo: str | None = None,
    tipo_viagem: str | None = None,
    data_inicio: str | None = None,
    data_fim: str | None = None,
) -> FilterParams:
    return FilterParams(
        orgao=orgao or [],
        beneficiario=beneficiario,
        cargo=cargo,
        tipo_viagem=tipo_viagem,
        data_inicio=data_inicio,
        data_fim=data_fim,
    )


@app.on_event("shutdown")
def shutdown() -> None:
    close_pool()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/filters", response_model=FilterOptions)
def filters() -> dict:
    return get_filter_options()


@app.get("/kpis", response_model=KpiSummary)
def kpis(filters: FilterParams = Depends(parse_filters)) -> dict:
    return get_kpis(filters)


@app.get("/rankings/{dimension}", response_model=list[RankingRow])
def rankings(
    dimension: RankingDimension,
    limit: int = Query(default=20, ge=1, le=100),
    filters: FilterParams = Depends(parse_filters),
) -> list[dict]:
    return get_ranking(dimension, filters, limit)


@app.get("/timeseries", response_model=list[TimeSeriesPoint])
def timeseries(filters: FilterParams = Depends(parse_filters)) -> list[dict]:
    return get_time_series(filters)


@app.get("/map", response_model=list[MapPoint])
def map_points(filters: FilterParams = Depends(parse_filters)) -> list[dict]:
    return get_map_points(filters)
