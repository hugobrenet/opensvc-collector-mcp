from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator


def _is_none(value: object) -> bool:
    return value is None


class UserFilterRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    filters: dict[str, str] = Field(
        default_factory=dict,
        description=(
            "Exact-match user property filters. Keys must be Collector user "
            "properties returned by list_user_props."
        ),
        examples=[{"email": "user@example.com", "lock_filter": "False"}],
    )
    username: str | None = Field(default=None, description="Exact login username.")
    email: str | None = Field(default=None, description="Exact user email address.")
    first_name: str | None = Field(default=None, description="Exact user first name.")
    last_name: str | None = Field(default=None, description="Exact user last name.")
    lock_filter: str | None = Field(
        default=None,
        description="Exact Collector lock_filter value for the user.",
    )

    @model_validator(mode="after")
    def normalize_filters(self) -> "UserFilterRequest":
        self.filters = {
            key.strip(): value.strip()
            for key, value in self.filters.items()
            if key.strip() and value.strip()
        }
        return self

    def merged_filters(self) -> dict[str, str]:
        merged = dict(self.filters)
        for field in (
            "username",
            "email",
            "first_name",
            "last_name",
            "lock_filter",
        ):
            value = getattr(self, field)
            if value is None:
                continue
            value = value.strip()
            if not value:
                continue
            existing = merged.get(field)
            if existing is not None and existing != value:
                raise ValueError(f"Conflicting filter values for {field!r}")
            merged[field] = value
        return merged


class UserCollectionRequest(UserFilterRequest):
    props: str | None = Field(
        default=None,
        description=(
            "Comma-separated user properties to include in the response. "
            "Defaults to a compact user inventory view that excludes reset keys."
        ),
    )
    orderby: str | None = Field(
        default=None,
        description="Collector orderby expression, for example email or ~id.",
    )
    search: str | None = Field(
        default=None,
        description="Collector full-text search expression when supported by /users.",
    )
    limit: int = Field(
        default=20,
        ge=1,
        le=1000,
        description="Maximum number of users to return.",
    )
    offset: int = Field(
        default=0,
        ge=0,
        description="Number of matching users to skip.",
    )


class ListUsersRequest(UserCollectionRequest):
    pass


class UsersByPrimaryGroupRequest(UserFilterRequest):
    primary_group: str = Field(
        min_length=1,
        description="Exact Collector group role used as the user primary group.",
        examples=["GAPP_OPENSVC_ADMIN"],
    )
    props: str | None = Field(
        default=None,
        description=(
            "Comma-separated user properties to include for matching users. "
            "The id property is always included internally for primary group lookup."
        ),
    )
    orderby: str | None = Field(
        default=None,
        description="Collector orderby expression used while scanning /users.",
    )
    search: str | None = Field(
        default=None,
        description="Collector full-text search expression used while scanning /users.",
    )
    max_users: int = Field(
        default=5000,
        ge=1,
        le=50000,
        description=(
            "Maximum number of users to scan from /users before checking "
            "/users/<id>/primary_group for each user."
        ),
    )


class UserPropsResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    count: int = Field(description="Number of user properties exposed by Collector.")
    available_props: list[str] = Field(
        description="Raw Collector user properties, including table prefixes."
    )
    user_props: list[str] = Field(
        description="User property names without the auth_user. table prefix."
    )


class UserRow(BaseModel):
    model_config = ConfigDict(extra="allow")

    id: int | None = Field(
        default=None,
        description="Collector internal user row id.",
        exclude_if=_is_none,
    )
    username: str | None = Field(
        default=None,
        description="Collector login username.",
        exclude_if=_is_none,
    )
    email: str | None = Field(
        default=None,
        description="User email address.",
        exclude_if=_is_none,
    )
    first_name: str | None = Field(
        default=None,
        description="User first name.",
        exclude_if=_is_none,
    )
    last_name: str | None = Field(
        default=None,
        description="User last name.",
        exclude_if=_is_none,
    )
    lock_filter: bool | str | None = Field(
        default=None,
        description="Collector lock_filter value for the user.",
        exclude_if=_is_none,
    )
    quota_app: int | None = Field(
        default=None,
        description="User application quota as exposed by Collector.",
        exclude_if=_is_none,
    )
    quota_org_group: int | None = Field(
        default=None,
        description="User organisation group quota as exposed by Collector.",
        exclude_if=_is_none,
    )
    quota_docker_registries: int | None = Field(
        default=None,
        description="User Docker registry quota as exposed by Collector.",
        exclude_if=_is_none,
    )


class UserRowsResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    meta: dict[str, Any] = Field(default_factory=dict)
    data: list[UserRow]


class UserPrimaryGroupRow(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: int | str | None = Field(
        default=None,
        description="Collector group id.",
        exclude_if=_is_none,
    )
    role: str | None = Field(
        default=None,
        description="Collector group role/name.",
        exclude_if=_is_none,
    )
    description: str | None = Field(
        default=None,
        description="Collector group description.",
        exclude_if=_is_none,
    )
    privilege: bool | None = Field(
        default=None,
        description="Whether the group is privileged.",
        exclude_if=_is_none,
    )


class UserByPrimaryGroupRow(UserRow):
    primary_group: UserPrimaryGroupRow = Field(
        description="Primary group row returned by /users/<id>/primary_group."
    )


class UsersByPrimaryGroupResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    meta: dict[str, Any] = Field(default_factory=dict)
    data: list[UserByPrimaryGroupRow]
