[![MseeP.ai Security Assessment Badge](https://mseep.net/culpeo_zqinyx.jpg)](https://mseep.ai/app/dstreefkerk-ms-sentinel-mcp-server)

# Microsoft Sentinel MCP Server

A [Model Context Protocol][mcp] (MCP) server for Microsoft Sentinel. This server enables read-only access to a Microsoft Sentinel instance, including advanced querying, incident viewing, and resource exploration for Azure Sentinel environments. It provides a modular and extensible platform for observation-only security operations and analysis.

---

## ⚠️ IMPORTANT SECURITY NOTICE ⚠️

**TEST ENVIRONMENTS ONLY**: This Microsoft Sentinel MCP server only supports read-only operations and is intended exclusively for TEST environments. It is not intended to be connected to production Sentinel instances.

**PRIVACY WARNING**: Connecting this server to a production Microsoft Entra ID (Azure AD) or Sentinel environment may expose sensitive user and directory data to LLM operators or public LLMs. Use only with non-production/test tenants, or a private LLM with MCP support.

**SECURITY WARNING**: Connecting a production Microsoft Sentinel instance to a public LLM poses significant privacy and security risks. Use only private, secured environments for production security operations.

---

## ✨ Features

- **KQL Query Execution**: Run and validate KQL queries, test with mock data
- **Log Analytics Management**: Workspace info, table listings and schemas
- **Security Incidents**: List and view detailed incident information
- **Analytics Rules**: List, view, and analyze by MITRE tactics/techniques
- **Rule Templates**: Access and analyze templates by MITRE framework
- **Hunting Queries**: List, view details, and analyze by tactic
- **Data Connectors**: List and view connector details
- **Watchlists**: Manage watchlists and their items
- **Threat Intelligence**: Domain WHOIS and IP geolocation lookups

- **Metadata & Source Control**: List and view repository details
- **ML Analytics**: Access ML analytics settings
- **Authorization**: View RBAC role assignments
- **Entra ID Users & Groups**: View user and group details from Microsoft Entra ID

---

## 🚀 Quick Start

### 1. Authenticate with Azure CLI

Before using the MCP server, you must have authenticated to Azure with an account that has access to a Microsoft Sentinel workspace:

```bash
az login
```

### 2. Clone the Repository

```bash
git clone https://github.com/dstreefkerk/ms-sentinel-mcp-server.git
cd ms-sentinel-mcp-server
```

### 3. Install with PowerShell Script (Recommended)

Use the provided PowerShell installation script to set up the MCP server:

```powershell
# Run from the repository root directory
.\install.ps1
```

The script will:
- Check for Python installation
- Create a virtual environment and install dependencies
- Generate a Claude Desktop configuration file
- Copy the configuration to your clipboard

After running the script, you can paste the configuration directly into your MCP client (Claude Desktop, Cursor, etc.).

### 4. Use the MCP server

The MCP server will be ready for use after you've configured your MCP client config with the relevant workspace info. 

Just remember that if you're using Azure CLI auth, you need to remove 
`AZURE_CLIENT_ID` and `AZURE_CLIENT_SECRET` from your MCP client config.

---

## 🧰 Tool Reference

Below are the available tools. For full documentation, see the `resources/tool_docs/` directory. Tool names and descriptions are kept in sync with the MCP server's tool registry, so that the MCP Client can retrieve them.

| Tool                                      | Category           | Description                                                      |
|-------------------------------------------|-------------------|------------------------------------------------------------------|
| `entra_id_list_users`                     | Entra ID          | List all users in Microsoft Entra ID (Azure AD)                  |
| `entra_id_get_user`                       | Entra ID          | Get a user by UPN or object ID from Entra ID                     |
| `entra_id_list_groups`                    | Entra ID          | List all groups in Microsoft Entra ID (Azure AD)                 |
| `entra_id_get_group`                      | Entra ID          | Get a group by object ID from Entra ID                           |
| `sentinel_logs_search`                    | KQL               | Run a KQL query against Azure Monitor Logs                       |
| `sentinel_query_validate`                 | KQL               | Validate KQL query syntax locally                                |
| `sentinel_logs_search_with_dummy_data`    | KQL               | Test a KQL query with mock data                                  |
| `sentinel_logs_tables_list`               | Log Analytics     | List available tables in the Log Analytics workspace             |
| `sentinel_logs_table_details_get`         | Log Analytics     | Get details for a Log Analytics table                            |
| `sentinel_logs_table_schema_get`          | Log Analytics     | Get schema for a Log Analytics table                             |
| `sentinel_workspace_get`                  | Log Analytics     | Get workspace information                                        |
| `sentinel_incident_details_get`           | Incidents         | Get detailed information about a specific Sentinel incident      |
| `sentinel_incident_list`                  | Incidents         | List security incidents in Microsoft Sentinel                    |
| `sentinel_analytics_rule_list`            | Analytics Rules   | List all analytics rules with key fields                         |
| `sentinel_analytics_rule_get`             | Analytics Rules   | Get details for a specific analytics rule                        |
| `sentinel_analytics_rules_count_by_tactic`| Analytics Rules   | Count Sentinel analytics rules by tactic                         |
| `sentinel_analytics_rules_count_by_technique` | Analytics Rules | Count Sentinel analytics rules by MITRE technique                |
| `sentinel_analytics_rule_templates_list`  | Rule Templates    | List all Sentinel analytics rule templates                       |
| `sentinel_analytics_rule_template_get`    | Rule Templates    | Get a specific Sentinel analytics rule template                  |
| `sentinel_analytics_rule_templates_count_by_tactic` | Rule Templates | Count Sentinel analytics rule templates by tactic         |
| `sentinel_analytics_rule_templates_count_by_technique` | Rule Templates | Count Sentinel analytics rule templates by MITRE technique |
| `sentinel_hunting_queries_list`           | Hunting           | List all Sentinel hunting queries with optional filtering         |
| `sentinel_hunting_query_get`              | Hunting           | Get full details of a Sentinel hunting query by name or ID       |
| `sentinel_hunting_queries_count_by_tactic`| Hunting           | Count Sentinel hunting queries by tactic                         |
| `sentinel_connectors_list`                | Data Connectors   | List data connectors                                             |
| `sentinel_connectors_get`                 | Data Connectors   | Get a specific data connector by ID                              |
| `sentinel_watchlists_list`                | Watchlists        | List all Sentinel watchlists                                     |
| `sentinel_watchlist_get`                  | Watchlists        | Get a specific Sentinel watchlist                                |
| `sentinel_watchlist_items_list`           | Watchlists        | List all items in a Sentinel watchlist                           |
| `sentinel_watchlist_item_get`             | Watchlists        | Get a specific item from a Sentinel watchlist                    |
| `sentinel_domain_whois_get`               | Threat Intel      | Get WHOIS information for a domain                               |
| `sentinel_ip_geodata_get`                 | Threat Intel      | Get geolocation data for an IP address                           |
| `sentinel_metadata_list`                  | Metadata          | List all Sentinel metadata in the current workspace              |
| `sentinel_metadata_get`                   | Metadata          | Get details for specific Sentinel metadata by ID                 |
| `sentinel_source_controls_list`           | Source Control    | List all Sentinel source controls in the current workspace       |
| `sentinel_source_control_get`             | Source Control    | Get details for a specific Sentinel source control by ID         |
| `sentinel_ml_analytics_settings_list`     | ML Analytics      | List all Sentinel ML analytics settings                          |
| `sentinel_ml_analytics_setting_get`       | ML Analytics      | Get a specific Sentinel ML analytics setting by name             |
| `sentinel_authorization_summary`          | Authorization     | Summarize Azure RBAC role assignments for Sentinel access        |
| `log_analytics_saved_searches_list`       | Saved Searches    | List all saved searches in a Log Analytics workspace             |
| `log_analytics_saved_search_get`          | Saved Searches    | Get a specific saved search from a Log Analytics workspace       |
---

## 🛠️ Usage

### Installing in Claude Desktop or similar Environments

Use the provided PowerShell installation script to set up the MCP server for Claude Desktop or other MCP-compatible clients:

```powershell
# Run from the repository root directory
.\install.ps1
```

The script will:
1. Check for Python installation
2. Create a virtual environment and install dependencies
3. Run post-installation steps
4. Generate a Claude Desktop configuration file
5. Copy the configuration to your clipboard

After running the script, you can paste the configuration directly into your MCP client (Claude Desktop, Cursor, etc.). The script generates Claude-compatible MCP Server configuration. Keep this in mind if you're going to use a different MCP client.

### Advanced Installation Options

#### Manual Environment Setup

If you prefer to set up the environment manually:

1. **Configure Environment Variables**

   Copy the provided template and fill in your Azure credentials:

   ```bash
   cp .env.example .env
   # Edit .env and set:
   # AZURE_TENANT_ID, AZURE_CLIENT_ID, AZURE_CLIENT_SECRET, AZURE_SUBSCRIPTION_ID, AZURE_RESOURCE_GROUP, AZURE_WORKSPACE_NAME, AZURE_WORKSPACE_ID
   ```

2. **Install Dependencies (with uv)**

   ```bash
   uv venv
   uv pip install -e .
   ```

3. **Alternative Server Run Options**

   **Using MCP CLI:**
   ```bash
   mcp run wrapper.py
   ```

   **Development & Hot Reload:**
   ```bash
   mcp dev wrapper.py
   ```

   **SSE Mode (for IDEs):**
   ```bash
   python wrapper.py --sse
   ```

### Inspector UI

The MCP Inspector UI is available at http://127.0.0.1:6274 when running in dev mode (`mcp dev wrapper.py`).

---

## 🧩 Development

- **Resources:** Add Python files to `resources/` and implement a `register_resources(mcp)` function.
- **Tools:** Add Python files to `tools/` and implement a `register_tools(mcp)` function. Tools must follow the structure defined in `docs/tool-architecture-and-implementation-requirements.md`.
- **Prompts:** Add prompt templates to `prompts/` for LLM-driven workflows.

All components in the `resources/`, `tools/`, and `prompts/` directories are auto-discovered and registered at server startup. No manual imports are needed.

---

## 🔐 Authentication & Environment Variables

The MCP Server supports any authentication method supported by the Azure Python SDK's `DefaultAzureCredential`.

### Service Principal authentication instead of Azure CLI

Set up an App Registration in Azure and assign the following roles:

- `Log Analytics Reader`
- `Microsoft Sentinel Reader`

If you're feeling brave, you can also grant the App Registration the following Microsoft Graph permissions:

- `User.Read.All`
- `Group.Read.All`

Then, use the following environment variables in your `.env` file or MCP Server configuration:

- `AZURE_TENANT_ID`
- **`AZURE_CLIENT_ID`**
- **`AZURE_CLIENT_SECRET`**
- `AZURE_SUBSCRIPTION_ID`
- `AZURE_RESOURCE_GROUP`
- `AZURE_WORKSPACE_NAME`
- `AZURE_WORKSPACE_ID`

See `.env.example` for a template.

### Azure CLI Authentication

```bash
az login
```

If you use Azure CLI authentication, you can omit `AZURE_CLIENT_SECRET` and `AZURE_CLIENT_ID` from your config.

---

## 🐛 Debugging

Enable debug mode by setting the `MCP_DEBUG_LOG` environment variable to `true` in your `.env` file:

```
MCP_DEBUG_LOG=true
```

Logs are written to your temp directory as `sentinel_mcp_server.log`.

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).

[mcp]: https://modelcontextprotocol.io/
