from django.core.files.uploadedfile import SimpleUploadedFile
from ..forms import PostForm
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from datetime import datetime
from django import forms
from django.conf import settings
from django.core.cache import cache
from django.shortcuts import get_object_or_404
import shutil
import tempfile

from ..models import Comment, Follow, Post, Group

User = get_user_model()


class PostsPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        settings.MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
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
        cls.form = PostForm()

    def setUp(self):
        self.user = User.objects.create_user(username='StasBasov')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)

    def test_pages_use_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            reverse('index'): 'index.html',
            (reverse('group_posts',
                     kwargs={'slug': 'test-slug'}
                     )
             ): 'group.html',
            reverse('new_post'): 'posts/new_post.html',
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_create_post_image(self):
        """Проверка создания поста в базе из формы с картинкой"""
        group = PostsPagesTests.group
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00'
            b'\x01\x00\x00\x01\x00\x21\xf9\x04'
            b'\x01\x0a\x00\x01\x00\x2c\x00\x00'
            b'\x00\x00\x01\x00\x01\x00\x00\x02'
            b'\x02\x4c\x01\x00\x3b'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        form_data = {
            'text': 'Тестовый пост для проверки формы',
            'group': group.id,
            'image': uploaded,
        }
        self.authorized_client.post(
            reverse('new_post'),
            data=form_data,
            follow=True
        )
        print(form_data['image'].name)
        db_post = Post.objects.first()
        self.assertTrue(db_post.image.name)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.posts = []
        cls.user = User.objects.create_user(username="Kek")
        cls.group = Group.objects.create(
            title='test_goup' * 3,
            slug='test-slug',
            description='описание группы огого',
        )
        for i in range(13):
            cls.posts.append(
                Post(
                    text=f'Тестовый текстТестовый текстТестовый текст  {i}',
                    pub_date=datetime.now(),
                    group=cls.group,
                    author=cls.user,
                )
            )
        Post.objects.bulk_create(cls.posts)

    def setUp(self):
        self.user = User.objects.create_user(username='StasBasov')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_profile_page_contains_ten_records(self):
        """
        Паджинатор делит 13 постов по страницам
        10 на первой, и 3 на второй на примере страницы
        профиля, индекса и группы.
        """
        pages = {f'/{PaginatorViewsTest.user.username}/': 10,
                 f'/{PaginatorViewsTest.user.username}/?page=2': 3,
                 '/': 10,
                 '/?page=2': 3,
                 f'/group/{PaginatorViewsTest.group.slug}/': 10,
                 f'/group/{PaginatorViewsTest.group.slug}/?page=2': 3}
        for url, post_count in pages.items():
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(
                    len(response.context.get('page').object_list),
                    post_count)


class ContextsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username="kek1")
        cls.user2 = User.objects.create_user(username="kek2")
        cls.group = Group.objects.create(
            title='test_goup' * 3,
            slug='test-slug',
            description='описание группы огого',
        )
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00'
            b'\x01\x00\x00\x01\x00\x21\xf9\x04'
            b'\x01\x0a\x00\x01\x00\x2c\x00\x00'
            b'\x00\x00\x01\x00\x01\x00\x00\x02'
            b'\x02\x4c\x01\x00\x3b'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        cls.post = Post.objects.create(
            text='пост без групп',
            group=None,
            author=cls.user,
            image=uploaded
        )
        cls.post.pub_date = datetime(2021, 5, 27)
        cls.post.save()
        print(cls.post.pub_date)
        cls.post2 = Post.objects.create(
            text='пост с группой',
            group=cls.group,
            author=cls.user,
            image=uploaded
        )
        cls.post2.pub_date = datetime(2021, 5, 28)
        cls.post2.save()
        print(cls.post2.pub_date)
        cls.post3 = Post.objects.create(
            text='третий пост',
            group=cls.group,
            author=cls.user2,
            image=uploaded
        )
        print(cls.post3.pub_date)

    def setUp(self):
        self.user = User.objects.get(username='kek1')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.guest_client = Client()

    def test_index_page_shows_correct_context(self):
        """Шаблон index сформирован с правильным контекстом
        пост с группой попал на главную."""
        response = self.authorized_client.get(reverse('index'))
        post_0 = response.context.get('page').object_list[0]
        self.assertEqual(post_0, ContextsTests.post3)

    def test_group_show_correct_context(self):
        """Шаблон group сформирован с правильным контекстом,
        пост с группой на соответсвующей странице группы."""
        response = self.authorized_client.get(
            reverse('group_posts', kwargs={'slug': 'test-slug'})
        )
        self.assertEqual(response.context['group'].slug, 'test-slug')
        post_2 = response.context.get('page').object_list[0]
        group_from_context = post_2.group
        group_from_base = ContextsTests.post2.group
        self.assertEqual(group_from_context, group_from_base)
        self.assertEqual(response.context['posts'].count(), 2)

    def test_new_post_show_correct_context(self):
        """Шаблон new_post сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('new_post'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.models.ModelChoiceField,
            'image': forms.fields.ImageField
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_profile_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('profile', kwargs={'username': 'kek1'})
        )
        post = response.context.get('page').object_list[0]
        author_from_post = post.author
        author_from_context = ContextsTests.post.author
        self.assertEqual(author_from_post, author_from_context)

    def test_post_edit_show_correct_context(self):
        """Шаблон post_edit сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('post_edit',
                    kwargs={
                        'username': ContextsTests.post.author.username,
                        'post_id': ContextsTests.post.pk,
                    },
                    ),
            follow=True
        )
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.models.ModelChoiceField,
            'image': forms.fields.ImageField
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_post__show_correct_context(self):
        """Шаблон post сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('post',
                    kwargs={
                        'username': ContextsTests.post.author.username,
                        'post_id': ContextsTests.post.pk,
                    },
                    ),
            follow=True
        )
        post_from_context = response.context.get('post')
        post = ContextsTests.post
        print(post_from_context)
        self.assertEqual(post_from_context, post)

    def test_index_list_page_list_is_3(self):
        response = self.authorized_client.get(reverse('index'))
        self.assertEqual(response.context['post_list'].count(), 3)


class CacheTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.post1 = Post.objects.create(
            text='Тестовый текст',
            author=User.objects.create_user(username='Kekes'),
        )

    def setUp(self):
        self.user = User.objects.get(username='Kekes')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_cache(self):
        """Проверяется работа кэширования страницы index.html"""
        try_1 = self.authorized_client.get(reverse('index'))
        post1 = Post.objects.get(pk=1)
        post1.text = 'Измененный текст2'
        post1.save()
        try_2 = self.authorized_client.get(reverse('index'))
        self.assertEqual(try_1.content, try_2.content)
        cache.clear()
        try_3 = self.authorized_client.get(reverse('index'))
        self.assertNotEqual(try_1.content, try_3.content)


class FollowingTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.follow1 = Follow.objects.create(
            user=User.objects.create_user(username='Kekes'),
            author=User.objects.create_user(username='Post_Author'),
        )
        cls.post1 = Post.objects.create(
            text='Тестовый текст',
            author=User.objects.get(username='Post_Author'),
        )
        cls.post2 = Post.objects.create(
            text='Тестовый текст2',
            author=User.objects.create_user(username='User_2'),
        )

    def setUp(self):
        self.user = User.objects.get(username='Kekes')
        self.user2 = User.objects.get(username='User_2')
        self.user3 = User.objects.get(username='Post_Author')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.guest_client = Client()

    def test_following_create(self):
        """Подписки создаются в БД
        авторизованным пользователем."""
        self.authorized_client.post(reverse(
            'profile_follow',
            kwargs={'username': CommentTests.post1.author.username}),
        )
        self.assertTrue(Follow.objects.filter(
            user=self.user, author=self.user3).exists()
        )

    def test_follow_delete(self):
        """Подписки удаляются из БД авторизованным пользователем."""
        follow_count = self.user.follower.count()
        Follow.objects.create(user=self.user, author=self.user2)
        self.authorized_client.post(reverse(
            'profile_unfollow',
            kwargs={'username': 'User_2'}),
        )
        self.assertEqual(follow_count, self.user.follower.count())

    def test_following_context(self):
        """Подписки создаются с правильным контекстом"""
        response = self.authorized_client.get(reverse('follow_index'))
        first_follow = response.context['page'][0]
        self.assertEqual(first_follow.author, self.user3)
        self.assertEqual(len(response.context['page']), 1)

    def test_new_post_in_following(self):
        """Новая запись пользователя появляется в ленте тех,
        кто на него подписан и исчезает после удаления."""
        post_new = Post.objects.create(
            text='новый пост текст',
            author=User.objects.get(username='Post_Author'))
        response = self.authorized_client.get(reverse('follow_index'))
        post_in_context = response.context.get('page').object_list[0]
        self.assertEqual(post_new, post_in_context)
        get_object_or_404(Post, text='новый пост текст').delete()
        response2 = self.authorized_client.get(reverse('follow_index'))
        self.assertEqual(len(response2.context['page']), 1)

    def test_new_post_in_following(self):
        """Новая запись пользователя не появляется в ленте тех,
        кто на него не подписан."""
        self.authorized_client.force_login(self.user2)
        response = self.authorized_client.get(reverse('follow_index'))
        Post.objects.create(
            text='новый пост текст3',
            author=User.objects.get(username='Post_Author'))
        response = self.authorized_client.get(reverse('follow_index'))
        self.assertEqual(len(response.context['page']), 0)


class CommentTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.post1 = Post.objects.create(
            text='Тестовый текст',
            author=User.objects.create_user(username='Post_Author'),
        )
        cls.comment1 = Comment.objects.create(
            post=cls.post1,
            text='Тестовый коммент',
            author=cls.post1.author,
        )

    def setUp(self):
        self.user = User.objects.get(username='Post_Author')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.guest_client = Client()

    def test_add_comment_noauthor(self):
        """Страница add_comment недоступна неавторизованному пользователю
        и переадресована на логин."""
        response = self.guest_client.get(
            reverse('add_comment',
                    kwargs={
                        'username': CommentTests.post1.author.username,
                        'post_id': CommentTests.post1.pk,
                    },
                    )
        )
        username = CommentTests.post1.author.username
        post_id = CommentTests.post1.id
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response,
            f'/auth/login/?next=/{username}/{post_id}/comment'
        )
        self.guest_client.post(reverse(
            'add_comment',
            kwargs={'username': CommentTests.post1.author.username,
                    'post_id': CommentTests.post1.id
                    }),
            data={'text': 'попытка неавторизованного'},
        )
        self.assertFalse(Comment.objects.filter(
            text='попытка неавторизованного').exists())

    def test_add_comment_author(self):
        """Коммент создался и
        add_comment доступна авторизованному пользователю."""
        self.authorized_client.post(reverse(
            'add_comment',
            kwargs={'username': CommentTests.post1.author.username,
                    'post_id': CommentTests.post1.id
                    }),
            data={'text': 'тестовый коммент111'},
        )
        self.assertTrue(Comment.objects.filter(
            text='тестовый коммент111').exists())
        response = self.authorized_client.get(
            reverse('add_comment',
                    kwargs={
                        'username': CommentTests.post1.author.username,
                        'post_id': CommentTests.post1.pk,
                    },
                    )
        )
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response,
            reverse('post',
                    kwargs={
                        'username': CommentTests.post1.author.username,
                        'post_id': CommentTests.post1.pk,
                    },
                    )
        )
