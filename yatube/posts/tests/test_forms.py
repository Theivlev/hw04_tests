from http import HTTPStatus

from django.test import Client, TestCase
from django.urls import reverse

from posts.forms import PostForm
from posts.models import Group, Post, User


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
        cls.form = PostForm()

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(FormTest.user)

    def test_create_post(self):
        """при создания поста создаётся новая запись в базе данных"""
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
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(Post.objects.count(), tasks_post_count + 1)
        self.assertTrue(
            Post.objects.filter(
                text='Текст для теста форм',
                group=FormTest.group
            ).exists()
        )

    def test_create_post_edit(self):
        """при редактировании поста происходит изменение в базе данных."""
        self.post = Post.objects.create(
            author=FormTest.user,
            text='Тестовый текст',
            group=self.group,
        )
        self.test_group = Group.objects.create(
            title='W2',
            slug='test_slug_2',
            description='Тестовое описание_2'
        )
        form_data = {
            'text': 'Текст для теста форм_2',
            'group': self.test_group.id,
        }
        response = self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTrue(
            Post.objects.filter(
                text='Текст для теста форм_2',
                group=self.test_group.id,
            ).exists()
        )
        self.assertFalse(
            Post.objects.filter(
                text='Текст для теста форм_2',
                group=self.group,
            ).exists()
        )

    def test_post_edit_for_guest_client(self):
        """Страница create_post недоступна неавторизованному клиенту"""
        response = self.guest_client.post(
            reverse('posts:post_create'),
            follow=True
        )
        users_login = reverse('users:login')
        post_create = reverse('posts:post_create')
        self.assertRedirects(
            response, f'{users_login}?next={post_create}')

    def test_post_edit_for_guest2_client(self):
        """Страница post_edit недоступна неавторизованному клиенту"""
        self.post = Post.objects.create(
            author=FormTest.user,
            text='Тестовый текст',
            group=self.group,
        )
        response = self.guest_client.post(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}),
            follow=True
        )
        users_login = reverse('users:login')
        post_edit = reverse('posts:post_edit',
                            kwargs={'post_id': self.post.id})
        self.assertRedirects(
            response, f'{users_login}?next={post_edit}')

    def test_title_label(self):
        """labels формы совпадает с ожидаемым."""
        for field, expected_value in FormTest.form.Meta.labels.items():
            with self.subTest(field=field):
                self.assertEqual(
                    FormTest.form.fields[field].label, expected_value)

    def test_title_help_text(self):
        """help_text формы совпадает с ожидаемым."""
        for field, expected_value in FormTest.form.Meta.help_texts.items():
            with self.subTest(field=field):
                self.assertEqual(
                    FormTest.form.fields[field].help_text, expected_value)
