from django.shortcuts import render
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.shortcuts import get_object_or_404
from django.contrib import auth
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect, JsonResponse, HttpResponse, Http404
from django.urls import reverse, reverse_lazy
from django.views.decorators.http import require_POST, require_GET
from django.contrib.auth.decorators import login_required
from django.db.models import OuterRef, Subquery, Value,  IntegerField
from django.db.models.functions import Coalesce
import json
import os

from ask_permyakova.settings import STATIC_URL
from app.models import Question, Tag, Profile, Answer, LikeQuestion, LikeAnswer
from app.forms import LoginForm, RegisterForm, ProfileEditForm, QuestionForm, AnswerForm

def get_self_profile(request):
    if request.user.is_authenticated:
        try:
            return request.user.profile
        except Profile.DoesNotExist:
            return None
    return None

def paginate(objects_list, request, per_page=5):
    paginator = Paginator(objects_list, per_page) 
    
    page_number = request.GET.get('page')
    try:
        page = paginator.page(page_number)
    except PageNotAnInteger:
        page = paginator.page(1)
    except EmptyPage:
        page = paginator.page(paginator.num_pages)


    page_range = paginator.get_elided_page_range(
        number=page.number,
        on_each_side=1,
        on_ends=1
    )
    page.page_range = page_range

    return page

def add_user_vote_for_questions(questions, profile):
    if profile:
        user_vote_subquery = LikeQuestion.objects.filter(
            user=profile,
            question=OuterRef('pk')
        ).values('value')[:1]
        
        questions = questions.annotate(
            user_vote=Coalesce(
                Subquery(user_vote_subquery),
                Value(0)
            )
        )
    else:
        questions = questions.annotate(
            user_vote=Value(0, output_field=IntegerField())
        )
    return questions

def index(request):
    profile = get_self_profile(request)
    questions = Question.objects.get_new()
    questions = add_user_vote_for_questions(questions=questions, profile=profile)
    page = paginate(questions, request)
    return render(request, "index.html", context={
       'questions' : page.object_list,
       'page_obj' : page,
       'popular_tags' : Tag.objects.get_popular_tags(),
       'best_members' : Profile.objects.get_best_members_by_answers(),
       'profile' : profile,
    })

def hot(request):
    profile = get_self_profile(request)
    questions = Question.objects.get_hot_by_answers()
    questions = add_user_vote_for_questions(questions=questions, profile=profile)
    page = paginate(questions, request)
    return render(request, "hot.html", context={
       'questions' : page.object_list,
       'page_obj' : page,
       'popular_tags' : Tag.objects.get_popular_tags(),
       'best_members' : Profile.objects.get_best_members_by_answers(),
       'profile' : profile,
    })

def tag(request, tag_id):
    profile = get_self_profile(request)
    cur_tag = get_object_or_404(Tag, id=tag_id)
    questions = Question.objects.by_tag_id(tag_id)
    questions = add_user_vote_for_questions(questions=questions, profile=profile)
    page = paginate(questions, request)
    return render(request, "tag.html", context={
       'questions' : page.object_list,
       'page_obj' : page,
       'popular_tags' : Tag.objects.get_popular_tags(),
       'best_members' : Profile.objects.get_best_members_by_answers(),
       'profile' : profile,
       'cur_tag' : cur_tag,
    })

def question(request, question_id):
    profile = get_self_profile(request)
    cur_question = get_object_or_404(Question, id=question_id)
    cur_question.user_vote = cur_question.is_liked(profile)
    answers = Answer.objects.get_for_question(question_id)
    
    if request.method == 'POST':
        form = AnswerForm(cur_question, profile, request.POST) 
        if not profile:
            form.add_error(None, 'You are not authorized.')
        elif form.is_valid():
            answer = form.save()
            return HttpResponseRedirect(
                reverse('question', kwargs={'question_id': cur_question.id})+ f'#answer-{answer.id}'
            )
        else:
            form.add_error(None, 'Invalid input data.')
    else:
        form = AnswerForm(cur_question, profile)
    return render(request, "question.html", context={
        'form': form,
        'question' : cur_question,
        'answers' : answers,
        'popular_tags' : Tag.objects.get_popular_tags(),
        'best_members' : Profile.objects.get_best_members_by_answers(),
        'profile' : profile,
    })

@login_required(login_url=reverse_lazy('login'))
def ask(request):
    profile = get_self_profile(request)
    if request.method == 'POST':
        form = QuestionForm(profile, request.POST) 
        if form.is_valid():
            question = form.save()
            return HttpResponseRedirect(
                reverse('question', kwargs={'question_id': question.id}) 
            )
        else:
            form.add_error(None, 'Invalid input data.')
    else:
        form = QuestionForm(profile)
    return render(request, 'ask.html', context={
        'form': form,
        'popular_tags' : Tag.objects.get_popular_tags(),
        'best_members' : Profile.objects.get_best_members_by_answers(),
        'profile' : profile,
    })

def login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST) 
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = auth.authenticate(username=username, password=password)
            if user:
                auth.login(request, user)
                return HttpResponseRedirect(reverse('index'))
            else: 
                form.add_error(None, 'Invalid username or password.')
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})

def registration(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST, request.FILES) 
        if form.is_valid():
            user = form.save()
            auth.login(request, user)
            return HttpResponseRedirect(reverse('index'))
        else:
            form.add_error(None, 'Invalid input data.')
    else:
        form = RegisterForm()
    return render(request, 'registration.html', {'form': form})

def logout(request):
    auth.logout(request)
    return HttpResponseRedirect(reverse('index'))

@login_required(login_url=reverse_lazy('login'))
def settings(request):
    profile = get_self_profile(request)
    if request.method == 'POST':
        form = ProfileEditForm(
            profile,
            request.POST, 
            request.FILES
        )
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('settings'))
        else:
            form.add_error(None, 'Invalid input data.')
    else:
        form = ProfileEditForm(profile=profile)
    
    return render(request, "settings.html", {
        'form': form,
        'profile': profile
    })

@require_POST 
@login_required
def like_question(request, question_id):
    user=User.objects.get(id=request.user.id)
    profile = Profile.objects.get(user=user)
    question = Question.objects.get(id=question_id)
    question_like, is_created = LikeQuestion.objects.get_or_create(question=question, user=profile, defaults={'value':1})

    user_vote = 1
    if not is_created:
        if question_like.value == -1:
            user_vote = 0
            question_like.delete()
        else:
            user_vote = -1
            question_like.value = -1
            question_like.save()

    return JsonResponse({
        'likeCount': question.cnt_likes,
        'user_vote': user_vote,
    })

@require_POST 
@login_required
def like_answer(request, answer_id):
    user=User.objects.get(id=request.user.id)
    profile = Profile.objects.get(user=user)
    answer = Answer.objects.get(id=answer_id)
    answer_like, is_created = LikeAnswer.objects.get_or_create(answer=answer, user=profile, defaults={'value':1})

    user_vote = 1
    if not is_created:
        if answer_like.value == -1:
            user_vote = 0
            answer_like.delete()
        else:
            user_vote = -1
            answer_like.value = -1
            answer_like.save()

    return JsonResponse({
        'likeCount': answer.cnt_likes,
        'user_vote': user_vote,
    })

@require_POST
@login_required
def mark_answer_correct(request, answer_id):
    try:
        answer = Answer.objects.get(id=answer_id)
        user=User.objects.get(id=request.user.id)
        profile = Profile.objects.get(user=user)
        if profile != answer.question.user:
            return JsonResponse({'error': 'You are not author of this question'}, status=403)
        
        data = json.loads(request.body)
        answer.is_correct = data.get('is_correct', False)
        answer.save()
        return JsonResponse({
            'success': True
        })
    except Answer.DoesNotExist:
        return JsonResponse({'error': 'Answer.DoesNotExist'}, status=404)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'JSONDecodeError'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    

import random
import string

@require_GET
def dynamic_bench(request):
    kb_data = 30
    content = ''.join(random.choices(string.ascii_letters + ' ', k=kb_data * 1024))
    return HttpResponse(content, content_type='text/plain')

@require_GET
def static_bench(request):
    static_file = os.path.join(STATIC_URL, 'test_30kb.txt')
    try:
        with open(static_file, 'rb') as f:
            file_content = f.read()
        return HttpResponse(file_content, content_type='text/plain')
    except FileNotFoundError:
        raise Http404(f"File not found: {static_file}")
