# Documentation Navigation Guide

This guide helps LLMs and developers quickly find the right documentation for any task related to the Microsoft Sentinel MCP Server.

## 📋 Quick Navigation by Purpose

### 🚀 **Getting Started (New to the project)**
1. **[README.md](../README.md)** - Project overview, installation, and basic setup
2. **[LLM_QUICKSTART.md](../LLM_QUICKSTART.md)** - Essential guide for LLM interaction
3. **[docs/llm_instructions.md](llm_instructions.md)** - Detailed workflows and best practices

### 🏗️ **Understanding the System**
1. **[docs/SYSTEM_OVERVIEW.md](SYSTEM_OVERVIEW.md)** - Architecture and component relationships
2. **[docs/architecture/project-requirements-document.md](architecture/project-requirements-document.md)** - Project goals and scope
3. **[docs/architecture/tech-stack-document.md](architecture/tech-stack-document.md)** - Technology choices and dependencies

### ⚡ **Quick Reference (During development)**
1. **[docs/QUICK_REFERENCE.md](QUICK_REFERENCE.md)** - Tool categories and common patterns
2. **[docs/llm_instructions.md](llm_instructions.md)** - Workflow examples and best practices
3. **Use `tool_docs_search` tool** - Search all tool documentation

### 🔧 **Development & Extension**
1. **[docs/architecture/tool-architecture-and-implementation-requirements.md](architecture/tool-architecture-and-implementation-requirements.md)** - Tool development requirements
2. **[docs/architecture/backend-structure.md](architecture/backend-structure.md)** - Code organization
3. **[docs/architecture/naming_convention.md](architecture/naming_convention.md)** - Naming standards

### 🔒 **Security & Configuration**
1. **[docs/architecture/security-guideline-document.md](architecture/security-guideline-document.md)** - Security requirements
2. **[README.md#authentication](../README.md#-authentication--environment-variables)** - Authentication setup
3. **[docs/QUICK_REFERENCE.md#environment-variables-reference](QUICK_REFERENCE.md#environment-variables-reference)** - Configuration reference

## 📂 Documentation Structure

```
├── README.md                          # Main project documentation
├── LLM_QUICKSTART.md                  # Essential LLM guide (NEW)
├── docs/
│   ├── DOCUMENTATION_GUIDE.md         # This navigation guide (NEW)
│   ├── SYSTEM_OVERVIEW.md             # Architecture overview (NEW)
│   ├── QUICK_REFERENCE.md             # Tool reference (NEW)
│   ├── llm_instructions.md            # Enhanced LLM workflows (UPDATED)
│   └── architecture/                  # Detailed architectural docs
│       ├── project-requirements-document.md
│       ├── tech-stack-document.md
│       ├── tool-architecture-and-implementation-requirements.md
│       ├── backend-structure.md
│       ├── security-guideline-document.md
│       ├── naming_convention.md
│       ├── implementation-plan.md
│       ├── system-flow-document.md
│       ├── prompt-architecture-doc.md
│       └── libraries/               # External library documentation
├── resources/
│   ├── tool_docs/                  # Individual tool documentation (auto-generated)
│   └── markdown_templates/         # Result formatting templates
```

## 🎯 Documentation by User Type

### For LLMs (AI Assistants)
**Priority Reading Order:**
1. **[LLM_QUICKSTART.md](../LLM_QUICKSTART.md)** - Core concepts and patterns
2. **[docs/llm_instructions.md](llm_instructions.md)** - Detailed workflows
3. **[docs/QUICK_REFERENCE.md](QUICK_REFERENCE.md)** - Tool reference
4. **Use tools**: `tool_docs_search`, `tool_docs_list`, `tool_docs_get`

### For Developers (Contributing code)
**Priority Reading Order:**
1. **[README.md](../README.md)** - Setup and installation
2. **[docs/SYSTEM_OVERVIEW.md](SYSTEM_OVERVIEW.md)** - Architecture understanding
3. **[docs/architecture/tool-architecture-and-implementation-requirements.md](architecture/tool-architecture-and-implementation-requirements.md)** - Development requirements
4. **[docs/architecture/backend-structure.md](architecture/backend-structure.md)** - Code organization

### For Security Engineers (Using the tool)
**Priority Reading Order:**
1. **[README.md](../README.md)** - Installation and security warnings
2. **[docs/architecture/security-guideline-document.md](architecture/security-guideline-document.md)** - Security considerations
3. **[docs/llm_instructions.md](llm_instructions.md)** - Usage workflows
4. **[docs/QUICK_REFERENCE.md](QUICK_REFERENCE.md)** - Tool reference

### For Project Managers (Understanding scope)
**Priority Reading Order:**
1. **[docs/architecture/project-requirements-document.md](architecture/project-requirements-document.md)** - Project scope and goals
2. **[README.md](../README.md)** - Feature overview
3. **[docs/SYSTEM_OVERVIEW.md](SYSTEM_OVERVIEW.md)** - Technical architecture

## 🔍 Finding Specific Information

### Tool Usage and Parameters
```
Use tools: tool_docs_search, tool_docs_list, tool_docs_get
Or check: docs/QUICK_REFERENCE.md
```

### Workflow Examples
```
Primary: docs/llm_instructions.md
Secondary: LLM_QUICKSTART.md
```

### Architecture and Design Decisions
```
Primary: docs/SYSTEM_OVERVIEW.md  
Secondary: docs/architecture/project-requirements-document.md
```

### Error Troubleshooting
```
Primary: docs/QUICK_REFERENCE.md#error-resolution-quick-guide
Secondary: docs/llm_instructions.md#error-handling-strategies
```

### Environment Setup
```
Primary: README.md#authentication--environment-variables
Secondary: docs/QUICK_REFERENCE.md#environment-variables-reference
```

### Adding New Tools
```
Primary: docs/architecture/tool-architecture-and-implementation-requirements.md
Secondary: docs/SYSTEM_OVERVIEW.md#extension-points
```

## 🆕 What's New in This Documentation

### Recently Added (Latest improvements)
- **[LLM_QUICKSTART.md](../LLM_QUICKSTART.md)** - Replaces auto-generated `llms.txt` with curated content
- **[docs/SYSTEM_OVERVIEW.md](SYSTEM_OVERVIEW.md)** - Comprehensive architecture guide  
- **[docs/QUICK_REFERENCE.md](QUICK_REFERENCE.md)** - Tool categories and quick patterns
- **[docs/DOCUMENTATION_GUIDE.md](DOCUMENTATION_GUIDE.md)** - This navigation guide

### Enhanced (Significantly updated)
- **[docs/llm_instructions.md](llm_instructions.md)** - Added detailed workflow examples, tool combinations, and error handling

### Removed/Replaced
- **`llms.txt`** - Replaced with focused LLM_QUICKSTART.md (was 36k+ tokens, now ~5k tokens)

## 💡 Tips for Efficient Documentation Use

### For LLMs
- Start with `LLM_QUICKSTART.md` for core concepts
- Use `tool_docs_search` to find specific tool information
- Reference `QUICK_REFERENCE.md` for parameter patterns
- Follow workflow examples in `llm_instructions.md`

### For Developers  
- Read `SYSTEM_OVERVIEW.md` first to understand the architecture
- Follow patterns in existing tools (see `tools/` directory)
- Check `tool-architecture-and-implementation-requirements.md` for requirements
- Use auto-discovery system - no manual registration needed

### For Documentation Updates
- Keep `LLM_QUICKSTART.md` under 5k tokens for efficient LLM consumption
- Update `QUICK_REFERENCE.md` when adding new tool categories
- Add workflow examples to `llm_instructions.md` for new use cases
- Generate tool docs via the server's built-in documentation system

This documentation structure is designed to minimize the time needed for LLMs to understand and effectively use the Microsoft Sentinel MCP Server while providing comprehensive reference material for all user types.