from typing import Annotated

from fastapi import Depends
from fastapi import FastAPI
from fastapi import Query
from fastapi.middleware.cors import CORSMiddleware

from app.backend.db import close_pool
from app.backend.queries import get_filter_options
from app.backend.queries import get_cargo_distribution
from app.backend.queries import get_kpis
from app.backend.queries import get_map_points
from app.backend.queries import get_org_comparison
from app.backend.queries import get_outliers
from app.backend.queries import get_quality_report
from app.backend.queries import get_ranking
from app.backend.queries import search_filter_options
from app.backend.queries import get_time_series
from app.backend.queries import get_trip_details
from app.backend.schemas import DistributionRow
from app.backend.schemas import FilterOptions
from app.backend.schemas import FilterParams
from app.backend.schemas import KpiSummary
from app.backend.schemas import MapPoint
from app.backend.schemas import OutlierRow
from app.backend.schemas import Option
from app.backend.schemas import QualityReport
from app.backend.schemas import RankingDimension
from app.backend.schemas import RankingRow
from app.backend.schemas import TimeSeriesPoint
from app.backend.schemas import TripDetail


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
    motivo_contem: str | None = None,
    motivo_contem_alias: Annotated[str | None, Query(alias="motivo_contém")] = None,
    tipo_viagem: str | None = None,
    data_inicio: str | None = None,
    data_fim: str | None = None,
) -> FilterParams:
    return FilterParams(
        orgao=orgao or [],
        beneficiario=beneficiario,
        cargo=cargo,
        motivo_contem=motivo_contem or motivo_contem_alias,
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


@app.get("/filters/{kind}", response_model=list[Option])
def filter_search(
    kind: str,
    search: str = "",
    limit: int = Query(default=80, ge=1, le=200),
) -> list[dict]:
    if kind not in {"beneficiarios", "cargos"}:
        return []
    return search_filter_options(kind, search, limit)


@app.get("/kpis", response_model=KpiSummary)
def kpis(filters: FilterParams = Depends(parse_filters)) -> dict:
    return get_kpis(filters)


@app.get("/rankings/{dimension}", response_model=list[RankingRow])
def rankings(
    dimension: RankingDimension,
    limit: int = Query(default=20, ge=1, le=100),
    order_by: str = Query(default="valor", pattern="^(valor|quantidade)$"),
    filters: FilterParams = Depends(parse_filters),
) -> list[dict]:
    return get_ranking(dimension, filters, limit, order_by)


@app.get("/comparison/orgaos", response_model=list[RankingRow])
def org_comparison(filters: FilterParams = Depends(parse_filters)) -> list[dict]:
    return get_org_comparison(filters)


@app.get("/timeseries", response_model=list[TimeSeriesPoint])
def timeseries(filters: FilterParams = Depends(parse_filters)) -> list[dict]:
    return get_time_series(filters)


@app.get("/map", response_model=list[MapPoint])
def map_points(
    map_mode: str = Query(default="clusters", pattern="^(points|clusters)$"),
    limit: int = Query(default=1000, ge=1, le=5000),
    filters: FilterParams = Depends(parse_filters),
) -> list[dict]:
    return get_map_points(filters, map_mode, limit)


@app.get("/trips", response_model=list[TripDetail])
def trips(
    limit: int = Query(default=100, ge=1, le=500),
    filters: FilterParams = Depends(parse_filters),
) -> list[dict]:
    return get_trip_details(filters, limit)


@app.get("/distribution/cargos", response_model=list[DistributionRow])
def cargo_distribution(
    limit: int = Query(default=30, ge=1, le=100),
    filters: FilterParams = Depends(parse_filters),
) -> list[dict]:
    return get_cargo_distribution(filters, limit)


@app.get("/outliers/{kind}", response_model=list[OutlierRow])
def outliers(
    kind: str,
    limit: int = Query(default=30, ge=1, le=100),
    filters: FilterParams = Depends(parse_filters),
) -> list[dict]:
    return get_outliers(filters, kind, limit)


@app.get("/quality", response_model=QualityReport)
def quality(
    limit: int = Query(default=20, ge=1, le=100),
    filters: FilterParams = Depends(parse_filters),
) -> dict:
    return get_quality_report(filters, limit)
