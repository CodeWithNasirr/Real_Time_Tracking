from django.urls import path,include
from . import views
urlpatterns = [
    path('',views.index,name='Index'),
    path('status/<str:id>',views.order_status,name='status'),
    path('order-pizza/<int:id>',views.order,name="order"),

]