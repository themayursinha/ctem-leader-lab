from data import ASSETS, BUSINESS_SERVICES, EXPOSURES, REMEDIATION_ACTIONS
from models import Asset, Decision, Exposure, PrioritizedExposure, ScoreDriver


CRITICALITY_POINTS = {"Low": 4, "Medium": 10, "High": 16, "Critical": 22}
REACHABILITY_POINTS = {"Isolated": 0, "Indirect": 7, "Direct": 13}
PROXIMITY_POINTS = {"None": 0, "Adjacent": 5, "Same Service": 8, "Crown Jewel": 14}
EFFORT_POINTS = {"High": 1, "Medium": 3, "Low": 5}
EVIDENCE_POINTS = {"Low": 1, "Medium": 4, "High": 7}


def _asset_map() -> dict[str, Asset]:
    return {asset.id: asset for asset in ASSETS}


def _service_names() -> dict[str, str]:
    return {service.id: service.name for service in BUSINESS_SERVICES}


def _remediation_map() -> dict[str, str]:
    return {action.exposure_id: action.sla for action in REMEDIATION_ACTIONS}


def score_exposure(exposure: Exposure, asset: Asset) -> tuple[int, list[ScoreDriver]]:
    drivers = [
        ScoreDriver(
            name="Business criticality",
            value=CRITICALITY_POINTS[asset.criticality],
            explanation=f"{asset.name} supports a {asset.criticality.lower()} business service.",
        ),
        ScoreDriver(
            name="Internet reachability",
            value=REACHABILITY_POINTS[asset.reachable_from_internet],
            explanation=f"Reachability is {asset.reachable_from_internet.lower()} from external entry points.",
        ),
        ScoreDriver(
            name="Known exploitation",
            value=18 if exposure.kev_signal else 0,
            explanation="Known exploited signal present." if exposure.kev_signal else "No known exploited signal in the scenario.",
        ),
        ScoreDriver(
            name="Exploit likelihood",
            value=round(exposure.epss_probability * 16),
            explanation=f"EPSS-style probability is {exposure.epss_probability:.0%}.",
        ),
        ScoreDriver(
            name="Identity or privilege amplification",
            value=exposure.identity_risk * 3,
            explanation=f"Identity amplification rated {exposure.identity_risk}/5.",
        ),
        ScoreDriver(
            name="Control weakness",
            value=exposure.control_gap * 3,
            explanation=f"Preventive or detective control gap rated {exposure.control_gap}/5.",
        ),
        ScoreDriver(
            name="Attack-path proximity",
            value=PROXIMITY_POINTS[exposure.attack_path_proximity],
            explanation=f"Exposure proximity to crown jewels is {exposure.attack_path_proximity.lower()}.",
        ),
        ScoreDriver(
            name="Remediation feasibility",
            value=EFFORT_POINTS[exposure.remediation_effort],
            explanation=f"Remediation effort is {exposure.remediation_effort.lower()}, shaping near-term mobilization.",
        ),
        ScoreDriver(
            name="Evidence confidence",
            value=EVIDENCE_POINTS[exposure.evidence_confidence],
            explanation=f"Validation evidence confidence is {exposure.evidence_confidence.lower()}.",
        ),
    ]
    score = min(100, sum(driver.value for driver in drivers))
    return score, drivers


def decision_for_score(score: int) -> Decision:
    if score >= 75:
        return "Act"
    if score >= 55:
        return "Attend"
    if score >= 35:
        return "Monitor"
    return "Track"


def rationale_for(exposure: Exposure, asset: Asset, decision: Decision, service_name: str) -> str:
    if decision == "Act":
        return (
            f"Act because {exposure.title.lower()} has credible evidence, meaningful attacker utility, "
            f"and a plausible path into {service_name}."
        )
    if decision == "Attend":
        return (
            f"Attend because {exposure.title.lower()} affects a scoped service and needs leadership-backed "
            "coordination before the exposure ages into unacceptable risk."
        )
    if decision == "Monitor":
        return (
            f"Monitor because the issue is real, but current evidence does not show an urgent path "
            f"from {asset.name} to a crown-jewel outcome."
        )
    return (
        f"Track through normal maintenance because {asset.name} is isolated or low-context for the current CTEM sprint."
    )


def why_it_matters(exposure: Exposure, asset: Asset, service_name: str) -> str:
    if exposure.attack_path_proximity == "Crown Jewel":
        return f"This exposure can influence a crown-jewel path for {service_name}, so backlog age is the wrong primary metric."
    if exposure.identity_risk >= 4:
        return "Identity weakness can turn a contained technical issue into cross-service access."
    if exposure.kev_signal:
        return "Known exploitation changes the response from severity triage to threat response."
    if asset.reachable_from_internet == "Isolated":
        return "Validation currently shows isolation, which lets leaders protect remediation capacity for higher-risk paths."
    return "The exposure is useful context for posture management, but it is not the top path to business harm."


def prioritized_exposures() -> list[PrioritizedExposure]:
    assets = _asset_map()
    services = _service_names()
    slas = _remediation_map()
    prioritized = []

    for exposure in EXPOSURES:
        asset = assets[exposure.asset_id]
        service_name = services[asset.service_id]
        score, drivers = score_exposure(exposure, asset)
        decision = decision_for_score(score)
        prioritized.append(
            PrioritizedExposure(
                exposure_id=exposure.id,
                asset_id=asset.id,
                service_id=asset.service_id,
                title=exposure.title,
                description=exposure.description,
                exposure_type=exposure.exposure_type,
                severity=exposure.severity,
                decision=decision,
                ctem_score=score,
                rationale=rationale_for(exposure, asset, decision, service_name),
                why_it_matters=why_it_matters(exposure, asset, service_name),
                next_action=exposure.suggested_action,
                score_drivers=drivers,
                validation_evidence=exposure.evidence,
                owner=asset.owner,
                sla=slas.get(exposure.id, "Not assigned"),
                source=exposure.source,
                source_reference=exposure.source_reference,
                first_seen=exposure.first_seen,
                last_seen=exposure.last_seen,
                validated_at=exposure.validated_at,
                evidence_owner=exposure.evidence_owner,
                evidence_expires_at=exposure.evidence_expires_at,
            )
        )

    return sorted(prioritized, key=lambda item: item.ctem_score, reverse=True)
