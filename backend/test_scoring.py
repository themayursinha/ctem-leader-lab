from data import DATA
from scoring import decision_for_score, prioritized_exposures


def test_medium_identity_secret_outranks_isolated_high_cve():
    DATA.reset()
    prioritized = prioritized_exposures()
    by_id = {item.exposure_id: item for item in prioritized}

    assert by_id["exp-ci-token"].ctem_score > by_id["exp-dev-wiki-cve"].ctem_score
    assert by_id["exp-ci-token"].decision == "Act"
    assert by_id["exp-dev-wiki-cve"].decision == "Track"


def test_prioritized_exposure_contains_leader_rationale_and_owner():
    DATA.reset()
    top = prioritized_exposures()[0]

    assert top.rationale
    assert top.why_it_matters
    assert top.next_action
    assert top.validation_evidence
    assert top.owner
    assert top.sla
    assert top.score_drivers


def test_decision_thresholds_are_stable():
    assert decision_for_score(90) == "Act"
    assert decision_for_score(60) == "Attend"
    assert decision_for_score(40) == "Monitor"
    assert decision_for_score(20) == "Track"
