"""
URL configuration for ask_permyakova project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from app import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path("", views.index, name="index"),
    path("hot/", views.hot, name="hot"),
    path("tag/<int:tag_id>/", views.tag, name="tag"),
    path("question/<int:question_id>/", views.question, name="question"),
    path("ask/", views.ask, name="ask"),
    path("login/", views.login, name="login"),
    path('logout/', views.logout, name='logout'),
    path("signup/", views.registration, name="registration"), 
    path("profile/edit/", views.settings, name="settings"),
    path('question/<int:question_id>/like', views.like_question, name='like_question'),
    path('answer/<int:answer_id>/like', views.like_answer, name='like_answer'),
    path('answer/<int:answer_id>/mark-correct', views.mark_answer_correct, name='mark_answer_correct'),
    path('answer/html/<int:answer_id>/',views. get_one_answer_html, name='get_one_answer_html'),

    path("benchmark_test/dynamic", views.dynamic_bench, name="dynamic_benchmark_test"),
    path("benchmark_test/static", views.static_bench, name="static_benchmark_test"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

 