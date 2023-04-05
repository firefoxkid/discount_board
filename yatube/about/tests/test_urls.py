from django.test import Client, TestCase


class StaticURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.templates_url_names = {
            '/about/author/': 'about/author.html',
            '/about/tech/': 'about/tech.html',
        }

    def setUp(self):
        self.guest_client = Client()

    def test_about_urls_exists_at_desired_location(self):
        """Проверка доступности адресов в about."""
        for adress, template in StaticURLTests.templates_url_names.items():
            with self.subTest(adress=adress):
                response = self.guest_client.get(adress)
                self.assertEqual(response.status_code, 200)

    def test_about_urls_used_correct_template(self):
        """Проверка использования соответствующих
        шаблонов в приложении about."""
        for adress, template in StaticURLTests.templates_url_names.items():
            with self.subTest(adress=adress):
                response = self.guest_client.get(adress)
                self.assertTemplateUsed(response, template)
