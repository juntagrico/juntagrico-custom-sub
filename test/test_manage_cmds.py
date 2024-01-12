from io import StringIO
from unittest import TestCase

from django.core.management import call_command


class ManagementCommandsTest(TestCase):
    def test_generate_testdata(self):
        out = StringIO()
        call_command('cs_generate_testdata', stdout=out)
        self.assertEqual(out.getvalue(), '')
