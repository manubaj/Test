"""CLI entry: python -m app.agents --name Acme --website https://example.com"""

from __future__ import annotations

import argparse
import asyncio
import json

from app.agents.tool import ERPSalesIntelligenceTool, run_sales_intelligence_tool


def main() -> None:
    parser = argparse.ArgumentParser(
        description="ERP Sales Intelligence Tool — runs 6 AI agents"
    )
    parser.add_argument("--name", help="Company name")
    parser.add_argument("--website", help="Company website URL")
    parser.add_argument("--country", default=None)
    parser.add_argument("--industry", default=None)
    parser.add_argument(
        "--list-agents",
        action="store_true",
        help="List the six agents and exit",
    )
    args = parser.parse_args()

    tool = ERPSalesIntelligenceTool()
    if args.list_agents:
        print(json.dumps({"tool": tool.name, "agents": tool.list_agents()}, indent=2))
        return

    if not args.name or not args.website:
        parser.error("--name and --website are required unless --list-agents")

    result = asyncio.run(
        run_sales_intelligence_tool(
            company_name=args.name,
            website=args.website,
            country=args.country,
            industry=args.industry,
        )
    )
    print(json.dumps(result, indent=2, default=str))


if __name__ == "__main__":
    main()
