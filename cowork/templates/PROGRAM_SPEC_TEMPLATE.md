# Program Specification: <NAME>

**Customer:** <customer_id>
**System:** <system>
**Task ID:** <task_id>
**Application:** <application>
**Robot:** <model> / Controller: <KR C4 | KR C5> / KSS: <version>
**Author:** Architect agent
**Date:** <YYYY-MM-DD>
**Status:** Draft | Ready for Integration | Ready for Motion | In Progress | Complete

---

## 0. Machine-Readable Block

```json program_spec
{
  "$schema": "../../cowork/schemas/program_spec.schema.json",
  "task_id": "",
  "customer_id": "",
  "system": "",
  "application": "",
  "robot": { "model": "", "controller": "", "kss_version": "" },
  "tools": [],
  "bases": [],
  "modules": [
    {
      "name": "main",
      "kind": "main",
      "file": "main.src",
      "purpose": ""
    }
  ],
  "variables": [],
  "motion_blocks": [],
  "integration": {
    "fieldbus": "",
    "architecture": "",
    "signals": []
  },
  "safety": {
    "required_interrupts": [],
    "zones": [],
    "max_velocity_mm_s": null,
    "collaborative": false
  },
  "error_recovery": [],
  "dataset_refs": []
}
```

---

## 1. Application Overview

One to three paragraphs describing what the cell does, what the robot handles, and the cycle sequence at a high level.

## 2. Module Decomposition

| Module | Kind | File | Purpose |
|--------|------|------|---------|
| main | main | `main.src` | Entry point; dispatch |
| pick_part | subprogram | `pick_part.src` | Part acquisition |
| place_part | subprogram | `place_part.src` | Part delivery |
| ... | ... | ... | ... |

### Shared Data

| File | Contents |
|------|----------|
| `$config.dat` | Signal aliases, shared constants |
| `program_data.dat` | Program-local positions, frames |

## 3. Control Flow

State machine (or structured pseudocode):

```
STATE idle:
  on START + mastered + guard_closed -> STATE pick_ready
STATE pick_ready:
  call pick_part
  on pick_success -> STATE place_ready
  on pick_fault -> STATE recover_pick
...
```

Include a mermaid `stateDiagram-v2` if it clarifies the flow.

## 4. Variable Allocation

| Name | Type | Scope | Purpose | Init |
|------|------|-------|---------|------|
| gripper_state | INT | GLOBAL | 0=open 1=closed 2=fault | 0 |
| cycle_count | INT | GLOBAL | Parts completed this shift | 0 |
| ... | ... | ... | ... | ... |

### Frames / Positions

| Name | Type | Purpose |
|------|------|---------|
| pick_approach | E6POS | 50mm above pick target |
| pick_target | E6POS | Pick position |
| ... | ... | ... |

## 5. Motion Blocks

| ID | From | To | Motion | Velocity | Accel | Termination | Notes |
|----|------|-----|--------|----------|-------|-------------|-------|
| M01 | HOME | pick_approach | PTP | $VEL_AXIS 100% | default | C_PTP | rapid retract |
| M02 | pick_approach | pick_target | LIN | $VEL.CP=0.2 m/s | default | C_FINE | precise |
| M03 | pick_target | pick_retract | LIN | $VEL.CP=0.3 m/s | default | C_DIS | clearance |
| ... | | | | | | | |

Motion choice rationale should reference `kuka_knowledge` entries.

## 6. Integration Contract

Merged in from `INTEGRATION_SPEC_*.md`. Summary here:

| Alias | $IN/$OUT | Direction | Device | Safety-rated? |
|-------|----------|-----------|--------|---------------|
| part_present | $IN[17] | input | Sensor S1 | no |
| gripper_open_cmd | $OUT[12] | output | Gripper valve V1 | no |
| estop | $IN[1] | input | Safety controller | yes |
| ... | | | | |

## 7. Safety Constraints

From Safety agent Phase A:

- Max Cartesian velocity: <v> mm/s
- Required interrupts: <list>
- Referenced SafeOperation zones: <list> (defined in WorkVisual)
- Collaborative? <yes/no> — if yes, ISO/TS 15066 computation in `SAFETY_REVIEW_*.md`
- Mastering verification required on cold-start: <yes/no>
- Payload / tool data: `$LOAD_DATA[1]` = <kg>, `$TOOL` = <frame>

## 8. Error Handling & Recovery

| Fault | Detection | Recovery Subprogram | Action |
|-------|-----------|---------------------|--------|
| pick_timeout | WAIT FOR part_present timeout | recover_pick() | Back off, alarm, request human |
| place_collision | $STOPMESS ≥ 1 | recover_place() | E-stop, alarm, lockout |
| ... | | | |

## 9. Dataset References

| Entry | Used For |
|-------|----------|
| `kuka_dataset/normalized/reference/KUKA_REF_PTP_Motion.md` | Motion block M01 |
| `kuka_dataset/normalized/examples/EG_Pick_Approach_Retract.md` | Approach/retract pattern |
| ... | |

## 10. Open Questions / TBD

- [ ] Cycle-time target confirmation
- [ ] Which SafeOperation zone bounds pick area?
- [ ] ...

## 11. Acceptance Criteria (for QA)

- [ ] All modules in §2 exist as files.
- [ ] All variables in §4 declared with comments.
- [ ] All motion blocks in §5 implemented.
- [ ] All aliases in §6 used; none raw `$IN`/`$OUT`.
- [ ] All interrupts from §7 declared before first motion.
- [ ] All fault handlers from §8 present.
- [ ] `safety_lint` passes with no CRITICAL findings.
- [ ] Safety Phase-B review: `pass` or `conditional-pass`.
