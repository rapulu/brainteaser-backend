from django.contrib import admin

# Register your models here.
from .models import User,Category,Question,Options,UserGames,Game

admin.site.register(User)
admin.site.register(Category)
admin.site.register(Question)
admin.site.register(Options)
admin.site.register(Game)
admin.site.register(UserGames)