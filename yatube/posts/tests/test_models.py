from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        group = PostModelTest.group
        test_title = str(group)
        self.assertEqual(test_title, group.title, 'метод __str__ у группы'
                         'работает неверно')
        post = PostModelTest.post
        test_text = str(post)
        self.assertEqual(test_text, post.text[:15], 'метод __str__ у поста'
                         'работает неверно')
