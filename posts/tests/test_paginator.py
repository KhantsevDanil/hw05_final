from django.test import TestCase

from posts.models import Group, Post, User


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='test_user')
        cls.group = Group.objects.create(
            title='Test',
            description='Много букв'
        )
        posts = [Post(author=cls.user,
                      group=cls.group,
                      text=str(i)) for i in range(13)]
        for i in range(0, 12):
            posts.append({
                'author': cls.user,
                'text': i,
                'group': cls.group
            })
        Post.objects.bulk_create(posts)
