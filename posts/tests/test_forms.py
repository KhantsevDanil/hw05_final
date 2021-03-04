from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from posts.models import Comment, Group, Post

User = get_user_model()


class PostCreateFormTests(TestCase):
    group = None

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='Alex_Morgan')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            description='Описание тестовой группы',
        )
        cls.post = Post.objects.create(
            text='Тестовый пост',
            author=cls.user,
            group=cls.group
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post(self):
        posts_count = Post.objects.count()
        form_data = {
            'group': PostCreateFormTests.group.id,
            'text': 'Тестовый пост',
        }
        response = self.authorized_client.post(
            reverse('posts:new_post'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse('posts:index'))
        self.assertEqual(Post.objects.count(), posts_count + 1)
        test_group = Post.objects.last()
        self.assertEqual(test_group.text, form_data['text'])

    def test_edit_post(self):
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Измененный пост',
            'group': self.group.id,
        }
        test_post = Post.objects.create(
            text='Тестовый пост',
            author=self.user,
        )
        kwargs = {'username': self.user.username, 'post_id': test_post.id}
        response = self.authorized_client.post(
            reverse('posts:post_edit', kwargs=kwargs),
            data=form_data,
            follow=True
        )
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertRedirects(response, reverse('posts:post_view', kwargs=kwargs))
        test_group = Post.objects.last()
        self.assertEqual(test_group.text, form_data['text'])

        def test_create_comment(self):
            """Валидная форма создает запись в Comment."""
            comment_count = Comment.objects.count()
            form_data = {
                'text': 'Тестовый комментарий',
                'author': self.user,
                'post': self.post,
            }
            response = self.authorized_client.post(
                reverse('posts:add_comment', args=[self.user, self.post.id]),
                data=form_data,
                follow=True
            )
            self.assertRedirects(response, reverse('posts:post',
                                                   args=[self.user, self.post.id]))
            self.assertEqual(Comment.objects.count(), comment_count + 1)

    def test_post_edit_save_to_database(self):
        """Проверка редактирования поста в форме /<username>/<post_id>/edit/ -
        изменяется соответствующая запись"""
        posts_count = Post.objects.count()
        post = Post.objects.get(id=self.post.id)
        form_data = {
            'text': 'Измененный тестовый текст',
            'author': self.user,
            'group': PostCreateFormTests.group.id,
        }
        self.authorized_client.post(
            reverse('posts:post_edit', args=[post.author, post.id]),
            data=form_data,
            follow=True
        )
        # Проверяем, что тестовая запись изменилась
        self.assertNotEqual(post, post.refresh_from_db(),
                            'Запись /<username>/<post_id>/edit/ не изменилась')
        # Проверяем, что колиество записей не изменилось
        self.assertEqual(Post.objects.count(), posts_count,
                         'Кол-во записей увеличивается при редактировании!')
