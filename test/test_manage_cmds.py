from io import StringIO
from unittest import TestCase

from django.core.management import call_command

from test import JuntagricoCustomSubTestCase


class ManagementCommandsTest(TestCase):
    def test_generate_basic_data(self):
        out = StringIO()
        call_command('cs_generate_basic_data', stdout=out)
        self.assertEqual(out.getvalue(), '')

    def test_generate_testdata(self):
        out = StringIO()
        call_command('cs_generate_testdata', stdout=out)
        self.assertEqual(out.getvalue(), '')


class DepotlistTests(JuntagricoCustomSubTestCase):
    def test_cs_depot_list(self):
        out = StringIO()
        call_command('cs_generate_depot_list', '--force', stdout=out)
        self.assertEqual(out.getvalue(), '')
