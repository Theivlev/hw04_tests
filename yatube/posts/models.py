from django.contrib.auth import get_user_model
from django.db import models


User = get_user_model()


class Group(models.Model):

    title = models.CharField(max_length=200, verbose_name='Заголовок')
    slug = models.SlugField(unique=True, verbose_name='URL')
    description = models.TextField(verbose_name='Описание')

    def __str__(self):
        return self.title


class Post(models.Model):
    OUTPUT_OF_POSTS: int = 10
    SUMBOLS_MAX: int = 15

    text = models.TextField(verbose_name='Текст',
                            help_text='Введите текст поста')
    pub_date = models.DateTimeField(auto_now_add=True,
                                    verbose_name='Дата публикации')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Автор'
    )
    group = models.ForeignKey(
        Group,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='posts',
        verbose_name='Группа',
        help_text='Группа, к которой будет относиться пост',
    )

    def __str__(self):
        return self.text[:Post.SUMBOLS_MAX]

    class Meta:
        ordering = ('-pub_date', '-pk')
