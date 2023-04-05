from django.test import Client, TestCase
from django.urls import reverse


class StaticViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.views_url_names = {
            'about:author': 'about/author.html',
            'about:tech': 'about/tech.html',
        }

    def setUp(self):
        self.guest_client = Client()

    def test_view_page_accessible_by_name(self):
        """генерируемая при помощи view страница доступна"""
        for view, template in StaticViewsTests.views_url_names.items():
            with self.subTest(view=view):
                response = self.guest_client.get(reverse(view))
                self.assertEqual(response.status_code, 200)

    def test_tempalte_page_accessible_by_name(self):
        """проверка шаблонов, вызываемых во view"""
        for view, template in StaticViewsTests.views_url_names.items():
            with self.subTest(view=view):
                response = self.guest_client.get(reverse(view))
                self.assertTemplateUsed(response, template)
