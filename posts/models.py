from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Group(models.Model):
    title = models.CharField("Заголовок",
                             max_length=200,
                             help_text="Назовите как-то кгруппу")
    slug = models.SlugField("Введите понятную вам часть URL",
                            unique=True,
                            help_text="Часть Url - это как заголовок, "
                                      "но в адресной строке")
    description = models.TextField('Описание',
                                   max_length=1000,
                                   help_text="расскажите, что происходит "
                                             "в вашей группе )")

    def __str__(self):
        return self.title


class Post(models.Model):
    text = models.TextField(verbose_name="Текст",
                            help_text="основное содержание поста")
    pub_date = models.DateTimeField("Дата",
                                    auto_now_add=True,
                                    help_text="Дата создания Поста")
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               related_name="posts",
                               verbose_name="Имя автора",
                               help_text="имя автора")
    group = models.ForeignKey(Group, on_delete=models.SET_NULL,
                              related_name="group",
                              blank=True, null=True,
                              verbose_name="Название группы",
                              help_text="Название группы")
    image = models.ImageField("Картинка",
                              upload_to="posts/",
                              blank=True,
                              null=True,
                              help_text="Загрузите картинку")

    def __str__(self):
        return (self.text)


class Comment(models.Model):
    post = models.ForeignKey(Post,
                             verbose_name="Пост",
                             on_delete=models.CASCADE,
                             related_name="comments")
    author = models.ForeignKey(User,
                               verbose_name="Автор комментария",
                               on_delete=models.CASCADE,
                               related_name="comments")
    text = models.TextField(verbose_name="Комментарий",
                            help_text="Напишите ваш комментарий")
    created = models.DateTimeField(verbose_name="Дата создания",
                                   auto_now_add=True)

    class Meta:
        ordering = ["-created"]


class Follow(models.Model):
    user = models.ForeignKey(User, verbose_name="Подписчик",
                             on_delete=models.CASCADE,
                             related_name="follower")
    author = models.ForeignKey(User, verbose_name="Автор",
                               on_delete=models.CASCADE,
                               related_name="following")

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "author"],
                name="unique_follow"
            )
        ]