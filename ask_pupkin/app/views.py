from django.shortcuts import render
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.shortcuts import get_object_or_404
from django.contrib import auth
from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.contrib.auth.decorators import login_required

from app.models import Question, Tag, Profile, Answer
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

def index(request):
    questions = Question.objects.get_new()
    page = paginate(questions, request)
    return render(request, "index.html", context={
       'questions' : page.object_list,
       'page_obj' : page,
       'popular_tags' : Tag.objects.get_popular_tags(),
       'best_members' : Profile.objects.get_best_members_by_answers(),
       'profile' : get_self_profile(request),
    })

def hot(request):
    questions = Question.objects.get_hot_by_answers()
    page = paginate(questions, request)
    return render(request, "hot.html", context={
       'questions' : page.object_list,
       'page_obj' : page,
       'popular_tags' : Tag.objects.get_popular_tags(),
       'best_members' : Profile.objects.get_best_members_by_answers(),
       'profile' : get_self_profile(request),
    })

def tag(request, tag_id):
    cur_tag = get_object_or_404(Tag, id=tag_id)
    questions = Question.objects.by_tag_id(tag_id)
    page = paginate(questions, request)
    return render(request, "tag.html", context={
       'questions' : page.object_list,
       'page_obj' : page,
       'popular_tags' : Tag.objects.get_popular_tags(),
       'best_members' : Profile.objects.get_best_members_by_answers(),
       'profile' : get_self_profile(request),
       'cur_tag' : cur_tag,
    })

def question(request, question_id):
    cur_question = get_object_or_404(Question, id=question_id)
    answers = Answer.objects.get_for_question(question_id)
    profile = get_self_profile(request)
    if request.method == 'POST':
        form = AnswerForm(cur_question, profile, request.POST) 
        if not profile:
            form.add_error(None, 'You are not authorized.')
        elif form.is_valid():
            answer = form.save()
            print("----------- save \n")
            print(reverse('question', kwargs={'question_id': cur_question.id}) + f'#answer-{answer.id}', "\n")
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