from django.urls import path


from . import views

app_name = 'protocols'
urlpatterns = [
    # path('', views.index, name='index'),
    path('', views.IndexView.as_view(), name='index'),
    path('scheduler/', views.scheduler, name='scheduler'),
    path('scheduler/<int:experiment_id>/', views.scheduler_options, name='scheduler_options'),
    path('new_protocol/', views.ProtocolCreate.as_view(), name='add_protocol'),
    path('edit/<int:pk>/', views.ProtocolUpdate.as_view(), name='edit_protocol'),
    path('delete/<int:pk>/', views.ProtocolDelete.as_view(), name='delete_protocol'),
    path('new_event/', views.create_event, name='create_event'),
    path('<int:protocol_id>/', views.detail, name='detail'),
    path('calendar/', views.CalendarView.as_view(), name='calendar'),
    path('event/<int:event_id>/', views.event, name='event'),
    path('experiment/<int:experiment_id>/', views.experiment, name='experiment'),
    path('calendar/edit/<int:event_id>/', views.edit_event, name='event_edit'),
    path('calendar/delete/<int:event_id>/', views.delete_event, name="event_delete")
]