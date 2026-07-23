"""
Hardcoded catalog of major ERP solutions and services.

These are the default discovery targets — no manual user input required.
A discovery run searches the web (LinkedIn-indexed + company sites) for
companies showing demand for one or more of these offerings.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ERPOffering:
    """One sellable ERP product/service line."""

    key: str
    vendor: str
    product: str
    service: str
    label: str
    search_terms: tuple[str, ...]


# Comprehensive market catalog used as fixed input for every discovery run
ERP_OFFERINGS: tuple[ERPOffering, ...] = (
    # IFS
    ERPOffering("ifs_implementation", "IFS", "IFS", "Implementation", "IFS Implementation",
                ("IFS implementation", "implementing IFS", "IFS ERP project", "IFS Apps implementation")),
    ERPOffering("ifs_upgrade", "IFS", "IFS Apps", "Upgrade", "IFS Upgrade",
                ("IFS upgrade", "IFS Apps upgrade", "upgrade to IFS Cloud", "IFS reimplementation")),
    ERPOffering("ifs_cloud_migration", "IFS", "IFS Cloud", "Cloud Migration", "IFS Cloud Migration",
                ("IFS Cloud migration", "migrate to IFS Cloud", "IFS cloud transformation")),
    ERPOffering("ifs_managed_support", "IFS", "IFS", "Managed Support", "IFS Managed Support",
                ("IFS managed services", "IFS support partner", "IFS AMS", "IFS application support")),
    # SAP
    ERPOffering("sap_s4_migration", "SAP", "SAP S/4HANA", "Migration", "SAP S/4HANA Migration",
                ("S/4HANA migration", "SAP S/4HANA migration", "migrate to S/4HANA", "ECC to S/4HANA")),
    ERPOffering("sap_s4_implementation", "SAP", "SAP S/4HANA", "Implementation", "SAP S/4HANA Implementation",
                ("S/4HANA implementation", "implementing SAP S/4HANA", "SAP S/4 greenfield")),
    ERPOffering("sap_support", "SAP", "SAP", "Support", "SAP Support",
                ("SAP support partner", "SAP AMS", "SAP managed services", "SAP basis support")),
    ERPOffering("sap_ecc_support", "SAP", "SAP ECC", "Support", "SAP ECC Support",
                ("SAP ECC support", "ECC upgrade", "SAP R/3 support")),
    # Oracle
    ERPOffering("oracle_erp_migration", "Oracle", "Oracle ERP Cloud", "Migration", "Oracle ERP Migration",
                ("Oracle ERP migration", "Oracle Fusion migration", "migrate to Oracle Cloud ERP", "EBS to Oracle Cloud")),
    ERPOffering("oracle_erp_implementation", "Oracle", "Oracle ERP Cloud", "Implementation", "Oracle ERP Implementation",
                ("Oracle ERP implementation", "Oracle Fusion implementation", "Oracle Cloud ERP project")),
    ERPOffering("oracle_ebs_support", "Oracle", "Oracle EBS", "Support", "Oracle EBS Support",
                ("Oracle EBS support", "Oracle E-Business Suite support", "Oracle AMS")),
    # Infor
    ERPOffering("infor_ln_upgrade", "Infor", "Infor LN", "Upgrade", "Infor LN Upgrade",
                ("Infor LN upgrade", "Infor LN implementation", "Baan to Infor LN")),
    ERPOffering("infor_m3_upgrade", "Infor", "Infor M3", "Upgrade", "Infor M3 Upgrade",
                ("Infor M3 upgrade", "Infor M3 implementation", "Movex to M3")),
    ERPOffering("infor_cloudsuite", "Infor", "Infor CloudSuite", "Migration", "Infor CloudSuite Migration",
                ("Infor CloudSuite", "Infor cloud migration", "Infor CSI")),
    # Microsoft
    ERPOffering("dynamics_365_implementation", "Microsoft", "Dynamics 365", "Implementation", "Dynamics 365 Implementation",
                ("Dynamics 365 implementation", "D365 F&O implementation", "Dynamics 365 Finance")),
    ERPOffering("dynamics_365_migration", "Microsoft", "Dynamics 365", "Migration", "Dynamics 365 Migration",
                ("Dynamics AX to D365", "migrate to Dynamics 365", "NAV to Business Central")),
    # Other major ERPs
    ERPOffering("netsuite_implementation", "Oracle NetSuite", "NetSuite", "Implementation", "NetSuite Implementation",
                ("NetSuite implementation", "implementing NetSuite", "NetSuite ERP project")),
    ERPOffering("epicor_implementation", "Epicor", "Epicor Kinetic", "Implementation", "Epicor Implementation",
                ("Epicor implementation", "Epicor Kinetic", "Epicor ERP")),
    ERPOffering("syspro_implementation", "SYSPRO", "SYSPRO", "Implementation", "SYSPRO Implementation",
                ("SYSPRO implementation", "SYSPRO ERP")),
    ERPOffering("qad_implementation", "QAD", "QAD Adaptive ERP", "Implementation", "QAD Implementation",
                ("QAD implementation", "QAD ERP", "QAD Adaptive")),
    ERPOffering("acumatica_implementation", "Acumatica", "Acumatica", "Implementation", "Acumatica Implementation",
                ("Acumatica implementation", "Acumatica ERP")),
    ERPOffering("odoo_implementation", "Odoo", "Odoo", "Implementation", "Odoo Implementation",
                ("Odoo implementation", "Odoo ERP project")),
    # Cross-cutting services
    ERPOffering("erp_digital_transformation", "Multi", "ERP", "Digital Transformation", "ERP Digital Transformation",
                ("ERP digital transformation", "ERP modernization", "legacy ERP transformation")),
    ERPOffering("erp_performance_optimization", "Multi", "ERP", "Performance Optimization", "ERP Performance Optimization",
                ("ERP performance optimization", "optimize ERP", "ERP process improvement")),
)


def all_offerings() -> list[dict]:
    """Serialize catalog for API/UI."""
    return [
        {
            "key": o.key,
            "vendor": o.vendor,
            "product": o.product,
            "service": o.service,
            "label": o.label,
            "search_terms": list(o.search_terms),
        }
        for o in ERP_OFFERINGS
    ]


def offerings_by_key() -> dict[str, ERPOffering]:
    return {o.key: o for o in ERP_OFFERINGS}


def default_discovery_queries(max_per_offering: int = 2) -> list[tuple[str, str]]:
    """
    Build (offering_key, search_query) pairs for LinkedIn-indexed + web discovery.

    LinkedIn is queried via search engines (publicly indexed jobs/posts) because
    direct LinkedIn scraping violates LinkedIn ToS and is routinely blocked.
    """
    queries: list[tuple[str, str]] = []
    for offering in ERP_OFFERINGS:
        for term in offering.search_terms[:max_per_offering]:
            queries.append(
                (
                    offering.key,
                    f'site:linkedin.com/jobs "{term}"',
                )
            )
            queries.append(
                (
                    offering.key,
                    f'"{term}" (hiring OR careers OR "we are hiring" OR RFP OR implementation)',
                )
            )
    return queries
