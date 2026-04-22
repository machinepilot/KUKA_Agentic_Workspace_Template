# Integration Specification: <PROGRAM_NAME>

**Task ID:** <task_id>
**Author:** Integration agent
**Date:** <YYYY-MM-DD>
**Status:** Draft | Ready for Architect | Complete

---

## 0. Machine-Readable Block (slots into program_spec.integration)

```json integration
{
  "fieldbus": "Profinet|EtherNet/IP|EtherCAT|DeviceNet|Profibus",
  "architecture": "plc-master-robot-slave|robot-master|peer|external-rsi|external-eki",
  "cycle_time_ms": null,
  "mx_automation": false,
  "rsi": {
    "enabled": false,
    "cycle_ms": null,
    "data_contract": []
  },
  "eki": {
    "enabled": false,
    "xml_schema": null
  },
  "signals": [
    {
      "alias": "part_present",
      "direction": "in",
      "kuka_address": "$IN[17]",
      "fieldbus_device": "Sensor S1 on Profinet node 3",
      "width_bits": 1,
      "safety_rated": false,
      "category_pl": null,
      "debounce_ms": 10,
      "timeout_ms": 5000,
      "notes": ""
    }
  ],
  "handshakes": [
    {
      "name": "program_select",
      "description": "PLC selects program number and strobes select_req; robot acks.",
      "sequence": [
        { "actor": "PLC", "action": "set pgm_no (8b) + strobe pgm_select_req" },
        { "actor": "Robot", "action": "read pgm_no, verify valid, set pgm_select_ack" },
        { "actor": "PLC", "action": "clear pgm_select_req" },
        { "actor": "Robot", "action": "clear pgm_select_ack" }
      ],
      "timeout_ms": 2000
    }
  ]
}
```

---

## 1. Fieldbus Choice

| Option | Chosen? | Rationale |
|--------|---------|-----------|
| Profinet | ✓ / — | |
| EtherNet/IP | ✓ / — | |
| EtherCAT | ✓ / — | |
| DeviceNet (legacy) | ✓ / — | |
| Profibus (legacy) | ✓ / — | |

Citation: `kuka_dataset/normalized/protocols/<entry>.md`.

## 2. Architecture

| Pattern | Chosen? | Rationale |
|---------|---------|-----------|
| PLC-master / Robot-slave | | Most common for cell integration |
| Robot-master / PLC-slave | | Robot sequences cell |
| mxAutomation (PLC commands motion via FBs) | | PLC-driven motion (palletizing, multi-path) |
| RSI (real-time path correction) | | Seam tracking / visual servoing |
| EKI XML | | Loose-coupled messaging |

## 3. Signal List

| Alias | $IN/$OUT | Direction | Width | Device | Safety-rated (Cat / PL) | Debounce | Timeout | Notes |
|-------|----------|-----------|-------|--------|-------------------------|----------|---------|-------|
| | | | | | | | | |

## 4. Handshake Patterns

### 4.1 Program Select

```
PLC:     set pgm_no (8b)  → strobe pgm_select_req (rising)
Robot:   WAIT FOR pgm_select_req == TRUE
         verify pgm_no valid
         set pgm_select_ack = TRUE
PLC:     WAIT FOR pgm_select_ack == TRUE
         clear pgm_select_req
Robot:   WAIT FOR pgm_select_req == FALSE
         clear pgm_select_ack
```

Timeout: 2000 ms. Fallback: alarm + return to idle.

### 4.2 Start

```
<similar sequence>
```

### 4.3 Cycle Complete

```
<similar sequence>
```

### 4.4 Fault / E-stop

```
<similar sequence>
```

## 5. mxAutomation (if applicable)

- Robot-side application: `<name>`
- Function blocks used: `MC_Power`, `MC_GroupEnable`, `MC_MovePath`, `MC_MovePTP`, ...
- Cycle time expectation: `<ms>`
- Dataset references: `kuka_dataset/normalized/protocols/KUKA_mxAutomation.md`

## 6. RSI (if applicable)

- Cycle time: 12 ms (default) / other
- Data contract (in / out):
  | Direction | Signal | Units | Purpose |
  |-----------|--------|-------|---------|
  | | | | |

## 7. EKI XML (if applicable)

- Schema file: `<path>`
- Connection: TCP host:port
- Heartbeat: <ms>

## 8. Testing Matrix

| Scenario | Expected | How to verify |
|----------|----------|---------------|
| Program select valid | Robot acks within 2000 ms | Force PLC handshake in sim |
| Program select invalid | Robot alarms, no motion | |
| Start during fault | Start rejected | |
| Guard open mid-cycle | Category-1 stop | |

## 9. Dataset References

| Entry | Used For |
|-------|----------|
| | |

## 10. Open Items

- [ ] Confirm Profinet node assignment from plant IT.
- [ ] Obtain PLC tag list for cross-check.
- [ ] ...
