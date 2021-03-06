from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

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
            'posts/index.html': reverse('posts:index'),
            'posts/new_post.html': reverse('posts:new_post'),
        }
        for template, urls in templates_url_names.items():
            with self.subTest():
                response = self.authorized_client.get(urls)
                self.assertTemplateUsed(response, template)

    def test_correct_status_code_for_guest_client(self):
        url_status_code = {
            reverse('posts:index'): 200,
            f'/group/{self.group.slug}/': 200,
            reverse('posts:new_post'): 302
        }
        for reverse_name, status_code in url_status_code.items():
            with self.subTest():
                response = self.guest_client.get(reverse_name)
                self.assertEqual(response.status_code, status_code)

    def test_correct_status_code_for_authorized_client(self):
        url_status_code = {
            reverse('posts:index'): 200,
            f'/group/{self.group.slug}/': 200,
            reverse('posts:new_post'): 200,
            reverse('posts:profile_follow', args=[self.user.username]): 302,
            reverse('posts:profile_unfollow', args=[self.user.username]): 302,
        }
        for reverse_name, status_code in url_status_code.items():
            with self.subTest():
                response = self.authorized_client.get(reverse_name)
                self.assertEqual(response.status_code, status_code)
