---
name: shopify-performance
description: Review Shopify Liquid theme code for performance opportunities and write a clear, prioritised report explaining issues, affected code, fixes, and verification. Use for Shopify theme speed audits, LCP, TTFB, CLS, INP, and performance-focused code reviews. Covers Liquid storefront themes, not Hydrogen or checkout extensions.
metadata:
  version: "1.1.0"
---

# Shopify performance review

Review the theme like a Shopify performance engineer. Deliver a report a merchant can understand and a developer can act on. Support code-only audits and audits with a storefront URL or performance traces. A code-only audit is useful; do not block it on store access.

## Scope and evidence

- Review by default. If the user also requests fixes, implement focused changes and report what was changed and verified. A request for a report alone does not imply changing theme behaviour.
- Follow project instructions and locate the theme root. Identify source files versus generated assets before proposing edits. Support legacy Liquid templates and Online Store 2.0 JSON templates, sections, section groups, blocks, and snippets.
- Inspect available configuration and template order to establish which sections and assets are active. Configuration may differ from the live store; state that uncertainty. Never print credentials or private customer data from configuration or traces.
- If given only a URL, inspect the rendered page when tools permit, explain that Liquid internals are unavailable, and avoid invented repository locations. If neither code nor a usable URL is available, ask for the theme location or URL before writing findings.
- Interpret “TFB” as TTFB (Time to First Byte). LCP, CLS, and INP are Core Web Vitals; TTFB is a supporting diagnostic.
- Distinguish an observed code pattern, a probable runtime effect, and a measured bottleneck. Static code cannot establish actual LCP elements, field scores, savings in milliseconds, or conversion gains.

## Review workflow

1. **Map the storefront.** Start with layouts, template JSON/Liquid, shared sections/snippets, assets, and relevant theme settings. Trace calls and asset inclusion from entrypoints. For broad audits cover home, product, and collection pages plus shared navigation/cart/search where present; explain sampling and exclusions. For focused requests stay within scope and trace dependencies.
2. **Establish the baseline.** When runtime measurement is in scope, use the bundled [CLI measurement workflow](runtime.md) to run Lighthouse and, with store access, Shopify Liquid profiling. Incorporate the generated summaries and raw evidence into the report; record unavailable tooling or authentication.  Record revision, tools, URLs/page types, device conditions, and supplied metrics when available. Read [measurement.md](measurement.md) when interpreting data or planning verification. If no runtime evidence exists, label the audit “Code review — runtime performance not measured”.
3. **Inspect performance paths.** Read [theme-review.md](theme-review.md). Follow LCP resource discovery, image sizing/loading, CSS and fonts, Liquid work, JavaScript execution, layout stability, and app integrations. Search matches are leads, not findings: inspect callers, conditions, existing mitigations, and rendered markup if available.
4. **Validate candidates.** Confirm that the affected path can execute and explain the mechanism. Use the project's existing checks and Shopify Theme Check if available. Do not auto-correct during a review. Record unavailable checks instead of claiming they passed. Use traces or Theme Inspector to substantiate timing claims when available.
5. **Prioritise.** Rank by likely user impact, reach across pages, evidence, effort, and regression risk. Use High for a substantial obstacle on a primary journey, Medium for meaningful but narrower or uncertain impact, and Low for modest improvements. Keep confidence separate from priority. Put unresolved suspicions under “Needs measurement”; do not pad the issue count with speculative findings.
6. **Write the report.** Always follow [report.md](report.md). Unless the user chooses another format or destination, save a Markdown report in the project's usual reports/output location, or `shopify-performance-report.md` at the workspace root if none exists. Avoid overwriting an unrelated report. Link the report and give a short summary in chat. If file writing is unavailable, provide the complete report inline.

## Resolution quality

For each finding, identify the smallest useful change, the exact code owner/location, and a verification method. Include a short before/after example or patch when it makes the fix clearer; adapt it to actual variables and theme architecture. Do not present pseudocode as a tested patch.

Keep Shopify requirements, accessibility, product variants, cart behaviour, consent, analytics, localisation, theme editor section lifecycle, and merchant settings working. Never remove or rewrite `content_for_header` to suppress scripts. Attribute app problems to the responsible integration; disabling a business feature is a tradeoff to discuss, not an automatic optimisation.

If implementing authorised fixes, run relevant project checks and check affected journeys and responsive layouts where tools permit. Compare equivalent before/after measurements if available. Do not publish a theme or change live app settings merely to complete an audit. Be explicit about untested behaviour and work requiring store-side access.

## References and freshness

The references link to official Shopify and web.dev guidance, checked on 2026-10-21. Consult current primary documentation when a recommendation depends on a changing API, tool flag, platform behaviour, or metric definition. If browsing is unavailable, identify version-sensitive assumptions. The skill requires no particular paid service, browser connector, or agent vendor.
