from django.test import TestCase
from ..models import Post, Group
from django.contrib.auth import get_user_model
from datetime import datetime

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.post = Post.objects.create(
            text='Тестовый текстТестовый текстТестовый текст',
            pub_date=datetime.now(),
            group=None,
            author=User.objects.create_user(username="Petya"),
        )

    def test_post_object_name_is_text_field(self):
        """__str__  Post - это строчка с содержимым post.text[:15}."""
        post = PostModelTest.post
        expected_object_name = post.text[:15]
        self.assertEqual(expected_object_name,
                         str(post),
                         )


class GroupModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='ж' * 10,
            slug='ogogo',
            description='описание группы огого',
        )

    def test_group_object_name_is_title_field(self):
        """__str__  group - это строчка с содержимым group.title"""
        group = GroupModelTest.group
        expected_object_name = group.title
        self.assertEqual(expected_object_name,
                         str(group),
                         'ошибка в __str__  модели group')
