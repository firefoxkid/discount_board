from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Group(models.Model):
    title = models.CharField(max_length=200,
                             verbose_name="Название группы")
    slug = models.SlugField(max_length=200,
                            unique=True,
                            verbose_name="Адрес страницы")
    description = models.TextField(blank=True,
                                   null=True,
                                   verbose_name="Описание группы")

    def __str__(self):
        return self.title


class Post(models.Model):

    def __str__(self):
        return self.text[:15]
    text = models.TextField(help_text="Поле обязательно для заполнения!")
    pub_date = models.DateTimeField("date published", auto_now_add=True)
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               related_name="posts")
    group = models.ForeignKey(Group,
                              blank=True,
                              null=True,
                              on_delete=models.SET_NULL,
                              related_name="posts")
    image = models.ImageField(upload_to='posts/', blank=True, null=True)

    class Meta:
        ordering = ["-pub_date"]


class Comment(models.Model):

    def __str__(self):
        return self.text[:15]
    post = models.ForeignKey(Post,
                             on_delete=models.CASCADE,
                             related_name="comments")
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               related_name="comments")
    text = models.TextField(help_text="Поле обязательно для заполнения!")
    created = models.DateTimeField("date published", auto_now_add=True)

    class Meta:
        ordering = ["-created"]


class Follow(models.Model):
    class Meta:
        constraints = [
            models.CheckConstraint(
                name="prevent_self_follow",
                check=~models.Q(user=models.F("author")),
            ),
        ]
    """Подписка Кто на кого"""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Фоловер - тот, кто подписывается',
        related_name='follower'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор - на кого подписываются',
        related_name='following'
    )

    def __str__(self):
        return f'Результат: {self.user}  подписался на {self.author}'
