from django.db import models
from django.contrib.auth.models import User
from datetime import datetime
from django.contrib.postgres.search import SearchVectorField, SearchVector
from django.contrib.postgres.indexes import GinIndex

class ProfileManager(models.Manager):
    def get_best_members_by_answers(self, limit=10):
        return self.annotate(
            answers_count=models.Count('answer')
        ).order_by('-answers_count')[:limit]

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.PROTECT)
    nickname = models.CharField(max_length=255)
    avatar = models.ImageField(default='profile/avatar.jpg', upload_to='profile')  
    objects = ProfileManager()
 
    def __str__(self):
        return self.user.username
    
    @property
    def name(self):
        return self.user.username
    
    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user.id,
            "username": self.user.username,
            "email": self.user.email,
            "nickname": self.nickname,
            "avatar": self.avatar.url if self.avatar else None,
            "password": self.user.password
        }

    @staticmethod
    def from_dict(d):
        user = User(
            id=d["user_id"],
            username=d["username"],
            email=d["email"],
            password=d["password"],
        )
        profile = Profile(
            id=d.get("id"),
            user=user,
            nickname=d["nickname"],
            avatar=d["avatar"],
        )            
        return profile

class TagManager(models.Manager):
    def get_popular_tags(self, limit=10):
        return self.annotate(
            questions_count=models.Count('question')
        ).order_by('-questions_count')[:limit]

class Tag(models.Model): 
    title = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    objects = TagManager()

    def __str__(self):
        return self.title
    
    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            "updated_at": self.updated_at.strftime("%Y-%m-%d %H:%M:%S"),
        }

    @staticmethod
    def from_dict(d):
        tag = Tag(
            id = d.get("id"),
            title = d["title"],
            created_at = datetime.strptime(d["created_at"], "%Y-%m-%d %H:%M:%S"),
            updated_at = datetime.strptime(d["updated_at"], "%Y-%m-%d %H:%M:%S"),
        )
        return tag
    
class QuestionManager(models.Manager):    
    def by_tag_id(self, tag_id): 
        return self.filter(mm_tags__id=tag_id)
    
    def get_hot_by_answers(self):
        return self.annotate(
            answers_count=models.Count('answer')
        ).order_by('-answers_count')
    
    def get_new(self):
        return self.order_by('-created_at')

class Question(models.Model):
    title = models.CharField(max_length=255)
    text = models.TextField() 
    user = models.ForeignKey(Profile, on_delete=models.PROTECT)
    mm_tags = models.ManyToManyField(Tag, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = QuestionManager()

    search_vector = SearchVectorField(null=True, blank=True)    # полнотекстовsq поиск

    class Meta:
        indexes = [
            GinIndex(fields=['search_vector']),
            models.Index(fields=['title']),
            models.Index(fields=['text']),
        ]
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        Question.objects.filter(pk=self.pk).update(
            search_vector=SearchVector('title', 'text')
        )

    def __str__(self):
        return self.title
    
    @property
    def tags(self):
        return self.mm_tags.all() 
    
    @property
    def cnt_likes(self):
        return self.likes.aggregate(
            total=models.Sum('value')
        )['total'] or 0
    
    @property
    def cnt_answers(self):
        return self.answer_set.count()

    def is_liked(self, profile: Profile):
        """ like (1), dislike (-1), none (0) """
        try:
            like = self.likes.get(user=profile)
            return like.value
        except LikeQuestion.DoesNotExist:
            return 0

class LikeQuestion(models.Model):
    user = models.ForeignKey(Profile, on_delete=models.CASCADE)
    value = models.SmallIntegerField(choices=[(1, 'Like'), (-1, 'Dislike')])
    question = models.ForeignKey(
        Question, 
        on_delete=models.CASCADE,
        related_name='likes'  
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'question']

    def __str__(self):
        return f"{self.user} {self.value} вопрос: {self.question}"
    
class AnswerManager(models.Manager):    
    def get_for_question(self, question_id): 
        return self.filter(question_id=question_id).order_by('created_at')
    

class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    text = models.TextField()
    is_correct = models.BooleanField(default=False, blank=True, null=True)
    user = models.ForeignKey(Profile, on_delete=models.PROTECT)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    objects = AnswerManager()

    def __str__(self):
        return self.text[:50]
    
    @property
    def cnt_likes(self):
        return self.likes.aggregate(
            total=models.Sum('value')
        )['total'] or 0
    
    def is_liked(self, profile: Profile):
        """ like (1), dislike (-1), none (0) """
        try:
            like = self.likes.get(user=profile)
            return like.value
        except LikeAnswer.DoesNotExist:
            return 0

    def as_dict(self):
        return {
            "id": self.id,
            # "question"
            "text": self.text,
            "is_correct": self.is_correct,
            # "user"
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            "updated_at": self.updated_at.strftime("%Y-%m-%d %H:%M:%S")
        }

    
class LikeAnswer(models.Model):
    user = models.ForeignKey(Profile, on_delete=models.CASCADE)
    value = models.SmallIntegerField(choices=[(1, 'Like'), (-1, 'Dislike')])
    answer = models.ForeignKey(
        Answer, 
        on_delete=models.CASCADE,
        related_name='likes'  
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'answer']

    def __str__(self):
        return f"{self.user} {self.value} ответ: {self.question}"
    
