from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    email = models.EmailField(
        max_length=100,
        unique=True,
        verbose_name='Email',
    )
    username = models.CharField(
        max_length=105,
        unique=True,
        verbose_name='Логин',
    )
    first_name = models.CharField(
        max_length=95,
        verbose_name='Имя',
    )
    last_name = models.CharField(
        max_length=90,
        verbose_name='Фамилия',
    )
    password = models.CharField(
        max_length=110,
        verbose_name='Пароль'
    )

    class Meta:
        ordering = ('username',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username


class Subscribe(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscriber',
        verbose_name='Подписчик',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscribing',
        verbose_name='Подписан',
    )

    class Meta:
        verbose_name = 'Подписка на авторов'
        verbose_name_plural = 'Подписки на авторов'
        ordering = ('user', 'author')
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'author'),
                name='unique_subscribe',
            ),
            models.CheckConstraint(
                check=~models.Q(user=models.F('author')),
                name='subscribe_user_not_author',
            ),
        ]

    def __str__(self):
        return f'{self.user} подписан на {self.author}'
