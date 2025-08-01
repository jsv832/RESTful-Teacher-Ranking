from django.urls import path
from .views import (
    register_user, login_user, logout_user,
    list_module_instances, view_all_professor_ratings,
    average_rating_professor_module, rate_professor
)

urlpatterns = [

    #Endpoints:
    path('register/', register_user, name='register'),
    path('login/', login_user, name='login'),
    path('logout/', logout_user, name='logout'),

    path('list/', list_module_instances, name='list-module-instances'),
    path('view/', view_all_professor_ratings, name='view-prof-ratings'),
    path('average/<str:professor_id>/<str:module_code>/', average_rating_professor_module, name='average-rating'),
    path('rate-professor/', rate_professor, name='rate-professor'),
]
