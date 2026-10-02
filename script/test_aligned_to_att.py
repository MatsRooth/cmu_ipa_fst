#!/usr/bin/env python3
"""Small end-to-end regression checks; run with Python 3."""
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).with_name('aligned_to_att.py')


def paths(att):
    arcs, finals = {}, set()
    for line in att.read_text().splitlines():
        fields = line.split('\t')
        if len(fields) == 1:
            finals.add(int(fields[0]))
        else:
            s, t, u, l = fields
            arcs.setdefault(int(s), []).append((int(t), u, l))
    result = set()
    def visit(s, sequence):
        if s in finals:
            result.add(tuple(sequence))
        for t, u, l in arcs.get(s, []):
            visit(t, sequence + [(u, l)])
    visit(0, [])
    return result


class Conversion(unittest.TestCase):
    def test_formats_and_chunks(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            source = root / 'source'
            source.write_text('n|g}NG e}_\nx}K|S\n_}AH0\nn|g}NG e}_\n')
            expected = {(('ng', 'ŋ'), ('e', 'NULL')), (('x', 'k|s'),), (('NULL', 'ə0'),)}
            for representation in ('relation', 'interleaved', 'pairs'):
                out, orth = root / 'out.att', root / 'orth.att'
                phon = root / 'phon.att'
                subprocess.run([sys.executable, str(SCRIPT), str(source), '--representation', representation,
                                '--output', str(out), '--orthographic-output', str(orth), '--phonetic-output', str(phon)], check=True, capture_output=True)
                target = expected
                if representation == 'interleaved':
                    target = {tuple((s, s) for pair in path for s in pair) for path in expected}
                elif representation == 'pairs':
                    target = {tuple((u+'}'+l, u+'}'+l) for u, l in path) for path in expected}
                self.assertEqual(paths(out), target)
                self.assertIn((('n', '@0@'), ('g', 'ng')), paths(orth))
                self.assertIn((('@0@', 'NULL'),), paths(orth))
                self.assertEqual(paths(phon), {(('ŋ', 'ŋ'),), (('k|s', 'k'), ('@0@', 's')), (('ə0', 'ə0'),), (('NULL', '@0@'),)})

    def test_epsilon_and_stress(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            source, out = root / 'source', root / 'out'
            source.write_text('a}AH0 a}EY1 e}_\n')
            subprocess.run([sys.executable, str(SCRIPT), str(source), '--epsilon', '--stress', 'strip',
                            '--no-orthographic', '--no-phonetic', '--output', str(out)], check=True, capture_output=True)
            self.assertEqual(paths(out), {(('a', 'ə'), ('a', 'eɪ'), ('e', '@0@'))})

    def test_bad_phone_reports_line(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            source = root / 'source'
            source.write_text('a}BOGUS\n')
            out = root / 'out'
            r = subprocess.run([sys.executable, str(SCRIPT), str(source), '--output', str(out),
                                '--no-orthographic'], capture_output=True, text=True)
            self.assertNotEqual(r.returncode, 0)
            self.assertIn(':1:', r.stderr)
            self.assertFalse(out.exists())


if __name__ == '__main__':
    unittest.main()
