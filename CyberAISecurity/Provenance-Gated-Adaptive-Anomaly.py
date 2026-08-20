#!/usr/bin/env python3
"""
Provenance-Gated Adaptive Anomaly Detection
Single-file defensive cybersecurity algorithm.

Features:
- Behavioral baseline per agent
- Tool novelty scoring
- Request-rate anomaly scoring
- Blast-radius anomaly scoring
- Circadian deviation scoring
- Conformal-style empirical p-value calibration
- Online Page-Hinkley-style change detection
- Provenance / fingerprint security gate
- Controlled learning to reduce baseline poisoning
- States: LEARNING, ACTIVE, QUARANTINE, FROZEN
- Actions: ALLOW, MONITOR, RESTRICT, BLOCK
- Built-in demo with visible terminal output

Run:
    python3 Provenance-Gated-Adaptive-Anomaly-Detection.py
"""

from __future__ import annotations

from dataclasses import dataclass, field
from collections import deque
from enum import Enum
from typing import Deque
import statistics


# ENUMS

class State(Enum):
    LEARNING = "learning"
    ACTIVE = "active"
    QUARANTINE = "quarantine"
    FROZEN = "frozen"


class Action(Enum):
    ALLOW = "allow"
    MONITOR = "monitor"
    RESTRICT = "restrict"
    BLOCK = "block"


# DATA MODELS

@dataclass
class SecurityEvent:
    agent_id: str
    timestamp: float
    tool: str
    request_rate: float
    blast_radius: float
    hour: int
    fingerprint: str
    attested: bool = True


@dataclass
class Baseline:
    fingerprint: str

    state: State = State.LEARNING

    tools_seen: set[str] = field(default_factory=set)

    rate_history: Deque[float] = field(
        default_factory=lambda: deque(maxlen=256)
    )

    blast_history: Deque[float] = field(
        default_factory=lambda: deque(maxlen=256)
    )

    hour_history: Deque[int] = field(
        default_factory=lambda: deque(maxlen=256)
    )

    score_history: Deque[float] = field(
        default_factory=lambda: deque(maxlen=2048)
    )

    total_events: int = 0

    # Online change detector state
    running_mean: float = 0.0
    cumulative_change: float = 0.0


@dataclass
class Decision:
    agent_id: str
    risk_score: float
    p_value: float
    change_detected: bool
    state: State
    action: Action
    should_learn: bool
    feature_scores: dict[str, float]
    reasons: list[str]


# CORE ALGORITHM

class AdaptiveSentinel:
    """
    Provenance-gated adaptive behavioral anomaly detector.

    Security principle:
        Score first.
        Gate adaptation second.
        Learn only if authorized.

    This prevents suspicious observations from automatically
    redefining what the system considers "normal".
    """

    def __init__(
        self,
        warmup_events: int = 10,
        anomaly_threshold: float = 0.05,
        change_threshold: float = 6.0,
    ):
        self.baselines: dict[str, Baseline] = {}

        self.warmup_events = warmup_events
        self.anomaly_threshold = anomaly_threshold
        self.change_threshold = change_threshold

    # Statistical utility
    
    @staticmethod
    def safe_zscore(
        value: float,
        history: Deque[float],
        minimum_history: int = 5,
    ) -> float:

        if len(history) < minimum_history:
            return 0.0

        mean = statistics.mean(history)
        std = statistics.pstdev(history)

        if std < 1e-8:
            return 0.0 if abs(value - mean) < 1e-8 else 5.0

        return abs(value - mean) / std


    # 1. Behavioral scoring
   
    def score_event(
        self,
        baseline: Baseline,
        event: SecurityEvent,
    ) -> tuple[float, dict[str, float]]:

        # New tool/capability not seen in baseline
        tool_novelty = (
            1.0
            if baseline.tools_seen
            and event.tool not in baseline.tools_seen
            else 0.0
        )

        request_rate_score = self.safe_zscore(
            event.request_rate,
            baseline.rate_history,
        )

        blast_radius_score = self.safe_zscore(
            event.blast_radius,
            baseline.blast_history,
        )

        # Simple circadian deviation
        if baseline.hour_history:
            average_hour = statistics.mean(baseline.hour_history)
            circadian_score = min(
                abs(event.hour - average_hour) / 12.0,
                1.0,
            )
        else:
            circadian_score = 0.0

        feature_scores = {
            "tool_novelty": tool_novelty,
            "request_rate": request_rate_score,
            "blast_radius": blast_radius_score,
            "circadian": circadian_score,
        }

        # Weighted risk / surprisal score
        risk_score = (
            1.00 * tool_novelty
            + 0.35 * request_rate_score
            + 0.90 * blast_radius_score
            + 0.30 * circadian_score
        )

        return risk_score, feature_scores

    
    # 2. Empirical conformal-style calibration

    def calculate_p_value(
        self,
        baseline: Baseline,
        score: float,
    ) -> float:

        if len(baseline.score_history) < self.warmup_events:
            return 1.0

        greater_or_equal = sum(
            historical_score >= score
            for historical_score in baseline.score_history
        )

        return (
            greater_or_equal + 1
        ) / (
            len(baseline.score_history) + 1
        )

  
    # 3. Online change detection

    def detect_change(
        self,
        baseline: Baseline,
        score: float,
    ) -> bool:

        n = baseline.total_events + 1

        baseline.running_mean += (
            score - baseline.running_mean
        ) / n

        # Page-Hinkley-like cumulative deviation
        delta = score - baseline.running_mean - 0.05

        baseline.cumulative_change = max(
            0.0,
            baseline.cumulative_change + delta,
        )

        if baseline.cumulative_change > self.change_threshold:
            baseline.cumulative_change = 0.0
            return True

        return False

    # 4. Adaptation security gate
   
    def gate(
        self,
        baseline: Baseline,
        event: SecurityEvent,
        p_value: float,
        change_detected: bool,
    ) -> tuple[State, bool, list[str]]:

        reasons: list[str] = []

        fingerprint_changed = (
            event.fingerprint != baseline.fingerprint
        )

        # SECURITY INVARIANT:
        # Never trust an unattested identity/config mutation,
        # even during warmup.
        if fingerprint_changed and not event.attested:
            reasons.append("unattested fingerprint change")
            return State.FROZEN, False, reasons

        # Warmup comes after hard provenance checks.
        if baseline.total_events < self.warmup_events:
            reasons.append("baseline learning")
            return State.LEARNING, True, reasons

        # Persistent anomaly / drift
        if (
            p_value <= self.anomaly_threshold
            and change_detected
        ):
            reasons.append("persistent behavioral drift")
            return State.FROZEN, False, reasons

        # Attested config change still gets quarantined.
        if fingerprint_changed:
            reasons.append("attested fingerprint change")
            baseline.fingerprint = event.fingerprint
            return State.QUARANTINE, False, reasons

        # Point anomaly
        if p_value <= self.anomaly_threshold:
            reasons.append("point anomaly")
            return State.QUARANTINE, False, reasons

        reasons.append("behavior consistent with baseline")
        return State.ACTIVE, True, reasons

    
    # 5. Response policy
    
    @staticmethod
    def select_action(
        state: State,
        p_value: float,
    ) -> Action:

        if state == State.FROZEN:
            return Action.BLOCK

        if state == State.QUARANTINE:
            return Action.RESTRICT

        if p_value < 0.20:
            return Action.MONITOR

        return Action.ALLOW

    # 6. Controlled baseline learning
   
    @staticmethod
    def learn(
        baseline: Baseline,
        event: SecurityEvent,
        score: float,
    ) -> None:

        baseline.tools_seen.add(event.tool)
        baseline.rate_history.append(event.request_rate)
        baseline.blast_history.append(event.blast_radius)
        baseline.hour_history.append(event.hour)
        baseline.score_history.append(score)


    # MAIN DECISION FUNCTION
   
    def observe(
        self,
        event: SecurityEvent,
    ) -> Decision:

        # Initialize identity baseline
        baseline = self.baselines.get(event.agent_id)

        if baseline is None:
            baseline = Baseline(
                fingerprint=event.fingerprint
            )
            self.baselines[event.agent_id] = baseline

        # 1. Score BEFORE mutation
        risk_score, feature_scores = self.score_event(
            baseline,
            event,
        )

        # 2. Calibrate
        p_value = self.calculate_p_value(
            baseline,
            risk_score,
        )

        # 3. Detect behavioral drift
        change_detected = self.detect_change(
            baseline,
            risk_score,
        )

        # 4. Decide whether adaptation is allowed
        state, should_learn, reasons = self.gate(
            baseline,
            event,
            p_value,
            change_detected,
        )

        baseline.state = state

        # 5. Controlled adaptation
        if should_learn:
            self.learn(
                baseline,
                event,
                risk_score,
            )
        else:
            reasons.append("baseline adaptation refused")

        baseline.total_events += 1

        # 6. Select response
        action = self.select_action(
            state,
            p_value,
        )

        return Decision(
            agent_id=event.agent_id,
            risk_score=risk_score,
            p_value=p_value,
            change_detected=change_detected,
            state=state,
            action=action,
            should_learn=should_learn,
            feature_scores=feature_scores,
            reasons=reasons,
        )


# DEMO DATA

def build_demo_events() -> list[SecurityEvent]:
    """
    Generates normal activity followed by suspicious behavior.
    """

    events: list[SecurityEvent] = []

    # Build a normal baseline.
    for i in range(12):
        events.append(
            SecurityEvent(
                agent_id="agent-001",
                timestamp=float(i + 1),
                tool="search",
                request_rate=5 + (i % 3),
                blast_radius=2 + (i % 2),
                hour=9 + (i % 2),
                fingerprint="build-A",
                attested=True,
            )
        )

    # Mild unusual activity
    events.append(
        SecurityEvent(
            agent_id="agent-001",
            timestamp=13.0,
            tool="reporting",
            request_rate=12,
            blast_radius=5,
            hour=11,
            fingerprint="build-A",
            attested=True,
        )
    )

    # Strong behavioral anomaly, same trusted build
    events.append(
        SecurityEvent(
            agent_id="agent-001",
            timestamp=14.0,
            tool="database_admin",
            request_rate=80,
            blast_radius=90,
            hour=3,
            fingerprint="build-A",
            attested=True,
        )
    )

    # Unattested identity/config mutation
    events.append(
        SecurityEvent(
            agent_id="agent-001",
            timestamp=15.0,
            tool="database_admin",
            request_rate=95,
            blast_radius=100,
            hour=2,
            fingerprint="unknown-build",
            attested=False,
        )
    )

    return events


# OUTPUT

def print_decision(
    number: int,
    event: SecurityEvent,
    decision: Decision,
) -> None:

    print()
    print("=" * 72)
    print(f"EVENT #{number}")
    print("=" * 72)

    print(f"Agent:              {event.agent_id}")
    print(f"Timestamp:          {event.timestamp}")
    print(f"Tool:               {event.tool}")
    print(f"Request rate:       {event.request_rate}")
    print(f"Blast radius:       {event.blast_radius}")
    print(f"Hour:               {event.hour}")
    print(f"Fingerprint:        {event.fingerprint}")
    print(f"Attested:           {event.attested}")

    print()
    print("FEATURE SCORES")
    print("-" * 72)

    for feature, value in decision.feature_scores.items():
        print(f"{feature:20s}: {value:.4f}")

    print()
    print("DECISION")
    print("-" * 72)

    print(f"Risk score:         {decision.risk_score:.4f}")
    print(f"P-value:            {decision.p_value:.6f}")
    print(f"Change detected:    {decision.change_detected}")
    print(f"State:              {decision.state.value.upper()}")
    print(f"Action:             {decision.action.value.upper()}")
    print(f"Learn from event:   {decision.should_learn}")
    print(f"Reasons:            {', '.join(decision.reasons)}")


# MAIN

def main() -> None:

    print()
    print("PROVENANCE-GATED ADAPTIVE ANOMALY DETECTION")
    print("=" * 72)
    print("Defensive behavioral security algorithm")
    print("Score -> Calibrate -> Detect Change -> Gate -> Learn/Refuse -> Respond")
    print("=" * 72)

    sentinel = AdaptiveSentinel(
        warmup_events=10,
        anomaly_threshold=0.05,
        change_threshold=6.0,
    )

    events = build_demo_events()

    for number, event in enumerate(events, start=1):
        decision = sentinel.observe(event)

        # Print every event so execution is visibly obvious.
        print_decision(
            number,
            event,
            decision,
        )

    print()
    print("=" * 72)
    print("FINAL BASELINE STATE")
    print("=" * 72)

    for agent_id, baseline in sentinel.baselines.items():
        print(f"Agent:              {agent_id}")
        print(f"State:              {baseline.state.value.upper()}")
        print(f"Fingerprint:        {baseline.fingerprint}")
        print(f"Events observed:    {baseline.total_events}")
        print(f"Trusted tools:      {sorted(baseline.tools_seen)}")
        print(f"Baseline samples:   {len(baseline.score_history)}")

    print()
    print("Demo complete.")
    print()


if __name__ == "__main__":
    main()
