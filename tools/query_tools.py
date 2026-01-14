"""
query_tools.py

Azure Monitor query tools for the MCP server.

This module provides:
- SentinelLogsSearchTool: Run KQL queries against Azure Monitor Logs.
- SentinelLogsSearchWithDummyDataTool: Test KQL queries with mock data using a datatable construct.

All tools are MCPToolBase compliant and are designed for both server and direct invocation.
"""

import re
import time
import json
from datetime import timedelta, datetime, date
from typing import List, Dict, Optional, Tuple
from mcp.server.fastmcp import Context, FastMCP
from tools.base import (
    MCPToolBase,
)  # May show import error in some test runners; see project memories
from utilities.task_manager import (
    run_in_thread,
)  # May show import error in some test runners

# pylint: disable=too-few-public-methods, too-many-return-statements, too-many-branches, too-many-locals


def parse_timespan(timespan: str) -> Tuple[Optional[timedelta], Optional[str]]:
    """
    Parse a timespan string into a timedelta object.

    Supports multiple formats:
    - Simple format: '1d', '12h', '30m', '90d'
    - ISO 8601 duration: 'P90D', 'PT4H', 'P1DT12H', 'PT30M'

    Args:
        timespan: Timespan string to parse

    Returns:
        Tuple of (timedelta object or None, error message or None)
    """
    if not timespan:
        return None, "Empty timespan provided"

    timespan = timespan.strip()

    # Try ISO 8601 duration format first (starts with 'P')
    if timespan.upper().startswith('P'):
        return _parse_iso8601_duration(timespan)

    # Try simple format (e.g., '90d', '12h', '30m')
    return _parse_simple_timespan(timespan)


def _parse_iso8601_duration(duration: str) -> Tuple[Optional[timedelta], Optional[str]]:
    """
    Parse an ISO 8601 duration string into a timedelta.

    Supports formats like:
    - P90D (90 days)
    - PT4H (4 hours)
    - PT30M (30 minutes)
    - PT45S (45 seconds)
    - P1DT12H (1 day, 12 hours)
    - P7DT6H30M (7 days, 6 hours, 30 minutes)

    Args:
        duration: ISO 8601 duration string (must start with 'P')

    Returns:
        Tuple of (timedelta object or None, error message or None)
    """
    # ISO 8601 duration regex pattern
    # P[n]Y[n]M[n]DT[n]H[n]M[n]S - we support days, hours, minutes, seconds
    pattern = r'^P(?:(\d+)D)?(?:T(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?)?$'
    match = re.match(pattern, duration.upper())

    if not match:
        # Try alternate patterns for common variations
        # PT only format (no days)
        pt_pattern = r'^PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?$'
        pt_match = re.match(pt_pattern, duration.upper())
        if pt_match:
            hours = int(pt_match.group(1)) if pt_match.group(1) else 0
            minutes = int(pt_match.group(2)) if pt_match.group(2) else 0
            seconds = int(pt_match.group(3)) if pt_match.group(3) else 0
            return timedelta(hours=hours, minutes=minutes, seconds=seconds), None

        return None, f"Invalid ISO 8601 duration format: '{duration}'. Expected format like P90D, PT4H, P1DT12H"

    days = int(match.group(1)) if match.group(1) else 0
    hours = int(match.group(2)) if match.group(2) else 0
    minutes = int(match.group(3)) if match.group(3) else 0
    seconds = int(match.group(4)) if match.group(4) else 0

    # Validate that at least one component was specified
    if days == 0 and hours == 0 and minutes == 0 and seconds == 0:
        return None, f"Invalid ISO 8601 duration: '{duration}' specifies zero duration"

    return timedelta(days=days, hours=hours, minutes=minutes, seconds=seconds), None


def _parse_simple_timespan(timespan: str) -> Tuple[Optional[timedelta], Optional[str]]:
    """
    Parse a simple timespan format into a timedelta.

    Supports formats like:
    - 90d (90 days)
    - 12h (12 hours)
    - 30m (30 minutes)

    Args:
        timespan: Simple timespan string

    Returns:
        Tuple of (timedelta object or None, error message or None)
    """
    timespan_lower = timespan.lower()

    # Match pattern: number followed by unit (d, h, m)
    match = re.match(r'^(\d+)([dhm])$', timespan_lower)
    if not match:
        return None, f"Invalid timespan format: '{timespan}'. Use formats like '90d', '12h', '30m', or ISO 8601 like 'P90D', 'PT4H'"

    value = int(match.group(1))
    unit = match.group(2)

    if value <= 0:
        return None, f"Timespan value must be positive, got: {value}"

    if unit == 'd':
        return timedelta(days=value), None
    elif unit == 'h':
        return timedelta(hours=value), None
    elif unit == 'm':
        return timedelta(minutes=value), None

    return None, f"Unknown timespan unit: '{unit}'"


def detect_query_timespan(query: str) -> Optional[int]:
    """
    Detect time-based filters in a KQL query and return the largest timespan in days.

    Looks for patterns like:
    - ago(90d), ago(30d), ago(7d)
    - ago(24h), ago(12h)
    - TimeGenerated >= datetime(...)
    - TimeGenerated > ago(...)

    Args:
        query: The KQL query string

    Returns:
        The detected timespan in days, or None if no time filter detected
    """
    max_days = None

    # Pattern 1: ago(Nd) or ago(Nh) or ago(Nm)
    ago_pattern = r'ago\s*\(\s*(\d+)\s*([dhm])\s*\)'
    for match in re.finditer(ago_pattern, query, re.IGNORECASE):
        value = int(match.group(1))
        unit = match.group(2).lower()
        days = 1  # Default

        if unit == 'd':
            days = value
        elif unit == 'h':
            days = max(1, value // 24)  # Convert hours to days, minimum 1
        elif unit == 'm':
            days = 1  # Minutes = at least 1 day

        if max_days is None or days > max_days:
            max_days = days

    # Pattern 2: startofday(ago(Nd)) or similar
    startof_pattern = r'startof\w+\s*\(\s*ago\s*\(\s*(\d+)\s*([dhm])\s*\)\s*\)'
    for match in re.finditer(startof_pattern, query, re.IGNORECASE):
        value = int(match.group(1))
        unit = match.group(2).lower()
        days = 1  # Default

        if unit == 'd':
            days = value
        elif unit == 'h':
            days = max(1, value // 24)
        elif unit == 'm':
            days = 1

        if max_days is None or days > max_days:
            max_days = days

    return max_days


class SentinelLogsSearchTool(MCPToolBase):
    """
    Tool that runs a KQL query against Azure Monitor Logs.

    Supports both server and direct invocation (integration tests).
    """

    name = "sentinel_logs_search"
    description = "Run a KQL query against Azure Monitor"

    async def run(self, ctx: Context, **kwargs):
        """
        Run a KQL query against Azure Monitor Logs.

        Args:
            ctx (Context): The MCP context.
            **kwargs: Should include 'query' and optional 'timespan'.

        Returns:
            dict: Query results and metadata, or error information.
        """
        # Extract parameters using the centralized parameter extraction from MCPToolBase
        query = self._extract_param(kwargs, "query")
        timespan = self._extract_param(kwargs, "timespan", None)  # No default - will auto-detect
        logger = self.logger
        if not query:
            logger.error("Missing required parameter: query")
            return {
                "valid": False,
                "errors": ["Missing required parameter: query"],
                "error": "Missing required parameter: query",
                "result_count": 0,
                "columns": [],
                "rows": [],
                "warnings": ["Missing required parameter: query"],
                "message": "Missing required parameter: query",
            }

        logs_client, workspace_id = self.get_logs_client_and_workspace(ctx)
        if logs_client is None or workspace_id is None:
            logger.error(
                "Azure Monitor Logs client or workspace_id is not initialized."
            )
            return {
                "valid": False,
                "errors": [
                    (
                        "Azure Monitor Logs client or workspace_id is not initialized. "
                        # noqa: E501
                        "Check your credentials and configuration."
                    )
                ],
                "error": (
                    "Azure Monitor Logs client or workspace_id is not initialized. "
                    # noqa: E501
                    "Check your credentials and configuration."
                ),
                "result_count": 0,
                "columns": [],
                "rows": [],
                "warnings": [
                    "Azure Monitor Logs client or workspace_id is not initialized."
                ],
                "message": "Azure Monitor Logs client or workspace_id is not initialized.",
            }

        start_time = time.perf_counter()
        timespan_obj = None
        try:
            if timespan:
                # User explicitly provided a timespan - parse it
                timespan_obj, parse_error = parse_timespan(timespan)
                if parse_error:
                    logger.error("Invalid timespan format: %s", parse_error)
                    return {
                        "valid": False,
                        "error": parse_error,
                        "result_count": 0,
                        "columns": [],
                        "rows": [],
                        "warnings": [parse_error],
                        "message": parse_error,
                    }
                logger.info(f"Parsed timespan '{timespan}' to {timespan_obj}")
            else:
                # No timespan provided - try to auto-detect from query
                detected_days = detect_query_timespan(query)
                if detected_days:
                    # Add a small buffer (10%) to ensure we don't miss edge data
                    buffer_days = max(1, detected_days // 10)
                    total_days = detected_days + buffer_days
                    timespan_obj = timedelta(days=total_days)
                    logger.info(
                        f"Auto-detected timespan from query: {detected_days} days "
                        f"(using {total_days} days with buffer)"
                    )
                else:
                    # No time filter in query - use conservative default of 7 days
                    # This prevents expensive queries while still providing useful data
                    timespan_obj = timedelta(days=7)
                    logger.info(
                        "No timespan provided and no time filter detected in query. "
                        "Using default of 7 days. Specify timespan or add ago() to query for longer ranges."
                    )
        except Exception as e:
            logger.error("Invalid timespan format: %s", e)
            return {
                "valid": False,
                "error": (
                    f"Invalid timespan format: {e}. Use formats like '90d', '12h', '30m', "
                    "or ISO 8601 like 'P90D', 'PT4H', 'P1DT12H'."
                ),
                "result_count": 0,
                "columns": [],
                "rows": [],
                "warnings": [f"Invalid timespan format: {e}"],
                "message": f"Invalid timespan format: {e}",
            }

        warnings = []
        match = re.search(r"\b(take|limit)\s+(\d+)", query, re.IGNORECASE)
        if match:
            n = int(match.group(2))
            if n > 250:
                warnings.append(
                    f"Large result set requested ({n} rows). "
                    "Consider using a smaller limit for better performance."
                )  # noqa: E501

        try:
            # Execute the query using task manager for async compatibility
            response = await run_in_thread(
                logs_client.query_workspace,
                workspace_id=workspace_id,
                query=query,
                timespan=timespan_obj,
                name=f"query_logs_{hash(query) % 10000}",
            )
            exec_time_ms = int((time.perf_counter() - start_time) * 1000)

            def make_json_safe(val):
                if isinstance(val, datetime):
                    return val.isoformat()
                if isinstance(val, date):
                    return val.isoformat()
                return val

            def get_col_info(col, idx):
                # Azure SDK columns may have name/type/ordinal attributes,
                # or just be strings
                return {
                    "name": getattr(col, "name", col),
                    "type": getattr(col, "type", getattr(col, "column_type", "string")),
                    "ordinal": getattr(col, "ordinal", idx),
                }

            if response and getattr(response, "tables", None):
                table = response.tables[0]
                columns = [
                    get_col_info(col, idx) for idx, col in enumerate(table.columns)
                ]
                rows = [list(row) for row in table.rows]
                dict_rows = [
                    {
                        col["name"]: make_json_safe(cell)
                        for col, cell in zip(columns, row)
                    }
                    for row in rows
                ]
                result_obj = {
                    "valid": True,
                    "errors": [],
                    "query": query,
                    "timespan": timespan,
                    "result_count": len(dict_rows),
                    "columns": columns,
                    "rows": dict_rows,
                    "execution_time_ms": exec_time_ms,
                    "warnings": warnings,
                    "message": "Query executed successfully",
                }
                return result_obj
            else:
                result_obj = {
                    "valid": True,
                    "errors": [],
                    "query": query,
                    "timespan": timespan,
                    "result_count": 0,
                    "columns": [],
                    "rows": [],
                    "execution_time_ms": int((time.perf_counter() - start_time) * 1000),
                    "warnings": warnings,
                    "message": "Query returned no tables or results",
                }
                return result_obj

        except TimeoutError:
            logger.error("Query timed out after 60 seconds")
            return {
                "valid": False,
                "errors": ["Query timed out after 60 seconds"],
                "error": "Query timed out after 60 seconds",
                "result_count": 0,
                "columns": [],
                "rows": [],
                "warnings": ["Query timed out after 60 seconds"],
                "message": "Query timed out after 60 seconds",
            }
        except Exception as e:
            logger.error("Error executing logs query: %s", str(e), exc_info=True)
            return {
                "valid": False,
                "errors": [f"Error executing query: {str(e)}"],
                "error": f"Error executing query: {str(e)}",
                "result_count": 0,
                "columns": [],
                "rows": [],
                "warnings": [f"Error executing query: {str(e)}"],
                "message": f"Error executing query: {str(e)}",
            }


class SentinelLogsSearchWithDummyDataTool(MCPToolBase):
    """
    Tool to test a KQL query against user-provided mock data using a datatable construct.

    Validates the query locally before execution. Does not touch production data, but does run
    in Azure Monitor/Sentinel for a realistic simulation.
    """

    name = "sentinel_logs_search_with_dummy_data"
    description = "Test a KQL query with mock data using a datatable. Validates KQL locally first."

    async def run(self, ctx: Context, **kwargs):
        """
        Test a KQL query against mock data using a datatable construct.

        Args:
            ctx (Context): The MCP context.
            **kwargs: Should include 'query', either 'mock_data_xml' or 'mock_data_csv', and optional 'table_name'.

        Returns:
            dict: Query results and metadata, or error information.
        """
        # Extract parameters using the centralized parameter extraction from MCPToolBase
        query = self._extract_param(kwargs, "query")
        table_name = self._extract_param(kwargs, "table_name", "TestTable")
        logger = self.logger
        
        if not query:
            logger.error("Missing required parameter: query")
            return {
                "valid": False,
                "errors": ["Missing required parameter: query"],
                "error": "Missing required parameter: query",
                "result": None,
            }
            
        # Process mock data from different formats
        mock_data = None
        
        # Option 1: XML format (preferred)
        mock_data_xml = self._extract_param(kwargs, "mock_data_xml", None)
        if mock_data_xml:
            try:
                import xml.etree.ElementTree as ET
                
                # Parse XML string
                root = ET.fromstring(mock_data_xml)
                mock_data = []
                
                # Each row is a <row> element with column elements inside
                for row_elem in root.findall('./row'):
                    row_data = {}
                    for child in row_elem:
                        tag = child.tag
                        text = child.text
                        
                        # Try to convert values to appropriate types
                        if text is not None:
                            if text.isdigit():
                                row_data[tag] = int(text)
                            elif text.replace(".", "", 1).isdigit() and text.count(".") <= 1:
                                row_data[tag] = float(text)
                            elif text.lower() == 'true':
                                row_data[tag] = True
                            elif text.lower() == 'false':
                                row_data[tag] = False
                            elif text.startswith('{') and text.endswith('}'):
                                # Try to parse as JSON for nested objects
                                try:
                                    row_data[tag] = json.loads(text)
                                except json.JSONDecodeError:
                                    row_data[tag] = text
                            else:
                                row_data[tag] = text
                        else:
                            # Handle nested structure recursively by processing child elements
                            nested_data = {}
                            for nested_child in child:
                                nested_tag = nested_child.tag
                                nested_text = nested_child.text
                                
                                if nested_text is not None:
                                    if nested_text.isdigit():
                                        nested_data[nested_tag] = int(nested_text)
                                    elif nested_text.replace(".", "", 1).isdigit() and nested_text.count(".") <= 1:
                                        nested_data[nested_tag] = float(nested_text)
                                    elif nested_text.lower() == 'true':
                                        nested_data[nested_tag] = True
                                    elif nested_text.lower() == 'false':
                                        nested_data[nested_tag] = False
                                    else:
                                        nested_data[nested_tag] = nested_text
                            
                            if nested_data:
                                row_data[tag] = nested_data
                    
                    mock_data.append(row_data)
            except Exception as e:
                logger.error("Failed to parse mock_data_xml: %s", e)
                return {
                    "valid": False,
                    "errors": ["Failed to parse mock_data_xml: %s" % str(e)],
                    "error": "Failed to parse mock_data_xml: %s" % str(e),
                    "result": None,
                }
                
        # Option 2: CSV format (alternative)
        if not mock_data:
            mock_data_csv = self._extract_param(kwargs, "mock_data_csv", None)
            if mock_data_csv:
                try:
                    import csv
                    from io import StringIO
                    
                    csv_reader = csv.DictReader(StringIO(mock_data_csv))
                    mock_data = list(csv_reader)
                    
                    # Convert numeric strings to numbers where appropriate
                    for row in mock_data:
                        for key, value in row.items():
                            if isinstance(value, str):
                                # Try to convert to int or float if possible
                                if value.isdigit():
                                    row[key] = int(value)
                                elif value.replace(".", "", 1).isdigit() and value.count(".") <= 1:
                                    row[key] = float(value)
                                elif value.lower() == 'true':
                                    row[key] = True
                                elif value.lower() == 'false':
                                    row[key] = False
                except Exception as e:
                    logger.error("Failed to parse mock_data_csv: %s", e)
                    return {
                        "valid": False, 
                        "errors": ["Failed to parse mock_data_csv: %s" % str(e)],
                        "error": "Failed to parse mock_data_csv: %s" % str(e),
                        "result": None,
                    }
        
        # If no mock data provided in any format, return helpful error
        if not mock_data:
            logger.error("Missing required mock data")
            return {
                "valid": False,
                "errors": ["Missing required mock data in a supported format (XML or CSV)"],
                "error": "Please provide mock data in one of the supported formats: mock_data_xml or mock_data_csv",
                "sample_formats": {
                    "mock_data_xml": """<rows>
    <row>
        <TimeGenerated>2023-01-01T12:00:00Z</TimeGenerated>
        <EventID>4624</EventID>
        <Computer>TestComputer</Computer>
        <Properties>
            <IpAddress>192.168.1.1</IpAddress>
            <Port>445</Port>
        </Properties>
    </row>
</rows>""",
                    "mock_data_csv": "TimeGenerated,EventID,Computer,Account\n2023-01-01T12:00:00Z,4624,TestComputer,TestUser"
                },
                "result": None,
            }
        try:
            # Import inside function to avoid circular import issues
            # Importing KQLValidateTool here to avoid circular import issues
            # noqa: E402  # pylint: disable=C0415
            from tools.kql_tools import (
                KQLValidateTool,
            )

            kql_validator = KQLValidateTool()
            validation_result = await kql_validator.run(ctx, query=query)
            if not validation_result.get("valid", False):
                logger.error(
                    "KQL validation failed: %s", validation_result.get("errors")
                )
                return {
                    "valid": False,
                    "errors": validation_result.get("errors", []),
                    "error": validation_result.get("error", "KQL validation failed."),
                    "result": None,
                }
        except Exception as e:
            logger.error("Local KQL validation error: %s", e, exc_info=True)
            return {
                "valid": False,
                "errors": ["Local KQL validation error: %s" % str(e)],
                "error": "Local KQL validation error: %s" % str(e),
                "result": None,
            }
        # Step 2: Generate datatable definition
        try:
            datatable_def, datatable_var = self._generate_datatable_and_let(
                mock_data, table_name
            )
        except Exception as e:
            logger.error("Failed to generate datatable: %s", e, exc_info=True)
            return {
                "valid": False,
                "errors": ["Failed to generate datatable: %s" % str(e)],
                "error": "Failed to generate datatable: %s" % str(e),
                "result": None,
            }
        # Step 3: Rewrite query to use datatable
        try:
            # Replace all references to the original table with the datatable variable
            # Only replace whole word matches
            rewritten_query = re.sub(
                rf"\b{re.escape(table_name)}\b", datatable_var, query
            )
            test_query = (
                f"{datatable_def}\n\n// Original query with mock data table\n"
                f"{rewritten_query}"
            )
        except Exception as e:
            logger.error("Failed to rewrite query: %s", e, exc_info=True)
            return {
                "valid": False,
                "errors": ["Failed to rewrite query: %s" % str(e)],
                "error": "Failed to rewrite query: %s" % str(e),
                "result": None,
            }
        # Step 4: Execute live query via SentinelLogsSearchTool
        try:
            # Import inside function to avoid circular import issues
            # Importing SentinelLogsSearchTool here to avoid circular import issues
            # noqa: E402  # pylint: disable=C0415
            from tools.query_tools import (
                SentinelLogsSearchTool as _SentinelLogsSearchTool,
            )

            search_tool = _SentinelLogsSearchTool()
            result = await search_tool.run(ctx, query=test_query)
            return {
                "valid": result.get("valid", False),
                "errors": result.get("errors", []),
                "error": result.get("error", ""),
                "original_query": query,
                "table_name": table_name,
                "datatable_var": datatable_var,
                "test_query": test_query,
                "result": result,
            }
        except Exception as e:
            logger.error("Live query execution failed: %s", e, exc_info=True)
            return {
                "valid": False,
                "errors": ["Live query execution failed: %s" % str(e)],
                "error": "Live query execution failed: %s" % str(e),
                "result": None,
            }

    def _generate_datatable_and_let(self, mock_data: List[Dict], table_name: str):
        """
        Generate a KQL datatable definition and let binding for mock data.

        Args:
            mock_data (list): List of dictionaries representing mock table rows.
            table_name (str): Name for the resulting table.

        Returns:
            tuple: (datatable_def, datatable_var) where datatable_def
            is the KQL definition string and datatable_var is the variable name.
        """
        if not isinstance(mock_data, list) or not mock_data:
            raise ValueError("mock_data must be a non-empty list of records")
        first = mock_data[0]

        def kql_type(val):
            """
            Infer the KQL type for a Python value.

            Args:
                val: The value to infer type for.
            Returns:
                str: KQL type string.
            """
            if isinstance(val, bool):
                return "bool"
            if isinstance(val, int):
                return "long"
            if isinstance(val, float):
                return "real"
            if isinstance(val, dict):
                return "dynamic"
            if isinstance(val, list):
                return "dynamic"
            if isinstance(val, str):
                # Try to detect ISO8601 datetime
                dt_pattern = r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}"
                if re.match(dt_pattern, val):
                    return "datetime"
                return "string"
            return "string"

        keys = list(first.keys())
        col_types = {}
        dt_pattern = r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}"
        for k in keys:
            is_datetime = False
            for row in mock_data:
                v = row.get(k)
                if isinstance(v, str) and re.match(dt_pattern, v):
                    is_datetime = True
                    break
            if is_datetime:
                col_types[k] = "datetime"
            else:
                col_types[k] = kql_type(first[k])

        columns = [(k, col_types[k]) for k in keys]
        col_defs = ",\n    ".join([f"{k}:{t}" for k, t in columns])

        def kql_repr(val, typ):
            """
            Get the KQL string representation of a value for a given type.

            Args:
                val: The value.
                typ: The KQL type.
            Returns:
                str: KQL representation.
            """
            if typ == "string":
                return f'"{str(val).replace("\"", "\\\"")}"'
            if typ == "datetime":
                # If already formatted as datetime(<val>), pass through
                if isinstance(val, str) and val.startswith("datetime("):
                    return val
                return f"datetime({val})"
            if typ == "bool":
                return "true" if val else "false"
            if typ in ("long", "real"):
                return str(val)
            if typ == "dynamic":
                return f"dynamic({json.dumps(val)})"
            return f'"{str(val)}"'

        row_strs = []
        for row in mock_data:
            row_vals = []
            for k, t in columns:
                v = row.get(k)
                if (
                    t == "datetime"
                    and isinstance(v, str)
                    and not v.startswith("datetime(")
                ):
                    row_vals.append(f"datetime({v})")
                else:
                    row_vals.append(kql_repr(v, t))
            row_strs.append(", ".join(row_vals))
        datatable_var = f"{table_name}Dummy"
        datatable_def = (
            f"let {datatable_var} = datatable(\n    {col_defs}\n) [\n    "
            + ",\n    ".join(row_strs)
            + f"\n];\nlet {table_name} = {datatable_var};"
        )
        return datatable_def, datatable_var


def register_tools(mcp: FastMCP):
    """
    Register Azure Monitor query tools with the MCP server.

    Args:
        mcp (FastMCP): The MCP server.
    """
    SentinelLogsSearchTool.register(mcp)
    SentinelLogsSearchWithDummyDataTool.register(mcp)
