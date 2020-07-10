from rest_framework import serializers

from .models import Game, User, Question, Options, UserGames, Category


class GameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Game
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = '__all__'
    #def create(self, validated_data):
        #return Question.objects.create(**validated_data)


class OptionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Options
        fields = '__all__'


class UserGamesSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserGames
        fields = '__all__'

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'