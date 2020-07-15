from django.contrib.auth import authenticate, login, get_user_model, logout
from django.contrib.auth.models import User
from django.db import transaction
from django.db.models import F
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render

# Create your views here.
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from django.db import IntegrityError

from game.models import Game, Question, UserGames, Options, Category
from game.serializers import GameSerializer, QuestionSerializer, OptionsSerializer, UserGamesSerializer, \
    CategorySerializer, UserSerializer

from rest_framework.authtoken.models import Token


@api_view(['GET'])
def get_all_category(request):
    try:
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
@authentication_classes((TokenAuthentication,))
def create_category(request):
    if request.method == "POST":
        if 'name' not in request.data:
            return JsonResponse({
                "error": "Enter category name"
            }, status=status.HTTP_400_BAD_REQUEST)
        token = request.META['HTTP_AUTHORIZATION'].split(' ')
        try:
            user = Token.objects.get(key=token[1]).user
        except Token.DoesNotExist:
            return JsonResponse(
                {"error": "Invalid token"}, status=status.HTTP_401_UNAUTHORIZED
            )
        data = {
            'name': request.data['name'],
            'user': user.id
        }
        createcategory = CategorySerializer(data=data)
        if createcategory.is_valid():
            createcategory.save()
            return Response(createcategory.data, status=status.HTTP_201_CREATED)
        return Response(createcategory.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@authentication_classes((TokenAuthentication,))
def create_question(request):
    token = request.META['HTTP_AUTHORIZATION'].split(' ')
    try:
        user = Token.objects.get(key=token[1]).user
    except Token.DoesNotExist:
        return JsonResponse(
            {"error": "Invalid token"}, status=status.HTTP_401_UNAUTHORIZED
        )
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
    category = CategorySerializer(cats, many=True).data
    options = question['options']
    optionsList = []
    for option in options:
        optionData = Options.objects.filter(option=option)
        if len(optionData) == 0:
            option = {
                'option': option
            }
            serializer = OptionsSerializer(data=option, many=False)
            if serializer.is_valid():
                serializer.save()
        else:
            serializer = OptionsSerializer(optionData[0], many=False)
        optionsList.append(serializer.data['option'])
    question = {
        "question": question['question'],
        "category": category[0]['name'],
        "options": optionsList,
        "user": user.id,
        "answer": optionsList[index]
    }
    serializer = QuestionSerializer(data=question)
    if serializer.is_valid():
        serializer.save()
        return JsonResponse({
            "data": serializer.data
        }, status=status.HTTP_200_OK)
    return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
@authentication_classes((TokenAuthentication,))
def update_question(request):
    token = request.META['HTTP_AUTHORIZATION'].split(' ')
    try:
        user = Token.objects.get(key=token[1]).user
    except Token.DoesNotExist:
        return JsonResponse(
            {"error": "Invalid token"}, status=status.HTTP_401_UNAUTHORIZED
        )
    question = request.data.get('Question')
    questionData = Question.objects.filter(id=question['id'])

    if len(questionData) == 0:
        return JsonResponse(
            {"error": "There is no question with this id"}, status=status.HTTP_401_UNAUTHORIZED
        )
    ques = QuestionSerializer(questionData[0], many=False).data
    print(ques)
    if ques['user'] != user.id:
        return JsonResponse(
            {"error": "Cannot update the question .The questions can only be updated by the user who created"},
            status=status.HTTP_401_UNAUTHORIZED
        )

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
    category = CategorySerializer(cats, many=True).data
    options = question['options']
    optionsList = []
    for option in options:
        optionData = Options.objects.filter(option=option)
        if len(optionData) == 0:
            option = {
                'option': option
            }
            serializer = OptionsSerializer(data=option, many=False)
            if serializer.is_valid():
                serializer.save()
        else:
            serializer = OptionsSerializer(optionData[0], many=False)
        optionsList.append(serializer.data['option'])
    
    questionData = Question.objects.get(id=question['id'])
    questionData.question = question['question']    
    questionData.category = Category.objects.get(name=category[0]['name'])
    questionData.options.set(optionsList)
    questionData.user = user
    questionData.answer = Options.objects.get(option=optionsList[index])
    questionData.save()
    serializer = QuestionSerializer(questionData)
    return JsonResponse({
        "data": serializer.data
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@authentication_classes((TokenAuthentication,))
def get_questions(request):
    token = request.META['HTTP_AUTHORIZATION'].split(' ')
    try:
        user = Token.objects.get(key=token[1]).user
    except Token.DoesNotExist:
        return JsonResponse(
            {"error": "Invalid token"}, status=status.HTTP_401_UNAUTHORIZED
        )
    questions = Question.objects.filter()
    questionData = QuestionSerializer(questions, many=True).data
    questions = []
    for question in questionData:
        options = []
        for option in question['options']:
            optionQuery = Options.objects.get(option=option)
            optionData = OptionsSerializer(optionQuery, many=False).data
            options.append(optionData['option'])
        question['options'] = options
        questions.append(question)
    return JsonResponse({
        "data": questions
    }, status=status.HTTP_200_OK)


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

    data = {
        'user_name': request.data['user_name'],
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
        game = Game.objects.get(game_code=request.data['game_code'])
        gameData = GameSerializer(game).data
        if gameData['user_name'] == request.data['user_name']:
            return JsonResponse({"error": "Admin cannot play the game"}, status=status.HTTP_400_BAD_REQUEST)
        if gameData['active']:
            ug = UserGames.objects.filter(game_code=request.data['game_code'], user_name=request.data['user_name'])
            if len(ug) != 0:
                return JsonResponse({
                    "error": "Already played game"
                }, status=status.HTTP_400_BAD_REQUEST)
            questions = Question.objects.filter(category=gameData['category'])
            questionData = QuestionSerializer(questions, many=True).data
            questions = []
            for question in questionData:
                options = []
                for option in question['options']:
                    optionQuery = Options.objects.get(option=option)
                    optionData = OptionsSerializer(optionQuery, many=False).data
                    options.append(optionData['option'])
                question['options'] = options
                questions.append(question)
            serializer = UserGamesSerializer(data={
                'game_code': request.data['game_code'],
                'category': gameData['category'],
                'user_name': request.data['user_name']
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
        ug.score = ug.score + int(request.data['no_answers_crct'])
        ug.save()
        # ug = UserGames.objects.filter(id=request.data['user_game_id']).update(score=F['score'] + 1)
        ugSerializer = UserGamesSerializer(ug, many=False).data
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
    if request.query_params.get("game_code") is None:
        return JsonResponse(
            {"error": "Enter game_code"}, status=status.HTTP_400_BAD_REQUEST
        )
    try:
        data = UserGames.objects.filter(game_code=request.query_params.get("game_code")).order_by('-score')
        if request.query_params.get("n") is not None:
            n = int(request.query_params.get("n"))
            data = data[:n]
        userGames = UserGamesSerializer(data, many=True).data
        return JsonResponse({
            "data": userGames
        }, status=status.HTTP_200_OK)
    except Exception as error:
        return JsonResponse({
            "error": error
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def register(request):
    if "username" not in request.data:
        return JsonResponse(
            {"error": "Enter username"}, status=status.HTTP_400_BAD_REQUEST
        )
    if "email" not in request.data:
        return JsonResponse(
            {"error": "Enter email"}, status=status.HTTP_400_BAD_REQUEST
        )
    if "password" not in request.data:
        return JsonResponse(
            {"error": "Enter password"}, status=status.HTTP_400_BAD_REQUEST
        )
    user = User.objects.filter(username=request.data['username'])
    if len(user) != 0:
        return JsonResponse(
            {"error": "Username already exists"}, status=status.HTTP_400_BAD_REQUEST
        )
    user = User.objects.filter(email=request.data['email'])
    if len(user) != 0:
        return JsonResponse(
            {"error": "Email address already exists"}, status=status.HTTP_400_BAD_REQUEST
        )
    VALID_USER_FIELDS = [f.name for f in get_user_model()._meta.fields]
    serialized = UserSerializer(data=request.data)
    if serialized.is_valid():
        user_data = {field: data for (field, data) in request.data.items() if field in VALID_USER_FIELDS}
        user = get_user_model().objects.create_user(
            **user_data
        )
        return Response(UserSerializer(instance=user).data, status=status.HTTP_201_CREATED)
    else:
        return Response(serialized.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def login_user(request):
    if "user_name" not in request.data:
        return JsonResponse(
            {"error": "Enter user_name"}, status=status.HTTP_400_BAD_REQUEST
        )
    if "password" not in request.data:
        return JsonResponse(
            {"error": "Enter password"}, status=status.HTTP_400_BAD_REQUEST
        )
    user = User.objects.get(username__exact=request.data['user_name'])
    if user is not None and user.check_password(request.data['password']) == True:
        login(request, user)
        userData = UserSerializer(user).data
        try:
            token = Token.objects.create(user=request.user)
            return JsonResponse(
                {"token": token.key, "user": userData}, status=status.HTTP_200_OK
            )
        except IntegrityError:
            return JsonResponse(
                {"error": "User is already logged in"}, status=status.HTTP_400_BAD_REQUEST
            )
    else:
        return JsonResponse(
            {"error": "Invalid credentials"}, status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['POST'])
@authentication_classes((TokenAuthentication,))
def logout_user(request):
    print(request.META['HTTP_AUTHORIZATION'])
    print(request.user)
    token = request.META['HTTP_AUTHORIZATION'].split(' ')
    try:
        token = Token.objects.get(key=token[1])
        token.delete()
        logout(request)
        # print(request.META['HTTP_AUTHORIZATION'])
        # token = request.META['HTTP_AUTHORIZATION'].split(' ')
        # user = Token.objects.get(key=token[1]).user
        return JsonResponse(
            {"data": "Logged out successfully"}, status=status.HTTP_200_OK
        )
    except Token.DoesNotExist:
        return JsonResponse(
            {"error": "Invalid token"}, status=status.HTTP_401_UNAUTHORIZED
        )
    except Exception as error:
        return JsonResponse(
            {"error": error}, status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['GET'])
@authentication_classes((TokenAuthentication,))
def get_user_data(request):
    token = request.META['HTTP_AUTHORIZATION'].split(' ')
    try:
        # print(request.META['HTTP_AUTHORIZATION'])
        # token = request.META['HTTP_AUTHORIZATION'].split(' ')
        user = Token.objects.get(key=token[1]).user
        return JsonResponse(
            {"data": UserSerializer(user).data}, status=status.HTTP_200_OK
        )
    except Token.DoesNotExist:
        return JsonResponse(
            {"error": "Invalid token"}, status=status.HTTP_401_UNAUTHORIZED
        )
    except Exception as error:
        return JsonResponse(
            {"error": error}, status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['PUT'])
@authentication_classes((TokenAuthentication,))
def change_password(request):
    if "current_password" not in request.data:
        return JsonResponse(
            {"error": "Enter password"}, status=status.HTTP_400_BAD_REQUEST
        )
    if "password" not in request.data:
        return JsonResponse(
            {"error": "Enter password"}, status=status.HTTP_400_BAD_REQUEST
        )
    token = request.META['HTTP_AUTHORIZATION'].split(' ')
    try:
        user = Token.objects.get(key=token[1]).user
        if not user.check_password(request.data['current_password']):
            return JsonResponse(
                {"error": "Password entered is incorrect"}, status=status.HTTP_400_BAD_REQUEST
            )
        user.set_password(request.data['password'])
        user.save()
        return JsonResponse(
            {"data": UserSerializer(user).data}, status=status.HTTP_200_OK
        )
    except Token.DoesNotExist:
        return JsonResponse(
            {"error": "Invalid token"}, status=status.HTTP_401_UNAUTHORIZED
        )
    except Exception as error:
        return JsonResponse(
            {"error": error}, status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['PUT'])
def forgot_password(request):
    if "email" not in request.data:
        return JsonResponse(
            {"error": "Enter password"}, status=status.HTTP_400_BAD_REQUEST
        )
    if "password" not in request.data:
        return JsonResponse(
            {"error": "Enter password"}, status=status.HTTP_400_BAD_REQUEST
        )
    try:
        user = User.objects.get(email=request.data['email'])
        user.set_password(request.data['password'])
        user.save()
        return JsonResponse(
            {"data": UserSerializer(user).data}, status=status.HTTP_200_OK
        )
    except User.DoesNotExist:
        return JsonResponse(
            {"error": "Invalid email address"}, status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as error:
        return JsonResponse(
            {"error": error}, status=status.HTTP_400_BAD_REQUEST
        )

@api_view(['POST'])
@authentication_classes((TokenAuthentication,))
def delete_question(request):
    token = request.META['HTTP_AUTHORIZATION'].split(' ')
    if "id" not in request.data:
        return JsonResponse(
            {"error": "Enter correct question ID"}, status=status.HTTP_400_BAD_REQUEST
        )
    #questionData = request.data.get('Question')    
    #checkuser = QuestionSerializer.data
    #checkuser = Question.objects.filter(id=request.data['id'])
    #ques = QuestionSerializer(questionData, many=False).data
    #if ques['user'] != user.id:
    #    return JsonResponse(
    #        {"error": "Cannot delete the question .The questions can only be deleted by the user who created"},
    #        status=status.HTTP_401_UNAUTHORIZED
    #    )
    try:
        user = Token.objects.get(key=token[1]).user
    except Token.DoesNotExist:
        return JsonResponse(
            {"error": "Invalid token"}, status=status.HTTP_401_UNAUTHORIZED
        )
    Question.objects.filter(id=request.data['id']).delete()
    return JsonResponse(
        {"question":"Question deleted sucessfully"}, status = status.HTTP_204_NO_CONTENT
    )


@api_view(['POST'])
@authentication_classes((TokenAuthentication,))
def delete_category(request):
    token = request.META['HTTP_AUTHORIZATION'].split(' ')
    if "name" not in request.data:
        return JsonResponse(
            {"error": "Enter a valid category name"}, status=status.HTTP_400_BAD_REQUEST
        )
    try:
        user = Token.objects.get(key=token[1]).user
    except Token.DoesNotExist:
        return JsonResponse(
            {"error": "Invalid User token "}, status=status.HTTP_401_UNAUTHORIZED
        )
    Category.objects.filter(name=request.data['name']).delete()
    return JsonResponse(
        {"category":"Category name deleted sucessfully"}, status = status.HTTP_204_NO_CONTENT
    )


@api_view(['PUT'])
@authentication_classes((TokenAuthentication,))
def update_category(request):
    token = request.META['HTTP_AUTHORIZATION'].split(' ')
    if "name" not in request.data:
        return JsonResponse(
            {"error": "Enter a valid category name"}, status=status.HTTP_400_BAD_REQUEST
        )
    if "newname" not in request.data:
        return JsonResponse(
            {"error": "Enter a valid category name"}, status=status.HTTP_400_BAD_REQUEST
        )
    try:
        user = Token.objects.get(key=token[1]).user
    except Token.DoesNotExist:
        return JsonResponse(
            {"error": "Invalid User token "}, status=status.HTTP_401_UNAUTHORIZED
        )
    Category.objects.filter(name = request.data['name']).update(name=request.data['newname'])
    return JsonResponse(
        {"category":"Category name updated sucessfully"}, status = status.HTTP_201_CREATED
    )