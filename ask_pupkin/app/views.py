from django.shortcuts import render

QUESTIONS = []
for i in range(1,30):
  QUESTIONS.append({
    'title': 'title ' + str(i),
    'id': i,
    'text': 'text' + str(i)
  })


def index(request):
    return render(request, "index.html", context={
       'questions' : QUESTIONS,
    })

def hot(request):
    return render(request, "hot.html", context={
       'questions' : QUESTIONS[::-1],
    })