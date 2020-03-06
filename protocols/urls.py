from django.urls import path


from . import views

app_name = 'protocols'
urlpatterns = [
    # path('', views.index, name='index'),
    path('', views.IndexView.as_view(), name='index'),
    path('<int:protocol_id>/', views.detail, name='detail'),
    path('calendar/', views.CalendarView.as_view(), name='calendar'),
    path('calendar/edit/<int:event_id>/', views.event, name='event_edit')
]