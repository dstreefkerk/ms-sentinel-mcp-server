# Microsoft Sentinel MCP Server - Quick Reference Guide

## Tool Categories

### 🔍 Core Query & Validation Tools
| Tool | Purpose | Key Parameters |
|------|---------|----------------|
| `sentinel_logs_search` | Execute KQL queries | `query`, `timespan` |
| `sentinel_query_validate` | Validate KQL syntax | `query` |
| `sentinel_logs_search_with_dummy_data` | Test queries with mock data | `query` |

### 🏢 Workspace & Infrastructure
| Tool | Purpose | Key Parameters |
|------|---------|----------------|
| `sentinel_workspace_get` | Get workspace info | None |
| `sentinel_logs_tables_list` | List available tables | None |
| `sentinel_logs_table_schema_get` | Get table schema | `table_name` |
| `sentinel_logs_table_details_get` | Get table metadata | `table_name` |
| `sentinel_authorization_summary` | Check RBAC permissions | None |

### 🚨 Security Incidents & Analytics
| Tool | Purpose | Key Parameters |
|------|---------|----------------|
| `sentinel_incident_details_get` | Get incident details | `incident_id` |
| `sentinel_analytics_rule_list` | List detection rules | None |
| `sentinel_analytics_rule_get` | Get specific rule | `rule_id` |
| `sentinel_analytics_rules_count_by_tactic` | Count rules by MITRE tactic | None |
| `sentinel_analytics_rules_count_by_technique` | Count rules by MITRE technique | None |

### 📋 Rule Templates
| Tool | Purpose | Key Parameters |
|------|---------|----------------|
| `sentinel_analytics_rule_templates_list` | List rule templates | None |
| `sentinel_analytics_rule_template_get` | Get template details | `template_id` |
| `sentinel_analytics_rule_templates_count_by_tactic` | Count templates by tactic | None |
| `sentinel_analytics_rule_templates_count_by_technique` | Count templates by technique | None |

### 🎯 Threat Hunting
| Tool | Purpose | Key Parameters |
|------|---------|----------------|
| `sentinel_hunting_queries_list` | List hunting queries | None |
| `sentinel_hunting_query_get` | Get hunting query details | `query_name` or `query_id` |
| `sentinel_hunting_queries_count_by_tactic` | Count queries by tactic | None |

### 🔌 Data Connectors
| Tool | Purpose | Key Parameters |
|------|---------|----------------|
| `sentinel_connectors_list` | List data connectors | None |
| `sentinel_connectors_get` | Get connector details | `connector_id` |

### 👥 Identity & Access (Entra ID)
| Tool | Purpose | Key Parameters |
|------|---------|----------------|
| `entra_id_list_users` | List Entra ID users | None |
| `entra_id_get_user` | Get user details | `user_principal_name` or `object_id` |
| `entra_id_list_groups` | List Entra ID groups | None |
| `entra_id_get_group` | Get group details | `object_id` |

### 📊 Watchlists & Intelligence
| Tool | Purpose | Key Parameters |
|------|---------|----------------|
| `sentinel_watchlists_list` | List watchlists | None |
| `sentinel_watchlist_get` | Get watchlist details | `watchlist_alias` |
| `sentinel_watchlist_items_list` | List watchlist items | `watchlist_alias` |
| `sentinel_watchlist_item_get` | Get specific item | `watchlist_alias`, `watchlist_item_id` |
| `sentinel_domain_whois_get` | Get domain WHOIS | `domain` |
| `sentinel_ip_geodata_get` | Get IP geolocation | `ip` |

### 💾 Saved Searches
| Tool | Purpose | Key Parameters |
|------|---------|----------------|
| `log_analytics_saved_searches_list` | List saved searches | None |
| `log_analytics_saved_search_get` | Get saved search | `search_id` |

### 🤖 ML Analytics
| Tool | Purpose | Key Parameters |
|------|---------|----------------|
| `sentinel_ml_analytics_settings_list` | List ML settings | None |
| `sentinel_ml_analytics_setting_get` | Get ML setting details | `setting_name` |

### 📁 Metadata & Source Control
| Tool | Purpose | Key Parameters |
|------|---------|----------------|
| `sentinel_metadata_list` | List metadata | None |
| `sentinel_metadata_get` | Get metadata details | `metadata_id` |
| `sentinel_source_controls_list` | List source controls | None |
| `sentinel_source_control_get` | Get source control | `source_control_id` |

### 📚 Documentation & Templates
| Tool | Purpose | Key Parameters |
|------|---------|----------------|
| `tool_docs_list` | List all documentation | None |
| `tool_docs_get` | Get specific documentation | `path` |
| `tool_docs_search` | Search documentation | `query` |
| `markdown_templates_list` | List format templates | None |
| `markdown_template_get` | Get template content | `path` |
| `llm_instructions_get` | Get LLM instructions | None |

## Common Parameter Patterns

### Time Ranges (for `sentinel_logs_search`)
```
timespan="PT1H"     # Last 1 hour
timespan="P1D"      # Last 1 day  
timespan="P7D"      # Last 7 days
timespan="P30D"     # Last 30 days (default maximum)
```

### KQL Query Examples
```kql
# Basic event search
SecurityEvent | where TimeGenerated > ago(1h)

# Count by event type
SecurityEvent 
| where TimeGenerated > ago(24h)
| summarize count() by EventID

# Failed logins
SecurityEvent 
| where EventID == 4625
| where TimeGenerated > ago(1d)
| project TimeGenerated, Account, Computer, IpAddress
```

## Quick Start Workflows

### 1. First Time Setup (2 minutes)
```
1. sentinel_workspace_get                    # Verify connectivity
2. sentinel_authorization_summary            # Check permissions  
3. sentinel_logs_tables_list                 # See available data
4. sentinel_connectors_list                  # Check data sources
```

### 2. Incident Response (5 minutes)
```
1. sentinel_incident_details_get(incident_id="123")
2. sentinel_logs_search(query="SecurityEvent | where...")
3. sentinel_analytics_rule_get(rule_id="rule-guid")
4. markdown_template_get(path="sentinel_incident_get.md")
```

### 3. Threat Hunt (10 minutes)
```
1. sentinel_hunting_queries_list()
2. sentinel_hunting_query_get(query_name="PowerShell Execution")
3. sentinel_query_validate(query="DeviceProcessEvents | where...")
4. sentinel_logs_search(query="DeviceProcessEvents | where...")
```

### 4. Environment Assessment (15 minutes)
```
1. sentinel_workspace_get()
2. sentinel_connectors_list()
3. sentinel_analytics_rules_count_by_tactic()
4. sentinel_hunting_queries_count_by_tactic()
5. sentinel_authorization_summary()
```

## Error Resolution Quick Guide

### ❌ Authentication Errors
**Symptoms**: "DefaultAzureCredential failed", "Authentication failed"
**Solutions**:
1. Check `az login` status: `az account show`
2. Verify environment variables: `AZURE_TENANT_ID`, `AZURE_SUBSCRIPTION_ID`, etc.
3. Test with: `sentinel_workspace_get`

### ❌ Permission Errors  
**Symptoms**: "Forbidden", "Access denied", "Insufficient privileges"
**Solutions**:
1. Check RBAC roles: `sentinel_authorization_summary`
2. Verify required roles: `Microsoft Sentinel Reader`, `Log Analytics Reader`
3. For Entra ID tools: `User.Read.All`, `Group.Read.All` permissions

### ❌ Query Errors
**Symptoms**: "Invalid query", "Syntax error", "Table not found"
**Solutions**:
1. Validate syntax: `sentinel_query_validate(query="...")`
2. Check table exists: `sentinel_logs_tables_list`
3. Verify schema: `sentinel_logs_table_schema_get(table_name="...")`
4. Test with dummy data: `sentinel_logs_search_with_dummy_data`

### ❌ Timeout Errors
**Symptoms**: "Request timeout", "Query took too long"
**Solutions**:
1. Reduce time range: Use shorter `timespan` values
2. Add filters: Include `where` clauses to limit data
3. Optimize query: Use `take`, `limit`, or `summarize`

### ❌ Data Not Found
**Symptoms**: "No results", "Empty response", "Resource not found"
**Solutions**:
1. Check data availability: `sentinel_logs_tables_list`
2. Verify connectors: `sentinel_connectors_list`
3. Adjust time range: Data might be outside query window
4. Check table details: `sentinel_logs_table_details_get`

## Environment Variables Reference

### Required for All Operations
```
AZURE_TENANT_ID=<your-tenant-id>
AZURE_SUBSCRIPTION_ID=<your-subscription-id>
AZURE_RESOURCE_GROUP=<your-resource-group>
AZURE_WORKSPACE_NAME=<your-workspace-name>
AZURE_WORKSPACE_ID=<your-workspace-id>
```

### Service Principal Authentication (Optional)
```
AZURE_CLIENT_ID=<your-client-id>
AZURE_CLIENT_SECRET=<your-client-secret>
```

### Debugging (Optional)
```
MCP_DEBUG_LOG=true
```

## Performance Tips

### 🚀 Speed Optimizations
- Use `tool_docs_search` instead of multiple `tool_docs_get` calls
- Cache table lists and schemas for repeated queries
- Use specific time ranges rather than default 30-day spans
- Combine related data queries when possible

### 💾 Memory Management
- Summarize large result sets instead of returning raw data
- Use `take` or `limit` in KQL queries for large tables
- Request only needed columns with `project` in queries

### 🔄 Query Efficiency
- Always validate KQL with `sentinel_query_validate` first
- Test complex queries with `sentinel_logs_search_with_dummy_data`
- Use filters and time constraints to reduce data scanning
- Leverage built-in summarization and aggregation functions

This quick reference provides the essential information for efficient LLM interaction with the Microsoft Sentinel MCP Server.