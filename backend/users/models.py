from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models

from backend.constant import LENGTH_USERNAME, TEXT_LENGTH


class User(AbstractUser):
    """Модель пользователей, расширяющая стандартную модель AbstractUser."""
    username = models.CharField(
        max_length=LENGTH_USERNAME,
        unique=True,
        blank=False,
        null=False,
        verbose_name='Username аккаунта',
        validators=(UnicodeUsernameValidator(), )
    )
    email = models.EmailField(
        max_length=TEXT_LENGTH,
        unique=True,
        blank=False,
        null=False,
        verbose_name='Электронная почта',
    )

    first_name = models.CharField(
        max_length=LENGTH_USERNAME,
        blank=False,
        null=False,
        verbose_name='Имя',
    )
    last_name = models.CharField(
        max_length=LENGTH_USERNAME,
        blank=False,
        null=False,
        verbose_name='Фамилия',
    )
    password = models.CharField(
        max_length=LENGTH_USERNAME,
        blank=False,
        null=False,
        verbose_name='Пароль',
    )
    avatar = models.ImageField(
        upload_to='users/',
        null=True,
        default='',
        verbose_name='Аватар',
    )
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name', 'password']

    class Meta(AbstractUser.Meta):
        """Meta-класс для настройки модели User."""
        ordering = ('username',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        """Возвращает строковое представление пользователя."""
        return self.username


class Follow(models.Model):
    """Модель подписок, представляющая отношения между пользователями."""
    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='user',
        verbose_name='Пользователь'
    )
    is_following = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='is_following',
        verbose_name='Подписан на пользователя'
    )

    class Meta:
        """Meta-класс для настройки модели Follow."""
        constraints = (
            models.UniqueConstraint(
                fields=['user', 'is_following'],
                name='user_following'
            ),
        )
        ordering = ('-user',)
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'

    def clean(self):
        """Проверка на недопустимость подписки на самого себя."""
        if self.user == self.is_following:
            raise ValidationError(
                'Пользователь не может подписываться сам на себя.'
            )

    def __str__(self):
        """Возвращает строковое представление подписки."""
        return f'{self.user} подписан на {self.is_following}'
