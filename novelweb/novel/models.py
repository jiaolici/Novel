from django.db import models

# Create your models here.
class Novel(models.Model):
    author = models.CharField(max_length=50,null=False)
    name = models.CharField(max_length=50,null=False)
    intr = models.CharField(max_length=500,null=False)
    cover = models.CharField(max_length=100,null=False)
    novel_type = models.CharField(max_length=20,null=False)
    last_update_chapter = models.CharField(max_length=50,null=False)
    last_update_time = models.DateTimeField(null=False)
    status = models.BooleanField(default=False,null=False)
    source = models.CharField(max_length=50,null=False)
    novel_url = models.CharField(max_length=100,null=False)

    objects = models.Manager()
    class Meta():
        db_table = "novel"

class User(models.Model):
    user_name = models.CharField(max_length=20,null=False)
    password = models.CharField(max_length=18,null=False)
    Email = models.EmailField(null=False,unique=True,max_length=100)

    objects = models.Manager()
    class Meta():
        db_table = 'user'

class User_Collections(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE,to_field='id')
    novel = models.ForeignKey(Novel,on_delete=models.CASCADE,to_field='id')

    objects = models.Manager()
    class Meta():
        unique_together = ["user", "novel"]
        db_table = 'user_collections'

class Novel_Comment(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE,to_field='id')
    novel = models.ForeignKey(Novel,on_delete=models.CASCADE,to_field='id')
    content = models.TextField(null=False)
    comment = models.ForeignKey('self',on_delete=models.CASCADE,to_field='id')
    pub_time = models.DateTimeField(null=False)
    praise = models.IntegerField(null=False)
    objects = models.Manager()

    class Meta():
        db_table = 'novel_comment'

class Circle(models.Model):
    circle_name = models.CharField(max_length=20,null=False)
    interpretation = models.TextField(null=False)
    objects = models.Manager()

    class Meta():
        db_table = 'circle'

class User_Circle(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE,to_field='id')
    circle = models.ForeignKey(Circle,on_delete=models.CASCADE,to_field='id')
    objects = models.Manager()

    class Meta():
        db_table = 'user_circle'

class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, to_field='id')
    circle = models.ForeignKey(Circle, on_delete=models.CASCADE, to_field='id')
    title = models.CharField(max_length=500,null=False)
    content = models.TextField(null=False)
    pub_time = models.DateTimeField(null=False,auto_now_add=True)
    praise = models.IntegerField(null=False)
    shared = models.IntegerField(null=False)
    objects = models.Manager()

    class Meta():
        db_table = 'post'

class Post_Reply(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, to_field='id')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, to_field='id')
    reply = models.ForeignKey('self',on_delete=models.CASCADE,to_field='id')
    content = models.TextField(null=False)
    pub_time = models.DateTimeField(null=False, auto_now_add=True)
    praise = models.IntegerField(null=False)
    objects = models.Manager()

    class Meta():
        db_table = 'post_reply'

class Recommend(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, to_field='id')
    novel = models.ForeignKey(Novel, on_delete=models.CASCADE, to_field='id')
    reason = models.TextField(null=False)
    praise = models.IntegerField(null=False)
    tread = models.IntegerField(null=False)
    pub_time = models.DateTimeField(null=False, auto_now_add=True)
    objects = models.Manager()

    class Meta():
        db_table = 'recommend'

class Message(models.Model):
    msg_type = models.CharField(max_length=20,null=False)
    title = models.CharField(max_length=500,null=False)
    content = models.TextField(null=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, to_field='id')
    pub_time = models.DateTimeField(null=False, auto_now_add=True)
    objects = models.Manager()

    class Meta():
        db_table = 'message'