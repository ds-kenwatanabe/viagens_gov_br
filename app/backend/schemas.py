from datetime import date
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel
from pydantic import Field


RankingDimension = Literal["beneficiarios", "orgaos", "cargos", "ugs"]


class FilterParams(BaseModel):
    orgao: list[str] = Field(default_factory=list)
    orgao_nome: str | None = None
    beneficiario: str | None = None
    cargo: str | None = None
    motivo_contem: str | None = None
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
    id: int | None = None
    orgao_nome: str | None = None
    beneficiario_nome: str | None = None
    motivo: str | None = None
    tipo_viagem: str | None = None
    data_inicio_afastamento: date | None = None
    data_fim_afastamento: date | None = None
    cidade: str | None
    estado: str | None
    pais: str | None
    latitude: float
    longitude: float
    quantidade: int
    valor_total: Decimal
    confidence: float | None = None


class TripDetail(BaseModel):
    id: int
    orgao_nome: str | None = None
    beneficiario_nome: str | None = None
    cargo_descricao: str | None = None
    tipo_viagem: str | None = None
    motivo: str | None = None
    data_inicio_afastamento: date | None = None
    data_fim_afastamento: date | None = None
    valor_total_viagem: Decimal
    valor_total_diarias: Decimal | None = None
    valor_total_passagem: Decimal | None = None


class TripLocation(BaseModel):
    local_texto: str | None = None
    cidade: str | None = None
    estado: str | None = None
    pais: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    confidence: float | None = None
    fonte: str | None = None


class DistributionRow(BaseModel):
    nome: str
    quantidade: int
    valor_medio: Decimal


class OutlierRow(BaseModel):
    nome: str
    quantidade: int | None = None
    valor_total: Decimal | None = None
    valor_medio: Decimal | None = None
    detalhe: str | None = None


class QualitySummary(BaseModel):
    total_viagens: int
    motivo_vazio: int
    sem_local_extraido: int
    geocodificadas: int
    confianca_media: float | None = None


class SourceCount(BaseModel):
    fonte: str
    quantidade: int


class QualityReport(BaseModel):
    summary: QualitySummary
    fontes: list[SourceCount]
    motivos_sem_local: list[RankingRow]
