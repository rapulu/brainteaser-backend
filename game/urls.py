from django.urls import path

from game.views import create_a_game_code, check_if_game_code_isValid, end_game, update_score_usergame, \
    get_leader_board_game_code, get_leader_board

urlpatterns = [
    path('game', create_a_game_code),
    path('game/play', check_if_game_code_isValid),
    path('game/end', end_game),
    path('game/score',update_score_usergame),
    path('game/code/leaderboard', get_leader_board_game_code),
    path('game/leaderboard', get_leader_board)
]
