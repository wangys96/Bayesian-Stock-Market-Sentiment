from django.urls import path,re_path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("hot", views.hot, name="hot"),
    path("text", views.text, name="text"),
    path("search", views.search, name="search"),    
    path("detail/<str:code>",views.detail,name="detail")
]
