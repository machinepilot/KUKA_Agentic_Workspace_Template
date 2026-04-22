---
id: <ID_FORMAT>             # KUKA_REF_<topic> | ONE_<topic>_<slug> | EG_<scenario> | KUKA_<protocol>_<aspect> | KUKA_SAFETY_<topic>
title: <Human-Readable Title>
topic: <primary topic>       # motion | io | interrupts | safety | fieldbus | workvisual | mastering | palletizing | welding | ...
kuka_platform: [KR C4, KR C5]
controller: [KSS 8.3, KSS 8.6]
language: KRL                # KRL | JAVA (Sunrise) | Python (companion) | N/A
source:
  type: vendor_manual        # vendor_manual | application_note | training | error_code_ref | white_paper | third_party_integrator | community
  title: "<source title>"
  tier: T1                   # T1 | T2 | T3 | T4
  pages: [<start>, <end>]    # for PDFs
  section: "<section label>"
  access_date: <YYYY-MM-DD>
  url: null                  # set for non-vendor research sources
license: reference-only      # reference-only | open | mit | apache-2.0 | ...
revision_date: <YYYY-MM-DD>
related: []                  # list of related ids
difficulty: intermediate     # beginner | intermediate | advanced
tags: []
---

# <Title>

## Summary

Two to four sentences. What does this entry cover? When is it used?

## Syntax / Specification

Precise description, expressed in our own words (never verbatim vendor text beyond short quotes for precision).

```krl
; Example snippet showing canonical usage
```

## Semantics / Behavior

What the instruction / concept does. Preconditions, postconditions, side effects. Reference related entries.

## Common Pitfalls

- Pitfall 1
- Pitfall 2

## Worked Example

Minimal but complete example. Include context around the snippet so it makes sense without a full program.

```krl
; ...
```

## Related Entries

- `<id>` — <why related>
- `<id>` — <why related>

## Citations

- Source: <title>, tier <T1-T4>, pages <start>-<end>, accessed <date>.
- Additional: <inline citations>.

## Provenance

Who / which agent produced this entry. When. From which raw source file (path in `kuka_dataset/raw_sources/`).
