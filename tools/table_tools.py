"""
FILE: tools/table_tools.py

This module provides tools for working with Log Analytics tables in Azure Sentinel MCP.
It includes utilities to list tables, fetch schema information, and retrieve table metadata.
"""

from datetime import timedelta

from tools.base import Context, MCPToolBase
from utilities.cache import cache
from utilities.task_manager import run_in_thread


class ListTablesTool(MCPToolBase):
    """
    Tool to list available tables in the Log Analytics workspace.

    Parameters:
        filter_pattern (str, optional): Pattern to filter table names
        include_stats (bool, optional): Include row counts and last updated times (default: False)
                                       WARNING: Setting to True can be slow in large environments

    Returns:
        dict: {
            'found': int,            # Number of tables found
            'tables': list,          # List of table metadata dicts
                                    # If include_stats=False: [{'name': str}]
                                    # If include_stats=True: [{'name': str, 'lastUpdated': str, 'rowCount': int}]
            'error': str (optional)  # Error message if applicable
        }
    """

    name = "sentinel_logs_tables_list"
    description = "List available tables in the Log Analytics workspace"

    async def run(self, ctx: Context, **kwargs):
        """
        List available tables in the Log Analytics workspace.

        Args:
            ctx (Context): The MCP tool context.
            **kwargs: Optional filter_pattern to filter table names.
                     Optional include_stats (bool) to include row counts and last updated times.

        Returns:
            dict: Results as described in the class docstring.
        """
        filter_pattern = self._extract_param(kwargs, "filter_pattern", "")
        include_stats = self._extract_param(kwargs, "include_stats", False)

        logs_client, workspace_id = self.get_logs_client_and_workspace(ctx)
        cache_key = f"tables_json:{workspace_id}:{filter_pattern}:{include_stats}"
        cached = cache.get(cache_key)
        if cached:
            return cached
        if logs_client is None:
            result = {
                "error": (
                    "Azure Logs client is not initialized. "
                    "Check your credentials and configuration."
                )
            }
            cache.set(cache_key, result)
            return result
        try:
            # Simple query for table names only (fast)
            if not include_stats:
                kql_table_names = (
                    "search *\n"
                    "| distinct $table\n"
                    "| project TableName = $table\n"
                    "| order by TableName asc"
                )
                if filter_pattern:
                    kql_table_names = (
                        "search *\n"
                        "| distinct $table\n"
                        "| project TableName = $table\n"
                        f'| where TableName contains "{filter_pattern}"\n'
                        "| order by TableName asc"
                    )
                query = kql_table_names
                timespan = timedelta(days=1)  # Minimal timespan for fast query
            else:
                # Full query with stats (expensive)
                kql_table_info = (
                    "search *\n"
                    "| distinct $table\n"
                    "| extend TableName = $table\n"
                    "| project-away $table\n"
                    "| join kind=leftouter (\n"
                    "    union withsource=TableSource *\n"
                    "    | summarize LastUpdate=max(TimeGenerated),\n"
                    "      RowCount=count() by TableSource\n"
                    "    | project TableSource, LastUpdate, RowCount\n"
                    ") on $left.TableName == $right.TableSource\n"
                    "| project name=TableName, lastUpdated=LastUpdate, "
                    "rowCount=RowCount\n"
                    "| order by name asc"
                )
                if filter_pattern:
                    kql_table_info = (
                        "search *\n"
                        "| distinct $table\n"
                        "| extend TableName = $table\n"
                        "| project-away $table\n"
                        "| join kind=leftouter (\n"
                        "    union withsource=TableSource *\n"
                        "    | summarize LastUpdate=max(TimeGenerated),\n"
                        "      RowCount=count() by TableSource\n"
                        "    | project TableSource, LastUpdate, RowCount\n"
                        ") on $left.TableName == $right.TableSource\n"
                        "| project name=TableName, lastUpdated=LastUpdate, "
                        "rowCount=RowCount\n"
                        f'| where name contains "{filter_pattern}"\n'
                        "| order by name asc"
                    )
                query = kql_table_info
                timespan = timedelta(days=30)  # Reduced from 90 days for better performance

            response = await run_in_thread(
                logs_client.query_workspace,
                workspace_id=workspace_id,
                query=query,
                timespan=timespan,
                name="list_tables_info" if include_stats else "list_table_names",
            )
            if response and response.tables and len(response.tables[0].rows) > 0:
                tables = []
                for row in response.tables[0].rows:
                    if not include_stats:
                        # Simple mode: only table names
                        table = {"name": row[0]}
                    else:
                        # Full mode: include stats
                        table = {"name": row[0], "lastUpdated": row[1], "rowCount": row[2]}
                    tables.append(table)
                result = {"found": len(tables), "tables": tables}
                cache.set(cache_key, result)
                return result
            result = {
                "found": 0,
                "tables": [],
                "error": (
                    "No tables found. The workspace may be empty "
                    "or you may not have access to the data."
                ),
            }
            cache.set(cache_key, result)
            return result
        except TimeoutError:
            error_msg = (
                "Query timed out. The workspace may have too many tables or too much data. "
                "Try using include_stats=False for faster results, or use a filter_pattern to reduce the scope."
            )
            result = {"error": error_msg}
            self.logger.error("Query timeout in list tables: %s", error_msg)
            cache.set(cache_key, result)
            return result
        except Exception as e:
            result = {"error": "Failed to list tables: %s" % str(e)}
            self.logger.error("Failed to list tables: %s", str(e))
            cache.set(cache_key, result)
            return result


class GetTableSchemaTool(MCPToolBase):
    """
    Tool to get schema (columns/types) for a Log Analytics table.

    Returns:
        dict: {
            'table': str,            # Table name
            'schema': list,          # List of schema column metadata
            'error': str (optional)  # Error message if applicable
        }
    """

    name = "sentinel_logs_table_schema_get"
    description = "Get schema (columns/types) for a Log Analytics table"

    async def run(self, ctx: Context, **kwargs):
        """
        Get the schema (columns/types) for a Log Analytics table.

        Args:
            ctx (Context): The MCP tool context.
            **kwargs: Must include 'table_name'.

        Returns:
            dict: Results as described in the class docstring.
        """
        table_name = self._extract_param(kwargs, "table_name")
        if not table_name:
            return {"error": "Missing required parameter: table_name"}
        logs_client, workspace_id = self.get_logs_client_and_workspace(ctx)
        cache_key = f"table_schema_json:{workspace_id}:{table_name}"
        cached = cache.get(cache_key)
        if cached:
            return cached
        if logs_client is None:
            result = {
                "error": (
                    "Azure Logs client is not initialized. "
                    "Check your credentials and configuration."
                )
            }
            cache.set(cache_key, result)
            return result
        try:
            kql_schema = f"{table_name} | getschema"
            response = await run_in_thread(
                logs_client.query_workspace,
                workspace_id=workspace_id,
                query=kql_schema,
                timespan=timedelta(days=1),
                name="get_table_schema",
            )
            schema = []
            if response and response.tables and len(response.tables[0].rows) > 0:
                columns = response.tables[0].columns
                rows = response.tables[0].rows
                # Try to find the canonical getschema columns
                col_name_idx = col_type_idx = col_data_type_idx = col_ordinal_idx = None

                # Determine if columns are strings or objects
                def col_name(col):
                    """Return column name as lowercase string."""
                    return col.lower() if isinstance(col, str) else col.name.lower()

                for idx, col in enumerate(columns):
                    cname = col_name(col)
                    if cname == "columnname":
                        col_name_idx = idx
                    elif cname == "columntype":
                        col_type_idx = idx
                    elif cname == "datatype":
                        col_data_type_idx = idx
                    elif cname == "columnordinal":
                        col_ordinal_idx = idx
                if col_name_idx is not None and col_type_idx is not None:
                    # Return all metadata if available
                    for row in rows:
                        entry = {"name": row[col_name_idx], "type": row[col_type_idx]}
                        if col_data_type_idx is not None:
                            entry["dataType"] = row[col_data_type_idx]
                        if col_ordinal_idx is not None:
                            entry["ordinal"] = row[col_ordinal_idx]
                        schema.append(entry)
                else:
                    # Fallback: return all columns for each row
                    for row in rows:
                        schema.append(
                            {col.name: row[i] for i, col in enumerate(columns)}
                        )
                result = {"table": table_name, "schema": schema}
                cache.set(cache_key, result)
                return result
            result = {
                "table": table_name,
                "schema": [],
                "error": f"No schema found for table {table_name}.",
            }
            cache.set(cache_key, result)
            return result
        except Exception as e:
            result = {"error": "Failed to get table schema: %s" % str(e)}
            self.logger.error("Failed to get table schema: %s", str(e))
            cache.set(cache_key, result)
            return result


class GetTableDetailsTool(MCPToolBase):
    """
    Tool to get details (metadata, retention, row count, etc.) for a Log Analytics table.

    Returns:
        dict: {
            'table': str,            # Table name
            ...fields...,            # Various metadata fields
            'error': str (optional)  # Error message if applicable
        }
    """

    name = "sentinel_logs_table_details_get"
    description = (
        "Get details (metadata, retention, row count, etc.) for a Log Analytics table"
    )

    async def run(self, ctx: Context, **kwargs):
        """
        Get details (metadata, retention, row count, etc.) for a Log Analytics table.

        Args:
            ctx (Context): The MCP tool context.
            **kwargs: Must include 'table_name'.

        Returns:
            dict: Results as described in the class docstring.
        """
        table_name = self._extract_param(kwargs, "table_name")
        if not table_name:
            return {"error": "Missing required parameter: table_name"}
        logs_client, workspace_id = self.get_logs_client_and_workspace(ctx)
        cache_key = f"table_details_json:{workspace_id}:{table_name}"
        cached = cache.get(cache_key)
        if cached:
            return cached
        # Get Azure context
        resource_group = None
        workspace_name = None
        subscription_id = None
        if (
            hasattr(ctx, "request_context")
            and getattr(ctx, "request_context", None) is not None
        ):
            services_ctx = ctx.request_context.lifespan_context
            logs_client = getattr(services_ctx, "logs_client", None)
            workspace_id = getattr(services_ctx, "workspace_id", None)
            # We no longer need rest_client as we're using direct API calls
            resource_group = getattr(services_ctx, "resource_group", None)
            workspace_name = getattr(services_ctx, "workspace_name", None)
            subscription_id = getattr(services_ctx, "subscription_id", None)
        errors = []
        result = {"table": table_name}
        # --- REST API METADATA ---
        try:
            if resource_group and workspace_name and subscription_id:
                # We'll use the call_api method directly, no need to get the client separately

                # Construct the URL with API version 2017-04-26-preview as recommended
                # pylint: disable=line-too-long
                # ruff: noqa: E501
                url = (
                    f"https://management.azure.com/subscriptions/{subscription_id}/"
                    f"resourceGroups/{resource_group}/providers/Microsoft.OperationalInsights/"
                    f"workspaces/{workspace_name}/tables/{table_name}?api-version=2017-04-26-preview"
                )

                # Make the direct REST API call using the task manager
                try:
                    # Use the call_api method from the base class
                    table_data = await self.call_api(
                        ctx, "GET", url, name=f"get_table_details_{table_name}"
                    )

                    # Process the response
                    if table_data and "properties" in table_data:
                        props = table_data["properties"]

                        # Extract metadata properties (camelCase format from API)
                        result["retentionInDays"] = props.get("retentionInDays")
                        result["totalRetentionInDays"] = props.get(
                            "totalRetentionInDays"
                        )
                        if (
                            props.get("totalRetentionInDays") is not None
                            and props.get("retentionInDays") is not None
                        ):
                            result["archiveRetentionInDays"] = (
                                props["totalRetentionInDays"] - props["retentionInDays"]
                            )
                        else:
                            result["archiveRetentionInDays"] = None

                        # Extract other metadata fields
                        result["plan"] = props.get("plan")
                        result["provisioningState"] = props.get("provisioningState")

                        # Extract schema-related properties if available
                        if "schema" in props:
                            schema = props["schema"]
                            result["tableType"] = schema.get("tableType")
                            result["description"] = schema.get("description")
                        else:
                            result["tableType"] = props.get("tableType")
                            result["description"] = props.get("description")

                        # Extract other properties
                        result["isInherited"] = props.get("isInherited")
                        result["isTotalRetentionInherited"] = props.get(
                            "isTotalRetentionInherited"
                        )
                        self.logger.info(
                            "Successfully retrieved metadata for table: %s", table_name
                        )
                    else:
                        errors.append(
                            "REST API: No properties found in table metadata response."
                        )
                        self.logger.error(
                            "No properties found in table metadata response for: %s",
                            table_name,
                        )

                except StopIteration:
                    # Handle case where no data is returned
                    errors.append("REST API: No data returned for table metadata.")
                    self.logger.error(
                        "No data returned for table metadata: %s", table_name
                    )
                except Exception as e:
                    errors.append("REST API call error: %s" % str(e))
                    self.logger.error(
                        "Error during REST API call for table %s: %s", table_name, e
                    )
            else:
                errors.append(
                    "REST API: Missing required parameters for table metadata retrieval."
                )
                self.logger.error(
                    "Missing required parameters: resource_group=%s, workspace_name=%s, subscription_id=%s",
                    resource_group,
                    workspace_name,
                    subscription_id,
                )
        except Exception as e:
            errors.append("REST API client error: %s" % str(e))
        # --- KQL METADATA ---
        if logs_client:
            # Query for lastUpdated
            try:
                kql_last_updated = (
                    f"{table_name}\n| summarize lastUpdated=max(TimeGenerated)"
                )
                last_updated_resp = await run_in_thread(
                    logs_client.query_workspace,
                    workspace_id=workspace_id,
                    query=kql_last_updated,
                    timespan=timedelta(days=30),
                    name="get_table_last_updated",
                )
                if (
                    last_updated_resp
                    and last_updated_resp.tables
                    and len(last_updated_resp.tables[0].rows) > 0
                ):
                    row = last_updated_resp.tables[0].rows[0]
                    result["lastUpdated"] = row[0]
                else:
                    result["lastUpdated"] = None
            except TimeoutError:
                errors.append(
                    "KQL timeout: lastUpdated query exceeded time limit (30 days)"
                )
                result["lastUpdated"] = None
            except Exception as e:
                errors.append(f"KQL error (lastUpdated): {str(e)}")
                result["lastUpdated"] = None
            # Query for rowCount
            try:
                kql_row_count = f"{table_name}\n| count"
                row_count_resp = await run_in_thread(
                    logs_client.query_workspace,
                    workspace_id=workspace_id,
                    query=kql_row_count,
                    timespan=timedelta(days=30),
                    name="get_table_row_count",
                )
                if (
                    row_count_resp
                    and row_count_resp.tables
                    and len(row_count_resp.tables[0].rows) > 0
                ):
                    row = row_count_resp.tables[0].rows[0]
                    result["rowCount"] = row[0]
                else:
                    result["rowCount"] = 0
            except TimeoutError:
                errors.append(
                    "KQL timeout: rowCount query exceeded time limit (30 days)"
                )
                result["rowCount"] = 0
            except Exception as e:
                errors.append(f"KQL error (rowCount): {str(e)}")
                result["rowCount"] = 0
        else:
            errors.append("logs_client missing.")
        if errors:
            result["errors"] = errors
        return result


def register_tools(mcp):
    """
    Register all table tools with the given MCP instance.

    Args:
        mcp: The MCP instance to register tools with.
    """
    ListTablesTool.register(mcp)
    GetTableSchemaTool.register(mcp)
    GetTableDetailsTool.register(mcp)
