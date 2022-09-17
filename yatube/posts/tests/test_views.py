from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse
from django import forms

from ..models import Group, Post


User = get_user_model()


class ViewsTest(TestCase):
    POST_NUMBER: int = 0

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание',
        )

        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый текст',
            id=1,
            group=cls.group,
        )
        for i in range(2, 14):
            Post.objects.create(author=cls.user, text='Тестовый текст', id=i)

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(ViewsTest.user)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_list', kwargs={'slug': ViewsTest.group.slug}):
            'posts/group_list.html',
            reverse('posts:profile', kwargs={'username': ViewsTest.user}):
            'posts/profile.html',
            reverse('posts:post_detail', kwargs={'post_id': self.post.id}):
            'posts/post_detail.html',
            reverse('posts:post_edit', kwargs={'post_id': ViewsTest.post.id}):
            'posts/create_post.html',
            reverse('posts:post_create'): 'posts/create_post.html',
        }
        for reverse_name, template in templates_url_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_home_page_show_correct_context(self):
        number_of_post: int = 13
        """Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:index'))
        first_post = response.context['page_obj'][self.POST_NUMBER]
        post_text = first_post.text
        post_author = first_post.author.username
        post_id = first_post.id
        self.assertEqual(post_text, 'Тестовый текст')
        self.assertEqual(post_author, 'auth')
        self.assertEqual(post_id, number_of_post)

    def test_group_list_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse(
            'posts:group_list', kwargs={'slug': ViewsTest.group.slug}))
        first_post = response.context['page_obj'][self.POST_NUMBER]
        post_group = first_post.group.title
        post_description = first_post.group.description
        self.assertEqual(post_group, 'Тестовая группа')
        self.assertEqual(post_description, 'Тестовое описание')

    def test_profile_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:profile', kwargs={'username': ViewsTest.user}))
        first_post = response.context['page_obj'][self.POST_NUMBER]
        post_author = first_post.author
        post_text = first_post.text
        self.assertEqual(post_author, ViewsTest.user)
        self.assertEqual(post_text, 'Тестовый текст')

    def test_post_detail_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:post_detail', kwargs={'post_id': self.post.id}))
        first_post = response.context['post']
        post_group = first_post.group.title
        post_author = first_post.author
        post_text = first_post.text
        self.assertEqual(post_group, 'Тестовая группа')
        self.assertEqual(post_author, ViewsTest.user)
        self.assertEqual(post_text, 'Тестовый текст')

    def test__post_edit_show_correct_context(self):
        """Шаблон create_post сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse(
            'posts:post_edit', kwargs={'post_id': ViewsTest.post.id}))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_fields = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_fields, expected)

    def test_first_page_contains_ten_records(self):
        number_of_posts: int = 10
        response = self.guest_client.get(reverse('posts:index'))
        # Проверка: количество постов на первой странице равно 10.
        self.assertEqual(len(response.context['page_obj']), number_of_posts)

    def test_second_page_contains_three_records(self):
        number_of_posts: int = 3
        # Проверка: на второй странице должно быть три поста.
        response = self.guest_client.get(reverse('posts:index') + '?page=2')
        self.assertEqual(len(response.context['page_obj']), number_of_posts)

    def test_checking_when_creating_post(self):
        self.user = User.objects.create_user(username='auth_test_check')
        self.test_group = Group.objects.create(
            title='W1',
            slug='test_slug_1',
            description='Тестовое описание'
        )
        self.post_one = Post.objects.create(
            author=self.user,
            text='Тестовый текст1',
            id=15,
            group=self.test_group,
        )
        self.authorized_client1 = Client()
        self.authorized_client1.force_login(self.user)
        response_index = self.authorized_client1.get(
            reverse('posts:index'))
        response_group_list = self.authorized_client1.get(
            reverse('posts:group_list',
                    kwargs={'slug': f'{self.test_group.slug}'}))
        response_profile = self.authorized_client1.get(
            reverse('posts:profile',
                    kwargs={'username': f'{self.post_one.author}'}))
        index = response_index.context['page_obj']
        group_list = response_group_list.context['page_obj']
        profile = response_profile.context['page_obj']
        self.assertIn(self.post_one, index)
        self.assertIn(self.post_one, group_list)
        self.assertIn(self.post_one, profile)
        self.assertNotIn(self.post_one.group.title, 'Тестовая группа')
