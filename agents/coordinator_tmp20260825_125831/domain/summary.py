from dataclasses import asdict, dataclass
from datetime import date


@dataclass(frozen=True)
class MetricSummary:
    count: int
    percentage: float


@dataclass(frozen=True)
class DailySummary:
    country: str
    date: date
    total: int

    en_gondola: MetricSummary
    bodega: MetricSummary
    quiebre: MetricSummary

    def to_dict(self) -> dict:
        result = asdict(self)
        result["date"] = self.date.isoformat()
        return result