from django.contrib import admin

from app.models import Tag, Question, Answer, Profile, LikeQuestion, LikeAnswer

admin.site.register(Tag)
admin.site.register(Question)
admin.site.register(Answer)
admin.site.register(Profile)
admin.site.register(LikeQuestion)
admin.site.register(LikeAnswer)