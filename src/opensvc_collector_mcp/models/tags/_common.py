from pydantic import BaseModel, ConfigDict, Field, model_validator


class TagSelector(BaseModel):
    model_config = ConfigDict(extra="forbid")

    tag_id: str | None = Field(
        default=None,
        description="Exact Collector tag_id. Provide either tag_id or tag_name.",
        examples=["TAG-ID"],
    )
    tag_name: str | None = Field(
        default=None,
        description=(
            "Exact Collector tag_name. MCP resolves it to one tag_id and refuses "
            "ambiguous duplicate tag names. Provide either tag_id or tag_name."
        ),
        examples=["mcp-test-tag"],
    )

    @model_validator(mode="after")
    def normalize_selector(self) -> "TagSelector":
        self.tag_id = self.tag_id.strip() if self.tag_id else None
        self.tag_name = self.tag_name.strip() if self.tag_name else None
        if bool(self.tag_id) == bool(self.tag_name):
            raise ValueError("provide exactly one tag selector: tag_id or tag_name")
        return self
