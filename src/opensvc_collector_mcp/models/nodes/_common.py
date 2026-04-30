from pydantic import BaseModel, ConfigDict, Field


class NodeNameRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    nodename: str = Field(
        min_length=1,
        description="Exact OpenSVC Collector nodename.",
        examples=["lab-node-01"],
    )
