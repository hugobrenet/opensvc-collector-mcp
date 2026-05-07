from pydantic import BaseModel, ConfigDict, Field


class UserPropsResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    count: int = Field(description="Number of user properties exposed by Collector.")
    available_props: list[str] = Field(
        description="Raw Collector user properties, including table prefixes."
    )
    user_props: list[str] = Field(
        description="User property names without the auth_user. table prefix."
    )
