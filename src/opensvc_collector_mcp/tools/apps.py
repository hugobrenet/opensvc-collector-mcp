from typing import Annotated

from fastmcp import FastMCP
from pydantic import Field

from opensvc_collector_mcp.config import TOOL_TIMEOUT_SECONDS
from opensvc_collector_mcp.core.apps import (
    count_app_nodes as core_count_app_nodes,
    count_app_services as core_count_app_services,
    count_apps as core_count_apps,
    get_app as core_get_app,
    get_app_nodes as core_get_app_nodes,
    get_app_publications as core_get_app_publications,
    get_app_responsibles as core_get_app_responsibles,
    get_app_services as core_get_app_services,
    list_app_props as core_list_app_props,
    list_apps as core_list_apps,
)
from opensvc_collector_mcp.models.apps import (
    AppGroupRelationRequest,
    AppGroupRelationResponse,
    AppNodesRequest,
    AppNodesResponse,
    AppPropsResponse,
    AppRelationCountRequest,
    AppRelationCountResponse,
    AppRowsResponse,
    AppServicesRequest,
    AppServicesResponse,
    CountAppsRequest,
    CountAppsResponse,
    GetAppRequest,
    ListAppsRequest,
)


def register_apps_tools(mcp: FastMCP) -> None:
    @mcp.tool(
        timeout=TOOL_TIMEOUT_SECONDS,
        name="list_apps",
        description=(
            "List or search OpenSVC Collector application codes using "
            "exact-match filters, Collector search, pagination, ordering, "
            "and selectable props. Defaults to a compact app inventory view."
        ),
        tags={"apps", "inventory", "read"},
        annotations={
            "title": "List OpenSVC Apps",
            "readOnlyHint": True,
            "idempotentHint": True,
            "openWorldHint": False,
        },
    )
    async def list_apps(
        request: Annotated[
            ListAppsRequest,
            Field(description="Optional app listing parameters."),
        ] = ListAppsRequest(),
    ) -> AppRowsResponse:
        """Return OpenSVC Collector apps and their selected properties."""
        response = await core_list_apps(
            filters=request.merged_filters(),
            props=request.props,
            orderby=request.orderby,
            search=request.search,
            limit=request.limit,
            offset=request.offset,
        )
        return AppRowsResponse.model_validate(response)

    @mcp.tool(
        timeout=TOOL_TIMEOUT_SECONDS,
        name="count_apps",
        description=(
            "Count OpenSVC Collector application codes matching "
            "exact-match app filters. Use this when only the number "
            "of matching apps is needed."
        ),
        tags={"apps", "inventory", "count", "read"},
        annotations={
            "title": "Count OpenSVC Apps",
            "readOnlyHint": True,
            "idempotentHint": True,
            "openWorldHint": False,
        },
    )
    async def count_apps(
        request: Annotated[
            CountAppsRequest,
            Field(description="Exact-match filters used to count Collector apps."),
        ] = CountAppsRequest(),
    ) -> CountAppsResponse:
        """Return the number of apps matching the provided filters."""
        response = await core_count_apps(
            filters=request.merged_filters(),
            search=request.search,
        )
        return CountAppsResponse.model_validate(response)

    @mcp.tool(
        timeout=TOOL_TIMEOUT_SECONDS,
        name="get_app",
        description=(
            "Return OpenSVC Collector details for one application code "
            "selected by exact app code or Collector app row id."
        ),
        tags={"apps", "inventory", "read"},
        annotations={
            "title": "Get OpenSVC App",
            "readOnlyHint": True,
            "idempotentHint": True,
            "openWorldHint": False,
        },
    )
    async def get_app(
        request: Annotated[
            GetAppRequest,
            Field(description="App selector and optional property selection."),
        ],
    ) -> AppRowsResponse:
        """Return one OpenSVC Collector app by app code or row id."""
        response = await core_get_app(
            app=request.app,
            props=request.props,
        )
        return AppRowsResponse.model_validate(response)

    @mcp.tool(
        timeout=TOOL_TIMEOUT_SECONDS,
        name="get_app_nodes",
        description=(
            "Return all OpenSVC Collector nodes attached to one app "
            "selected by exact app code or Collector app row id. The tool "
            "follows Collector pagination until complete or max_nodes is reached."
        ),
        tags={"apps", "nodes", "inventory", "read"},
        annotations={
            "title": "Get OpenSVC App Nodes",
            "readOnlyHint": True,
            "idempotentHint": True,
            "openWorldHint": False,
        },
    )
    async def get_app_nodes(
        request: Annotated[
            AppNodesRequest,
            Field(description="App selector and optional node property selection."),
        ],
    ) -> AppNodesResponse:
        """Return nodes attached to one OpenSVC Collector app."""
        response = await core_get_app_nodes(
            app=request.app,
            props=request.props,
            max_nodes=request.max_nodes,
        )
        return AppNodesResponse.model_validate(response)

    @mcp.tool(
        timeout=TOOL_TIMEOUT_SECONDS,
        name="count_app_nodes",
        description=(
            "Count OpenSVC Collector nodes attached to one app selected "
            "by exact app code or Collector app row id. This uses a "
            "lightweight Collector count read from /apps/<id>/nodes."
        ),
        tags={"apps", "nodes", "count", "read"},
        annotations={
            "title": "Count OpenSVC App Nodes",
            "readOnlyHint": True,
            "idempotentHint": True,
            "openWorldHint": False,
        },
    )
    async def count_app_nodes(
        request: Annotated[
            AppRelationCountRequest,
            Field(description="App selector used to count attached nodes."),
        ],
    ) -> AppRelationCountResponse:
        """Return the number of nodes attached to one app."""
        response = await core_count_app_nodes(app=request.app)
        return AppRelationCountResponse.model_validate(response)

    @mcp.tool(
        timeout=TOOL_TIMEOUT_SECONDS,
        name="get_app_responsibles",
        description=(
            "Return OpenSVC Collector responsible groups attached to one "
            "app selected by exact app code or Collector app row id."
        ),
        tags={"apps", "groups", "responsibles", "read"},
        annotations={
            "title": "Get OpenSVC App Responsibles",
            "readOnlyHint": True,
            "idempotentHint": True,
            "openWorldHint": False,
        },
    )
    async def get_app_responsibles(
        request: Annotated[
            AppGroupRelationRequest,
            Field(description="App selector and optional group property selection."),
        ],
    ) -> AppGroupRelationResponse:
        """Return responsible groups attached to one OpenSVC Collector app."""
        response = await core_get_app_responsibles(
            app=request.app,
            props=request.props,
            limit=request.limit,
            offset=request.offset,
        )
        return AppGroupRelationResponse.model_validate(response)

    @mcp.tool(
        timeout=TOOL_TIMEOUT_SECONDS,
        name="get_app_publications",
        description=(
            "Return OpenSVC Collector publication groups attached to one "
            "app selected by exact app code or Collector app row id."
        ),
        tags={"apps", "groups", "publications", "read"},
        annotations={
            "title": "Get OpenSVC App Publications",
            "readOnlyHint": True,
            "idempotentHint": True,
            "openWorldHint": False,
        },
    )
    async def get_app_publications(
        request: Annotated[
            AppGroupRelationRequest,
            Field(description="App selector and optional group property selection."),
        ],
    ) -> AppGroupRelationResponse:
        """Return publication groups attached to one OpenSVC Collector app."""
        response = await core_get_app_publications(
            app=request.app,
            props=request.props,
            limit=request.limit,
            offset=request.offset,
        )
        return AppGroupRelationResponse.model_validate(response)

    @mcp.tool(
        timeout=TOOL_TIMEOUT_SECONDS,
        name="get_app_services",
        description=(
            "Return all OpenSVC Collector services attached to one app "
            "selected by exact app code or Collector app row id. The tool "
            "follows Collector pagination until complete or max_services is reached."
        ),
        tags={"apps", "services", "inventory", "read"},
        annotations={
            "title": "Get OpenSVC App Services",
            "readOnlyHint": True,
            "idempotentHint": True,
            "openWorldHint": False,
        },
    )
    async def get_app_services(
        request: Annotated[
            AppServicesRequest,
            Field(description="App selector and optional service property selection."),
        ],
    ) -> AppServicesResponse:
        """Return services attached to one OpenSVC Collector app."""
        response = await core_get_app_services(
            app=request.app,
            props=request.props,
            max_services=request.max_services,
        )
        return AppServicesResponse.model_validate(response)

    @mcp.tool(
        timeout=TOOL_TIMEOUT_SECONDS,
        name="count_app_services",
        description=(
            "Count OpenSVC Collector services attached to one app selected "
            "by exact app code or Collector app row id. This uses a "
            "lightweight Collector count read from /apps/<id>/services."
        ),
        tags={"apps", "services", "count", "read"},
        annotations={
            "title": "Count OpenSVC App Services",
            "readOnlyHint": True,
            "idempotentHint": True,
            "openWorldHint": False,
        },
    )
    async def count_app_services(
        request: Annotated[
            AppRelationCountRequest,
            Field(description="App selector used to count attached services."),
        ],
    ) -> AppRelationCountResponse:
        """Return the number of services attached to one app."""
        response = await core_count_app_services(app=request.app)
        return AppRelationCountResponse.model_validate(response)

    @mcp.tool(
        timeout=TOOL_TIMEOUT_SECONDS,
        name="list_app_props",
        description=(
            "List available OpenSVC Collector app properties. "
            "Use this before list_apps to choose valid props and "
            "exact-match filter names."
        ),
        tags={"apps", "inventory", "schema", "read"},
        annotations={
            "title": "List OpenSVC App Properties",
            "readOnlyHint": True,
            "idempotentHint": True,
            "openWorldHint": False,
        },
    )
    async def list_app_props() -> AppPropsResponse:
        """Return the available app properties exposed by the Collector."""
        response = await core_list_app_props()
        return AppPropsResponse.model_validate(response)
