# Measurement and verification

## Explain the metrics

| Metric | Plain-language meaning | Good reference value |
| --- | --- | --- |
| LCP | When the largest visible content appears | At most 2.5 seconds |
| INP | How quickly the page paints a response to an interaction | At most 200 milliseconds |
| CLS | How much visible content unexpectedly shifts | At most 0.1, unitless |
| TTFB | How long navigation waits for the first response byte | Diagnostic; assess against context and baseline |

Core Web Vitals targets apply at the 75th percentile of real visits, separating mobile and desktop. TTFB is not a Core Web Vital. Never infer that a store passes field Core Web Vitals from a Lighthouse score or a single navigation.

Source: [Google Web Vitals](https://web.dev/articles/vitals).

## Evidence sources

- **Code:** establishes reachable patterns and potential mechanisms, not measured savings.
- **Lab:** DevTools, Lighthouse, or WebPageTest can isolate load and interaction problems under stated conditions. A default navigation audit does not establish real-user INP.
- **Field:** available Shopify performance reports, CrUX, PageSpeed Insights field data, or existing real-user monitoring describe actual traffic. Identify date range, device class, sample limitations, and URL versus origin aggregation. An origin-level value does not establish performance for one product page.
- **Liquid profiling:** Theme Inspector helps localise rendering work. Do not equate its timings with end-to-end navigation TTFB.

When data is missing, write “Not measured” or “Unavailable”, never zero. Do not invent baseline values, projected milliseconds, Lighthouse scores, or business impact percentages.

## Practical comparison

Choose representative home, product, and collection URLs within scope. Include realistic product/variant counts, visible app blocks, and the relevant market/language. Record whether the environment is live, preview, editor, or local development; preview tooling and editor behaviour can affect results.

Use equivalent before/after conditions: page and content, viewport, device/CPU/network settings, consent state, cache state, location, and tool version. When practical run at least three comparable lab measurements and report the median and spread. Keep cold-cache and warm-cache results separate. This is a lab comparison, not a field percentile.

For LCP, identify the actual element and separate server response, resource discovery delay, download time, and rendering delay. For CLS, inspect shift sources during load and subsequent activity. For INP, exercise meaningful interactions and attribute long tasks/layout work. For TTFB, inspect redirects and network timing alongside Liquid profiling; streamed HTML can hide slow downstream content behind an early first byte.

Field data changes over its reporting window and may mix deployments. State that a fresh patch has not yet demonstrated a field improvement rather than claiming an immediate pass.

Sources: [LCP breakdown](https://web.dev/articles/optimize-lcp), [Shopify metric gaps](https://shopify.dev/docs/storefronts/themes/best-practices/performance/performance-gaps).

## Functional regression checks

Select checks related to the proposed change: responsive layout, image crops, product selection and availability, cart updates, filtering/pagination, keyboard and focus behaviour, consent, localisation, and editor section reordering/reloading. Use a preview/test environment for actions with store-side consequences. Report what actually ran and what still needs manual or store-access verification.
