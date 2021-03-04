from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Comment, Follow, Group, Post, User

USERNAME = 'test_user'
USERNAME_FOLLOWING = 'test_following'
SLUG = 'test_slug'
SLUG_2 = 'test_slug_2'
INDEX_URL = reverse('posts:index')
GROUP_URL = reverse('posts:group', args=[SLUG])
GROUP_2_URL = reverse('posts:group', args=[SLUG_2])
NEW_POST_URL = reverse('posts:new_post')
PROFILE_URL = reverse('posts:profile', args=[USERNAME])
ABOUT_AUTHOR_URL = reverse('about:author')
ABOUT_TECH_URL = reverse('about:tech')
FOLLOW_URL = reverse('posts:profile_follow', args=[USERNAME_FOLLOWING])
UNFOLLOW_URL = reverse('posts:profile_unfollow', args=[USERNAME_FOLLOWING])

class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Создадим запись в БД
        cls.user = User.objects.create(username=USERNAME)
        cls.group = Group.objects.create(
            title='Test',
            slug=SLUG,
            description='Много букв'
        )
        cls.group2 = Group.objects.create(
            title='Test 2',
            slug=SLUG_2,
            description='Много букв 2'
        )
        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=cls.user,
            group=cls.group,
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.post_page = reverse('posts:post_view', args=[USERNAME, self.post.id])
        self.post_edit_page = reverse(
            'posts:post_edit',
            args=[USERNAME, self.post.id]
        )

    def test_index_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_client.get(INDEX_URL)
        # Сравниваем объект из контекста и объект из фикстуры
        self.assertEquals(response.context['post_list'][0], self.post)

    def test_create_post_appears_on_the_group_page(self):
        """если при создании поста указать группу, то этот пост появляется
        на странице выбранной группы."""
        response = self.authorized_client.get(GROUP_URL)
        self.assertEquals(response.context['page'][0].text, self.post.text)
        self.assertEquals(response.context['page'][0].group, self.group)
        self.assertTrue(len(response.context['page'].object_list) != 0)
        self.assertEqual(response.status_code, 200)

    def test_created_post_dont_appears_on_another_group_page(self):
        """ Если при создании поста указать группу, то этот пост не появится
        на странице другой группы """
        response = self.authorized_client.get(GROUP_2_URL)
        self.assertNotEquals(self.post.group, self.group2)
        self.assertEquals(response.context['group'], self.group2)
        self.assertTrue(len(response.context['page'].object_list) == 0)
        self.assertEqual(response.status_code, 200)

    def test_group_page_shows_correct_context(self):
        """Шаблон group сформирован с правильным контекстом."""
        response = self.authorized_client.get(GROUP_URL)
        self.assertEquals(response.context['group'], self.group)
        self.assertEquals(response.context['page'][0], self.post)

    def test_post_page_show_correct_context(self):
        """Шаблон post сформирован с правильным контекстом."""
        response = self.authorized_client.get(self.post_page)
        self.assertEquals(response.context['post'], self.post)

    def test_profile_page_show_correct_context(self):
        """Шаблон frofile сформирован с правильным контекстом."""
        response = self.authorized_client.get(PROFILE_URL)
        self.assertEquals(response.context['author'], self.post.author)
        self.assertEquals(response.context['page'][0], self.post)

class FollowViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='test_user')
        cls.author = User.objects.create(username='test_author')
        cls.another_user = User.objects.create(username='another_user')
        cls.group = Group.objects.create(
            title='Test',
            description='Много букв'
        )

    def setUp(self):
        # Создаем авторизованного клиента
        self.authorized_client = Client()
        self.authorized_client_1 = Client()
        self.authorized_client_2 = Client()
        # Авторизуем пользователя
        self.authorized_client.force_login(self.user)
        self.authorized_client_1.force_login(self.author)
        self.authorized_client_2.force_login(self.another_user)

    def test_follow_myself(self):
        """Проверка невозможности подписки на самого себя"""
        before_follow = self.author.follower.count()
        self.authorized_client_1.get(reverse('posts:profile_follow',
                                             args=[self.author.username]))
        after_follow = self.author.follower.count()
        self.assertEqual(before_follow, after_follow,
                         'Проверьте, что нельзя подписаться на самого себя')

    def test_follow_author(self):
        """Проверка возможности подписки"""
        self.authorized_client.get(
            reverse('posts:profile_follow', args=[self.author.username]))
        after_follow = self.user.follower.count()
        self.assertEqual(after_follow, 1,
                         'Проверьте, что вы можете подписаться на пользователя'
                         )
        self.authorized_client.get(
            reverse('posts:profile_follow', args=[self.author.username]))
        second_follow = self.user.follower.count()
        self.assertTrue(after_follow == second_follow,
                        'Проверьте, что вы можете подписаться на пользователя '
                        'только один раз')

    def test_unfollow_author(self):
        """Проверка возможности отписки"""
        Follow.objects.create(
            user=self.user,
            author=self.author
        )
        self.authorized_client.get(
            reverse('posts:profile_unfollow', args=[self.author.username]))
        count = self.user.follower.count()
        self.assertTrue(count == 0,
                        'Проверьте, что вы можете отписаться от пользователя')

    def test_follow_context(self):
        """Новая запись пользователя появляется в ленте тех, кто на него
             подписан и не появляется в ленте тех, кто не подписан на него."""
        Post.objects.create(
            author=self.author,
            text='Тестовый текст',
            group=self.group
        )
        Post.objects.create(
            author=self.author,
            text='Тестовый текст1',
            group=self.group
        )
        Post.objects.create(
            author=self.user,
            text='Тестовый текст2',
            group=self.group
        )
        Follow.objects.create(
            user=self.user,
            author=self.author
        )
        Follow.objects.create(
            user=self.author,
            author=self.user
        )
        Follow.objects.create(
            user=self.another_user,
            author=self.user
        )
        Follow.objects.create(
            user=self.another_user,
            author=self.author
        )

        response = self.authorized_client.get(reverse('posts:follow_index'))
        self.assertTrue(len(response.context.get('page')) == 2,
                        'Проверьте, что на странице `/follow/` отображается'
                        'список статей авторов на которых подписаны')
        response_1 = self.authorized_client_1.get(reverse('posts:follow_index')
                                                  )
        self.assertTrue(len(response_1.context.get('page')) == 1,
                        'Проверьте, что на странице `/follow/` отображается'
                        'список статей авторов на которых подписаны')
        response_2 = self.authorized_client_2.get(reverse('posts:follow_index')
                                                  )
        self.assertTrue(len(response_2.context.get('page')) == 3,
                        'Проверьте, что на странице `/follow/` отображается'
                        'список статей авторов на которых подписаны')


class CommentViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='test_user')
        cls.group = Group.objects.create(
            title='Test',
            description='Много букв'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый текст',
            group=cls.group
        )

    def setUp(self):
        # Создаем авторизованного клиента
        self.authorized_client = Client()
        # Авторизуем пользователя
        self.authorized_client.force_login(self.user)

    def test_comment_add_view(self):
        response = self.authorized_client.post(
            reverse('posts:add_comment', args=[self.user.username,
                                               self.post.id]),
            data={'text': 'Новый коммент!'})
        self.assertRedirects(response, reverse('posts:post_view',
                                               args=[self.user.username,
                                                     self.post.id]), 302)
