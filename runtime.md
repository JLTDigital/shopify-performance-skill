# CLI measurements

Use [scripts/measure.py](scripts/measure.py) when the review includes a reachable storefront or an accessible Shopify store. Resolve the script relative to the installed skill directory, not the theme directory. The helper uses Python's standard library and invokes installed executables; installing the skill does not install Lighthouse or Shopify CLI.

## Prerequisites

- Python 3.10 or later.
- Lighthouse CLI and a compatible Chrome/Chromium installation for browser measurements. Follow [Lighthouse's official setup instructions](https://github.com/GoogleChrome/lighthouse#using-the-node-cli); current releases require Node 22 or later.
- Shopify CLI and an authenticated account with access to the target store/theme for Liquid measurements. Confirm supported options using `shopify theme profile --help`.

Example tool installation, when needed and authorised in the working environment:

```sh
npm install -g lighthouse @shopify/cli
```

The script uses `lighthouse` and `shopify` from PATH. `CHROME_PATH` can select an installed Chrome executable. It does not disable Chrome's sandbox, download packages automatically, publish themes, or modify storefront code.

## Lighthouse

From this repository (replace the script path when installed elsewhere):

```sh
python3 scripts/measure.py lighthouse https://example.com/products/example \
  --device mobile --runs 3 --output reports/product-mobile-before

python3 scripts/measure.py lighthouse https://example.com/products/example \
  --device desktop --runs 3 --output reports/product-desktop-before
```

Run once per page/device combination. Each output directory must be new. The default is three mobile runs with a 180-second timeout per run. Lighthouse uses its default storage reset and throttling for the chosen preset; exact settings and environment are retained in the JSON. It measures performance, accessibility, best practices, and SEO scores, plus available LCP, FCP, CLS, Speed Index, TBT, and document server-response timing. The latter is narrower than full navigation TTFB. A missing audit remains unavailable.

Outputs include each raw Lighthouse JSON, local stderr logs, `summary.json`, and a report-ready `summary.md` with medians, ranges, sample counts, versions, warnings, and final URLs. All runs must succeed for exit status 0; partial failures return 1 while retaining usable evidence. Syntax errors return 2. A timeout or unavailable score never counts as a zero score. This is a navigation test, not an INP test.

Confirm that the final page is correct. A password screen, bot challenge, or redirect can produce a valid score for the wrong content. The helper does not import browser cookies or authenticate password-protected storefronts for Lighthouse. Use an authorised accessible preview, or collect authenticated evidence separately and state that method.

## Shopify Liquid

Authenticate interactively before using the noninteractive helper. One way to establish the session and confirm the theme ID is:

```sh
shopify theme list --store example.myshopify.com
```

Then profile a specific remote theme and page:

```sh
python3 scripts/measure.py liquid --store example.myshopify.com \
  --theme 123456789 --path /products/example \
  --output reports/product-liquid-before
```

The helper calls `shopify theme profile --json --no-input` with explicit store, theme, and URL context. It profiles the remote theme, so unpushed local changes are not represented. Store-relative routes may include query parameters; quote them in shell commands. This covers supported storefront routes on stores the account can access, not arbitrary third-party stores or hosted checkout.

Current CLI implementation requires account authentication for profiling and rejects Admin API/Theme Access tokens despite exposing the shared password flag. The helper rejects `SHOPIFY_CLI_THEME_TOKEN` when set. For a password-protected storefront, configure `SHOPIFY_FLAG_STORE_PASSWORD` privately in the environment; never paste passwords into reports or committed commands. The helper disables interactive prompts and records authentication failures rather than hanging for login.

Outputs are `liquid.speedscope.json`, local stderr, `summary.json`, and `summary.md`. The summary supports evented and weighted sampled Speedscope time profiles, converts supported time units to milliseconds, and ranks frames by self time. Inclusive time includes descendants and overlaps between frames; do not add frame totals. Recursion is not counted twice within one stack. Unknown formats fail explicitly while raw output remains available for inspection. Open the raw file in a trusted local Speedscope-compatible viewer if a flamegraph is useful.

Sources: [Shopify theme profile](https://shopify.dev/docs/api/shopify-cli/theme/theme-profile), [CLI implementation and authentication limitation](https://github.com/Shopify/cli/blob/main/packages/theme/src/cli/services/profile.ts), [Speedscope format](https://github.com/jlfwong/speedscope/blob/main/src/lib/file-format-spec.ts).

## Integrate into the audit report

Read each `summary.md` and its supporting JSON. Add a measurement section for each page/device or page/theme, with links to the local raw evidence. Include failed runs, warnings, timing units, tool versions, sample counts, and capture time. Keep browser measurements separate from server-side Liquid profiling. The generated summaries are evidence appendices; the agent must still explain issues and resolutions using the report guidance.

Use Liquid hotspots to guide source inspection, matching the remote theme and revision. High inclusive time may reflect expensive children, while self time identifies work in the frame itself. A slow frame alone does not tell you what rewrite will preserve behaviour. Explain the code mechanism and how to retest it.

For before/after comparisons use a new directory, the same page, device, version, consent state, and theme context. Do not compare a public live page against an unrelated preview profile as if they were one experiment. If tools or authentication are unavailable, continue the code review and record the missing measurements.

Raw reports and CLI logs may contain store URLs, page content, screenshots, or sensitive diagnostics. Keep them local, inspect before sharing, and do not commit them with the skill. Only include necessary, reviewed evidence in a shareable audit report.

## Test the helper

```sh
python3 -m unittest discover -s tests -v
```

The tests cover nested/recursive/sampled timings, invalid profiles, missing metrics, partial failures, CLI argument handling, and output preservation. They use fixtures and do not access a store. A real Liquid capture requires your authorised store session.
