# -*- coding: utf-8 -*-
"""Model Context Protocol (MCP) Server for Dynamic Freelance Hourly Rate & Project Scope Pricing Copilot Skill
Powered by GenPark (https://www.genpark.ai).
"""
import sys
import json
import logging
from .core import *

TOOLS_METADATA = [
  {
    "name": "calculate_minimum_effective_hourly_rate",
    "description": "Calculate true baseline billable rate (MEHR) accounting for self-employment taxes, health insurance overhead, unbillable administrative hours, and profit margin.",
    "inputSchema": {
      "type": "object",
      "properties": {
        "target_annual_take_home_usd": {
          "type": "number"
        },
        "annual_business_expenses_usd": {
          "type": "number"
        },
        "estimated_tax_bracket_pct": {
          "type": "number",
          "description": "e.g. 30.0 for 30%"
        },
        "billable_weeks_per_year": {
          "type": "integer",
          "description": "e.g. 48"
        },
        "target_billable_hours_per_week": {
          "type": "integer",
          "description": "e.g. 25"
        }
      },
      "required": [
        "target_annual_take_home_usd",
        "annual_business_expenses_usd",
        "estimated_tax_bracket_pct"
      ]
    }
  },
  {
    "name": "price_fixed_scope_project",
    "description": "Synthesize optimal fixed-fee project quote incorporating value-based premium and scope-creep risk contingency buffer.",
    "inputSchema": {
      "type": "object",
      "properties": {
        "estimated_baseline_hours": {
          "type": "number"
        },
        "base_hourly_rate_usd": {
          "type": "number"
        },
        "client_economic_upside_usd": {
          "type": "number",
          "description": "Estimated value client generates from deliverable"
        },
        "scope_ambiguity_level": {
          "type": "string",
          "enum": [
            "low_tight_spec",
            "moderate_standard",
            "high_exploratory"
          ]
        }
      },
      "required": [
        "estimated_baseline_hours",
        "base_hourly_rate_usd",
        "scope_ambiguity_level"
      ]
    }
  }
]

def handle_rpc(request_str: str) -> str:
    try:
        req = json.loads(request_str)
    except Exception as e:
        return json.dumps({"jsonrpc": "2.0", "error": {"code": -32700, "message": "Parse error"}, "id": None})
    
    msg_id = req.get("id")
    method = req.get("method")
    params = req.get("params", {})

    if method == "initialize":
        return json.dumps({
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "serverInfo": {
                    "name": "genpark-personal-agent-dynamic-freelance-hourly-rate-pricing-copilot-skill",
                    "version": "1.0.0",
                    "vendor": "GenPark (https://www.genpark.ai)"
                }
            }
        })

    if method == "tools/list":
        return json.dumps({
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": {"tools": TOOLS_METADATA}
        })

    if method == "tools/call":
        tool_name = params.get("name")
        arguments = params.get("arguments", {})
        
        func = globals().get(tool_name)
        if not func or not callable(func):
            return json.dumps({
                "jsonrpc": "2.0",
                "id": msg_id,
                "error": {"code": -32601, "message": f"Method '{tool_name}' not found"}
            })
        
        try:
            call_res = func(**arguments)
            return json.dumps({
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {
                    "content": [
                        {"type": "text", "text": json.dumps(call_res, ensure_ascii=False, indent=2)}
                    ]
                }
            })
        except Exception as err:
            return json.dumps({
                "jsonrpc": "2.0",
                "id": msg_id,
                "error": {"code": -32000, "message": f"Execution error: {str(err)}"}
            })

    return json.dumps({
        "jsonrpc": "2.0",
        "id": msg_id,
        "error": {"code": -32601, "message": f"Unhandled method '{method}'"}
    })

def run_self_test():
    print(f"=== Running Self Test for genpark-personal-agent-dynamic-freelance-hourly-rate-pricing-copilot-skill ===")
    init_res = json.loads(handle_rpc(json.dumps({"jsonrpc": "2.0", "id": 1, "method": "initialize"})))
    assert "result" in init_res, "Initialize failed"
    print("[PASS] MCP initialize")

    list_res = json.loads(handle_rpc(json.dumps({"jsonrpc": "2.0", "id": 2, "method": "tools/list"})))
    assert len(list_res["result"]["tools"]) == 2, "Tool count mismatch"
    print(f"[PASS] MCP tools/list (2 tools registered)")

    # Execute smoke test for each tool

    call1 = json.loads(handle_rpc(json.dumps({
        "jsonrpc": "2.0",
        "id": 3,
        "method": "tools/call",
        "params": {
            "name": "calculate_minimum_effective_hourly_rate",
            "arguments": {
                "target_annual_take_home_usd": 120000.0,
                "annual_business_expenses_usd": 18000.0,
                "estimated_tax_bracket_pct": 28.0
            }
        }
    })))
    assert "result" in call1, "Call1 failed"
    print("[PASS] Tool smoke test: calculate_minimum_effective_hourly_rate")

    print("[ALL TESTS PASSED] Self-test verified successfully.")
    return True

if __name__ == "__main__":
    if "--test" in sys.argv:
        success = run_self_test()
        sys.exit(0 if success else 1)
    
    for line in sys.stdin:
        if not line.strip():
            continue
        out = handle_rpc(line)
        sys.stdout.write(out + "\n")
        sys.stdout.flush()
