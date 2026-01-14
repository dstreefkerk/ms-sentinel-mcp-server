# Sentinel Logs Search Tool Documentation

## Purpose
Runs a KQL query against Azure Monitor Logs (Log Analytics workspace) and returns structured results. Supports both MCP server and direct invocation for integration testing.

---

## Parameters
| Name        | Type   | Required | Description                                                         |
|-------------|--------|----------|---------------------------------------------------------------------|
| query       | string | Yes      | The Kusto Query Language (KQL) query to run.                        |
| timespan    | string | No       | Time window for the query. Supports simple formats (e.g., '90d', '12h', '30m') and ISO 8601 duration (e.g., 'P90D', 'PT4H', 'P1DT12H'). If not provided, auto-detects from query time filters or defaults to 7 days. |

### Supported Timespan Formats

**Simple format:**
- `90d` - 90 days
- `12h` - 12 hours
- `30m` - 30 minutes

**ISO 8601 duration format:**
- `P90D` - 90 days
- `PT4H` - 4 hours
- `PT30M` - 30 minutes
- `P1DT12H` - 1 day and 12 hours
- `P7DT6H30M` - 7 days, 6 hours, and 30 minutes

---

## Output Fields
| Name               | Type     | Description                                                                                 |
|--------------------|----------|---------------------------------------------------------------------------------------------|
| valid              | bool     | True if the query ran successfully, False otherwise.                                         |
| errors             | list     | List of error messages (empty if none).                                                      |
| error              | string   | Single error message (empty if none).                                                        |
| query              | string   | The KQL query that was executed.                                                             |
| timespan           | string   | The timespan used for the query.                                                             |
| result_count       | int      | Number of rows returned.                                                                     |
| columns            | list     | List of dicts describing columns: name, type, ordinal.                                       |
| rows               | list     | List of result rows (each is a dict mapping column name to value).                           |
| execution_time_ms  | int      | Query execution time in milliseconds.                                                        |
| warnings           | list     | List of warning messages (e.g., for large result sets).                                      |
| message            | string   | Human-readable status message.                                                                |

---

## Example Request
```
{
  "query": "Heartbeat | take 5"
}
```

---

## Example Response
```
{
  "valid": true,
  "errors": [],
  "query": "Heartbeat | take 5",
  "timespan": "1d",
  "result_count": 0,
  "columns": [
    {"name": "TenantId", "type": "string", "ordinal": 0},
    {"name": "SourceSystem", "type": "string", "ordinal": 1},
    {"name": "TimeGenerated", "type": "string", "ordinal": 2},
    ...
  ],
  "rows": [],
  "execution_time_ms": 1099,
  "warnings": [],
  "message": "Query executed successfully"
}
```

---

## Usage Notes
- The tool supports any valid KQL query against the configured Log Analytics workspace.
- If no results are returned, `rows` will be an empty list but `columns` will describe the expected schema.
- If the query requests a large result set (e.g., `take 10000`), a warning will be included in `warnings`.
- **Smart timespan handling:**
  - If you provide a `timespan` parameter, it will be used as the API time window.
  - If no `timespan` is provided, the tool auto-detects time filters in your query (e.g., `ago(90d)`) and uses that with a small buffer.
  - If no time filter is detected, defaults to 7 days (conservative default to avoid expensive queries).
- For historical data analysis, either include `ago(90d)` in your query OR pass `timespan="90d"` / `timespan="P90D"`.
- The API timespan acts as an outer boundary - if your query has `where TimeGenerated >= ago(90d)` but `timespan="1d"`, you'll only get 1 day of data.
- The maximum queryable timespan depends on your workspace's data retention settings.

---

## Error Cases
| Error Message                                              | When it Occurs                                                    |
|-----------------------------------------------------------|-------------------------------------------------------------------|
| Missing required parameter: query                         | The `query` parameter was not provided.                           |
| Invalid timespan format: '<value>'                        | The `timespan` parameter was not in a valid format (e.g., '90d', 'P90D'). |
| Azure Monitor Logs client or workspace_id is not initialized. Check your credentials and configuration. | Azure credentials or workspace info missing or invalid.           |
| Query timed out after 60 seconds                          | The query did not complete within the timeout window.              |
| Error executing query: <details>                          | Any other unexpected error during query execution.                 |

---

## See Also
- [sentinel_query_validate.md](sentinel_query_validate.md)
- [Azure Monitor KQL documentation](https://docs.microsoft.com/azure/azure-monitor/logs/query-language)

---

*This documentation uses only fictional or placeholder values and never exposes real workspace or credential details.*
