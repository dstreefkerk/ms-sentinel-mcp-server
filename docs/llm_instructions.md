# Microsoft Sentinel MCP Server Instructions

This server provides access to Microsoft Sentinel workspaces, data, and functionality through the Model Context Protocol.

## Essential Workflow

1. **Documentation First**: Before using any tool, retrieve and review its documentation using:
   - `tool_docs_list` - See all available documentation
   - `tool_docs_get` - Get specific documentation by path
   - `tool_docs_search` - Search across documentation

2. **Tool Usage**: After understanding the tool, use it with proper parameters

3. **Formatting Results**: Use markdown templates when available:
   - `markdown_templates_list` - Discover available templates
   - `markdown_template_get` - Retrieve specific template content
   - Templates are named after their associated tools (e.g., `sentinel_incident_get.md`)

## Detailed Workflow Examples

### 1. Security Incident Investigation
```
Step 1: Get incident details
→ sentinel_incident_details_get(incident_id="12345")

Step 2: Analyze related data  
→ sentinel_logs_search(query="SecurityEvent | where TimeGenerated > ago(1h)")

Step 3: Check detection rules
→ sentinel_analytics_rule_get(rule_id="rule-guid")

Step 4: Format findings
→ markdown_template_get(path="sentinel_incident_get.md")
```

### 2. Threat Hunting Workflow
```
Step 1: Explore available hunting queries
→ sentinel_hunting_queries_list()

Step 2: Get specific query details
→ sentinel_hunting_query_get(query_name="Suspicious PowerShell")

Step 3: Adapt and validate query
→ sentinel_query_validate(query="DeviceProcessEvents | where...")

Step 4: Execute hunt
→ sentinel_logs_search(query="DeviceProcessEvents | where...")

Step 5: Analyze results and create summary
```

### 3. Environment Assessment
```
Step 1: Get workspace overview
→ sentinel_workspace_get()

Step 2: Check data connectors
→ sentinel_connectors_list()

Step 3: Review analytics rules
→ sentinel_analytics_rules_count_by_tactic()

Step 4: Assess authorization
→ sentinel_authorization_summary()

Step 5: Generate comprehensive report
```

### 4. KQL Query Development
```
Step 1: Explore available tables
→ sentinel_logs_tables_list()

Step 2: Understand table schema
→ sentinel_logs_table_schema_get(table_name="SecurityEvent")

Step 3: Test query with dummy data
→ sentinel_logs_search_with_dummy_data(query="SecurityEvent | take 10")

Step 4: Validate actual query
→ sentinel_query_validate(query="SecurityEvent | where EventID == 4624")

Step 5: Execute against real data
→ sentinel_logs_search(query="SecurityEvent | where EventID == 4624")
```

### 5. Intelligence Enrichment
```
Step 1: Get domain information
→ sentinel_domain_whois_get(domain="suspicious-domain.com")

Step 2: Get IP geolocation
→ sentinel_ip_geodata_get(ip="192.168.1.1")

Step 3: Check watchlists
→ sentinel_watchlists_list()

Step 4: Query watchlist items
→ sentinel_watchlist_items_list(watchlist_alias="threat-indicators")

Step 5: Correlate with security events
```

## Tool Combination Patterns

### Data Discovery Pattern
```
sentinel_workspace_get → sentinel_logs_tables_list → sentinel_logs_table_schema_get
```
Use this pattern to understand what data is available before crafting queries.

### Query Development Pattern  
```
sentinel_logs_table_schema_get → sentinel_query_validate → sentinel_logs_search_with_dummy_data → sentinel_logs_search
```
Use this pattern to safely develop and test KQL queries.

### Investigation Pattern
```
sentinel_incident_details_get → sentinel_logs_search → sentinel_analytics_rule_get → markdown_template_get
```
Use this pattern for thorough incident investigations with proper documentation.

### Assessment Pattern
```
sentinel_workspace_get → sentinel_authorization_summary → sentinel_connectors_list → sentinel_analytics_rule_list
```
Use this pattern to assess the security posture of a Sentinel workspace.

## Best Practices

### Query Construction
- Always validate KQL queries with `sentinel_query_validate` before execution
- Use table schemas to understand available fields and data types
- Limit query time ranges to avoid timeouts (default: 30 days max)
- Test complex queries with dummy data first
- Use proper KQL syntax highlighting in code blocks

### Result Handling
- Summarize large result sets rather than displaying all raw data
- Focus on security-relevant findings and patterns
- Use markdown templates for consistent formatting
- Include context and explanations for non-technical users

### Security Practices
- Never expose sensitive data (connection strings, API keys, tokens, passwords)
- Explain security incidents in a structured, clear manner
- Provide context and disclaimers for security recommendations  
- Respect data privacy and compliance requirements
- Always mention that findings should be verified by security professionals

### Performance Optimization
- Use `tool_docs_search` instead of reading multiple individual tool docs
- Cache workspace and table information for repeated queries
- Use appropriate time ranges and filters to limit result sets
- Combine related API calls when possible

## Error Handling Strategies

### Authentication Issues
```
1. Check workspace connectivity: sentinel_workspace_get
2. Verify permissions: sentinel_authorization_summary  
3. Review environment configuration
```

### Query Problems
```
1. Validate syntax: sentinel_query_validate
2. Check table availability: sentinel_logs_tables_list
3. Verify schema: sentinel_logs_table_schema_get
4. Test with dummy data: sentinel_logs_search_with_dummy_data
```

### Data Access Issues
```
1. Confirm workspace access: sentinel_workspace_get
2. Check data connector status: sentinel_connectors_list
3. Verify RBAC permissions: sentinel_authorization_summary
```

## Key Capabilities

- Execute and validate KQL queries against Sentinel and Log Analytics data
- Retrieve and investigate security incidents, alerts, and related entities
- Manage and enumerate analytics rules, rule templates, and ML analytics settings
- List, configure, and get details for data connectors
- Access workspace metadata and configuration
- Manage and query watchlists for enrichment and investigation
- Retrieve and use markdown templates for consistent report formatting
- Explore and search comprehensive tool and resource documentation
- Perform threat intelligence lookups (WHOIS, IP geolocation)
- Analyze MITRE ATT&CK framework mappings

## Getting Started Checklist

1. **Verify Access**: `sentinel_workspace_get` - Check workspace details and connectivity
2. **Understand Data**: `sentinel_logs_tables_list` - List available tables
3. **Explore Schema**: `sentinel_logs_table_schema_get` - Get table structure for key tables
4. **Test Queries**: `sentinel_query_validate` - Validate KQL syntax
5. **Execute Safely**: `sentinel_logs_search` - Run queries against workspace
6. **Document Results**: `markdown_template_get` - Use templates for consistent formatting

## Security and Compliance Notes

- All operations are performed using the configured identity's permissions
- Subject to Azure RBAC controls and data access policies
- Server provides READ-ONLY access to Sentinel data
- Designed for TEST environments; use caution with production data
- All queries and results should be treated as potentially sensitive
- Follow your organization's data handling and privacy policies