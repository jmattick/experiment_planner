from django.urls import path


from . import views

app_name = 'protocols'
urlpatterns = [
    # path('', views.index, name='index'),
    path('', views.IndexView.as_view(), name='index'),
    path('scheduler/', views.scheduler, name='scheduler'),
    path('scheduler/<int:experiment_id>/', views.scheduler_options, name='scheduler_options'),
    path('new_protocol', views.ProtocolCreate.as_view(), name = 'add_protocol'),
    path('new_event/', views.create_event, name='create_event'),
    path('<int:protocol_id>/', views.detail, name='detail'),
    path('calendar/', views.CalendarView.as_view(), name='calendar'),
    path('calendar/edit/<int:event_id>/', views.event, name='event_edit')
]