# Pagination

Raw collection tools return exactly one Collector page per MCP call. The LLM or
harness decides whether the user request needs another page.

## Response contract

Paginated responses expose `pagination` and `data`, plus an object selector such
as `app`, `array`, `svcname`, or `tag_id` when relevant:

```json
{
  "pagination": {
    "limit": 20,
    "offset": 0,
    "returned": 20,
    "next_offset": 20,
    "complete": false,
    "truncated": false
  },
  "data": []
}
```

- `limit` and `offset` describe the requested page.
- `returned` is the number of rows in this page.
- `next_offset` is the exact offset for the next call, or `null` when complete.
- `complete=true` means this call proved that no later row exists.
- `truncated` is always `false` for a raw one-page call. It is reserved for
  bounded internal business scans.

Collector collection metadata is deliberately disabled with `meta=false` for
these calls. Property discovery and exact counts have dedicated tools, so raw
`meta.available_props` and `meta.total` do not need to be repeated on every
page.

## Client loop

To read more rows:

1. Call the collection tool with a suitable fixed `limit` and `offset=0`.
2. Process `data`.
3. If `pagination.complete` is `false`, call the same tool again with
   `offset=pagination.next_offset`.
4. Keep `limit`, filters, search, props, and ordering unchanged.
5. Stop when `complete=true` or `next_offset=null`.

Do not increase `limit` on each iteration. A full page is not proof that the
collection is complete: when the result count is an exact multiple of `limit`,
one final empty page may be needed to prove completion.

When only a count is requested, use the domain `count_*` tool. When one object
is requested, use its detail tool instead of scanning all pages.

## Dynamic property discovery

Do not guess how a business phrase maps to Collector data. Each main domain
provides a property-discovery tool such as `list_node_props`,
`list_service_props`, or `list_app_props`.

For a request such as “list the physical production nodes”, a robust agent can:

1. call `list_node_props` to discover candidate fields;
2. use a compact sample or `get_nodes_inventory_stats` to inspect relevant
   values when needed;
3. map “physical” to the observed `type=physical` value and discover the actual
   environment field/value used by that Collector;
4. call `list_nodes` with those exact filters and a stable ordering;
5. follow `next_offset` until the user request is satisfied or the collection
   is complete.

This keeps the mapping dynamic across Collector installations without relying
on a static RAG dictionary that may drift from the infrastructure.
