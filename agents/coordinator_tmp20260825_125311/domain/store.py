from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class Store:
    country: str
    loc_cod: int
    store_name: str
    store_zone: str | None = None

    def to_dict(self) -> dict:
        return asdict(self)