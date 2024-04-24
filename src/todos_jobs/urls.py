from django.urls import include, path
from .views import All_Jobs
urlpatterns = [
    path('all-jobs',  All_Jobs),

]
