import random
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from django.db import transaction
from django.contrib.auth.hashers import make_password
from app.models import Profile, Tag, Question, Answer, LikeQuestion, LikeAnswer


class Command(BaseCommand):
    help = "Fill database with test data"

    def add_arguments(self, parser):
        parser.add_argument('ratio', type=int, help='Fill ratio coefficient')

    def handle(self, *args, **options):
        ratio = options['ratio']
        num_users = ratio
        num_questions = ratio * 10
        num_answers = ratio * 100
        num_tags = ratio
        num_likes = ratio * 200
        self.stdout.write(f'Ratio: {ratio}')
        self.stdout.write(f'Creating {num_users} users')
        self.stdout.write(f'Creating {num_questions} questions')
        self.stdout.write(f'Creating {num_answers} answers')
        self.stdout.write(f'Creating {num_tags} tags')
        self.stdout.write(f'Creating {num_likes} likes')

        with transaction.atomic():
            self.create_users(num_users)
            self.create_tags(num_tags)
            self.create_questions(num_questions, 2, 5)
            self.create_answers(num_answers)
            self.create_likes_questions(num_likes)
            self.create_likes_answers(num_likes)
        
        self.stdout.write(
            self.style.SUCCESS('Successfully filled database with test data')
        )
    
    def create_users(self, num_users): 
        users, profiles = [], []
        for i in range(num_users):
            users.append(
                User(
                    username=f'user_{i}',
                    email=f'user_{i}@example.com',
                    password=make_password('testpassword123')
                ) 
            )
        User.objects.bulk_create(users)
    
        # created_users = User.objects.filter(username__startswith='user_')
        for user in users:
            profiles.append(Profile(
                user=user, 
                nickname=user.username,
            ))
        Profile.objects.bulk_create(profiles)

        print(f"End create {num_users} users")

    def create_tags(self, num_tags):
        tags = []
        for i in range(num_tags):
            tags.append(Tag(title=f'tag_{i}'))
        Tag.objects.bulk_create(tags)

        print(f"End create {num_tags} tags")

    def create_questions(self, num_questions, min_tags_one, max_tags_one):
        questions = []
        profiles = list(Profile.objects.all())
        if not profiles:
            raise CommandError('No profiles found!')
        tags = list(Tag.objects.all())
        if not tags:
            raise CommandError('No tags found!')
                
        for i in range(num_questions):
            author = random.choice(profiles)
            question = Question(
                title=f'Question_{i}',
                text=f'Text question {i}. ' * 10,
                user=author
            )
            questions.append(question)
        Question.objects.bulk_create(questions)
        
        for question in questions:
            question_tags = random.sample(tags, k=random.randint(min_tags_one, max_tags_one))
            question.mm_tags.set(question_tags)

        print(f"End create {num_questions} questions")

    def create_answers(self, num_answers):
        answers = []
        profiles = list(Profile.objects.all())
        if not profiles:
            raise CommandError('No profiles found!')
        questions = list(Question.objects.all())
        if not questions:
            raise CommandError('No questions found!')
        
        for i in range(num_answers):
            question = random.choice(questions)
            author = random.choice(profiles)
            answer = Answer(
                question=question,
                text=f'This is answer {i} for question {question.id}. ' * 5,
                user=author,
                is_correct=random.choice([True, False, False, False])  
            )
            answers.append(answer)
        Answer.objects.bulk_create(answers)

        print(f"End create {num_answers} answers")

    def create_likes_questions(self, num_likes):
        likes = []
        profiles = list(Profile.objects.all())
        if not profiles:
            raise CommandError('No profiles found!')
        questions = list(Question.objects.all())
        if not questions:
            raise CommandError('No questions found!')
        
        for _ in range(num_likes):
            user = random.choice(profiles)
            question = random.choice(questions)
            
            like = LikeQuestion(
                user=user,
                value=random.choice([-1, 1, 1, 1]),
                question=question
            )
            likes.append(like)
        LikeQuestion.objects.bulk_create(likes, ignore_conflicts=True)

        print(f"End create {num_likes} question likes")

    def create_likes_answers(self, num_likes):
        likes = []
        profiles = list(Profile.objects.all())
        if not profiles:
            raise CommandError('No profiles found!')
        answers = list(Answer.objects.all())
        if not answers:
            raise CommandError('No answers found!')
        
        for _ in range(num_likes):
            user = random.choice(profiles)
            answer = random.choice(answers)
            
            like = LikeAnswer(
                user=user,
                value=random.choice([-1, 1, 1, 1]),
                answer=answer
            )
            likes.append(like)
        LikeAnswer.objects.bulk_create(likes, ignore_conflicts=True)

        print(f"End create {num_likes} answers likes")

