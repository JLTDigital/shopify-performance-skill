# Run Lighthouse and Shopify Liquid tests

This guide shows exactly what to enter in your terminal, which values to replace, and where to find the results.

| What do you want to check? | Use this test | Access needed |
| --- | --- | --- |
| How quickly a page loads in a browser, plus Lighthouse scores | **Lighthouse** | A page reachable by Chrome; Shopify admin access is not required for public pages |
| Which Liquid templates, sections, or snippets take time to render | **Shopify Liquid profiler** | An authenticated Shopify account with access to the store and remote theme |

Both tests use [scripts/measure.py](scripts/measure.py). They produce Markdown and JSON summaries that your agent can include in its performance report. They do not edit or publish your theme.

## 1. Set up your computer once

You need:

- **Python 3.10 or later** to run the helper.
- **Node.js 22 or later and npm** to install the CLIs. Check each CLI's current requirements if installation reports a version error.
- **Google Chrome or compatible Chromium** for Lighthouse.
- **Git** if you use the clone command below. Alternatively, download and extract this repository using GitHub's **Code → Download ZIP** option.

Check Python and Node in your terminal:

```sh
python3 --version
node --version
npm --version
```

Install the CLIs:

```sh
npm install -g lighthouse @shopify/cli
```

Confirm that they are available:

```sh
lighthouse --version
shopify version
```

Installing the skill with `npx skills` does **not** install these tools or Chrome.

## 2. Download the helper and open its folder

For manual use, cloning this repository is the simplest starting point:

```sh
git clone https://github.com/JLTDigital/shopify-performance-skill.git
cd shopify-performance-skill
```

Run the remaining commands **from this folder**, where `scripts/measure.py` exists. If you downloaded a ZIP, open a terminal in the extracted folder instead.

If you already installed the skill with `npx skills`, you can use that copy. Replace `scripts/measure.py` in every command with the full path to the installed helper, or ask your agent to locate it. Installation paths vary by agent and installation scope. Relative output paths are resolved from the terminal's current folder.

The commands below are written on one line so they can be copied without shell-specific line-continuation characters. On Windows, if `python3` is unavailable, replace it with `py -3` or your Python 3 command.

## 3. Run a Lighthouse test

### Copy this command and replace the page URL

```sh
python3 scripts/measure.py lighthouse "https://your-store.com/products/your-product" --device mobile --runs 3 --output reports/product-mobile-before
```

**Replace `https://your-store.com/products/your-product` with the full URL of the actual page you want to test.** Keep the quotation marks. You can change the output folder name to describe your page.

This runs three mobile tests and saves the results in `reports/product-mobile-before`. It does not test the entire store; run a separate command for each page and device you want to measure.

### Lighthouse parameters

| Parameter | Required? | What to enter | Default |
| --- | --- | --- | --- |
| URL immediately after `lighthouse` | Yes | A full `https://` or `http://` page URL, such as `"https://your-store.com/products/your-product"`. There is no `--url` flag in this helper. | None |
| `--device` | No | `mobile` or `desktop` | `mobile` |
| `--runs` | No | A whole number from `1` to `20`. Use `3` for a useful repeated-run comparison. | `3` |
| `--output` | Yes | A **new** folder for this test's results, such as `reports/product-mobile-before` | None |
| `--timeout` | No | Positive whole-number seconds allowed for **each run**, such as `300` | `180` |

### More examples

**Homepage, mobile:**

```sh
python3 scripts/measure.py lighthouse "https://your-store.com/" --device mobile --runs 3 --output reports/home-mobile-before
```

**Product page, desktop:**

```sh
python3 scripts/measure.py lighthouse "https://your-store.com/products/your-product" --device desktop --runs 3 --output reports/product-desktop-before
```

**Collection page, allowing up to five minutes per run:**

```sh
python3 scripts/measure.py lighthouse "https://your-store.com/collections/your-collection" --device mobile --runs 3 --timeout 300 --output reports/collection-mobile-before
```

**Retest after making changes:**

```sh
python3 scripts/measure.py lighthouse "https://your-store.com/products/your-product" --device mobile --runs 3 --output reports/product-mobile-after
```

Use the same page, device, run count, and tool version for before/after comparisons. Always use a new output folder: the helper deliberately refuses to overwrite earlier evidence.

### What Lighthouse measures

The summary includes performance, accessibility, best-practices, and SEO scores out of 100, plus available LCP, FCP, CLS, Speed Index, TBT, and document server-response timing. It shows the median, minimum, maximum, and successful sample count.

These are **lab measurements**. TBT is not INP, document server-response timing is not full navigation TTFB, and a Lighthouse score does not establish a field Core Web Vitals pass. Missing audits remain unavailable rather than becoming zero.

Check the final URL and raw report to confirm the intended page was tested. A password screen, bot challenge, or error page may receive a valid score. The helper does not import your browser's login cookies or log into protected pages for Lighthouse. Its default storage reset and device/throttling settings come from Lighthouse; exact settings are retained in the raw JSON.

## 4. Run a Shopify Liquid profile

### A. Find your Shopify store domain

Use your store's **`myshopify.com` domain**, such as `your-store.myshopify.com`. This can differ from the public custom domain used for Lighthouse.

### B. Sign in and find the theme ID

Replace the example store domain, then run:

```sh
shopify theme list --store your-store.myshopify.com
```

Follow any Shopify login prompts. From the returned theme list, copy the ID of the theme you want to profile. Choose the live theme or a specific preview theme intentionally.

### C. Run the profile

```sh
python3 scripts/measure.py liquid --store your-store.myshopify.com --theme 123456789 --path "/products/your-product" --output reports/product-liquid-before
```

Replace these three values:

1. **`your-store.myshopify.com`** → your Shopify store domain.
2. **`123456789`** → the actual theme ID from `shopify theme list`.
3. **`/products/your-product`** → the page path, starting with `/`. Do not put the full website URL here.

You can also change `reports/product-liquid-before` to a descriptive, unused folder name.

### Liquid profiler parameters

| Parameter | Required? | What to enter | Default |
| --- | --- | --- | --- |
| `--store` | Yes | Your `myshopify.com` domain or store prefix. Prefer the domain for clarity. | None |
| `--theme` | Yes | Remote theme ID or name. Prefer the ID copied from the theme list. Quote names containing spaces. | None |
| `--path` | No | A store-relative route, such as `"/"`, `"/products/your-product"`, or `"/collections/your-collection"`. Query parameters are allowed; keep the path quoted. Do not include a `#fragment`. | `/` (homepage) |
| `--output` | Yes | A **new** results folder, such as `reports/product-liquid-before` | None |
| `--timeout` | No | Positive whole-number seconds for the profile command, such as `300` | `180` |

### More examples

**Homepage:**

```sh
python3 scripts/measure.py liquid --store your-store.myshopify.com --theme 123456789 --path "/" --output reports/home-liquid-before
```

**Collection page:**

```sh
python3 scripts/measure.py liquid --store your-store.myshopify.com --theme 123456789 --path "/collections/your-collection" --output reports/collection-liquid-before
```

**A collection URL with sorting and pagination:**

```sh
python3 scripts/measure.py liquid --store your-store.myshopify.com --theme 123456789 --path "/collections/your-collection?sort_by=price-ascending&page=2" --output reports/collection-page2-liquid-before
```

**Retest a product after updating the remote theme:**

```sh
python3 scripts/measure.py liquid --store your-store.myshopify.com --theme 123456789 --path "/products/your-product" --timeout 300 --output reports/product-liquid-after
```

Every example requires your real store domain, theme ID, and page handle.

### Important differences from Lighthouse

- The profiler measures **the remote Shopify theme**, not your local files. Unuploaded local changes will not appear in its results.
- It works on supported storefront routes for stores your account can access, not arbitrary third-party stores or hosted checkout.
- It measures Liquid execution, not browser load time or end-to-end TTFB.
- **Self time** is work in a frame itself. **Inclusive time** includes its descendants. Inclusive times overlap, so do not add the rows together.

The helper calls Shopify's `theme profile` command with `--json` and `--no-input`. Authenticate first: it will not open an interactive login prompt while collecting evidence. In the helper, `--path` is the page route; it is passed to Shopify CLI as `--url`. This differs from Shopify CLI's own `--path` option, which means a local working directory.

Current profiling implementation requires account authentication and rejects Theme Access/Admin API tokens. The helper refuses to run if `SHOPIFY_CLI_THEME_TOKEN` is set. If applicable, remove that variable from the current terminal environment and authenticate with your account instead.

For a password-protected storefront, configure `SHOPIFY_FLAG_STORE_PASSWORD` privately in your environment before profiling. Do not put passwords into reports or committed commands. This setting applies to the Shopify profiler, not Lighthouse.

## 5. Open the results

When collection completes, the helper prints `Evidence saved to ...` with the output directory. Open that folder in your file browser or editor and start with **`summary.md`**.

| File | Created by | What it contains |
| --- | --- | --- |
| `summary.md` | Both tests | Readable results for the audit report |
| `summary.json` | Both tests | Structured results, status, and measurement context |
| `lighthouse-1.json`, `lighthouse-2.json`, etc. | Lighthouse | Full raw results for each run that produced a report |
| `lighthouse-1.stderr.txt`, etc. | Lighthouse | Per-run diagnostics |
| `liquid.speedscope.json` | Liquid | Raw profile; usable in a trusted local Speedscope-compatible viewer when valid |
| `liquid.stderr.txt` | Liquid | Profiler diagnostics |

The Liquid Markdown summary lists up to 20 frames per profile, ranked by self time. The JSON summary retains the full frame list. Supported evented and weighted sampled time profiles are normalised to milliseconds; unknown or malformed formats are reported as failures.

Successful collection returns exit status `0`. Failed or partially failed collection returns `1`; invalid command arguments return `2`. Partial Lighthouse results are retained. Preflight failures, such as a missing CLI, may stop before summaries are written. Check the terminal message as well as the output folder.

## 6. Ask your agent to use the results

After running the tests, use a prompt such as:

> Use the Shopify performance skill to review this theme. Include the Lighthouse results in reports/product-mobile-before and the Liquid profile in reports/product-liquid-before. Write a clear report explaining the issues, where they occur, how to fix them, and how to verify the improvements.

For a comparison:

> Compare the before and after measurements in reports/product-mobile-before and reports/product-mobile-after. Explain what changed, which measurements improved or regressed, and any limits in the evidence.

The summaries are evidence appendices, not the full audit. The agent should connect measurements to verified theme code and recommended fixes, following [report.md](report.md). Include page/device or store/theme context, capture times, versions, warnings, failed runs, and links to raw evidence. Keep Lighthouse and Liquid results separate.

Before comparing results, confirm that the browser URL and Liquid theme refer to the intended version. Keep device, consent state, content, and tool settings consistent. If tools or store access are unavailable, continue the code review and identify the missing measurements.

Keep raw reports and logs local and review them before sharing: they can contain store content or sensitive diagnostics. The repository ignores `reports/` so test output is not accidentally committed.

## Troubleshooting

| Problem | What to do |
| --- | --- |
| `python3`, `lighthouse`, or `shopify` is not found | Install the relevant prerequisite, reopen your terminal, and repeat the version checks. On Windows, try `py -3` for Python. |
| Python cannot find `scripts/measure.py` | Run from the cloned repository folder, or use the full path to the installed helper. |
| `File exists` for the output folder | Choose a new name, such as `reports/product-mobile-before-2`. Even a failed attempt may have created the folder. |
| `Unable to connect to Chrome` | Confirm Chrome is installed and can launch. Check the local stderr log and environment restrictions. If needed, set `CHROME_PATH` to the installed Chrome executable. |
| The result describes a password or challenge page | Do not use that score as a storefront measurement. Provide an accessible authorised page, or collect authenticated browser evidence separately. |
| Liquid authentication or access fails | Run `shopify theme list --store your-store.myshopify.com` interactively, complete login, and verify that the theme belongs to that store. |
| Liquid rejects token authentication | Remove `SHOPIFY_CLI_THEME_TOKEN` from the current environment and use account authentication. |
| A run times out | Retry in a new folder with `--timeout 300`; inspect the log if it still fails. |
| Liquid returns invalid JSON or an unsupported profile | Retain the raw output and stderr for inspection. Confirm your CLI version and supported flags; do not interpret the failed run as a fast result. |

Show the helper's built-in help:

```sh
python3 scripts/measure.py lighthouse --help
python3 scripts/measure.py liquid --help
```

## For contributors: test the helper

```sh
python3 -m unittest discover -s tests -v
```

These fixture-based tests do not access a store. Real Liquid validation requires an authorised store session.

## Official references

- [Lighthouse CLI setup and options](https://github.com/GoogleChrome/lighthouse#using-the-node-cli)
- [Shopify theme profile](https://shopify.dev/docs/api/shopify-cli/theme/theme-profile)
- [Shopify profiling implementation and authentication limitation](https://github.com/Shopify/cli/blob/main/packages/theme/src/cli/services/profile.ts)
- [Speedscope file format](https://github.com/jlfwong/speedscope/blob/main/src/lib/file-format-spec.ts)
