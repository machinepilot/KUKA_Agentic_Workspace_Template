"""Seed rule catalog for safety_lint.

Each rule is a simple regex-based check over the lines of a .src file. A rule
returns a list of (line_no, column, message, fix_hint). The server wraps these
with rule_id + severity from the catalog.

Extend by adding entries to RULES. For anything beyond a regex, add a
callable and register via `custom=<fn>` field.
"""

from __future__ import annotations

import re
from collections.abc import Callable
from dataclasses import dataclass, field


@dataclass
class RuleDef:
    rule_id: str
    severity: str
    category: str
    description: str
    rationale: str
    normative_refs: list[str]
    pattern: re.Pattern | None = None
    matcher: Callable[[list[str]], list[tuple[int, int, str, str]]] | None = None
    message: str = ""
    fix_hint: str = ""


def _regex_match(pattern: re.Pattern, message: str, fix_hint: str):
    def run(lines: list[str]) -> list[tuple[int, int, str, str]]:
        hits: list[tuple[int, int, str, str]] = []
        for i, line in enumerate(lines, start=1):
            m = pattern.search(line)
            if m:
                hits.append((i, m.start() + 1, message, fix_hint))
        return hits

    return run


def _regex_absence_before_motion(pattern: re.Pattern, message: str, fix_hint: str):
    """Flag if `pattern` never appears in the lines before first motion token."""
    motion_re = re.compile(r"^\s*(PTP|LIN|CIRC|SPLINE|SLIN|SCIRC|SPTP)\b", re.IGNORECASE)

    def run(lines: list[str]) -> list[tuple[int, int, str, str]]:
        seen = False
        for i, line in enumerate(lines, start=1):
            if pattern.search(line):
                seen = True
            if motion_re.search(line):
                if not seen:
                    return [(i, 1, message, fix_hint)]
                return []
        return []

    return run


_INTERRUPT_DECL_RE = re.compile(r"\bINTERRUPT\s+DECL\b", re.IGNORECASE)
_TOOL_SET_RE = re.compile(r"\$TOOL\s*=", re.IGNORECASE)
_BASE_SET_RE = re.compile(r"\$BASE\s*=", re.IGNORECASE)
_VEL_SET_RE = re.compile(r"\$VEL(\.CP|_AXIS)", re.IGNORECASE)


def _wait_for_without_timeout(lines: list[str]) -> list[tuple[int, int, str, str]]:
    hits: list[tuple[int, int, str, str]] = []
    wait_re = re.compile(r"\bWAIT\s+FOR\b", re.IGNORECASE)
    timeout_context_re = re.compile(r"(INTERRUPT|WAIT\s+SEC|WAIT\s+FOR\s+.*\sOR\s)", re.IGNORECASE)
    for i, line in enumerate(lines, start=1):
        if wait_re.search(line):
            context = " ".join(lines[max(0, i - 5):i + 3])
            if not timeout_context_re.search(context):
                hits.append((
                    i,
                    1,
                    "Unbounded WAIT FOR without timeout fallback",
                    "Wrap in INTERRUPT with timeout or add WAIT FOR ... OR (timeout) clause.",
                ))
    return hits


def _raw_io_in_body(lines: list[str]) -> list[tuple[int, int, str, str]]:
    hits: list[tuple[int, int, str, str]] = []
    raw_re = re.compile(r"\$(IN|OUT|ANIN|ANOUT)\s*\[", re.IGNORECASE)
    signal_decl_re = re.compile(r"\bSIGNAL\b", re.IGNORECASE)
    in_config = False
    for i, line in enumerate(lines, start=1):
        stripped = line.strip()
        if stripped.lower().startswith(";"):
            continue
        if signal_decl_re.search(line):
            continue
        if raw_re.search(line):
            hits.append((
                i,
                1,
                "Raw $IN/$OUT/$ANIN/$ANOUT in program body; use a SIGNAL alias.",
                "Declare SIGNAL alias in $config.dat and reference by name.",
            ))
    return hits


def _decl_without_comment(lines: list[str]) -> list[tuple[int, int, str, str]]:
    hits: list[tuple[int, int, str, str]] = []
    decl_re = re.compile(r"^\s*(DECL|GLOBAL\s+DECL)\b", re.IGNORECASE)
    comment_re = re.compile(r";.+\S")
    for i, line in enumerate(lines, start=1):
        if decl_re.search(line) and not comment_re.search(line):
            hits.append((
                i,
                1,
                "DECL without descriptive comment",
                "Add a trailing '; purpose/units/range' comment.",
            ))
    return hits


def _ov_pro_modification(lines: list[str]) -> list[tuple[int, int, str, str]]:
    hits: list[tuple[int, int, str, str]] = []
    re_assign = re.compile(r"\$OV_PRO\s*=", re.IGNORECASE)
    for i, line in enumerate(lines, start=1):
        if re_assign.search(line):
            hits.append((
                i,
                1,
                "Programmatic modification of $OV_PRO detected",
                "Override is operator-controlled; remove this assignment.",
            ))
    return hits


def _spline_without_bas(lines: list[str]) -> list[tuple[int, int, str, str]]:
    text = "\n".join(lines)
    spline_re = re.compile(r"\bSPLINE\b", re.IGNORECASE)
    bas_re = re.compile(r"BAS\s*\(\s*#INITMOV\s*,\s*0\s*\)", re.IGNORECASE)
    hits: list[tuple[int, int, str, str]] = []
    if spline_re.search(text) and not bas_re.search(text):
        for i, line in enumerate(lines, start=1):
            if spline_re.search(line):
                hits.append((
                    i,
                    1,
                    "SPLINE without BAS(#INITMOV,0) initialization",
                    "Call BAS(#INITMOV, 0) before the first SPLINE block.",
                ))
                break
    return hits


RULES: list[RuleDef] = [
    RuleDef(
        rule_id="KRL-SAFETY-001",
        severity="CRITICAL",
        category="safety",
        description="Missing INTERRUPT DECL before first motion.",
        rationale="Safety-relevant interrupts (E-stop, guard) must be armed before any motion command.",
        normative_refs=["ISO 10218-2:2011 §5.3", "KUKA KSS Programming Manual"],
        matcher=_regex_absence_before_motion(
            _INTERRUPT_DECL_RE,
            "No INTERRUPT DECL before first motion.",
            "Declare INTERRUPT DECL for E-stop/guard before the first PTP/LIN/CIRC/SPLINE.",
        ),
    ),
    RuleDef(
        rule_id="KRL-SAFETY-002",
        severity="CRITICAL",
        category="safety",
        description="Programmatic modification of $OV_PRO detected.",
        rationale="Operator override must remain operator-controlled.",
        normative_refs=["ISO 10218-1:2011", "KUKA SafeOperation"],
        matcher=_ov_pro_modification,
    ),
    RuleDef(
        rule_id="KRL-SAFETY-003",
        severity="CRITICAL",
        category="safety",
        description="Unbounded WAIT FOR (no timeout fallback).",
        rationale="A signal never arriving must not hang the program forever.",
        normative_refs=["house convention"],
        matcher=_wait_for_without_timeout,
    ),
    RuleDef(
        rule_id="KRL-MOTION-001",
        severity="WARNING",
        category="motion",
        description="$TOOL not set before first motion.",
        rationale="Relying on inherited tool frame risks crashes and inaccurate payload dynamics.",
        normative_refs=["KUKA KRL conventions"],
        matcher=_regex_absence_before_motion(
            _TOOL_SET_RE,
            "$TOOL not assigned before first motion.",
            "Add $TOOL = tool_data[n] in the INI / setup section.",
        ),
    ),
    RuleDef(
        rule_id="KRL-MOTION-002",
        severity="WARNING",
        category="motion",
        description="$BASE not set before first motion.",
        rationale="Uninitialized base leads to wrong Cartesian references.",
        normative_refs=["KUKA KRL conventions"],
        matcher=_regex_absence_before_motion(
            _BASE_SET_RE,
            "$BASE not assigned before first motion.",
            "Add $BASE = base_data[n] in the setup section.",
        ),
    ),
    RuleDef(
        rule_id="KRL-MOTION-003",
        severity="WARNING",
        category="motion",
        description="$VEL / $VEL_AXIS not set before first motion.",
        rationale="Inherited speed from previous program is unsafe.",
        normative_refs=["KUKA KRL conventions"],
        matcher=_regex_absence_before_motion(
            _VEL_SET_RE,
            "$VEL / $VEL_AXIS not set before first motion.",
            "Set $VEL.CP or $VEL_AXIS[] in the setup section.",
        ),
    ),
    RuleDef(
        rule_id="KRL-MOTION-004",
        severity="WARNING",
        category="motion",
        description="SPLINE without BAS(#INITMOV,0) initialization.",
        rationale="Path initialization undefined; may produce unexpected trajectories.",
        normative_refs=["KUKA KRL conventions"],
        matcher=_spline_without_bas,
    ),
    RuleDef(
        rule_id="KRL-IO-001",
        severity="WARNING",
        category="io",
        description="Raw $IN/$OUT/$ANIN/$ANOUT in program body.",
        rationale="Aliases document intent and isolate code from WorkVisual I/O remapping.",
        normative_refs=["house convention"],
        matcher=_raw_io_in_body,
    ),
    RuleDef(
        rule_id="KRL-STYLE-001",
        severity="INFO",
        category="style",
        description="DECL without descriptive comment.",
        rationale="Every declaration should record its purpose/units/range.",
        normative_refs=["house convention"],
        matcher=_decl_without_comment,
    ),
]
