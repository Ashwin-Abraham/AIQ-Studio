---
name: programme-brief
description: Create or revise a site or building Programme Brief from user-given uses, areas, capacities, or workloads, with region-specific guidance and a spreadsheet area schedule.
---

# Programme Brief

Produce a quantitative brief of **uses and intended amounts**. Accept the user's preferred starting measure, such as floor area, dwellings, hotel keys, pupil places, beds, seats, staff, or visits per day. Keep project goals, site facts, design concepts, and by-laws in their own records. Cite applicable rules here only when they inform a programme quantity.

## Establish the basis

Identify the project location and jurisdiction, project type and service level, planning horizon, and whether the work is new construction, conversion, or expansion. Where available, read the overall project intent at `<will insert path in future>` to guide which programme questions matter. Ask about missing uses and capacities that materially change the schedule, such as parking spaces, hotel amenities, or special outdoor spaces for retail. For example, before estimating areas for a 30-key hotel, establish its location, hotel type, service level, and intended amenities. Record unresolved facts as assumptions when a provisional brief is useful.

## Develop the schedule

1. Preserve each user-given quantity and its unit. Distinguish simultaneous capacity from workload per period.
2. Find current local or regional standards first, then relevant international or industry guidance. Check applicability and access to the full source. Treat Neufert and similar references as guidance only when the relevant edition and figures can be verified. Record the edition, jurisdiction, link or citation, and date checked.
3. Add the spaces and quantities needed to serve the stated use at the chosen level of detail. Show each conversion assumption, such as area per key or net-to-gross allowance. Label estimated values and their sources. Keep user targets distinct from calculated requirements and legal minima.
4. Check that subtotals use the same area basis and that the schedule covers the stated capacity. Present open choices that could change the result. Revise the schedule when the user resolves them.

## Area brief data format

Deliver an editable spreadsheet with **Programme**, **Assumptions**, and **Sources** sheets. Keep a companion Markdown file with the project region, project type, revision, open questions, and the same tables. Use the Markdown file as the source data when generating the spreadsheet. If the user later edits the spreadsheet, treat that edited workbook as the current source.

Give each programme row a stable ID. Use these columns in the Programme table and sheet: `ID | Use | Subtype | Measure | Value | Unit | Area basis | Status | Calculation | Source ID`. Use one row per measure, so a use may have rows for keys, area per key, and total area. Record a range with separate minimum and maximum rows. For every workload, state its period in the unit. For every area, state what its boundary includes, using a defined basis such as net room area, gross internal area, gross floor area, or outdoor land area. Leave an unknown value empty and name it in the open questions.

Use `user target`, `estimated`, or `required` for Status. Keep client quantities distinct from calculated estimates and legal minima. Put the equation in Calculation using stable row IDs, and use spreadsheet formulas for calculated values. The Assumptions sheet records `ID | Assumption | Value | Unit | Source ID | Status`. The Sources sheet records `ID | Title | Edition or date | Jurisdiction | Link or citation | Date checked`. Cite the assumption or standard behind each added quantity. Sum only areas with the same basis.

The brief is complete when every stated use has a measurable target or a recorded open question, each area has a unit and basis, and every added quantity has a traceable source or calculation.
