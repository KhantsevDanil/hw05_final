# posts/tests/test_urls.py
from django.contrib.auth import get_user_model
from django.test import Client, TestCase

from posts.models import Group


class GroupURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            slug='cats',
            description='Текст описания'
        )

    def setUp(self):
        self.guest_client = Client()
        self.user = get_user_model().objects.create_user(username='Danil')
        self.user = get_user_model().objects.create_user(username='Alex')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_urls_uses_correct_template(self):
        templates_url_names = {
            'posts/index.html': '/',
            'group.html': f'/group/{self.group.slug}/',
            'posts/new_post.html': '/new/',
        }
        for template, urls in templates_url_names.items():
            with self.subTest():
                response = self.authorized_client.get(urls)
                self.assertTemplateUsed(response, template)

    def test_correct_status_code_for_guest_client(self):
        url_status_code = {
            '/': 200,
            f'/group/{self.group.slug}/': 200,
            '/new/': 302
        }
        for reverse_name, status_code in url_status_code.items():
            with self.subTest():
                response = self.guest_client.get(reverse_name)
                self.assertEqual(response.status_code, status_code)

    def test_correct_status_code_for_authorized_client(self):
        url_status_code = {
            '/': 200,
            f'/group/{self.group.slug}/': 200,
            '/new/': 200,
            '/Danil/follow/': 302,
            '/Danil/unfollow/': 302,
        }
        for reverse_name, status_code in url_status_code.items():
            with self.subTest():
                response = self.authorized_client.get(reverse_name)
                self.assertEqual(response.status_code, status_code)
