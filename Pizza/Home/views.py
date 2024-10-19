from django.shortcuts import render,redirect
from django.contrib import messages
# Create your views here.
from .models import Pizza,Order

def index(request):
    pizza=Pizza.objects.all()
    order=Order.objects.all()
    context={
        'pizzas':pizza,
        'orders':order
    }
    return render(request,'pizzatracker/index.html',context)


def order_status(request,id):
    order_details=Order.objects.get(pk=id)
    return render(request,'pizzatracker/orderstatus.html',context = {'order':order_details})



def order(request,id):
    pizza = Pizza.objects.get(id=id)
    Order.objects.create(
            pizza = pizza,
            user = request.user,
            amount = pizza.price
        )
    messages.add_message(request, messages.INFO, "Order Placed")
    return redirect('/')