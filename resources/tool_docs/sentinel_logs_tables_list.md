# Tool: sentinel_logs_tables_list

## Purpose
List available tables in the Log Analytics workspace.

## Parameters
| Name           | Type   | Required | Description                                                    |
|----------------|--------|----------|----------------------------------------------------------------|
| filter_pattern | str    | No       | Pattern to filter table names (case-insensitive substring).    |
| include_stats  | bool   | No       | Include row counts and last updated times (default: False). WARNING: Can be slow in large environments. |

## Output Fields
| Name         | Type   | Description                                                      |
|--------------|--------|------------------------------------------------------------------|
| found        | int    | Number of tables found.                                          |
| tables       | list   | List of tables. Format depends on `include_stats` parameter (see below). |
| error        | str    | Error message (optional, present if an error occurred).           |

### Table Format
- **When `include_stats=False` (default):** `[{"name": "TableName"}]`
- **When `include_stats=True`:** `[{"name": "TableName", "lastUpdated": "2025-04-22T14:53:00Z", "rowCount": 485120}]`

## Example Requests

### Simple mode (fast, default)
```json
{
  "filter_pattern": "SignIn"
}
```

### With statistics (slower)
```json
{
  "filter_pattern": "SignIn",
  "include_stats": true
}
```

## Example Responses

### Simple mode response
```json
{
  "found": 2,
  "tables": [
    { "name": "SignInLogs" },
    { "name": "SignInSummary" }
  ]
}
```

### With statistics response
```json
{
  "found": 2,
  "tables": [
    { "name": "SignInLogs", "lastUpdated": "2025-04-22T14:53:00Z", "rowCount": 485120 },
    { "name": "SignInSummary", "lastUpdated": "2025-04-22T14:50:00Z", "rowCount": 12480 }
  ]
}
```

## Usage Notes
- **Performance:** Default mode (`include_stats=False`) only lists table names and is very fast.
- **Statistics Mode:** When `include_stats=True`, the tool performs expensive queries to count rows and find last update times. This can timeout in large environments.
- Returns all tables if `filter_pattern` is not provided.
- Results are cached for performance.
- Timespan: 1 day for simple mode, 30 days for statistics mode.

## Error Cases
| Error Message                                               | Cause                                      |
|------------------------------------------------------------|--------------------------------------------|
| Azure Logs client is not initialized. Check your credentials and configuration. | Credentials or config missing/invalid       |
| No tables found.                                           | No tables exist or filter excludes all      |
| Query timed out. The workspace may have too many tables... | Query exceeded time limit (large environment) |
| KQL error: ...                                             | KQL query failed                           |
| REST API client error: ...                                 | REST API call failed                       |

## See Also
- [sentinel_logs_table_schema_get.md](sentinel_logs_table_schema_get.md)
- [sentinel_logs_table_details_get.md](sentinel_logs_table_details_get.md)
