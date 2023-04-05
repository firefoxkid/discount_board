from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from datetime import datetime

from ..models import Post, Group

User = get_user_model()


class StaticURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_homepage(self):
        response = self.guest_client.get('/')
        self.assertEqual(response.status_code, 200)


class YatubeURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.post = Post.objects.create(
            text='Тестовый текстТестовый текстТестовый текст',
            pub_date=datetime.now(),
            group=None,
            author=User.objects.create_user(username="Petya"),
        )
        cls.group = Group.objects.create(
            title='test_goup' * 3,
            slug='test-slug',
            description='описание группы огого',
        )

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='AndreyG')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_client2 = Client()
        self.authorized_client2.force_login(YatubeURLTests.post.author)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            '/': 'index.html',
            '/group/test-slug/': 'group.html',
            '/new/': 'posts/new_post.html',
        }
        for adress, template in templates_url_names.items():
            with self.subTest(adress=adress):
                response = self.authorized_client.get(adress)
                self.assertTemplateUsed(response, template)

    def test_url_edit_correct_template(self):
        """URL-адрес /<username>/<post_id>/edit/ использует шаблон
        new_post.html для автора."""
        username = YatubeURLTests.post.author.username
        post_id = YatubeURLTests.post.id
        response = self.authorized_client2.get(
            f'/{username}/{post_id}/edit/',
            follow=True
        )
        self.assertTemplateUsed(response, 'posts/new_post.html')

    def test_url_edit_correct_template(self):
        """URL-адрес /<username>/<post_id>/edit/ использует шаблон
        post.html для неавтора."""
        username = YatubeURLTests.post.author.username
        post_id = YatubeURLTests.post.id
        response = self.authorized_client.get(
            f'/{username}/{post_id}/edit/',
            follow=True
        )
        self.assertTemplateUsed(response, 'posts/post.html')

    def test_urls_exists_at_desired_location(self):
        """Страницы доступные любому пользователю."""
        response = self.guest_client.get('/')
        self.assertEqual(response.status_code, 200)
        templates_url_names = [
            '/',
            '/group/test-slug/',
            f'/{YatubeURLTests.post.author.username}/',
            f'/{YatubeURLTests.post.author.username}/{YatubeURLTests.post.id}/'
        ]
        for adress in templates_url_names:
            with self.subTest(adress=adress):
                response = self.guest_client.get(adress)
                self.assertEqual(response.status_code, 200)

    def test_new_post_url_exists_at_desired_location(self):
        """Страница new_post недоступна неавторизованному пользователю
        и переадресована на логин."""
        response = self.guest_client.get('/new/')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/auth/login/?next=/new/')

    def test_post_edit_page_unauthorized(self):
        """Страница post_edit редиректит неавторизованного пользователя
        и на страницу логина"""
        username = YatubeURLTests.post.author.username
        post_pk = YatubeURLTests.post.pk
        response = self.guest_client.get(
            f'/{username}/{post_pk}/edit/',
            kwargs={'username': YatubeURLTests.post.author.username,
                    'post_id': YatubeURLTests.post.pk,
                    },
            follow=True
        )
        self.assertRedirects(
            response,
            f'/auth/login/?next=/{username}/{post_pk}/edit/')

    def test_post_edit_page_authorized(self):
        """Страница post_edit доступна для автора поста."""
        username = YatubeURLTests.post.author.username
        post_id = YatubeURLTests.post.id
        response = self.authorized_client2.get(
            f'/{username}/{post_id}/edit/',
            follow=True
        )
        self.assertEqual(response.status_code, 200)

    def test_post_edit_page_authorized_notauthor(self):
        """авторизованный неавтор редиректится на post."""
        username = YatubeURLTests.post.author.username
        post_id = YatubeURLTests.post.id
        response = self.authorized_client.get(
            f'/{username}/{post_id}/edit/',
            follow=True
        )
        self.assertRedirects(
            response,
            f'/{username}/{post_id}/'
        )
