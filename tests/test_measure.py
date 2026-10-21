import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location('measure', Path(__file__).parents[1] / 'scripts/measure.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


def profile(events=None):
    return {'shared': {'frames': [{'name': 'layout'}, {'name': 'product', 'file': 'sections/product.liquid', 'line': 4}]},
            'profiles': [{'name': 'page', 'type': 'evented', 'unit': 'microseconds',
                          'startValue': 0, 'endValue': 10000, 'events': events or [
                              {'type': 'O', 'frame': 0, 'at': 0},
                              {'type': 'O', 'frame': 1, 'at': 2000},
                              {'type': 'C', 'frame': 1, 'at': 6000},
                              {'type': 'C', 'frame': 0, 'at': 10000}]}]}


def lighthouse(score=.8):
    return {'lighthouseVersion': '13.4.1', 'categories': {'performance': {'score': score}},
            'audits': {'largest-contentful-paint': {'numericValue': 2400}},
            'requestedUrl': 'https://example.com', 'finalDisplayedUrl': 'https://example.com',
            'configSettings': {'formFactor': 'mobile'}}


class MeasurementTests(unittest.TestCase):
    def test_nested_self_and_inclusive(self):
        rows = {r['name']: r for r in m.profile_result(profile())[0]['frames']}
        self.assertEqual(rows['layout']['inclusiveMs'], 10)
        self.assertEqual(rows['layout']['selfMs'], 6)
        self.assertEqual(rows['product']['selfMs'], 4)

    def test_recursion_not_double_counted(self):
        p = profile()
        p['profiles'][0]['events'][1]['frame'] = 0
        p['profiles'][0]['events'][2]['frame'] = 0
        row = m.profile_result(p)[0]['frames'][0]
        self.assertEqual(row['inclusiveMs'], 10)
        self.assertEqual(row['selfMs'], 10)

    def test_sampled_seconds(self):
        p = profile()
        p['profiles'][0] = {'name': 'sampled', 'type': 'sampled', 'unit': 'seconds',
                            'startValue': 0, 'endValue': .01, 'samples': [[0, 1], [0]], 'weights': [.004, .006]}
        rows = {r['name']: r for r in m.profile_result(p)[0]['frames']}
        self.assertEqual(rows['layout']['selfMs'], 6)
        self.assertEqual(rows['product']['selfMs'], 4)

    def test_malformed_profile_rejected(self):
        for mutation in ('unbalanced', 'order', 'unit', 'frame'):
            p = profile()
            if mutation == 'unbalanced': p['profiles'][0]['events'].pop()
            if mutation == 'order': p['profiles'][0]['events'][1]['at'] = -1
            if mutation == 'unit': p['profiles'][0]['unit'] = 'bytes'
            if mutation == 'frame': p['profiles'][0]['events'][0]['frame'] = 99
            with self.subTest(mutation=mutation), self.assertRaises(ValueError): m.profile_result(p)

    def test_null_scores_and_missing_metrics(self):
        p = lighthouse()
        p['categories']['seo'] = {'score': None}
        r = m.lighthouse_result(p)
        self.assertIsNone(r['categories']['seo'])
        self.assertIsNone(r['metrics']['CLS']['value'])
        self.assertEqual(r['categories']['performance'], 80)

    def test_lighthouse_runtime_error_rejected(self):
        p = lighthouse()
        p['runtimeError'] = {'code': 'NO_FCP'}
        with self.assertRaises(ValueError): m.lighthouse_result(p)

    def test_failed_runs_excluded_from_median(self):
        data = [{'status': 'ok', 'result': m.lighthouse_result(lighthouse(score))} for score in (.4, .8, .9)]
        data.append({'status': 'failed'})
        result = m.aggregate(data)
        self.assertEqual(result['categories']['performance']['median'], 80)
        self.assertEqual(result['categories']['performance']['n'], 3)
        self.assertEqual(result['metrics']['CLS']['n'], 0)

    def test_lighthouse_cli_artifacts_and_partial_failure(self):
        calls = []
        def fake(args, timeout):
            calls.append(args)
            if len(calls) == 2: raise subprocess.TimeoutExpired(args, timeout)
            target = next(a.split('=', 1)[1] for a in args if a.startswith('--output-path='))
            Path(target).write_text(json.dumps(lighthouse()))
            return subprocess.CompletedProcess(args, 0, '', '')
        with tempfile.TemporaryDirectory() as tmp, patch.object(m.shutil, 'which', return_value='/bin/lighthouse'), patch.object(m, 'execute', side_effect=fake):
            out = Path(tmp) / 'evidence'
            code = m.main(['lighthouse', 'https://example.com/?x=a&y=b', '--output', str(out), '--device', 'desktop'])
            self.assertEqual(code, 1)
            result = json.loads((out / 'summary.json').read_text())
            self.assertEqual(result['successfulRuns'], 2)
            self.assertTrue((out / 'summary.md').exists())
            self.assertIn('--preset=desktop', calls[0])
            self.assertEqual(calls[0][1], 'https://example.com/?x=a&y=b')

    def test_liquid_cli_artifacts(self):
        calls = []
        def fake(args, timeout):
            calls.append(args)
            return subprocess.CompletedProcess(args, 0, '4.9.4' if args[-1] == 'version' else json.dumps(profile()), '')
        with tempfile.TemporaryDirectory() as tmp, patch.dict('os.environ', {}, clear=True), patch.object(m.shutil, 'which', return_value='/bin/shopify'), patch.object(m, 'execute', side_effect=fake):
            out = Path(tmp) / 'evidence'
            self.assertEqual(m.main(['liquid', '--store', 'example.myshopify.com', '--theme', '123', '--path', '/products/example', '--output', str(out)]), 0)
            self.assertTrue((out / 'liquid.speedscope.json').exists())
            self.assertIn('--json', calls[0])
            self.assertIn('--no-input', calls[0])
            self.assertEqual(json.loads((out / 'summary.json').read_text())['status'], 'ok')

    def test_liquid_invalid_json_keeps_raw_and_reports_failure(self):
        def fake(args, timeout):
            return subprocess.CompletedProcess(args, 0, '4.9.4' if args[-1] == 'version' else '<html>login</html>', 'diagnostic')
        with tempfile.TemporaryDirectory() as tmp, patch.dict('os.environ', {}, clear=True), patch.object(m.shutil, 'which', return_value='/bin/shopify'), patch.object(m, 'execute', side_effect=fake):
            out = Path(tmp) / 'evidence'
            self.assertEqual(m.main(['liquid', '--store', 'example', '--theme', '123', '--output', str(out)]), 1)
            self.assertEqual((out / 'liquid.speedscope.json').read_text(), '<html>login</html>')
            self.assertEqual((out / 'liquid.stderr.txt').read_text(), 'diagnostic')
            self.assertEqual(json.loads((out / 'summary.json').read_text())['status'], 'failed')

    def test_token_auth_rejected_without_executing_cli(self):
        with tempfile.TemporaryDirectory() as tmp, patch.dict('os.environ', {'SHOPIFY_CLI_THEME_TOKEN': 'test-only'}), patch.object(m, 'execute') as execute:
            self.assertEqual(m.main(['liquid', '--store', 'example', '--theme', '123', '--output', str(Path(tmp) / 'evidence')]), 1)
            execute.assert_not_called()

    def test_existing_output_not_overwritten(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / 'summary.json'
            p.write_text('keep')
            self.assertEqual(m.main(['lighthouse', 'https://example.com', '--output', tmp]), 1)
            self.assertEqual(p.read_text(), 'keep')


if __name__ == '__main__': unittest.main()
