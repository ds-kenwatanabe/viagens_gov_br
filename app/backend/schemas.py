from datetime import date
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel
from pydantic import Field


RankingDimension = Literal["beneficiarios", "orgaos", "cargos", "ugs"]


class FilterParams(BaseModel):
    orgao: list[str] = Field(default_factory=list)
    beneficiario: str | None = None
    cargo: str | None = None
    tipo_viagem: str | None = None
    data_inicio: date | None = None
    data_fim: date | None = None


class Option(BaseModel):
    value: str
    label: str


class FilterOptions(BaseModel):
    orgaos: list[Option]
    beneficiarios: list[Option]
    cargos: list[Option]
    tipos_viagem: list[Option]


class KpiSummary(BaseModel):
    valor_total: Decimal
    valor_diarias: Decimal
    valor_passagens: Decimal
    numero_viagens: int
    ticket_medio: Decimal


class RankingRow(BaseModel):
    nome: str
    quantidade: int
    valor_total: Decimal


class TimeSeriesPoint(BaseModel):
    periodo: date
    quantidade: int
    valor_total: Decimal


class MapPoint(BaseModel):
    cidade: str | None
    estado: str | None
    pais: str | None
    latitude: float
    longitude: float
    quantidade: int
    valor_total: Decimal
    confidence: float | None = None
