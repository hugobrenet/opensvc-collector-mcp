# User Tools

This document describes the OpenSVC Collector MCP tools for user inventory.

User business logic lives under `src/opensvc_collector_mcp/core/users/`.
User Pydantic models live under `src/opensvc_collector_mcp/models/users/`.
MCP tool definitions live in `src/opensvc_collector_mcp/tools/users.py`.

## Tools

### `list_user_props`

Returns the user properties exposed by the Collector.

Use this before building generic filters for `list_users`, or before selecting
custom `props` for user rows. The raw Collector property names include the
`auth_user.` table prefix; the response also includes `user_props` without that
prefix.

Typical properties include:

```text
id
username
email
first_name
last_name
lock_filter
quota_app
quota_org_group
quota_docker_registries
```

Output fields:

```text
count
available_props
user_props
```

### `list_users`

Lists one page of OpenSVC Collector users.

By default, this tool returns a compact user inventory view and deliberately
does not include reset or registration key fields. Use `props` when the user
asks for a specific Collector user property.

This tool follows the standard Collector collection contract: `limit`, `offset`,
`orderby`, `filters`, `search`, and `props`. Use `offset` to request the next
page. It is also the user search tool: use exact-match shortcut filters such as
`username`, `email`, `first_name`, `last_name`, `lock_filter`, or generic
`filters` discovered through `list_user_props`.

Default props:

```text
id,username,email,first_name,last_name,lock_filter,quota_app,quota_org_group,quota_docker_registries
```

Example:

```json
{
  "request": {
    "filters": {
      "lock_filter": "False"
    },
    "props": "id,email,first_name,last_name,lock_filter",
    "limit": 20,
    "offset": 0,
    "orderby": "email"
  }
}
```

Output fields:

```text
meta
data
```


### `count_users`

Counts OpenSVC Collector users matching exact-match filters without returning
user rows. This uses the `/users` collection metadata and performs one GET.

Example:

```json
{
  "request": {
    "filters": {
      "lock_filter": "False"
    }
  }
}
```

Output fields:

```text
count
filters
search
```

### `get_user`

Returns one OpenSVC Collector user selected by `self`, numeric Collector user id,
exact username, or exact email address.

By default this tool performs one API GET and returns only user properties. Set
`include_primary_group` and/or `include_groups` when the caller needs relation
data. Those options add one GET each:

```text
/users/<id>/primary_group
/users/<id>/groups
```

Example:

```json
{
  "request": {
    "user": "self",
    "props": "id,username,email,first_name,last_name",
    "include_primary_group": true,
    "include_groups": true
  }
}
```

Output fields:

```text
meta
data
primary_group
groups
```



### `count_users_by_group`

Counts users who are member of the requested group role. This checks all group
memberships, not only the primary group.

This is a bounded business tool implemented only with OpenSVC Collector REST API
GET calls. It first reads `/users`, then checks `/users/<id>/groups` for each
scanned user. It does not call UI AJAX endpoints.

Example:

```json
{
  "request": {
    "group": "group_role",
    "max_users": 5000
  }
}
```

Output fields:

```text
count
group
filters
search
scanned_users
max_users
complete
collector_total
```

### `search_users_by_group`

Returns users who are member of the requested group role. This checks all group
memberships, not only the primary group.

This is a bounded business tool implemented only with OpenSVC Collector REST API
GET calls. It first reads `/users`, then checks `/users/<id>/groups` for each
scanned user. It does not call UI AJAX endpoints.

Common arguments:

- `group`: exact Collector group role, for example `group_role`.
- `filters`: optional exact-match filters applied to the initial `/users` scan.
- `props`: comma-separated user properties to include for matching users.
- `orderby`: Collector order expression used while scanning `/users`.
- `search`: Collector full-text search expression used while scanning `/users`.
- `max_users`: maximum number of users to scan before checking groups.

Example:

```json
{
  "request": {
    "group": "group_role",
    "props": "id,username,email,first_name,last_name",
    "max_users": 5000
  }
}
```

Output fields:

```text
meta
data
```


### `count_users_by_primary_group`

Counts users whose primary group role exactly matches the requested value.

This is a bounded business tool implemented only with OpenSVC Collector REST API
GET calls. It first reads `/users`, then checks `/users/<id>/primary_group` for
each scanned user. It does not call UI AJAX endpoints.

Example:

```json
{
  "request": {
    "primary_group": "group_role",
    "max_users": 5000
  }
}
```

Output fields:

```text
count
primary_group
filters
search
scanned_users
max_users
complete
collector_total
```

### `search_users_by_primary_group`

Returns users whose primary group role exactly matches the requested value.

This is a bounded business tool implemented only with OpenSVC Collector REST API
GET calls. It first reads `/users`, then checks `/users/<id>/primary_group` for
each scanned user. It does not call UI AJAX endpoints such as
`/init/users/ajax_users/data`.

Common arguments:

- `primary_group`: exact Collector group role, for example `group_role`.
- `filters`: optional exact-match filters applied to the initial `/users` scan.
- `props`: comma-separated user properties to include for matching users.
- `orderby`: Collector order expression used while scanning `/users`.
- `search`: Collector full-text search expression used while scanning `/users`.
- `max_users`: maximum number of users to scan before checking primary groups.

Example:

```json
{
  "request": {
    "primary_group": "opensvc_primary_group",
    "props": "id,username,email,first_name,last_name",
    "max_users": 5000
  }
}
```

Output fields:

```text
meta
data
```
