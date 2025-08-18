# Microsoft Sentinel MCP Server - System Architecture Overview

## High-Level Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   LLM Client    │    │   MCP Server    │    │  Azure Sentinel │
│  (Claude, etc.) │◄──►│     FastMCP     │◄──►│   Workspace     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Component Discovery │
                    │   & Registration    │
                    └─────────────────────┘
                               │
                ┌──────────────┼──────────────┐
                ▼              ▼              ▼
        ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
        │   Tools/    │ │ Resources/  │ │  Prompts/   │
        │ (Functions) │ │(Static Data)│ │(Templates)  │
        └─────────────┘ └─────────────┘ └─────────────┘
```

## Core Components

### 1. Server Entry Point (`server.py`)

The main server file implements:
- **Azure Services Lifecycle Management**: Creates and manages Azure SDK clients
- **Environment Configuration**: Loads Azure credentials and workspace settings
- **Component Auto-Discovery**: Automatically finds and registers tools, resources, and prompts
- **Error Handling**: Graceful degradation when Azure services are unavailable

#### Key Functions:
```python
@asynccontextmanager
async def azure_services_lifespan(mcp) -> AzureServicesContext:
    # Initializes Azure clients and provides context to tools
    
def load_instructions() -> str:
    # Loads LLM instructions from docs/llm_instructions.md
```

### 2. Component Auto-Discovery (`register_components.py`)

Implements a dynamic loading system that:
- Scans `tools/`, `resources/`, and `prompts/` directories
- Imports Python modules and calls their registration functions
- Enables adding new functionality without modifying core server code

#### Discovery Pattern:
```python
def load_components(mcp, component_dir: str, register_func_name: str):
    # 1. List all .py files in directory (excluding __init__.py)
    # 2. Import each module using importlib
    # 3. Call the register_* function if it exists
    # 4. Log successful registrations
```

#### Registration Functions Required:
- `tools/`: `register_tools(mcp)`
- `resources/`: `register_resources(mcp)` 
- `prompts/`: `register_prompts(mcp)`

### 3. Tool Base Class (`tools/base.py`)

`MCPToolBase` provides the foundation for all tools with:

#### Azure Client Management:
```python
def get_logs_client_and_workspace(self, ctx) -> (LogsQueryClient, str)
def get_securityinsight_client(self, subscription_id) -> SecurityInsights
def get_loganalytics_client(self, subscription_id) -> LogAnalyticsManagementClient
def get_authorization_client(self, subscription_id) -> AuthorizationManagementClient
```

#### Context Extraction:
```python
def get_azure_context(self, ctx) -> (workspace_name, resource_group, subscription_id)
def _extract_param(self, kwargs, name, default=None) -> Any
```

#### Async Execution:
```python
async def call_api(self, ctx, method, url, ...) -> Any
# Uses task_manager.run_in_thread() for blocking operations
```

#### Tool Structure Pattern:
```python
class MyTool(MCPToolBase):
    name = "tool_name"
    description = "Tool description"
    
    async def run(self, ctx: Context, **kwargs) -> Any:
        # Extract parameters
        param = self._extract_param(kwargs, "param_name", default_value)
        
        # Get Azure clients
        client = self.get_securityinsight_client(subscription_id)
        
        # Make API calls (wrapped in run_in_thread)
        result = await run_in_thread(client.some_method, param)
        
        return result
    
    @classmethod
    def register(cls, mcp):
        instance = cls()
        @mcp.tool(instance.name, instance.description)
        async def tool_entrypoint(ctx: Context, **kwargs):
            return await instance(ctx, **kwargs)
```

### 4. Azure Services Context

The server maintains a shared context object containing:
```python
@dataclass
class AzureServicesContext:
    credential: DefaultAzureCredential
    logs_client: LogsQueryClient
    metrics_client: MetricsQueryClient
    security_insights_client: SecurityInsights
    loganalytics_client: LogAnalyticsManagementClient
    workspace_id: str
    workspace_name: str
    subscription_id: str
    resource_group: str
    config: Dict[str, Any]
```

This context is passed to all tools and provides authenticated Azure clients.

## Component Types

### Tools (`tools/`)
Executable functions that interact with Azure APIs:
- Must inherit from `MCPToolBase`
- Implement `async def run(self, ctx, **kwargs)`
- Handle parameter extraction and validation
- Use `run_in_thread()` for blocking Azure SDK calls
- Return serializable Python objects

**Examples**: `sentinel_logs_search`, `sentinel_incident_details_get`

### Resources (`resources/`)
Static content and documentation:
- Tool documentation (`tool_docs/`)
- Markdown templates (`markdown_templates/`)
- Reference materials (`kql_examples.py`, `kql_basics.py`)
- Instruction content (`instructions.py`)

**Examples**: Individual tool documentation, result formatting templates

### Prompts (`prompts/`)
Templates for LLM-driven workflows:
- Security investigation workflows
- KQL query building assistance
- Structured analysis templates

**Examples**: `security_investigation.py`, `kql_builder.py`

## Data Flow

### 1. Tool Invocation Flow
```
LLM Request → MCP Protocol → FastMCP Server → Tool Instance → MCPToolBase
    ↓
Tool.run() → Parameter Extraction → Azure Client Setup → API Call
    ↓  
run_in_thread() → Azure SDK → Azure Sentinel API → Response
    ↓
Result Processing → MCP Response → LLM Client
```

### 2. Context Propagation
```
Server Startup → Azure Authentication → Context Creation
    ↓
Tool Invocation → Context Injection → Client Extraction
    ↓
API Call → Authenticated Request → Azure Response
```

### 3. Error Handling Chain
```
Azure API Error → MCPToolBase Exception Handler → MCP Error Response
    ↓
Logging → Error Content → LLM Error Message
```

## Key Design Patterns

### 1. Dependency Injection
Azure clients are injected via context rather than created in tools, enabling:
- Consistent authentication across tools
- Easier testing and mocking
- Resource efficiency through client reuse

### 2. Async/Await with Threading
- MCP server runs async event loop
- Azure SDK calls are synchronous 
- `run_in_thread()` bridges async/sync boundary without blocking

### 3. Parameter Flexibility
Tools support multiple parameter passing patterns:
```python
# Direct parameters
{"param": "value"}

# Nested parameters (SSE/HTTP mode)
{"kwargs": {"param": "value"}}
```

### 4. Graceful Degradation
- Server starts even if Azure authentication fails
- Tools return meaningful errors rather than crashing
- Missing dependencies are handled gracefully

## Extension Points

### Adding New Tools
1. Create new file in `tools/` directory
2. Implement class inheriting from `MCPToolBase`
3. Add `register_tools(mcp)` function
4. Tool will be auto-discovered on server restart

### Adding New Resources
1. Create new file in `resources/` directory
2. Implement resource content (static data, documentation)
3. Add `register_resources(mcp)` function
4. Resources will be auto-discovered on server restart

### Modifying Authentication
- Azure credential logic is centralized in `server.py`
- Environment variable handling in `azure_services_lifespan()`
- Client creation methods in `MCPToolBase`

This architecture provides a robust, extensible foundation for LLM interaction with Microsoft Sentinel while maintaining security, performance, and maintainability.