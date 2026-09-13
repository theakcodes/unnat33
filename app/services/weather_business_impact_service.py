"""
app/services/weather_business_impact_service.py

Deterministic Weather -> Business Activity Impact Heuristic Service:

IMPORTANT ARCHITECTURAL INVARIANT & ZERO-FABRICATION CONTRACT:
1. INDICATIVE PRODUCT HEURISTIC:
   This service is an indicative product heuristic to demonstrate how district-level weather
   conditions may influence general business activity, walk-in customer patterns, and logistics.
   It is NOT a scientifically validated footfall or weather-impact model.
   It is NOT a measured footfall index, statistically validated forecast, prediction of actual customer traffic,
   or validated economic indicator.

2. ZERO DATA FABRICATION:
   - NO actual customer counts are predicted or invented.
   - NO revenue impacts or sales numbers are predicted or invented.
   - NO specific percentage claims (e.g. "footfall will drop 25%") are made.
   - NO fake historical footfall or fake 12-month weather datasets are created.
   - UI / response contract: "Indicative weather impact on business activity — not observed footfall or a sales forecast."

3. TRANSPARENT, EXPLAINABLE FORMULA & WEIGHTS:
   Composite Activity Impact Score (0 to 100):
   - Precipitation Subscore (45% weight)
   - Temperature Subscore (35% weight)
   - Wind & Weather Severity Subscore (20% weight)
"""

import logging
from typing import Optional, List, Dict, Tuple
from app.schemas.weather import DistrictWeatherContext, CurrentWeatherMetrics, DailyForecastDay
from app.schemas.market_intelligence import (
    WeatherActivityImpactAnalysis,
    WeatherRiskSignals,
    DailyWeatherOutlookItem,
)

logger = logging.getLogger(__name__)


class WeatherBusinessImpactService:
    """
    Service providing transparent, deterministic, heuristic assessment of how district weather
    influences general business activity and customer footfall context.
    """

    # Transparent Model Weights (Sum = 1.0)
    WEIGHT_PRECIPITATION = 0.45
    WEIGHT_TEMPERATURE = 0.35
    WEIGHT_WIND_SEVERITY = 0.20

    # Categorical Score Thresholds (0-100)
    SCORE_VERY_FAVOURABLE = 80.0
    SCORE_FAVOURABLE = 60.0
    SCORE_NEUTRAL = 40.0
    SCORE_DISRUPTIVE = 20.0

    def calculate_impact(
        self,
        weather_context: Optional[DistrictWeatherContext],
        business_type: Optional[str] = None,
    ) -> WeatherActivityImpactAnalysis:
        """
        Evaluate indicative business activity impact from district weather context.
        Gracefully returns an honest unavailable state if weather context is missing or offline.
        """
        # Step 1: Graceful failure isolation if weather data is unavailable
        if (
            not weather_context
            or not weather_context.is_available
            or not weather_context.current
        ):
            return WeatherActivityImpactAnalysis(
                is_available=False,
                activity_impact_score=None,
                activity_impact_label="Unavailable",
                potential_footfall_effect="Weather intelligence unavailable for this district.",
                risk_signals=None,
                business_type_implication=None,
                weather_outlook_3days=[],
                methodology_disclaimer="Indicative weather impact on business activity — not observed footfall or a sales forecast.",
                heuristic_notes=[
                    "Live weather data is currently unavailable from Open-Meteo.",
                    "No fallback numbers or synthetic footfall figures are generated.",
                ],
            )

        cur: CurrentWeatherMetrics = weather_context.current

        # Step 2: Compute Transparent Heuristic Subscores
        precip_subscore, rain_signal = self._evaluate_precipitation(cur.precipitation_mm)
        temp_subscore, heat_signal = self._evaluate_temperature(cur.temperature_c, cur.apparent_temperature_c)
        wind_severity_subscore, outdoor_signal, logistics_signal = self._evaluate_wind_and_severity(
            cur.wind_speed_kmh, cur.weather_code, cur.precipitation_mm
        )

        # Step 3: Weighted Composite Score (0-100)
        composite_score = round(
            (self.WEIGHT_PRECIPITATION * precip_subscore)
            + (self.WEIGHT_TEMPERATURE * temp_subscore)
            + (self.WEIGHT_WIND_SEVERITY * wind_severity_subscore),
            1,
        )

        # Bottleneck / Limiting Factor Heuristic:
        # Severe single-variable extremes (e.g. torrential rain >20mm or heatwaves >44°C)
        # constrain outdoor business activity regardless of mild secondary factors.
        if rain_signal == "Severe":
            composite_score = min(composite_score, 35.0)
        elif rain_signal == "High":
            composite_score = min(composite_score, 48.0)

        if heat_signal == "Severe":
            composite_score = min(composite_score, 45.0)
        elif heat_signal == "High":
            composite_score = min(composite_score, 55.0)

        if wind_severity_subscore <= 20.0:
            composite_score = min(composite_score, 30.0)

        composite_score = max(0.0, min(100.0, composite_score))
        activity_label = self._get_activity_label(composite_score)

        # Refine outdoor activity signal based on overall score
        if composite_score >= 80.0:
            final_outdoor_signal = "Favourable"
        elif composite_score >= 60.0:
            final_outdoor_signal = "Normal"
        elif composite_score >= 40.0:
            final_outdoor_signal = "Moderate Disruption"
        else:
            final_outdoor_signal = "Lower"

        risk_signals = WeatherRiskSignals(
            heat_stress=heat_signal,
            rain_disruption=rain_signal,
            outdoor_activity=final_outdoor_signal,
            logistics_disruption=logistics_signal,
        )

        # Step 4: Qualitative Potential Footfall / Activity Effect (NO fake numbers or percentages)
        potential_footfall = self._evaluate_potential_footfall_effect(composite_score, cur)

        # Step 5: Domain / Sector Specific Qualitative Implication
        business_implication = self._evaluate_business_type_implication(
            business_type=business_type,
            score=composite_score,
            precip_mm=cur.precipitation_mm,
            temp_c=cur.temperature_c,
            wind_kmh=cur.wind_speed_kmh,
            weather_code=cur.weather_code,
        )

        # Step 6: 3-Day Forecast Activity Outlook
        outlook_3days = self._evaluate_forecast_outlook(weather_context.forecast_3days)

        heuristic_notes = [
            "Indicative product heuristic: Evaluates temperature, precipitation, and wind against operational thresholds.",
            f"Weights applied: Rain {int(self.WEIGHT_PRECIPITATION*100)}%, Temperature {int(self.WEIGHT_TEMPERATURE*100)}%, Wind/Severity {int(self.WEIGHT_WIND_SEVERITY*100)}%.",
            "Zero data fabrication: Sourced strictly from Open-Meteo atmospheric readings with no synthetic customer counts.",
        ]

        return WeatherActivityImpactAnalysis(
            is_available=True,
            activity_impact_score=composite_score,
            activity_impact_label=activity_label,
            potential_footfall_effect=potential_footfall,
            risk_signals=risk_signals,
            business_type_implication=business_implication,
            weather_outlook_3days=outlook_3days,
            methodology_disclaimer="Indicative weather impact on business activity — not observed footfall or a sales forecast.",
            heuristic_notes=heuristic_notes,
        )

    # -------------------------------------------------------------------------
    # Subscore Evaluators (Deterministic Heuristics)
    # -------------------------------------------------------------------------

    def _evaluate_precipitation(self, precip_mm: float) -> Tuple[float, str]:
        """
        Evaluate precipitation subscore (0-100) and discrete rain disruption signal.
        - 0 mm: No rain -> 100 subscore, 'None'
        - 0.1 to 2.5 mm: Light drizzle -> 85 subscore, 'Low'
        - 2.5 to 7.5 mm: Moderate rain -> 55 subscore, 'Moderate'
        - 7.5 to 20.0 mm: Heavy rain -> 30 subscore, 'High'
        - > 20.0 mm: Severe downpour / torrential -> 10 subscore, 'Severe'
        """
        if precip_mm <= 0.0:
            return 100.0, "None"
        elif precip_mm <= 2.5:
            return 85.0, "Low"
        elif precip_mm <= 7.5:
            return 55.0, "Moderate"
        elif precip_mm <= 20.0:
            return 30.0, "High"
        else:
            return 10.0, "Severe"

    def _evaluate_temperature(self, temp_c: float, apparent_c: Optional[float] = None) -> Tuple[float, str]:
        """
        Evaluate temperature subscore (0-100) and heat/cold stress level.
        Comfortable ambient temperatures (20°C - 32°C) support normal walk-in activity.
        - 20°C - 32°C: Comfortable -> 100 subscore, 'Low' stress
        - 32°C - 38°C or 12°C - 20°C: Warm / Cool -> 80 subscore, 'Moderate' stress
        - 38°C - 44°C or 5°C - 12°C: Hot / Cold -> 50 subscore, 'High' stress
        - > 44°C or < 5°C: Extreme Heat / Cold -> 20 subscore, 'Severe' stress
        """
        eff_temp = apparent_c if apparent_c is not None else temp_c

        if 20.0 <= temp_c <= 32.0 and eff_temp <= 34.0:
            return 100.0, "Low"
        elif (32.0 < temp_c <= 38.0) or (12.0 <= temp_c < 20.0):
            return 80.0, "Moderate"
        elif (38.0 < temp_c <= 44.0) or (5.0 <= temp_c < 12.0):
            return 50.0, "High"
        else:
            return 20.0, "Severe"

    def _evaluate_wind_and_severity(
        self, wind_kmh: float, weather_code: int, precip_mm: float
    ) -> Tuple[float, str, str]:
        """
        Evaluate wind speed and WMO severe weather phenomena.
        Returns:
            (wind_severity_subscore, outdoor_signal, logistics_signal)
        WMO Codes:
            - 95, 96, 99: Thunderstorm, squall, hail -> severe disruption
            - 45, 48: Dense fog
            - 51-67, 80-82: Drizzle / Rain
        """
        is_thunderstorm = weather_code in (95, 96, 99)
        is_fog = weather_code in (45, 48)

        if wind_kmh < 20.0:
            base_wind = 100.0
            logistics = "Low"
        elif wind_kmh < 35.0:
            base_wind = 75.0
            logistics = "Low" if precip_mm < 5.0 else "Moderate"
        elif wind_kmh < 50.0:
            base_wind = 45.0
            logistics = "Moderate"
        else:
            base_wind = 20.0
            logistics = "High"

        if is_thunderstorm:
            base_wind = min(base_wind, 20.0)
            outdoor = "Lower"
            logistics = "High"
        elif is_fog:
            base_wind = min(base_wind, 50.0)
            outdoor = "Moderate Disruption"
            logistics = "Moderate" if logistics == "Low" else logistics
        elif wind_kmh >= 35.0 or precip_mm >= 7.5:
            outdoor = "Moderate Disruption"
        else:
            outdoor = "Favourable"

        return base_wind, outdoor, logistics

    def _get_activity_label(self, score: float) -> str:
        """Map 0-100 composite score to discrete categorical indicator."""
        if score > self.SCORE_VERY_FAVOURABLE:
            return "Very Favourable"
        elif score > self.SCORE_FAVOURABLE:
            return "Favourable"
        elif score > self.SCORE_NEUTRAL:
            return "Neutral"
        elif score > self.SCORE_DISRUPTIVE:
            return "Potentially Disruptive"
        else:
            return "Highly Disruptive"

    def _evaluate_potential_footfall_effect(
        self, score: float, cur: CurrentWeatherMetrics
    ) -> str:
        """
        Provide qualitative walk-in and customer activity implication.
        ZERO numbers, ZERO percentages, ZERO fabricated customer metrics.
        """
        if cur.temperature_c >= 40.0:
            return "Lower outdoor customer activity likely during peak afternoon heat; morning and late evening trading preferred."
        elif cur.precipitation_mm >= 15.0:
            return "Lower outdoor customer activity likely during periods of steady or heavy rainfall."
        elif score > self.SCORE_VERY_FAVOURABLE:
            return "Favourable conditions for outdoor activity and walk-in customer visits."
        elif score > self.SCORE_FAVOURABLE:
            return "Limited weather-related disruption expected for walk-in traffic and daily routines."
        elif score > self.SCORE_NEUTRAL:
            if cur.temperature_c >= 35.0:
                return "Moderate activity disruption possible; mid-day outdoor walk-ins may shift toward cooler evening hours."
            elif cur.precipitation_mm > 0.0:
                return "Moderate activity disruption possible; intermittent rain may temporarily slow casual walk-ins."
            else:
                return "Moderate activity conditions; overall commercial traffic remains stable with selective outdoor slowdowns."
        elif score > self.SCORE_DISRUPTIVE:
            if cur.precipitation_mm >= 7.5:
                return "Lower outdoor customer activity likely during periods of steady or heavy rainfall."
            elif cur.temperature_c >= 42.0:
                return "Lower outdoor customer activity likely during peak afternoon heat; morning and late evening trading preferred."
            else:
                return "Lower outdoor customer activity likely due to prevailing weather conditions."
        else:
            return "Substantial outdoor activity disruption likely due to severe weather; walk-ins expected to be minimal."

    def _evaluate_business_type_implication(
        self,
        business_type: Optional[str],
        score: float,
        precip_mm: float,
        temp_c: float,
        wind_kmh: float,
        weather_code: int,
    ) -> str:
        """
        Qualitative domain-specific operational guidance tailored to registered business type.
        """
        b_type_norm = (business_type or "").lower().strip()

        # 1. Retail / Trading
        if any(w in b_type_norm for w in ("retail", "trading", "shop", "store", "textile", "handloom", "kirana")):
            if precip_mm >= 7.5:
                return "Outdoor walk-in footfall may be disrupted by rainfall. Consider promoting delivery channels, phone orders, or extending evening store hours."
            elif temp_c >= 38.0:
                return "Afternoon walk-in footfall may slow due to heat stress. Ensure store cooling/ventilation and prepare for evening shopping peaks."
            elif score >= 60.0:
                return "Ambient conditions support regular walk-in retail traffic and open storefront displays."
            else:
                return "Inclement conditions may dampen casual walk-ins. Focus on essential goods inventory and existing customer outreach."

        # 2. Street Food / Food & Beverage
        elif any(w in b_type_norm for w in ("street food", "food", "restaurant", "cafe", "bakery", "sweet", "catering")):
            if precip_mm > 2.5:
                return "Outdoor seating and street-level counter service may be disrupted by rain. Providing covered waiting space or takeaway packaging helps maintain order volume."
            elif temp_c >= 38.0:
                return "High ambient heat demands careful cold-storage management for perishable ingredients and higher beverage demand."
            elif score >= 60.0:
                return "Pleasant weather conditions encourage outdoor dining, quick-service street counters, and evening foot traffic."
            else:
                return "Unfavourable weather may compress walk-in dining hours. Pre-packaged takeaway and scheduled orders can mitigate weather risk."

        # 3. Agriculture / Rural Agribusiness
        elif any(w in b_type_norm for w in ("agri", "farm", "crop", "dairy", "poultry", "fishery", "seed", "fertilizer")):
            if precip_mm >= 15.0:
                return "Heavy rainfall may restrict field operations, input delivery, and farm-to-mandi transport. Protect harvested produce and secure drainage."
            elif precip_mm > 0.0:
                return "Active precipitation provides moisture for sowing and cultivation, though rural dirt roads may slow input supply dispatches."
            elif temp_c >= 40.0:
                return "Intense thermal conditions elevate crop and livestock water stress. Schedule irrigation and transport early in the morning."
            else:
                return "Clear conditions facilitate routine agricultural tasks, harvesting, and unhampered commodity transport."

        # 4. Manufacturing / Workshops
        elif any(w in b_type_norm for w in ("manufactur", "workshop", "fabricat", "factory", "assembly", "carpentry", "metal")):
            if weather_code in (95, 96, 99) or wind_kmh >= 40.0 or precip_mm >= 20.0:
                return "Severe weather may impact worker transit and outdoor raw material staging. Ensure secure warehouse shelter and check power redundancy."
            elif temp_c >= 40.0:
                return "Elevated factory floor temperatures necessitate adequate worker hydration breaks and well-ventilated machinery bays."
            else:
                return "Stable environmental conditions support uninterrupted production schedules and routine freight handling."

        # 5. Local Services / Repair / Personal Care
        elif any(w in b_type_norm for w in ("service", "repair", "saloon", "beauty", "plumb", "electric", "mechanic")):
            if precip_mm >= 7.5 or weather_code in (95, 96, 99):
                return "Field service appointments and on-site customer visits may experience transit delays. Prioritize emergency call-outs and indoor shop repairs."
            elif score >= 60.0:
                return "Favourable conditions support on-schedule field service calls and steady walk-in client appointments."
            else:
                return "Moderate weather slowdowns can be managed by confirming customer bookings in advance and pre-routing technician travel."

        # 6. Tourism / Outdoor / Hospitality
        elif any(w in b_type_norm for w in ("touris", "travel", "outdoor", "hotel", "resort", "guide", "heritage")):
            if precip_mm >= 7.5 or weather_code in (95, 96, 99):
                return "Outdoor sightseeing, ghats/monument visits, and excursions face significant disruption. Encourage indoor cultural activities and flexible itinerary rebooking."
            elif score >= 70.0:
                return "Comfortable weather conditions are highly conducive to outdoor exploration, heritage walking tours, and tourist footfall."
            else:
                return "Variable weather warrants informing travelers about afternoon heat or localized showers to optimize daytime outings."

        # 7. Logistics / Delivery-sensitive Businesses
        elif any(w in b_type_norm for w in ("logistic", "delivery", "courier", "transport", "freight", "cargo")):
            if wind_kmh >= 35.0 or precip_mm >= 10.0:
                return "Elevated wind and rain increase roadway transit times and hazard risks for two-wheeler dispatch. Allocate extra buffer for scheduled deliveries."
            else:
                return "Predictable road conditions support on-time dispatches and standard fleet logistics operations."

        # Default / General Micro-Enterprise
        else:
            if precip_mm >= 10.0:
                return "Rainfall may temporarily affect street-facing walk-ins and local customer travel. Sheltered operations and telephone orders can offset outdoor slowdowns."
            elif temp_c >= 39.0:
                return "Elevated temperatures may dampen daytime commercial outings. Peak customer visits are likely to concentrate in the morning and evening."
            elif score >= 65.0:
                return "Current weather conditions present no significant operational impediments for general micro-enterprise activities."
            else:
                return "Inclement conditions warrant monitoring daily forecasts to adjust local procurement and customer operating hours accordingly."

    def _evaluate_forecast_outlook(
        self, forecast_days: Optional[List[DailyForecastDay]]
    ) -> List[DailyWeatherOutlookItem]:
        """
        Evaluate 3-day daily forecast from Open-Meteo into indicative daily activity impact signals.
        """
        if not forecast_days:
            return []

        outlook_items: List[DailyWeatherOutlookItem] = []
        day_labels = ["Today", "Tomorrow", "Day 3", "Day 4"]

        for idx, day in enumerate(forecast_days[:3]):
            p_sub, r_sig = self._evaluate_precipitation(day.precipitation_sum_mm)
            t_sub, h_sig = self._evaluate_temperature(day.temp_max_c)
            w_sub, out_sig, _ = self._evaluate_wind_and_severity(
                day.wind_speed_max_kmh, day.weather_code, day.precipitation_sum_mm
            )

            daily_score = round(
                (self.WEIGHT_PRECIPITATION * p_sub)
                + (self.WEIGHT_TEMPERATURE * t_sub)
                + (self.WEIGHT_WIND_SEVERITY * w_sub),
                1,
            )

            # Bottleneck Limiting Factor Heuristic for Forecast Days
            if r_sig == "Severe":
                daily_score = min(daily_score, 35.0)
            elif r_sig == "High":
                daily_score = min(daily_score, 48.0)

            if h_sig == "Severe":
                daily_score = min(daily_score, 45.0)
            elif h_sig == "High":
                daily_score = min(daily_score, 55.0)

            if w_sub <= 20.0:
                daily_score = min(daily_score, 30.0)

            daily_score = max(0.0, min(100.0, daily_score))
            daily_label = self._get_activity_label(daily_score)
            lbl = day_labels[idx] if idx < len(day_labels) else day.date

            outlook_items.append(
                DailyWeatherOutlookItem(
                    date=day.date,
                    day_name=lbl,
                    temp_range=f"{round(day.temp_max_c)}° / {round(day.temp_min_c)}°C",
                    precipitation_sum_mm=round(day.precipitation_sum_mm, 1),
                    precipitation_probability_pct=day.precipitation_probability_pct,
                    weather_description=day.weather_description,
                    impact_score=daily_score,
                    impact_label=daily_label,
                    outdoor_activity_signal=out_sig,
                )
            )

        return outlook_items


# Singleton Instance
weather_business_impact_service = WeatherBusinessImpactService()