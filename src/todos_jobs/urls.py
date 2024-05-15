from django.urls import include, path
from .views import All_Jobs,backlogUserAll,showtaskusersAll
urlpatterns = [
    path('gerir-time',  All_Jobs),
    path('ajax/backlog-user-all',  backlogUserAll),
    path('ajax/show-tasks-for-user-all',  showtaskusersAll),

]
