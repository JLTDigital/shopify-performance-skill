# Required performance report

Write for two readers: the person deciding what to fix and the developer making the changes. Lead with the outcome in ordinary language. Explain technical terms on first use. Use short paragraphs, specific headings, and compact tables. Do not dump tool logs or use a Lighthouse score as the report's conclusion.

Use the structure below, adapting its length to the actual findings. Omit empty boilerplate, but always include scope, limitations, and verification status. A report with no confirmed issues should say so and describe the coverage; it must not claim that an unmeasured store is fast.

## 1. Summary

State the review date, theme/revision if known, review type (code-only or code plus measurements), and pages examined. Explain the main opportunities and recommended first action in a few sentences. Include issue counts only if they match the detailed findings.

## 2. Priorities at a glance

| ID | Issue in plain language | Affected pages | Priority | Evidence | Effort |
| --- | --- | --- | --- | --- | --- |

Use High/Medium/Low priority. Evidence should distinguish “Observed in code; effect unmeasured” from “Measured in lab” or “Observed in field”. Use Small/Medium/Large effort with a brief explanation where necessary; avoid precise time estimates without context.

## 3. Findings and resolutions

For each issue use a descriptive title such as “The main product image waits until JavaScript runs”. Include:

- **What is happening:** a short explanation of the actual behaviour and trigger.
- **Why it matters:** the effect on the shopper, affected metric(s), and scope. State uncertainty explicitly.
- **Where:** verified repository-relative file path and line number/range, plus template/section/caller context. For runtime-only findings use URL, element/request, and trace evidence instead of invented code locations.
- **Evidence and confidence:** a short excerpt or observation; distinguish confirmed code behaviour from inferred impact. Confidence is High/Medium/Low with a reason.
- **Recommended fix:** concrete steps in order, including the responsible owner if outside the theme. Show a short adapted before/after snippet when useful, clearly labelled “Suggested — not applied” or “Applied”. Preserve important surrounding behaviour.
- **Tradeoffs:** relevant functionality, accessibility, design, or integration risks. Do not clutter the report with hypothetical risks unrelated to this fix.
- **How to verify:** a reproducible action and expected observable result. Separate functional correctness from measured speed improvement.
- **Status:** Suggested, Applied but not verified, or Applied and verified; name what was actually verified. Lint success alone does not verify a performance gain.

Avoid reporting the same root cause as separate issues for every caller; group affected locations. Do not bury major shared-template issues under cosmetic cleanups.

## 4. Recommended order of work

Provide a short sequence based on impact and dependencies. Separate theme changes, merchant/app configuration decisions, and investigations needing runtime evidence. Explain why the first item is first. If fixes were applied, identify remaining work rather than implying completion.

## 5. Measurements and checks

If measurements exist, tabulate metric, page/device, before/after, evidence source, and conditions. Keep lab and field measurements distinct. With no measurements, use a concise “Runtime performance not measured” statement and a tailored verification plan; do not fill a table with invented estimates.

List completed checks, failures, and checks not run with the reason. Explain coverage limits: unreviewed templates, unavailable app internals, missing live settings, or a sampled code review. Put plausible but unproven issues in a clearly labelled “Needs measurement” subsection, outside confirmed issue counts.

## Writing standard

Prefer “Customers wait longer to see the main product image” to “Suboptimal LCP resource prioritisation”. Use the technical term alongside the explanation when it helps implementation. Every actionable issue must answer: what is wrong, where is it, what should change, and how will we know it worked?

## CLI evidence appendices

When collected, incorporate the helper's `summary.md` and `summary.json` outputs from [runtime.md](runtime.md). Present Lighthouse category scores out of 100 separately from timing metrics, with device/preset, median, min/max, successful/requested runs, version, capture time, and final-page checks. Keep missing audits and failed runs visible. Do not label TBT as INP or document server-response timing as full navigation TTFB.

For Shopify Liquid, state store, remote theme, route, CLI version, and capture time. Include the most relevant frames with self and inclusive milliseconds, link raw Speedscope evidence, and connect hotspots to verified source code and concrete fixes. Explain that inclusive times overlap and are not additive. If no authorised store access exists, say Liquid profiling was not run. Avoid duplicating an entire machine-generated appendix when a focused table and evidence link suffice.
