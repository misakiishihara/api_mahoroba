#https://docs.djangoproject.com/en/4.2/ref/contrib/auth/

from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.conf import settings

def upload_avatar_path(instance, filename):
    #右端の拡張子(.jpeg等)を-1で切り出してext内に格納
    ext = filename.split('.')[-1]
    return '/'.join(['avatar', str(instance.userProfile.id)+str(instance.nickName)+str(".")+str(ext)])

def upload_post_path(instance, filename):
    #右端の拡張子(.jpeg等)を-1で切り出してext内に格納
    ext = filename.split('.')[-1]
    return '/'.join(['posts', str(instance.userPost.id)+str(instance.title )+str(".")+str(ext)])

#
class UserManager(BaseUserManager):
    def create_user(self, email, password=None):
        if not email:
            raise ValueError('email is must')

        user = self.model(email=self.normalize_email(email))
        #パスワードをハッシュ化
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password):
        user = self.create_user(email, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using= self._db)

        return user
#userモデルを定義
class User(AbstractBaseUser, PermissionsMixin):

    email = models.EmailField(max_length=50, unique=True)
    is_active = models.BooleanField(default=True)
    #adminへのアクセス権限を付与しない
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'

    def __str__(self):
        return self.email

class Profile(models.Model):
    nickName = models.CharField(max_length=20)
    userProfile = models.OneToOneField(
        settings.AUTH_USER_MODEL, related_name='userProfile',
        #参照されたモデルを削除する際に、
        #紐づいた関連モデルも削除する処理
        on_delete=models.CASCADE
    )
    created_on = models.DateTimeField(auto_now_add=True)
    img = models.ImageField(blank=True, null=True, upload_to=upload_avatar_path)

    def __str__(self):
        return self.nickName

class Post(models.Model):
    #maxlengthはどれくらいがいいんだろう？
    title = models.CharField(max_length=144)
    userPost = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name='userPost',
        on_delete=models.CASCADE
    )
    created_on = models.DateTimeField(auto_now_add=True)
    img = models.ImageField(blank=True, null=True, upload_to=upload_post_path)
    #各ユーザーは複数の投稿にいいねできる
    #各投稿は複数のユーザーを持つことができる => Many to Many
    liked = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='liked', blank=True)

    def __str__(self):
        return self.title

class Comment(models.Model):
    text = models.CharField(max_length=80)
    userComment = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name='userComment',
        on_delete=models.CASCADE
    )
    post = models.ForeignKey(Post, on_delete=models.CASCADE)