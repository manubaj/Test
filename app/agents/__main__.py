"""CLI: python -m app.agents --discover"""

from __future__ import annotations

import argparse
import asyncio
import json

from app.agents.discovery import ERPDiscoveryTool
from app.agents.erp_catalog import all_offerings
from app.agents.tool import ERPSalesIntelligenceTool, run_sales_intelligence_tool


def main() -> None:
    parser = argparse.ArgumentParser(
        description="ERP Sales Intelligence — discovery & company analysis tools"
    )
    parser.add_argument(
        "--discover",
        action="store_true",
        help="Run global ERP demand discovery (hardcoded ERPs → up to 100 leads)",
    )
    parser.add_argument("--leads", type=int, default=100, help="Max leads for discovery")
    parser.add_argument("--list-offerings", action="store_true")
    parser.add_argument("--list-agents", action="store_true")
    parser.add_argument("--name", help="Company name (legacy single-company analysis)")
    parser.add_argument("--website", help="Company website (legacy single-company analysis)")
    parser.add_argument("--country", default=None)
    parser.add_argument("--industry", default=None)
    args = parser.parse_args()

    if args.list_offerings:
        print(json.dumps(all_offerings(), indent=2))
        return

    if args.discover or args.list_agents:
        tool = ERPDiscoveryTool(target_lead_count=args.leads)
        if args.list_agents:
            print(json.dumps({"tool": tool.name, "agents": tool.list_agents()}, indent=2))
            return
        result = asyncio.run(tool.run())
        print(json.dumps(result, indent=2, default=str))
        return

    # Legacy single-company tool
    legacy = ERPSalesIntelligenceTool()
    if args.list_agents:
        print(json.dumps(legacy.list_agents(), indent=2))
        return
    if not args.name or not args.website:
        parser.error("Use --discover for lead finding, or --name/--website for one company")
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
