from django.shortcuts import render
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.shortcuts import get_object_or_404
from app.models import Question, Tag, Profile, Answer


def get_self_profile():
    return Profile.objects.all()[0]
    # return None

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
       'profile' : get_self_profile(),
    })

def hot(request):
    questions = Question.objects.get_hot_by_answers()
    page = paginate(questions, request)
    return render(request, "hot.html", context={
       'questions' : page.object_list,
       'page_obj' : page,
       'popular_tags' : Tag.objects.get_popular_tags(),
       'best_members' : Profile.objects.get_best_members_by_answers(),
       'profile' : get_self_profile(),
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
       'profile' : get_self_profile(),
       'cur_tag' : cur_tag,
    })

def question(request, question_id):
    cur_question = get_object_or_404(Question, id=question_id)
    answers = Answer.objects.all()
    return render(request, "question.html", context={
        'question' : cur_question,
        'answers' : answers,
        'popular_tags' : Tag.objects.get_popular_tags(),
        'best_members' : Profile.objects.get_best_members_by_answers(),
        'profile' : get_self_profile(),
    })

def ask(request):
    return render(request, "ask.html", context={
        'popular_tags' : Tag.objects.get_popular_tags(),
        'best_members' : Profile.objects.get_best_members_by_answers(),
        'profile' : get_self_profile(),
    })

def login(request):
    return render(request, "login.html", context={
        'profile' : get_self_profile(),
    })

def registration(request):
    return render(request, "registration.html", context={
        'profile' : get_self_profile(),
    })

def settings(request):
    return render(request, "settings.html", context={
        'profile' : get_self_profile(),
    })