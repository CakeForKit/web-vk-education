from django.shortcuts import render
from django.core.paginator import Paginator

IS_AUTHORIZED = True

def question_templ(i):
    return {
        'title': 'Question ' + str(i),
        'id': i,
        'text': 'text' + str(i),
        'cnt_likes' : i+2,
        'cnt_answers' : i+5,
        'tags' : [{
            'id': i*j,
            'title' : 'tag ' + str(i*j),
        } for j in range(1,4)],
        # 'answers'
    }

QUESTIONS = [question_templ(i) for i in range(1,130)]

ANSWERS = [{
    'text' : 'Answer_text',
    'is_correct' : i % 2,
    'cnt_likes' : i+2,
} for i in range(1,3)]

POPULAT_TAGS = [{
    'id': i,
    'title' : 'tag ' + str(i),
} for i in range(1,9)]

BEST_MEMBERS = [{
    'id': i,
    'name' : 'Member name ' + str(i),
} for i in range(1,5)]

PERSON = {
    'id': 0,
    'name' : 'Person name',
}

def paginate(objects_list, request, per_page=5):
    paginator = Paginator(objects_list, per_page) 
    
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number) # обработка ошибок PageNotAnInteger и EmptyPage внутри функции get_page

    page_range = paginator.get_elided_page_range(
        number=page.number,
        on_each_side=1,
        on_ends=1
    )
    page.page_range = page_range

    return page

def index(request):
    page = paginate(QUESTIONS, request)
    return render(request, "index.html", context={
       'questions' : page.object_list,
       'page_obj' : page,
       'popular_tags' : POPULAT_TAGS,
       'best_members' : BEST_MEMBERS,
       'is_authz' : IS_AUTHORIZED,
    })

def hot(request):
    page = paginate(QUESTIONS[::-1], request)
    return render(request, "hot.html", context={
       'questions' : page.object_list,
       'page_obj' : page,
       'popular_tags' : POPULAT_TAGS,
       'best_members' : BEST_MEMBERS,
       'is_authz' : IS_AUTHORIZED,
    })

def tag(request, tag_id):
    page = paginate(QUESTIONS[::tag_id], request)
    TAG = {
        'id': tag_id,
        'title' : 'tag ' + str(tag_id),
    }
    return render(request, "tag.html", context={
       'questions' : page.object_list,
       'page_obj' : page,
       'popular_tags' : POPULAT_TAGS,
       'best_members' : BEST_MEMBERS,
       'is_authz' : IS_AUTHORIZED,
       'cur_tag' : TAG,
    })

def question(request, question_id):
    return render(request, "question.html", context={
        'question' : question_templ(question_id),
        'answers' : ANSWERS,
        'popular_tags' : POPULAT_TAGS,
        'best_members' : BEST_MEMBERS,
        'is_authz' : IS_AUTHORIZED,
    })

def ask(request):
    return render(request, "ask.html", context={
        'popular_tags' : POPULAT_TAGS,
        'best_members' : BEST_MEMBERS,
        'is_authz' : IS_AUTHORIZED,
    })

def login(request):
    return render(request, "login.html", context={
        'is_authz' : IS_AUTHORIZED,
    })

def registration(request):
    return render(request, "registration.html", context={
        'is_authz' : IS_AUTHORIZED,
    })

def settings(request):
    return render(request, "settings.html", context={
        'person' : PERSON,
        'is_authz' : True,
    })