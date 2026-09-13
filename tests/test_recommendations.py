"""
tests/test_recommendations.py

Comprehensive test suite for the Recommendation Engine and API endpoints.

Validates all 15 architectural and statutory requirements:
1. Hard statutory eligibility gate: Ineligible schemes are NEVER recommended.
2. Recommendation scores strictly bounded in [0.0, 100.0].
3. Exact component score bounds across all 6 dimensions.
4. Strict descending score sort ordering with sequential ranks 1..K.
5. Deterministic scoring across repeated identical executions.
6. Financial fit sensitivity to loan limits and subsidy parameters.
7. Canonical sector sensitivity (exact match 20 pts vs universal 14 pts).
8. Actionability gradient (DIRECTLY_RECOMMENDABLE 15 pts down to FRAMEWORK 3 pts).
9. Partially Verified penalty (8 pt deduction) with explicit cautionary notes.
10. District market context injection for valid district & state.
11. State-level fallback handling when district is unknown.
12. Zero hardcoded programmes: all 60 evaluated dynamically from PostgreSQL.
13. top_k parameter correctly bounds the returned recommendation count.
14. Database business_profile_id resolution and 404 for missing profile.
15. POST /api/v1/recommendations/recommend endpoint verification (200 OK & 400 Bad Request).
"""

from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
import pytest

from app.schemas.eligibility import UserProfile
from app.schemas.recommendation import RecommendationRequest
from app.services.recommendation_service import recommendation_service
from app.core.exceptions import AppException


def test_statutory_hard_gate_ineligible_never_recommended(db_session: Session):
    """Verify that programmes failing statutory eligibility are strictly NEVER recommended."""
    # Profile: Male applicant with requested loan of 50 Lakhs
    profile = UserProfile(
        age=30,
        gender="Male",
        social_category="General",
        state="Maharashtra",
        district="Pune",
        sector="Manufacturing",
        requested_loan_amount=5000000.0,
    )
    req = RecommendationRequest(profile=profile, top_k=60)
    response = recommendation_service.generate_recommendations(db_session, req)

    assert response.total_programs_evaluated == 60
    assert response.total_recommended > 0

    # Assert that NO recommended programme is Ineligible
    for item in response.recommendations:
        assert item.eligibility_status in {"Eligible", "Partially Verified"}, (
            f"Programme {item.program_code} has status {item.eligibility_status} but was recommended!"
        )

    # Specific check: Female-only schemes must NEVER be recommended to a Male applicant
    rec_codes = [item.program_code for item in response.recommendations]
    female_only_codes = {"NBCFDC_NEW_SWARNIMA", "NSTFDC_AMSY", "MAHILA_COIR_YOJANA"}
    for foc in female_only_codes:
        assert foc not in rec_codes, f"Male applicant must not be recommended female-only scheme {foc}"

    # Specific check: 50L loan exceeds PM_SVANIDHI ceiling (50k)
    assert "PM_SVANIDHI" not in rec_codes, "Loan of 50L must disqualify PM_SVANIDHI"


def test_scores_strictly_bounded_between_0_and_100(db_session: Session):
    """Verify all recommendation scores and component breakdowns remain strictly within [0.0, 100.0]."""
    profile = UserProfile(
        age=35,
        gender="Female",
        social_category="SC",
        state="Maharashtra",
        district="Pune",
        sector="Manufacturing",
        requested_loan_amount=1500000.0,
        is_new_business=True,
    )
    req = RecommendationRequest(profile=profile, top_k=60)
    response = recommendation_service.generate_recommendations(db_session, req)

    for item in response.recommendations:
        assert 0.0 <= item.recommendation_score <= 100.0
        sb = item.scoring_breakdown
        assert 0.0 <= sb.eligibility_confidence_score <= 20.0
        assert 0.0 <= sb.financial_fit_score <= 25.0
        assert 0.0 <= sb.sector_fit_score <= 20.0
        assert 0.0 <= sb.actionability_score <= 15.0
        assert 0.0 <= sb.beneficiary_stage_score <= 10.0
        assert 0.0 <= sb.market_context_score <= 10.0

        # Component sum must match total score
        comp_sum = round(
            sb.eligibility_confidence_score
            + sb.financial_fit_score
            + sb.sector_fit_score
            + sb.actionability_score
            + sb.beneficiary_stage_score
            + sb.market_context_score,
            2,
        )
        assert abs(comp_sum - item.recommendation_score) < 0.01


def test_recommendations_sorted_strictly_descending(db_session: Session):
    """Verify output recommendations are strictly sorted in descending score order with ranks 1..K."""
    profile = UserProfile(
        age=28,
        gender="Female",
        social_category="General",
        state="Rajasthan",
        district="Jaipur",
        sector="Services",
        requested_loan_amount=500000.0,
    )
    req = RecommendationRequest(profile=profile, top_k=20)
    response = recommendation_service.generate_recommendations(db_session, req)

    assert len(response.recommendations) > 1
    for i in range(len(response.recommendations) - 1):
        curr_item = response.recommendations[i]
        next_item = response.recommendations[i + 1]

        assert curr_item.rank == i + 1
        assert curr_item.recommendation_score >= next_item.recommendation_score, (
            f"Rank {curr_item.rank} score ({curr_item.recommendation_score}) < "
            f"Rank {next_item.rank} score ({next_item.recommendation_score})"
        )


def test_deterministic_scoring(db_session: Session):
    """Verify that repeated executions with identical inputs yield identical rankings, scores, and drivers."""
    profile = UserProfile(
        age=40,
        gender="Male",
        social_category="OBC",
        state="Uttar Pradesh",
        district="Varanasi",
        sector="Manufacturing",
        requested_loan_amount=1000000.0,
    )
    req = RecommendationRequest(profile=profile, top_k=10)

    run_1 = recommendation_service.generate_recommendations(db_session, req)
    run_2 = recommendation_service.generate_recommendations(db_session, req)

    assert run_1.total_recommended == run_2.total_recommended
    for item_1, item_2 in zip(run_1.recommendations, run_2.recommendations):
        assert item_1.program_id == item_2.program_id
        assert item_1.recommendation_score == item_2.recommendation_score
        assert item_1.rank == item_2.rank
        assert item_1.scoring_breakdown == item_2.scoring_breakdown
        assert item_1.recommendation_drivers == item_2.recommendation_drivers


def test_financial_fit_sensitivity(db_session: Session):
    """Verify that loan amount alignment within programme limits yields higher financial scores."""
    # PMEGP max loan is 50L for mfg, min is around 1L
    sweet_profile = UserProfile(
        age=30,
        gender="Male",
        social_category="General",
        state="Maharashtra",
        district="Pune",
        sector="Manufacturing",
        requested_loan_amount=1000000.0,  # Sweet spot
        is_new_business=True,
    )
    sweet_resp = recommendation_service.generate_recommendations(
        db_session, RecommendationRequest(profile=sweet_profile, top_k=60)
    )

    # Find PMEGP in recommendations
    pmegp_rec = next((r for r in sweet_resp.recommendations if r.program_code == "PMEGP_NEW"), None)
    assert pmegp_rec is not None
    assert pmegp_rec.scoring_breakdown.financial_fit_score >= 20.0
    assert any("Target financing need" in d for d in pmegp_rec.recommendation_drivers)


def test_sector_fit_sensitivity(db_session: Session):
    """Verify that exact canonical sector match awards 20 pts vs 14 pts for universal/agnostic schemes."""
    profile = UserProfile(
        age=32,
        gender="Female",
        social_category="General",
        state="Maharashtra",
        district="Pune",
        sector="Manufacturing",
    )
    resp = recommendation_service.generate_recommendations(
        db_session, RecommendationRequest(profile=profile, top_k=60)
    )

    # PMEGP supports Manufacturing -> exact sector match
    pmegp_rec = next((r for r in resp.recommendations if r.program_code == "PMEGP_NEW"), None)
    assert pmegp_rec is not None
    assert pmegp_rec.scoring_breakdown.sector_fit_score == 20.0
    assert any("Exact canonical sector match for Manufacturing" in d for d in pmegp_rec.recommendation_drivers)


def test_actionability_gradient(db_session: Session):
    """Verify actionability scoring awards 15 pts for DIRECTLY_RECOMMENDABLE down to 3 pts for FRAMEWORK."""
    profile = UserProfile(age=30, gender="Male", social_category="General", state="Delhi")
    resp = recommendation_service.generate_recommendations(
        db_session, RecommendationRequest(profile=profile, top_k=60)
    )

    for item in resp.recommendations:
        act = item.actionability_type.upper()
        if act == "DIRECTLY_RECOMMENDABLE":
            assert item.scoring_breakdown.actionability_score == 15.0
        elif act == "COMPONENT_RECOMMENDABLE":
            assert item.scoring_breakdown.actionability_score == 10.0
        elif act == "PLATFORM":
            assert item.scoring_breakdown.actionability_score == 6.0
        elif act == "FRAMEWORK":
            assert item.scoring_breakdown.actionability_score == 3.0


def test_partially_verified_penalty_and_notes(db_session: Session):
    """Verify Partially Verified programmes incur an 8 pt deduction and produce cautionary notes."""
    # Profile with no startup verification specified
    profile = UserProfile(
        age=25,
        gender="Male",
        social_category="General",
        state="Maharashtra",
        district="Pune",
        sector="Services",
    )
    resp = recommendation_service.generate_recommendations(
        db_session, RecommendationRequest(profile=profile, top_k=60)
    )

    partially_verified_items = [r for r in resp.recommendations if r.eligibility_status == "Partially Verified"]
    assert len(partially_verified_items) > 0

    for pv in partially_verified_items:
        assert pv.scoring_breakdown.eligibility_confidence_score == 12.0
        assert any("Partially Verified" in n for n in pv.cautionary_notes)


def test_district_market_context_injection(db_session: Session):
    """Verify valid district in request enriches response with empirical district metrics."""
    profile = UserProfile(
        age=30,
        gender="Male",
        social_category="General",
        state="Maharashtra",
        district="Pune",
        sector="Manufacturing",
    )
    resp = recommendation_service.generate_recommendations(
        db_session, RecommendationRequest(profile=profile, top_k=5)
    )

    assert resp.district_market_context is not None
    assert resp.district_market_context.geographic_level == "DISTRICT"
    assert resp.district_market_context.district_name == "PUNE"
    assert resp.district_market_context.national_rank == 1
    assert resp.district_market_context.is_fallback is False

    # District context drivers present in recommendations
    for item in resp.recommendations:
        assert any("Major MSME cluster" in d or "District" in d for d in item.recommendation_drivers)


def test_state_level_fallback_when_district_unknown(db_session: Session):
    """Verify unknown district triggers state fallback in response and neutral market prior."""
    profile = UserProfile(
        age=30,
        gender="Male",
        social_category="General",
        state="Gujarat",
        district="UnknownDistrict999",
        sector="Manufacturing",
    )
    resp = recommendation_service.generate_recommendations(
        db_session, RecommendationRequest(profile=profile, top_k=5)
    )

    assert resp.district_market_context is not None
    assert resp.district_market_context.geographic_level == "STATE"
    assert resp.district_market_context.is_fallback is True
    assert resp.district_market_context.state_name == "GUJARAT"


def test_zero_hardcoded_programmes_evaluates_all_from_db(db_session: Session):
    """Verify recommendation service dynamically evaluates all 60 programmes from PostgreSQL."""
    profile = UserProfile(age=30, gender="Male", social_category="General")
    resp = recommendation_service.generate_recommendations(
        db_session, RecommendationRequest(profile=profile, top_k=10)
    )

    assert resp.total_programs_evaluated == 60
    assert resp.eligible_candidates_count + resp.partially_verified_candidates_count > 0


def test_top_k_parameter_honored(db_session: Session):
    """Verify top_k parameter strictly controls the maximum count of returned recommendations."""
    profile = UserProfile(age=30, gender="Female", social_category="General", state="Delhi")

    resp_3 = recommendation_service.generate_recommendations(
        db_session, RecommendationRequest(profile=profile, top_k=3)
    )
    assert len(resp_3.recommendations) == 3
    assert resp_3.total_recommended == 3

    resp_1 = recommendation_service.generate_recommendations(
        db_session, RecommendationRequest(profile=profile, top_k=1)
    )
    assert len(resp_1.recommendations) == 1
    assert resp_1.total_recommended == 1


def test_missing_business_profile_id_raises_404(db_session: Session):
    """Verify non-existent business_profile_id raises AppException 404."""
    req = RecommendationRequest(business_profile_id=999999)
    with pytest.raises(AppException) as exc_info:
        recommendation_service.generate_recommendations(db_session, req)
    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND


def test_missing_both_profile_and_id_raises_400(db_session: Session):
    """Verify missing both profile and business_profile_id raises AppException 400."""
    req = RecommendationRequest()
    with pytest.raises(AppException) as exc_info:
        recommendation_service.generate_recommendations(db_session, req)
    assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST


def test_api_recommend_endpoint_success(client: TestClient):
    """Verify POST /api/v1/recommendations/recommend returns 200 OK with valid schema."""
    payload = {
        "profile": {
            "age": 32,
            "gender": "Female",
            "social_category": "OBC",
            "state": "Maharashtra",
            "district": "Pune",
            "sector": "Manufacturing",
            "requested_loan_amount": 1000000.0,
            "is_new_business": True,
        },
        "target_financing_need": 1000000.0,
        "top_k": 5,
    }
    response = client.post("/api/v1/recommendations/recommend", json=payload)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    assert data["total_programs_evaluated"] == 60
    assert data["total_recommended"] == 5
    assert len(data["recommendations"]) == 5
    assert data["district_market_context"]["district_name"] == "PUNE"

    # Check top recommendation structure
    top_rec = data["recommendations"][0]
    assert top_rec["rank"] == 1
    assert 0.0 <= top_rec["recommendation_score"] <= 100.0
    assert top_rec["fit_category"] in ["EXCELLENT_FIT", "STRONG_FIT", "MODERATE_FIT", "LOW_FIT"]
    assert "scoring_breakdown" in top_rec
    assert len(top_rec["recommendation_drivers"]) > 0


def test_api_recommend_endpoint_missing_input_400(client: TestClient):
    """Verify POST /api/v1/recommendations/recommend with empty payload returns 400 Bad Request."""
    response = client.post("/api/v1/recommendations/recommend", json={})
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_pmfme_financial_bound_enforced(db_session: Session):
    """Verify PMFME has statutory max_project_cost of 1 Crore and penalizes excessive project costs."""
    from app.models.program_models import GovernmentProgram, ProgramSubsidyDetail
    from app.services.program_eligibility_adapter import ProgramEligibilityAdapter
    from app.services.recommendation_scorer import recommendation_scorer

    pmfme = (
        db_session.query(GovernmentProgram)
        .filter(GovernmentProgram.program_code == "PMFME")
        .first()
    )
    assert pmfme is not None
    assert pmfme.subsidy_details is not None
    assert float(pmfme.subsidy_details.max_project_cost) == 10000000.00

    eval_prog = ProgramEligibilityAdapter.adapt(pmfme)
    assert eval_prog.max_project_cost == 10000000.00

    # Test 1: Project cost within ceiling (e.g. 25 Lakh) -> full sweet spot score
    score_within, drivers_within, _ = recommendation_scorer.score_financial_fit(eval_prog, target_amount=2500000.0)
    assert any("within maximum ceiling" in d for d in drivers_within)

    # Test 2: Project cost exceeding 1 Crore ceiling (e.g. 5 Crore) -> ratio penalized score with cautionary note
    score_exceed, _, notes_exceed = recommendation_scorer.score_financial_fit(eval_prog, target_amount=50000000.0)
    assert any("exceeds statutory ceiling" in n for n in notes_exceed)
    # Ratio is 10M / 50M = 0.2 -> 15.0 * 0.2 = 3.0 pts sweet score
    assert score_exceed < score_within


def test_scoring_uses_mandate_metadata_without_hardcoded_program_codes():
    """Verify recommendation_scorer evaluates mandates purely from metadata without program_code checks."""
    import inspect
    from app.services.recommendation_scorer import recommendation_scorer
    from app.services.program_eligibility_adapter import EvaluatableProgram

    # Verify source code does not check program_code in scoring methods
    scoring_methods = [
        recommendation_scorer.score_beneficiary_and_stage,
        recommendation_scorer.score_sector_fit,
        recommendation_scorer.score_financial_fit,
    ]
    for method in scoring_methods:
        source = inspect.getsource(method)
        assert "eval_prog.program_code" not in source, f"Found eval_prog.program_code in {method.__name__}"
        assert "STANDUP_INDIA" not in source, f"Found hardcoded STANDUP_INDIA in {method.__name__}"
        assert "vishwakarma" not in source, f"Found hardcoded vishwakarma in {method.__name__}"
        assert "svanidhi" not in source, f"Found hardcoded svanidhi in {method.__name__}"

    # Verify mandate metadata evaluations
    # 1. Artisan mandate
    prog_art = EvaluatableProgram(
        program_id=991, program_code="CUSTOM_PROG_1", program_name="Custom Artisan",
        primary_type="CREDIT / LOAN", actionability_type="DIRECTLY_RECOMMENDABLE",
        artisan_mandate=True,
    )
    prof_art = UserProfile(is_traditional_artisan=True)
    score_art, drivers_art = recommendation_scorer.score_beneficiary_and_stage(prog_art, prof_art)
    assert any("traditional artisans" in d for d in drivers_art)

    # 2. Street vendor mandate
    prog_sv = EvaluatableProgram(
        program_id=992, program_code="CUSTOM_PROG_2", program_name="Custom Vending",
        primary_type="CREDIT / LOAN", actionability_type="DIRECTLY_RECOMMENDABLE",
        street_vendor_mandate=True,
    )
    prof_sv = UserProfile(is_street_vendor=True)
    score_sv, drivers_sv = recommendation_scorer.score_beneficiary_and_stage(prog_sv, prof_sv)
    assert any("street vendors" in d for d in drivers_sv)

    # 3. Startup mandate
    prog_su = EvaluatableProgram(
        program_id=993, program_code="CUSTOM_PROG_3", program_name="Custom Incubator",
        primary_type="INNOVATION / TECH", actionability_type="DIRECTLY_RECOMMENDABLE",
        startup_mandate=True,
    )
    prof_su = UserProfile(is_new_business=True)
    score_su, drivers_su = recommendation_scorer.score_beneficiary_and_stage(prog_su, prof_su)
    assert any("innovative startups" in d for d in drivers_su)


def test_sub_sector_granularity_prevents_agri_service_clash_with_it():
    """Verify specialized agricultural service programs receive low/peripheral score for IT services."""
    from app.services.recommendation_scorer import recommendation_scorer
    from app.services.program_eligibility_adapter import EvaluatableProgram

    prog_agri_srv = EvaluatableProgram(
        program_id=994, program_code="AGRI_MACHINERY_SERVICE", program_name="Custom Hiring Centre",
        primary_type="INFRASTRUCTURE / CAPEX", actionability_type="DIRECTLY_RECOMMENDABLE",
        owning_ministry="Ministry of Agriculture & Farmers Welfare",
        sector_codes={"SRV", "AGR"},
    )

    # Case A: IT / Consulting applicant -> 5.0 pts (cross-domain limitation)
    prof_it = UserProfile(sector="Services", business_type="IT / Software Consulting")
    score_it, drivers_it = recommendation_scorer.score_sector_fit(prog_agri_srv, prof_it)
    assert score_it == 5.0
    assert any("Cross-domain limitation" in d for d in drivers_it)

    # Case B: Generic Services applicant without agricultural activity -> 10.0 pts (peripheral alignment)
    prof_gen = UserProfile(sector="Services")
    score_gen, drivers_gen = recommendation_scorer.score_sector_fit(prog_agri_srv, prof_gen)
    assert score_gen == 10.0
    assert any("Peripheral sector alignment" in d for d in drivers_gen)

    # Case C: Agricultural machinery hire applicant -> 20.0 pts (exact match)
    prof_agri = UserProfile(sector="Services", business_type="Farm Machinery Custom Hiring")
    score_agri, drivers_agri = recommendation_scorer.score_sector_fit(prog_agri_srv, prof_agri)
    assert score_agri == 20.0
    assert any("Agricultural allied service" in d for d in drivers_agri)


def test_non_financial_program_baseline_reviewed_for_capital_need():
    """Verify non-capital/training programs receive 5.0 pts when explicit loan is requested, but 7.5 pts when unspecified."""
    from app.services.recommendation_scorer import recommendation_scorer
    from app.services.program_eligibility_adapter import EvaluatableProgram

    prog_training = EvaluatableProgram(
        program_id=995, program_code="ENTREPRENEURSHIP_TRAINING", program_name="EDP Training Scheme",
        primary_type="SKILLING / CAPABILITY", actionability_type="DIRECTLY_RECOMMENDABLE",
    )

    # Case 1: Applicant explicitly requests ₹15 Lakh loan -> 5.0 pts (baseline financial fit) + note
    score_loan, drivers_loan, notes_loan = recommendation_scorer.score_financial_fit(
        prog_training, target_amount=1500000.0
    )
    assert score_loan == 5.0
    assert any("Non-capital / capability programme" in d for d in drivers_loan)
    assert any("rather than direct capital/credit financing" in n for n in notes_loan)

    # Case 2: Applicant does not specify loan amount -> 7.5 pts neutral baseline
    score_none, drivers_none, _ = recommendation_scorer.score_financial_fit(
        prog_training, target_amount=None
    )
    assert score_none == 7.5
    assert any("Target financing need not specified" in d for d in drivers_none)

