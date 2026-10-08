import json
from typing import Any

import structlog
from langchain_groq import ChatGroq

from app.config import settings
from app.database.models import Incident, IncidentType, RiskAssessment

logger = structlog.get_logger(__name__)


class GroqClient:
    def __init__(self) -> None:
        self.model_id = settings.GROQ_MODEL

    def _build_climate_prompt(self, assessment: RiskAssessment, location_name: str) -> str:
        risk_details = []
        risk_fields = [
            ("heat", "heat"),
            ("flood", "flood"),
            ("water_stress", "waterStress"),
            ("drought", "drought"),
        ]
        for risk_name, field_prefix in risk_fields:
            score = getattr(assessment, f"{field_prefix}Risk")
            severity = getattr(assessment, f"{field_prefix}Severity")
            factors = assessment.contributingFactors.get(risk_name, [])
            factor_details = ", ".join(factors) if factors else "No specific factors reported"
            risk_details.append(
                f"- {risk_name.replace('_', ' ').title()}: {score}% ({severity.value}) - "
                f"Factors: {factor_details}"
            )

        return f"""You are a climate risk analyst for ClimateOps. Provide a clear, actionable explanation for the following climate risk assessment.

Location: {location_name}
Risk Assessment:
{chr(10).join(risk_details)}

Data Sources: {', '.join(assessment.dataSources)}

Return one JSON object with exactly these keys and value types:
- summary: a 2-3 sentence string describing the overall risk situation
- key_factors: an array of strings naming the key factors for the highest risks; use [] if none
- recommendations: an array of 3-5 specific, prioritized recommendation strings
- potential_impacts: an array of strings describing impacts if conditions persist or worsen"""

    def _build_incident_prompt(
        self, incident: Incident, assessment: RiskAssessment, location_name: str
    ) -> str:
        risk_score_map = {
            IncidentType.HEAT: assessment.heatRisk,
            IncidentType.FLOOD: assessment.floodRisk,
            IncidentType.HEAVY_RAIN: assessment.floodRisk,
            IncidentType.WATER_STRESS: assessment.waterStressRisk,
            IncidentType.DROUGHT: assessment.droughtRisk,
        }

        current_risk = risk_score_map.get(incident.type, 0)
        factors = assessment.contributingFactors.get(
            incident.type.value.lower().replace(" ", "_"), []
        )

        return f"""You are an emergency response analyst for ClimateOps. Provide a clear explanation for the following active emergency incident.

Location: {location_name}
Incident Type: {incident.type.value}
Severity: {incident.severity.value}
Status: {incident.status.value}
Risk Score: {current_risk}%
Contributing Factors: {', '.join(factors) if factors else 'See risk assessment'}

Return one JSON object with exactly these keys and value types:
- why_emergency: a concise explanation of the incident and its current risk score
- key_factors: an array of strings explaining the evidence behind the risk
- immediate_actions: an array of prioritized, practical actions to reduce exposure and address the underlying risk
- monitoring_priorities: an array of measurable signals or advisories to check next
- escalation_scenarios: an array of plausible conditions that would increase the risk

Do not claim an action will guarantee resolution. Distinguish available evidence from uncertainty."""

    def _build_simulation_prompt(
        self,
        original_risks: dict[str, int],
        simulated_risks: dict[str, int],
        location_name: str,
        scenario_description: str,
    ) -> str:
        return f"""You are a climate risk analyst for ClimateOps. Explain the impact of a what-if climate scenario.

Location: {location_name}
Scenario: {scenario_description}

Risk Comparison:
- Heat Risk: {original_risks.get('heat', 0)}% → {simulated_risks.get('heat', 0)}%
- Flood Risk: {original_risks.get('flood', 0)}% → {simulated_risks.get('flood', 0)}%
- Water Stress: {original_risks.get('water_stress', 0)}% → {simulated_risks.get('water_stress', 0)}%
- Drought Risk: {original_risks.get('drought', 0)}% → {simulated_risks.get('drought', 0)}%

Please provide:
1. Summary of how the scenario changes risk profile
2. Which risks are most affected and why
3. Practical implications for the location
4. Whether this scenario represents a significant threat

Format as JSON with keys: summary, most_affected_risks, implications, threat_level"""

    async def invoke_model(self, prompt: str) -> str:
        if not settings.GROQ_API_KEY:
            raise RuntimeError(
                "GROQ_API_KEY is not configured. Add your Groq API key to the backend .env file."
            )

        model = ChatGroq(
            model=self.model_id,
            temperature=0.3,
            api_key=settings.GROQ_API_KEY,
        )
        try:
            response = await model.ainvoke(prompt, response_format={"type": "json_object"})
        except Exception:
            logger.exception("Groq request failed", model=self.model_id)
            raise

        content = response.content
        if isinstance(content, str):
            return content
        if isinstance(content, list):
            text_parts = [
                block["text"]
                for block in content
                if isinstance(block, dict) and isinstance(block.get("text"), str)
            ]
            if text_parts:
                return "\n".join(text_parts)
        raise TypeError("Groq returned a response without text content")

    @staticmethod
    def _parse_response(response: str) -> dict[str, Any]:
        try:
            parsed = json.loads(response)
        except json.JSONDecodeError:
            return {"raw_response": response}
        if not isinstance(parsed, dict):
            return {"raw_response": response}
        return parsed

    async def explain_climate_risk(
        self, assessment: RiskAssessment, location_name: str
    ) -> dict[str, Any] | None:
        response = await self.invoke_model(self._build_climate_prompt(assessment, location_name))
        return self._parse_response(response)

    async def explain_incident(
        self, incident: Incident, assessment: RiskAssessment, location_name: str
    ) -> dict[str, Any] | None:
        response = await self.invoke_model(
            self._build_incident_prompt(incident, assessment, location_name)
        )
        return self._parse_response(response)

    async def explain_simulation(
        self,
        original_risks: dict[str, int],
        simulated_risks: dict[str, int],
        location_name: str,
        scenario_description: str,
    ) -> dict[str, Any] | None:
        response = await self.invoke_model(
            self._build_simulation_prompt(
                original_risks, simulated_risks, location_name, scenario_description
            )
        )
        return self._parse_response(response)


groq_client = GroqClient()
