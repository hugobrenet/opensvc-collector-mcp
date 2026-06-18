from pydantic import BaseModel, ConfigDict, Field, model_validator

from opensvc_collector_mcp.models.common import ToolConfirmation


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


class ConfirmedTagIdRequest(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "examples": [
                {
                    "tag_id": "TAG-ID",
                    "confirm_tag_id": "TAG-ID",
                    "confirm_tag_name": "mcp-test-tag",
                    "confirmation": {
                        "phrase": "ACTION tag TAG-ID mcp-test-tag",
                    },
                }
            ]
        },
    )

    tag_id: str = Field(
        description=(
            "Required tag execution selector. Never pass tag_name as tag_id. If "
            "the user provided only a tag_name, first call get_tag to resolve "
            "exactly one Collector tag_id, then call this tool with that resolved "
            "tag_id. This selector must match confirm_tag_id."
        ),
        min_length=1,
        examples=["TAG-ID"],
    )
    confirm_tag_id: str = Field(
        description=(
            "Correlation confirmation value read from the resolved tag snapshot. "
            "Required before executing the tool. This is not a second selector. "
            "It must match tag_id."
        ),
        min_length=1,
        examples=["TAG-ID"],
    )
    confirm_tag_name: str = Field(
        description=(
            "Correlation confirmation value read from the resolved tag snapshot. "
            "Required before executing the tool. This is not a second selector. "
            "Use this field for the tag_name that appears in the human "
            "confirmation phrase."
        ),
        min_length=1,
        examples=["mcp-test-tag"],
    )
    confirmation: ToolConfirmation = Field(
        description=(
            "Required confirmation gate for this state-changing tag tool. Before "
            "calling the tool, resolve the target tag with get_tag when the user "
            "gave a tag_name, generate a concise phrase containing the exact "
            "resolved tag_id and tag_name, ask the user to repeat it verbatim, "
            "and set this field to that full phrase only when it appears in the "
            "latest user message. The phrase must contain both values, but tag "
            "execution uses tag_id only."
        ),
    )

    @model_validator(mode="after")
    def normalize_confirmed_tag_id(self) -> "ConfirmedTagIdRequest":
        self.tag_id = self.tag_id.strip()
        self.confirm_tag_id = self.confirm_tag_id.strip()
        self.confirm_tag_name = self.confirm_tag_name.strip()
        if not self.tag_id:
            raise ValueError("tag_id must not be empty")
        if not self.confirm_tag_id:
            raise ValueError("confirm_tag_id must not be empty")
        if not self.confirm_tag_name:
            raise ValueError("confirm_tag_name must not be empty")
        if self.confirm_tag_id != self.tag_id:
            raise ValueError("confirm_tag_id must match tag_id")
        return self
