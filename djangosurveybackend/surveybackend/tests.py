# Create your tests here.
from django.test import TestCase


class ViewsTestCase(TestCase):
    def test_index_loads_properly(self):
        """The index page loads properly"""
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
