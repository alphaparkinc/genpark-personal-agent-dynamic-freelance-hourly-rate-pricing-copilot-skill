# -*- coding: utf-8 -*-
"""Dynamic Freelance Hourly Rate Pricing Copilot Skill for GenPark Personal Agents."""
import json
from typing import Dict, Any

def calculate_minimum_effective_hourly_rate(target_annual_take_home_usd: float, annual_business_expenses_usd: float, estimated_tax_bracket_pct: float, billable_weeks_per_year: int = 48, target_billable_hours_per_week: int = 25) -> Dict[str, Any]:
    # Gross revenue required before taxes and expenses
    tax_divisor = max(0.1, 1.0 - (estimated_tax_bracket_pct / 100.0))
    pre_tax_salary_needed = target_annual_take_home_usd / tax_divisor
    gross_revenue_needed = pre_tax_salary_needed + annual_business_expenses_usd

    total_billable_hours = max(100, billable_weeks_per_year * target_billable_hours_per_week)
    mehr_hourly_usd = round(gross_revenue_needed / total_billable_hours, 2)

    return {
        "target_take_home_usd": target_annual_take_home_usd,
        "annual_operating_expenses_usd": annual_business_expenses_usd,
        "gross_revenue_required_usd": round(gross_revenue_needed, 2),
        "total_annual_billable_hours": total_billable_hours,
        "unbillable_admin_hours_est": (52 * 40) - total_billable_hours,
        "minimum_effective_hourly_rate_usd": mehr_hourly_usd,
        "recommended_market_rate_usd": round(mehr_hourly_usd * 1.25, 2),
        "solopreneur_copilot": "GenPark Freelance Economic Arbiter"
    }

def price_fixed_scope_project(estimated_baseline_hours: float, base_hourly_rate_usd: float, scope_ambiguity_level: str, client_economic_upside_usd: float = 0.0) -> Dict[str, Any]:
    cost_plus_base = estimated_baseline_hours * base_hourly_rate_usd

    # Scope ambiguity risk buffer
    if scope_ambiguity_level == "high_exploratory":
        buffer_multiplier = 0.40 # 40% risk buffer
    elif scope_ambiguity_level == "moderate_standard":
        buffer_multiplier = 0.20 # 20% risk buffer
    else:
        buffer_multiplier = 0.10 # 10% risk buffer

    risk_buffer_usd = round(cost_plus_base * buffer_multiplier, 2)
    
    # Value-based pricing adder: 10% of client expected economic lift
    value_share_usd = round(client_economic_upside_usd * 0.10, 2) if client_economic_upside_usd > 0 else 0.0

    optimal_fixed_quote_usd = round(cost_plus_base + risk_buffer_usd + value_share_usd, 2)

    return {
        "baseline_hours_estimated": estimated_baseline_hours,
        "cost_plus_floor_usd": round(cost_plus_base, 2),
        "scope_risk_buffer_usd": risk_buffer_usd,
        "value_based_upside_share_usd": value_share_usd,
        "recommended_fixed_fee_quote_usd": optimal_fixed_quote_usd,
        "effective_realized_hourly_rate_usd": round(optimal_fixed_quote_usd / max(1.0, estimated_baseline_hours), 2),
        "contract_terms_advice": "Mandate 50% deposit upfront upon kickoff, 25% upon design sign-off, and 25% upon final deployment."
    }
