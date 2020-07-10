from django.db import transaction
from django.db.models import F
from django.http import JsonResponse
from django.shortcuts import render

# Create your views here.
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from game.models import Game, User, Question, UserGames, Options, Category
from game.serializers import UserSerializer, GameSerializer, QuestionSerializer, OptionsSerializer, UserGamesSerializer, CategorySerializer

@api_view(['GET'])
def get_all_category(request):
    try:
        category = str(request.query_params.get("Category"))
        data = Category.objects.all()
        question = CategorySerializer(data, many=True).data
        return JsonResponse({
            "data": question
        }, status=status.HTTP_200_OK)
    except Exception as error:
        return JsonResponse({
            "error": error
        }, status=status.HTTP_400_BAD_REQUEST)




@api_view(['POST'])
def create_category(request):
    if request.method == "POST":
        createcategory = CategorySerializer(data=request.data)
        if createcategory.is_valid():
            createcategory.save()
            return Response(createcategory.data, status = status.HTTP_201_CREATED)
            return Response(createcategory.data, status = status.HTTP_400_BAD_REQUEST)



@api_view(['POST'])
def create_question(request):
    question = request.data.get('Question')
    cats = Category.objects.filter(name=question['category'])
    if len(cats) == 0:
        return JsonResponse(
            {"error": "Enter valid category"}, status=status.HTTP_400_BAD_REQUEST
        )
    try:
        index = question['options'].index(question['answer'])
    except Exception as error:
        return JsonResponse(
            {"error": "There is no option with the answer "}, status=status.HTTP_400_BAD_REQUEST
        )
    category = CategorySerializer(cats,many=True).data
    print(category)
    options = question['options']
    optionsList = []
    for option in options:
        optionData = Options.objects.filter(option=option)
        if len(optionData) == 0:
            option={
                'option':option
            }
            serializer = OptionsSerializer(data=option, many=False)
            if serializer.is_valid():
                serializer.save()
        else:
            serializer = OptionsSerializer(optionData[0], many=False)
        optionsList.append(serializer.data['option'])
    question = {
        "question":question['question'],
        "category": category[0]['name'],
        "options":optionsList,
        "answer":optionsList[index]
    }
    serializer = QuestionSerializer(data=question)
    if serializer.is_valid():
        serializer.save()
        return JsonResponse({
            "data": serializer.data
        }, status=status.HTTP_200_OK)
    return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
def create_a_game_code(request):
    if "user_name" not in request.data:
        return JsonResponse(
            {"error": "Enter user_name"}, status=status.HTTP_400_BAD_REQUEST
        )
    if "category" not in request.data:
        return JsonResponse(
            {"error": "Enter category"}, status=status.HTTP_400_BAD_REQUEST
        )
    try:
        user = User.objects.get(name=request.data['user_name'])
        user = UserSerializer(user).data
    except User.DoesNotExist:
        data = {
            'name': request.data['user_name']
        }
        user = UserSerializer(data=data)
        print(user)
        if user.is_valid():
            user.save()
        user = user.data
    data = {
        'user': user['id'],
        'category': request.data['category']
    }
    game = GameSerializer(data=data)
    if game.is_valid():
        game.save()
        return JsonResponse(game.data, status=status.HTTP_200_OK)
    return JsonResponse(game.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
def check_if_game_code_isValid(request):
    if "game_code" not in request.data:
        return JsonResponse(
            {"error": "Enter game_code"}, status=status.HTTP_400_BAD_REQUEST
        )
    if "user_name" not in request.data:
        return JsonResponse(
            {"error": "Enter user_name"}, status=status.HTTP_400_BAD_REQUEST
        )
    try:
        user = User.objects.filter(name=request.data['user_name'])
        print(len(user))
        if len(user) == 0:
            data = {
                'name': request.data['user_name']
            }
            user = UserSerializer(data=data)
            if user.is_valid():
                user.save()
            user = user.data
        else:
            user = UserSerializer(user, many=True).data
            user = user[0]
        ug = UserGames.objects.filter(game_code=request.data['game_code'], user=user['id'])
        if len(ug) != 0:
            return JsonResponse({
                "error": "Already played game"
            }, status=status.HTTP_400_BAD_REQUEST)
        game = Game.objects.get(game_code=request.data['game_code'])
        print(game)
        gameData = GameSerializer(game).data
        if gameData['active']:
            questions = Question.objects.filter(category=gameData['category'])
            questionData = QuestionSerializer(questions, many=True).data
            questions = []
            for question in questionData:
                options = []
                for option in question['options']:
                    print(option)
                    optionQuery = Options.objects.get(option=option)
                    optionData = OptionsSerializer(optionQuery, many=False).data
                    options.append(optionData['option'])
                question['options'] = options
                questions.append(question)
            serializer = UserGamesSerializer(data={
                'game_code': request.data['game_code'],
                'category': gameData['category'],
                'user': user['id']
            })
            if serializer.is_valid():
                serializer.save()
                return JsonResponse({
                    "data": {
                        'questions': questions,
                        'usergameData': serializer.data
                    }
                }, status=status.HTTP_200_OK)
            return JsonResponse({
                "error": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        else:
            return JsonResponse({"error": "Game code is expired"}, status=status.HTTP_400_BAD_REQUEST)
    except Game.DoesNotExist:
        return JsonResponse({
            "error": "Invalid game code"
        }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as error:
        return
        JsonResponse({"error": error}, status=status.HTTP_400_BAD_REQUEST)


@api_view(["PUT"])
def end_game(request):
    if "game_code" not in request.data:
        return JsonResponse(
            {"error": "Enter game_code"}, status=status.HTTP_400_BAD_REQUEST
        )
    try:
        game = Game.objects.get(game_code=request.data['game_code'])
        updated = Game.objects.filter(game_code=request.data['game_code']).update(active=False)
        game = Game.objects.get(game_code=request.data['game_code'])
        gameData = GameSerializer(game).data
        return JsonResponse({
            "data": gameData
        }, status=status.HTTP_200_OK)
    except Game.DoesNotExist:
        return JsonResponse({
            "error": "Invalid game code"
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
def update_score_usergame(request):
    if "user_game_id" not in request.data:
        return JsonResponse(
            {"error": "Enter user_game_id"}, status=status.HTTP_400_BAD_REQUEST
        )
    try:
        ug = UserGames.objects.get(id=request.data['user_game_id'])
        ug.score = ug.score + 1
        ug.save()
        # ug = UserGames.objects.filter(id=request.data['user_game_id']).update(score=F['score'] + 1)
        ugSerializer = UserGamesSerializer(ug, many=False).data
        user = User.objects.get(id=ugSerializer['user'])
        user.score = user.score + 1
        user.save()
        return JsonResponse({
            "data": ugSerializer
        }, status=status.HTTP_200_OK)
    except UserGames.DoesNotExist:
        return JsonResponse({
            "error": "Invalid user_game_id"
        }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as error:
        return JsonResponse({
            "error": error
        }, status=status.HTTP_400_BAD_REQUEST)

@api_view(["POST"])
def update_score_count_usergame(request):
    if "user_game_id" not in request.data:
        return JsonResponse(
            {"error": "Enter user_game_id"}, status=status.HTTP_400_BAD_REQUEST
        )
    if "no_answers_crct" not in request.data:
        return JsonResponse(
            {"error": "Enter no_answers_crct"}, status=status.HTTP_400_BAD_REQUEST
        )
    try:
        ug = UserGames.objects.get(id=request.data['user_game_id'])
        ug.score = ug.score +int(request.data['no_answers_crct'])
        ug.save()
        # ug = UserGames.objects.filter(id=request.data['user_game_id']).update(score=F['score'] + 1)
        ugSerializer = UserGamesSerializer(ug, many=False).data
        user = User.objects.get(id=ugSerializer['user'])
        user.score = user.score + int(request.data['no_answers_crct'])
        user.save()
        return JsonResponse({
            "data": ugSerializer
        }, status=status.HTTP_200_OK)
    except UserGames.DoesNotExist:
        return JsonResponse({
            "error": "Invalid user_game_id"
        }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as error:
        return JsonResponse({
            "error": error
        }, status=status.HTTP_400_BAD_REQUEST)

@api_view(["GET"])
def get_leader_board_game_code(request):
    if request.query_params.get("n") is None:
        return JsonResponse(
            {"error": "Enter n"}, status=status.HTTP_400_BAD_REQUEST
        )
    if request.query_params.get("game_code") is None:
        return JsonResponse(
            {"error": "Enter game_code"}, status=status.HTTP_400_BAD_REQUEST
        )
    try:
        n = int(request.query_params.get("n"))
        data = UserGames.objects.filter(game_code=request.query_params.get("game_code")).order_by('-score')[
               :n]
        userGames = UserGamesSerializer(data, many=True).data
        users = []
        for ug in userGames:
            user = User.objects.get(id=ug['user'])
            userData = UserSerializer(user).data
            ug['user'] = userData
        return JsonResponse({
            "data": userGames
        }, status=status.HTTP_200_OK)
    except Exception as error:
        return JsonResponse({
            "error": error
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
def get_leader_board(request):
    if request.query_params.get("n") is None:
        return JsonResponse(
            {"error": "Enter n"}, status=status.HTTP_400_BAD_REQUEST
        )
    try:
        n = int(request.query_params.get("n"))
        data = User.objects.all().order_by('-score')[:n]
        user = UserSerializer(data, many=True).data
        return JsonResponse({
            "data": user
        }, status=status.HTTP_200_OK)
    except Exception as error:
        return JsonResponse({
            "error": error
        }, status=status.HTTP_400_BAD_REQUEST)
