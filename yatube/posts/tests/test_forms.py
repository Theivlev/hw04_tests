# deals/tests/tests_form.py
from django.test import Client, TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from posts.models import Group, Post

User = get_user_model()


class FormTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='FormAuth')
        cls.group = Group.objects.create(
            title='группа формы',
            slug='form_slug',
            description='описание формы',
        )

    def setUp(self):
        # Создаем неавторизованный клиент
        self.guest_client = Client()
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(FormTest.user)

    def test_create_post(self):
        tasks_post_count = Post.objects.count()
        form_data = {
            'text': 'Текст для теста форм',
            'group': FormTest.group.id,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Post.objects.count(), tasks_post_count + 1)
        self.assertTrue(
            Post.objects.filter(
                text='Текст для теста форм',
                group=FormTest.group
            ).exists()
        )

    def test_create_post_edit(self):
        """при создания поста создаётся новая запись в базе данных"""
        self.post = Post.objects.create(
            author=FormTest.user,
            text='Тестовый текст',
            id=1,
            group=self.group,
        )
        form_data = {
            'text': 'Текст для теста форм_2',
        }
        response = self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            Post.objects.filter(
                text='Текст для теста форм_2',
            ).exists()
        )
