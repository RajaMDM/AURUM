"""
AURUM MCP Server
Exposes the AURUM pipeline as an MCP-compatible server.
Invokable from Claude Code, Cursor, and Hermes/Nous runtimes.
"""
import sys
from pathlib import Path
ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT))

try:
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False

if not MCP_AVAILABLE:
    print("mcp package not installed. Run: pip install mcp")
    sys.exit(0)

server = Server("aurum-mdm")

@server.list_tools()
async def list_tools():
    from mcp.types import Tool
    return [
        Tool(name="assay_schema", description="Inspect a CSV source file — field types, nulls, cardinality", inputSchema={"type":"object","properties":{"file_path":{"type":"string"}},"required":["file_path"]}),
        Tool(name="unearth_profile", description="Profile a customer CSV for DQ issues", inputSchema={"type":"object","properties":{"file_path":{"type":"string"}},"required":["file_path"]}),
        Tool(name="refine_match", description="Find duplicate candidates in a customer dataset", inputSchema={"type":"object","properties":{"file_path":{"type":"string"},"sample_size":{"type":"integer","default":30}},"required":["file_path"]}),
    ]

@server.call_tool()
async def call_tool(name: str, arguments: dict):
    import json
    if name == "assay_schema":
        from assay.schema_inspector.inspector import SchemaInspector
        result = SchemaInspector("mcp_source").inspect(arguments["file_path"])
        return [{"type": "text", "text": json.dumps(result, indent=2)}]

    elif name == "unearth_profile":
        from unearth.profiler.domain_profiler import CustomerProfiler
        result = CustomerProfiler().profile(arguments["file_path"]).summary()
        return [{"type": "text", "text": json.dumps(result, indent=2)}]

    elif name == "refine_match":
        import pandas as pd
        from refine.matching.matcher import find_candidates
        df = pd.read_csv(arguments["file_path"], dtype=str, keep_default_na=False)
        candidates = find_candidates(df, sample_size=arguments.get("sample_size", 30))
        result = [{"a": c.record_a_id, "b": c.record_b_id, "score": c.composite_score, "match": c.is_match} for c in candidates[:20]]
        return [{"type": "text", "text": json.dumps(result, indent=2)}]

    return [{"type": "text", "text": f"Unknown tool: {name}"}]

if __name__ == "__main__":
    import asyncio
    asyncio.run(stdio_server(server))
