from django.db import models
from django.contrib.auth.models import User

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
    
