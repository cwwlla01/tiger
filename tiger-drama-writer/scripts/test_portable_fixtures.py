"""Reject missing portable fixtures and accidental absolute runtime dependencies."""
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
REQUIRED=("bridge_letters_raw.md", "five_first_draft.md", "lockbox_five_raw.md", "lockbox_five_revised.md", "EP04_revision1.md", "EP04_timing_plan.json")

class PortableFixtureTests(unittest.TestCase):
    def test_all_fixtures_are_bundled(self):
        for name in REQUIRED:
            with self.subTest(name=name):
                file=ROOT/'tests'/'fixtures'/name
                self.assertTrue(file.is_file(), f"Missing required regression fixture: {file}")
                self.assertGreater(file.stat().st_size, 100)
    def test_no_version_specific_absolute_fixture_paths(self):
        for name in ('test_release_gate.py','test_scene_checkpoint.py','test_audit_rehearsal.py'):
            source=(ROOT/'scripts'/name).read_text(encoding='utf-8')
            with self.subTest(script=name):
                self.assertNotIn('/mnt/data/v',source)
                self.assertNotIn("parents[2] / 'trials'",source)
    def test_release_gate_fixtures_are_not_optional(self):
        s=(ROOT/'scripts'/'test_release_gate.py').read_text()
        self.assertNotIn('if fixture.exists()',s)
        self.assertNotIn('if legacy.exists()',s)

if __name__=='__main__':unittest.main()
