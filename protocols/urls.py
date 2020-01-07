from django.urls import path


from . import views

app_name = 'protocols'
urlpatterns = [
    path('', views.index, name='index'),
    path('<int:protocol_id>/', views.detail, name='detail'),
]