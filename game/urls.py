from django.urls import path

from game.views import create_a_game_code, check_if_game_code_isValid, end_game, update_score_usergame, \
    get_leader_board_game_code, get_leader_board, update_score_count_usergame, get_all_category, create_category, \
    create_question, get_user_dasboard

urlpatterns = [
    path('game', create_a_game_code),
    path('game/play', check_if_game_code_isValid),
    path('game/end', end_game),
    path('game/score',update_score_usergame),
    path('game/score/count',update_score_count_usergame),
    path('game/code/leaderboard', get_leader_board_game_code),
    path('game/leaderboard', get_leader_board),
    path('game/category', get_all_category),
    path('game/create/category', create_category),
    path('game/create/question', create_question),
    path('game/user/dashboard', get_user_dasboard)
]

