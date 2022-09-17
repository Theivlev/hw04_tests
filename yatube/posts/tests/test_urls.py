from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse

from ..models import Group, Post


User = get_user_model()


class UrlsTest(TestCase):
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
            text='Тестовый пост',
            id=1,
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(UrlsTest.user)

    def test_index_url_exists_at_desred_location(self):
        response = self.guest_client.get('')
        self.assertEqual(response.status_code, 200)

    def test_group_url_exists_at_desred_location(self):
        response = self.guest_client.get(
            reverse('posts:group_list', kwargs={'slug': UrlsTest.group.slug}))
        self.assertEqual(response.status_code, 200)

    def test_post_detail_url_exists_at_desred_location(self):
        response = self.guest_client.get(
            reverse('posts:post_detail', kwargs={'post_id': UrlsTest.post.id}))
        self.assertEqual(response.status_code, 200)

    def test_profile_url_exists_at_desred_location(self):
        response = self.guest_client.get(
            reverse('posts:profile', kwargs={'username': UrlsTest.user}))
        self.assertEqual(response.status_code, 200)

    def test_create_post_url_exists_at_desred_location(self):
        response = self.authorized_client.get('/create/')
        self.assertEqual(response.status_code, 200)

    def test_post_edit_exists_at_desred_location(self):
        response = self.authorized_client.get(
            reverse('posts:post_detail', kwargs={'post_id': UrlsTest.post.id}))
        self.assertEqual(response.status_code, 200)

    def test_unexisting_page_exists_at_desired_location(self):
        response = self.guest_client.get('/unexisting_page/')
        self.assertEqual(response.status_code, 404)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            '': 'posts/index.html',
            '/group/test_slug/': 'posts/group_list.html',
            '/profile/auth/': 'posts/profile.html',
            '/posts/1/': 'posts/post_detail.html',
            '/create/': 'posts/create_post.html',
            '/posts/1/edit/': 'posts/create_post.html',
        }
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)
