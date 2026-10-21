#!/usr/bin/env python3
"""Collect Lighthouse or Shopify Liquid evidence using installed CLIs. Python 3.10+."""
import argparse
from datetime import datetime, timezone
import json
import math
from pathlib import Path
import shutil
import statistics
import subprocess
import sys
from urllib.parse import urlsplit


METRICS = {
    'largest-contentful-paint': ('LCP', 'ms'),
    'first-contentful-paint': ('FCP', 'ms'),
    'speed-index': ('Speed Index', 'ms'),
    'total-blocking-time': ('TBT (not INP)', 'ms'),
    'cumulative-layout-shift': ('CLS', 'unitless'),
    'server-response-time': ('Document server response (not navigation TTFB)', 'ms'),
}


def number(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def cell(value):
    return str(value).replace('|', '\\|').replace('\n', ' ').replace('\r', ' ')


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + '\n')


def execute(args, timeout=180):
    # Argument arrays avoid shell interpolation; no automatic package downloads.
    return subprocess.run(args, capture_output=True, text=True, timeout=timeout, check=True)


def lighthouse_result(data):
    if data.get('runtimeError'):
        raise ValueError('Lighthouse reported a runtime error; inspect the raw report')
    if not data.get('lighthouseVersion') or not isinstance(data.get('audits'), dict):
        raise ValueError('Not a Lighthouse result')
    categories = {}
    for key, category in data.get('categories', {}).items():
        score = category.get('score')
        categories[key] = round(score * 100, 2) if number(score) and 0 <= score <= 1 else None
    metrics = {}
    for key, (label, unit) in METRICS.items():
        audit = data['audits'].get(key, {})
        value = audit.get('numericValue')
        metrics[label] = {'value': value if number(value) and audit.get('scoreDisplayMode') != 'error' else None,
                          'unit': unit}
    if not number(categories.get('performance')):
        raise ValueError('Lighthouse performance score is unavailable')
    return {'categories': categories, 'metrics': metrics,
            'requestedUrl': data.get('requestedUrl'), 'finalUrl': data.get('finalDisplayedUrl') or data.get('finalUrl'),
            'fetchTime': data.get('fetchTime'), 'lighthouseVersion': data['lighthouseVersion'],
            'configSettings': data.get('configSettings'), 'environment': data.get('environment'),
            'warnings': data.get('runWarnings', [])}


def statistics_for(values):
    values = [value for value in values if number(value)]
    if not values:
        return {'n': 0, 'median': None, 'min': None, 'max': None}
    return {'n': len(values), 'median': statistics.median(values), 'min': min(values), 'max': max(values)}


def aggregate(runs):
    valid = [run['result'] for run in runs if run['status'] == 'ok']
    categories = sorted({key for run in valid for key in run['categories']})
    return {
        'categories': {key: statistics_for([run['categories'].get(key) for run in valid]) for key in categories},
        'metrics': {label: {**statistics_for([run['metrics'][label]['value'] for run in valid]), 'unit': unit}
                    for label, unit in METRICS.values()},
    }


def profile_result(data):
    """Summarise supported Speedscope profiles; inclusive values overlap across frames."""
    frames = data['shared']['frames']
    profiles = data['profiles']
    if not isinstance(frames, list) or not profiles:
        raise ValueError('Profile has no frames or profiles')
    result = []
    scales = {'seconds': 1000, 'milliseconds': 1, 'microseconds': .001, 'nanoseconds': .000001}
    for profile in profiles:
        scale = scales.get(profile.get('unit'))
        if scale is None:
            raise ValueError('Unsupported profile timing unit')
        start, end = profile['startValue'], profile['endValue']
        if not number(start) or not number(end) or end < start:
            raise ValueError('Invalid profile bounds')
        inclusive, own = [0.0] * len(frames), [0.0] * len(frames)

        def credit(stack, duration):
            for frame in stack:
                if type(frame) is not int or not 0 <= frame < len(frames):
                    raise ValueError('Invalid frame index')
            if not number(duration) or duration < 0:
                raise ValueError('Invalid profile duration')
            for frame in set(stack):
                inclusive[frame] += duration * scale
            if stack:
                own[stack[-1]] += duration * scale

        if profile['type'] == 'evented':
            stack, previous = [], start
            for event in profile['events']:
                at, frame = event['at'], event['frame']
                if not number(at) or not previous <= at <= end:
                    raise ValueError('Out-of-order or out-of-bounds profile event')
                if type(frame) is not int or not 0 <= frame < len(frames):
                    raise ValueError('Invalid frame index')
                credit(stack, at - previous)
                if event['type'] == 'O':
                    stack.append(frame)
                elif event['type'] == 'C' and stack and stack[-1] == frame:
                    stack.pop()
                else:
                    raise ValueError('Unbalanced profile events')
                previous = at
            if stack:
                raise ValueError('Unclosed profile frames')
        elif profile['type'] == 'sampled':
            samples, weights = profile['samples'], profile['weights']
            if len(samples) != len(weights):
                raise ValueError('Sample/weight count mismatch')
            for stack, weight in zip(samples, weights):
                credit(stack, weight)
            if sum(weights) > end - start + max(1e-9, (end - start) * 1e-6):
                raise ValueError('Sample weights exceed profile bounds')
        else:
            raise ValueError('Unsupported Speedscope profile type')
        rows = [{'name': frame['name'], 'file': frame.get('file'), 'line': frame.get('line'),
                 'selfMs': own[i], 'inclusiveMs': inclusive[i]}
                for i, frame in enumerate(frames) if inclusive[i] > 0]
        result.append({'name': profile.get('name'), 'type': profile['type'],
                       'durationMs': (end - start) * scale,
                       'frames': sorted(rows, key=lambda row: row['selfMs'], reverse=True)})
    return result


def run_lighthouse(args, out):
    binary = shutil.which('lighthouse')
    if not binary:
        raise ValueError('Install Lighthouse CLI and Chrome first; see runtime.md')
    runs = []
    for index in range(1, args.runs + 1):
        raw = out / f'lighthouse-{index}.json'
        command = [binary, args.url, '--output=json', '--output-path=' + str(raw),
                   '--chrome-flags=--headless', '--quiet', '--only-categories=performance,accessibility,best-practices,seo']
        if args.device == 'desktop':
            command.append('--preset=desktop')
        try:
            completed = execute(command, args.timeout)
            (out / f'lighthouse-{index}.stderr.txt').write_text(completed.stderr)
            parsed = lighthouse_result(json.loads(raw.read_text()))
            runs.append({'run': index, 'status': 'ok', 'raw': raw.name, 'result': parsed})
        except (subprocess.SubprocessError, OSError, ValueError, KeyError, TypeError) as error:
            # Keep raw CLI errors local; reports deliberately avoid echoing credentials or URLs from errors.
            stderr = getattr(error, 'stderr', '') or ''
            if isinstance(stderr, bytes):
                stderr = stderr.decode(errors='replace')
            if stderr or not (out / f'lighthouse-{index}.stderr.txt').exists():
                (out / f'lighthouse-{index}.stderr.txt').write_text(stderr)
            runs.append({'run': index, 'status': 'failed', 'errorType': type(error).__name__, 'raw': raw.name if raw.exists() else None})
        print(f'Lighthouse run {index}/{args.runs}: {runs[-1]["status"]}', flush=True)
    summary = {'kind': 'lighthouse', 'createdAt': datetime.now(timezone.utc).isoformat(),
               'url': args.url, 'device': args.device, 'requestedRuns': args.runs,
               'successfulRuns': sum(run['status'] == 'ok' for run in runs), 'runs': runs,
               'aggregate': aggregate(runs)}
    lines = ['# Lighthouse lab measurements', '', f'Page: {cell(args.url)}',
             f'Device preset: {args.device}. Successful runs: {summary["successfulRuns"]}/{args.runs}.', '',
             'Scores are 0–100. These are lab results, not field Core Web Vitals. INP was not measured.', '',
             '| Measurement | Median | Min | Max | Samples | Unit |', '| --- | ---: | ---: | ---: | ---: | --- |']
    for group in ('categories', 'metrics'):
        for name, stat in summary['aggregate'][group].items():
            vals = ['Not measured' if stat[k] is None else f'{stat[k]:.3f}' for k in ('median', 'min', 'max')]
            lines.append('| ' + ' | '.join([cell(name), *vals, str(stat['n']), stat.get('unit', 'score / 100')]) + ' |')
    lines += ['', '## Run evidence', '']
    for run in runs:
        lines.append(f'- Run {run["run"]}: {run["status"]}. Raw: {run["raw"] or "unavailable"}.')
        if run['status'] == 'ok':
            r = run['result']
            lines.append(f'  Final page: {cell(r["finalUrl"])}; Lighthouse {cell(r["lighthouseVersion"])}; {cell(r["fetchTime"])}.')
            if r['warnings']:
                lines.append('  Warnings: ' + '; '.join(cell(warning) for warning in r['warnings']))
    lines += ['', 'Confirm the final page is the intended storefront, not a password/challenge/error page.',
              'Inspect raw configSettings/environment for throttling and browser details. Compare like-for-like runs.',
              'A missing document server-response audit is unavailable, not zero; that audit is not full navigation TTFB.',
              'Measurements require interpretation alongside theme code; this appendix is not a complete audit.']
    return summary, '\n'.join(lines) + '\n', summary['successfulRuns'] == args.runs


def run_liquid(args, out):
    import os
    if os.environ.get('SHOPIFY_CLI_THEME_TOKEN'):
        raise ValueError('Liquid profiling requires account authentication; unset SHOPIFY_CLI_THEME_TOKEN')
    binary = shutil.which('shopify')
    if not binary:
        raise ValueError('Install Shopify CLI and authenticate first; see runtime.md')
    command = [binary, 'theme', 'profile', '--store', args.store, '--theme', args.theme,
               '--url', args.path, '--json', '--no-color', '--no-input']
    raw = out / 'liquid.speedscope.json'
    summary = {'kind': 'liquid', 'createdAt': datetime.now(timezone.utc).isoformat(),
               'store': args.store, 'theme': args.theme, 'path': args.path, 'status': 'failed'}
    try:
        completed = execute(command, args.timeout)
        raw.write_text(completed.stdout)
        (out / 'liquid.stderr.txt').write_text(completed.stderr)
        summary['profiles'] = profile_result(json.loads(completed.stdout))
        summary['status'] = 'ok'
    except (subprocess.SubprocessError, OSError, ValueError, KeyError, TypeError) as error:
        summary['errorType'] = type(error).__name__
        stderr = getattr(error, 'stderr', '') or ''
        if isinstance(stderr, bytes):
            stderr = stderr.decode(errors='replace')
        if stderr or not (out / 'liquid.stderr.txt').exists():
            (out / 'liquid.stderr.txt').write_text(stderr)
    try:
        summary['shopifyCliVersion'] = execute([binary, 'version'], 15).stdout.strip()
    except (subprocess.SubprocessError, OSError):
        summary['shopifyCliVersion'] = 'Unavailable'
    lines = ['# Shopify Liquid profile', '', f'Store: {cell(args.store)}; theme: {cell(args.theme)}; path: {cell(args.path)}.',
             f'Status: {summary["status"]}. CLI: {cell(summary["shopifyCliVersion"])}.',
             f'Captured: {summary["createdAt"]}.', '',
             'Liquid execution timings are not browser LCP or navigation TTFB. Inclusive timings overlap; do not sum them.']
    if summary['status'] == 'ok':
        for profile in summary['profiles']:
            lines += ['', f'## {cell(profile["name"])}', '', f'Profile span: {profile["durationMs"]:.3f} ms.', '',
                      '| Frame | Source reported by profiler | Self ms | Inclusive ms |', '| --- | --- | ---: | ---: |']
            for row in profile['frames'][:20]:
                source = f'{row["file"]}:{row["line"]}' if row['file'] else 'Not supplied'
                lines.append(f'| {cell(row["name"])} | {cell(source)} | {row["selfMs"]:.3f} | {row["inclusiveMs"]:.3f} |')
        lines += ['', 'Raw evidence: liquid.speedscope.json. Full frame summaries: summary.json.',
                  'Verify profiler source locations against the matching local theme revision before recommending a patch.']
    else:
        lines += ['', 'No usable timings. Inspect local liquid.stderr.txt and any raw output; verify authentication, theme, and path.',
                  'Do not treat this failed measurement as a fast result.']
    return summary, '\n'.join(lines) + '\n', summary['status'] == 'ok'


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    lh = commands.add_parser('lighthouse', help='Run repeated browser measurements')
    lh.add_argument('url')
    lh.add_argument('--runs', type=int, default=3)
    lh.add_argument('--device', choices=['mobile', 'desktop'], default='mobile')
    liquid = commands.add_parser('liquid', help='Profile a page on an accessible Shopify theme')
    liquid.add_argument('--store', required=True, help='Store prefix or myshopify.com domain')
    liquid.add_argument('--theme', required=True, help='Explicit remote theme ID or name')
    liquid.add_argument('--path', default='/', help='Store-relative page path, optionally with query')
    for command in (lh, liquid):
        command.add_argument('--output', required=True, type=Path, help='New output directory; must not already exist')
        command.add_argument('--timeout', type=int, default=180, help='Seconds per CLI invocation')
    args = parser.parse_args(argv)
    if args.timeout < 1:
        parser.error('--timeout must be positive')
    if args.command == 'lighthouse':
        url = urlsplit(args.url)
        if url.scheme not in ('https', 'http') or not url.hostname or url.username or url.password:
            parser.error('Use an HTTP(S) URL without embedded credentials')
        if not 1 <= args.runs <= 20:
            parser.error('--runs must be between 1 and 20')
    elif not args.path.startswith('/') or args.path.startswith('//') or urlsplit(args.path).fragment:
        parser.error('--path must be a store-relative path without a fragment')
    out = args.output.resolve()
    try:
        out.mkdir(parents=True, exist_ok=False, mode=0o700)
        summary, markdown, ok = (run_lighthouse if args.command == 'lighthouse' else run_liquid)(args, out)
        write_json(out / 'summary.json', summary)
        (out / 'summary.md').write_text(markdown)
        print(f'Evidence saved to {out}')
        return 0 if ok else 1
    except (ValueError, OSError) as error:
        print(str(error), file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
