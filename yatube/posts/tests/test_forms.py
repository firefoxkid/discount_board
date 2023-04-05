from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from ..forms import PostForm
from ..models import Post

User = get_user_model()


class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username="kek1")
        cls.post = Post.objects.create(
            text='Тестовый пост',
            group=None,
            author=cls.user,
        )
        cls.form = PostForm()

    def setUp(self):
        self.user = User.objects.get(username='kek1')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post(self):
        """Валидная форма создает запись Post."""
        post_count = Post.objects.count()
        form_data = {
            'text': 'Тестовый пост2',
        }
        response = self.authorized_client.post(
            reverse('new_post'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse('index'))
        self.assertEqual(Post.objects.count(), post_count + 1)
        self.assertTrue(
            Post.objects.filter(
                text='Тестовый пост2',
            ).exists()
        )

    def test_post_edit_correct_save(self):
        """При редактировании поста изменяется запись в базе данных."""
        post = Post.objects.first()
        form_data = {'text': 'Измененный тестовый пост'}
        self.authorized_client.post(reverse(
            'post_edit', kwargs={'username': self.user.username,
                                 'post_id': post.id}),
            data=form_data, follow=True)
        self.assertEqual(Post.objects.get(
            text='Измененный тестовый пост'), post)

    def test_cant_create_existing_text(self):
        """Проверим, форма не дала создать неуникальный 'Тестовый пост'"""
        post_count = Post.objects.count()
        form_data = {
            'text': 'Тестовый пост',
        }
        response = self.authorized_client.post(
            reverse('new_post'),
            data=form_data,
            follow=True
        )
        self.assertEqual(Post.objects.count(), post_count)
        self.assertEqual(response.status_code, 200)
