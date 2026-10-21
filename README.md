# Shopify performance skill

An agent skill for reviewing Shopify theme performance and producing a clear, actionable Markdown report. It covers Liquid, images, CSS, fonts, JavaScript, app integrations, LCP, TTFB, CLS, and INP.

The skill works with theme code alone. Storefront URLs, traces, and real-user metrics improve the evidence but are optional. It reviews by default and changes theme code only when requested. It does not deploy themes.

## Install

Run this from the project where you want the skill installed:

```sh
npx skills add JLTDigital/shopify-performance-skill --skill shopify-performance
```

Choose your agent when prompted. To inspect available skills without installing:

```sh
npx skills add JLTDigital/shopify-performance-skill --list
```

To install from a local checkout, use its directory instead of the GitHub repository:

```sh
npx skills add ./shopify-performance-skill --skill shopify-performance
```

Requires Node.js/npm and an agent supported by the skills installer. The repository contains reusable agent instructions and references; no separate npm package is needed.

Installer documentation: [skills CLI](https://github.com/vercel-labs/skills/blob/main/docs/commands.md).

## Use

Ask your agent:

> Use the shopify-performance skill to review this Shopify theme. Write a clear report explaining each issue, where it occurs, how to fix it, and how to verify the improvement. Prioritise the most useful changes. Do not modify the theme.

Or focus the review:

> Use shopify-performance to investigate product-page LCP and layout shifts. Review the theme code and these performance traces, then save the report in reports/product-performance.md.

For implementation:

> Use shopify-performance to review this theme, implement the high-confidence theme fixes, and write a report of changes, checks, and remaining recommendations.

## Report output

Every completed review produces a report with a plain-language summary, priority table, file-level findings, recommended fixes, verification steps, and scope limitations. It distinguishes code observations from measured bottlenecks and does not invent scores or expected savings. Markdown is the default; an agent can use a requested document format if its environment supports it.

## Contents

- `SKILL.md`: workflow and required report output.
- `theme-review.md`: Shopify-specific review guidance.
- `measurement.md`: metric definitions and verification practices.
- `report.md`: report structure and writing standard.

Guidance references official Shopify and web.dev documentation, checked on 21 October 2026. Validate the skill against real themes before treating it as a production audit standard. It supplies reusable instructions to a compatible agent; it is not a standalone scanner or hosted auditing service.

## Validation

Skill frontmatter and naming validation passed. All local reference links resolve. Discovery and an isolated local copy installation passed with skills CLI 1.7.4, and installed files match the package. Real-theme review quality and live performance outcomes have not yet been evaluated.

## Contributing

Issues and pull requests are welcome. Include a minimal, anonymised theme example for a proposed rule, explain the shopper impact, and link to relevant official documentation. Distinguish code-level risks from measured performance results. Do not submit store credentials or customer data.

## License

[MIT](LICENSE). You may use, modify, and share the skill under the license terms.
