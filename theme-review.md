# Theme review guide

Use these checks as investigation prompts. Report a problem only after checking whether the code is active and whether its surrounding context already addresses it.

## LCP: get the main content on screen

Trace the likely hero or product media from template to snippet. It is a candidate until a trace identifies it; the LCP element can also be text and can differ by breakpoint.

- For a visible candidate, check whether lazy loading, JavaScript insertion, a CSS background, or a reveal animation delays discovery or display. Render meaningful initial content in HTML where appropriate.
- Give a confirmed primary image eager loading and consider `fetchpriority="high"`. Do not give every card or slide high priority. Hidden carousel slides and below-fold images need different treatment.
- Check `srcset` and `sizes` against actual CSS widths and device pixel ratios. Oversized downloads can persist even with responsive markup when `sizes` is wrong.
- Prefer Shopify image filters to hand-built CDN transformations. Inspect generated output: `image_tag` supplies dimensions and can choose lazy loading by section position. Omitted explicit attributes in Liquid are not automatically defects.
- For different mobile and desktop artwork, inspect whether CSS-hidden image pairs both download. Consider `picture` with matching sources; preserve crops, focal points, alt text, and aspect ratios.
- Preload only when evidence shows a late-discovered critical resource. Match the eventual URL, responsive candidates, and request mode to avoid duplicate requests. Eager loading, high priority, and preloading have different purposes.

Section position is a hint, not proof of viewport visibility. Check `section.location` as well as `section.index`: header and template positions are separate contexts. Indices can be nil for static sections, the editor, and Section Rendering API responses. A reusable image snippet should accept context from its caller instead of assuming that every first image is the LCP image. Define and test a sensible nil fallback; do not turn missing position data into missing content or an accidentally lazy hero.

Sources: [Shopify image_tag](https://shopify.dev/docs/api/liquid/filters/image_tag), [section position](https://shopify.dev/docs/storefronts/themes/best-practices/performance/use-section-index), [LCP optimisation](https://web.dev/articles/optimize-lcp).

## Liquid and TTFB: investigate server work

Trace repeated work across render calls, particularly nested product/variant loops, repeated transformations of the same data, and large generated HTML or JSON payloads. Determine how cost scales with catalog size. Move genuinely invariant work out of loops when scope and output remain equivalent. Do not flag every loop, metafield access, or snippet call as inherently slow.

Check whether the theme retrieves or serialises substantially more data than the UI needs. Use supported pagination where appropriate and retain pagination links, filtering, sorting, and product availability semantics. A loop `limit` limits iteration; it does not necessarily constrain data fetching. Confirm the current array-specific Liquid behaviour before promising database savings.

Use Shopify Theme Inspector to identify expensive Liquid paths when accessible. Static complexity suggests a profiling target, not a measured server bottleneck. TTFB also includes redirects, network and connection setup, cache behaviour, and platform response time. Shopify controls hosting and CDN configuration; do not prescribe generic server configuration edits for hosted themes. With streamed responses, an early first byte can precede expensive section rendering, so inspect content arrival as well as TTFB.

Sources: [Shopify performance](https://shopify.dev/docs/storefronts/themes/best-practices/performance), [Liquid pagination](https://shopify.dev/docs/api/liquid/tags/paginate), [metric gaps and streaming](https://shopify.dev/docs/storefronts/themes/best-practices/performance/performance-gaps).

## CSS, fonts, and assets

Check render-blocking styles, repeated inclusion, unused page-specific bundles, and oversized assets. Keep above-fold styling available for initial rendering. Deferring all CSS can cause flashes and layout shifts; inlining a whole stylesheet increases HTML and loses reusable caching. Base selective loading on actual template/section usage, including dynamically rendered sections.

For fonts, inspect used families/weights, request timing, fallback metrics, and display behaviour. `font-display: swap` can improve text visibility but still shift layout with a mismatched fallback. Preload only required early fonts with matching request attributes; loading every weight competes with more important resources. Keep essential icons and accessible text usable while fonts load.

Distinguish source size from transferred/compressed size and execution cost. Minification alone is not a substitute for reducing unused work. Use the existing asset pipeline rather than hand-editing compiled output.

## JavaScript and INP: keep shopping responsive

Trace product option changes, add-to-cart/cart drawers, filters, search, and menus. Look for expensive synchronous handlers, repeated DOM traversal, alternating layout reads/writes, large rerenders, duplicated listeners, and unnecessary library initialisation.

Split long work and limit the DOM affected by each update when profiling supports it. Schedule nonessential work after immediate feedback, preserving interaction ordering and focus. Debounce appropriate input requests without delaying essential feedback. Prevent stale search/filter responses from replacing newer results.

For classic external scripts, `defer` preserves document order and runs after parsing; `async` does not preserve dependency order. Modules defer by default, and `defer` does not postpone inline classic scripts. Check inline consumers before changing external dependencies. Deferred JavaScript still consumes main-thread time.

Initialise components idempotently and clean up listeners on section replacement. Test editor reloads and Section Rendering API updates. Hidden components may still execute code. Lazy initialisation must not drop the first click or break keyboard interaction. TBT and bundle size are clues, not measurements of INP.

Source: [INP optimisation](https://web.dev/articles/optimize-inp).

## CLS: keep the page stable

Inspect media dimensions or reserved aspect ratios, font swaps, banners, review widgets, app embeds, sticky headers, and content inserted above existing content. Dimensions need to match the rendered responsive geometry; attribute absence alone is not proof of a shift if CSS already reserves space.

Reserve realistic space for asynchronous content. Keep gallery and variant-image transitions stable across different ratios. Prefer transforms for suitable motion instead of repeatedly changing layout dimensions. Avoid hard-coded heights that clip translations or zoomed text.

Use a layout-shift trace to distinguish the elements that moved from the element that caused movement. Inspect post-load states, scrolling, and delayed widgets: a navigation-only test can miss real CLS. Some shifts associated with recent user input are excluded from CLS, so report actual metric evidence separately from visible movement.

Source: [CLS optimisation](https://web.dev/articles/optimize-cls).

## Apps and Shopify constraints

Trace manually added snippets, app blocks/embeds, and external request initiators. Establish ownership before attributing a cost. A third-party domain or large script alone does not prove it is unnecessary. Local theme code may not expose app settings or all injected scripts.

Recommend removing duplicate or unused integrations only with evidence and a stated business impact. Respect consent and Customer Privacy behaviour. Do not gate essential commerce scripts on arbitrary timers or first interaction to improve a synthetic score. Preserve `content_for_header`, dynamic checkout behaviour, and required Shopify integrations.

## Tools

Use existing project commands first. If Shopify CLI is installed, run `shopify theme check` from the theme root with the project's configuration, without auto-correction. Report actual findings and tool versions. Theme Check is a static linter, not proof of runtime speed. A missing CLI or store login should not prevent a code-only review.

Source: [Shopify Theme Check](https://shopify.dev/docs/storefronts/themes/tools/theme-check).
