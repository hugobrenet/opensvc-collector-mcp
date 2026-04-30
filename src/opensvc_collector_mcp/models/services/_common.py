from pydantic import BaseModel, ConfigDict, Field


def _is_none(value: object) -> bool:
    return value is None


class ServiceNameRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    svcname: str = Field(
        min_length=1,
        description="Exact OpenSVC Collector service name.",
        examples=["tst-lab-service"],
    )
