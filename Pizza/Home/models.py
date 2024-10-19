from django.db import models
import uuid
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import json

# A dictionary to map order statuses to progress percentages.
order_mapper = {
    'Order Recieved': 20,
    'Baking': 40,
    'Baked': 60,
    'Out of Delivery': 80,
    'Order Develivery': 100,
}

class Pizza(models.Model):
    # Defines the Pizza model, representing an item that can be ordered.
    name = models.CharField(max_length=100)
    price = models.FloatField(default=100)
    image = models.URLField(max_length=250)
    desc = models.TextField(max_length=250)

    def __str__(self):
        return self.name

class Order(models.Model):
    # Choices for the status field, representing different order stages.
    STATUS = (
        ("Order Recieved", "Order Recieved"),
        ("Baking", "Baking"),
        ("Baked", "Baked"),
        ("Out of Delivery", "Out of Delivery"),
        ("Order Develivery", "Order Develivery"),
    )

    # Defines the Order model which includes a foreign key to the Pizza model and other order-specific fields.
    pizza = models.ForeignKey(Pizza, on_delete=models.CASCADE)   
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    order_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    amount = models.FloatField()
    status = models.CharField(max_length=100, choices=STATUS, default="Order Recieved")
    created_at = models.DateField(auto_now_add=True)  # Automatically set the date when the order is created.
    created_time = models.TimeField(auto_now_add=True)  # Automatically set the time when the order is created.

    def __str__(self):
        return f"{self.pizza} - {self.status}"

    @staticmethod
    def give_order_details(order_id):
        # This static method fetches order details by order_id and formats them for WebSocket consumption.
        instance = Order.objects.get(order_id=order_id)
        return {
            'order_id': str(instance.order_id),
            'amount': instance.amount,
            'status': instance.status,
            'date': str(instance.created_at),
            'progress_percentage': order_mapper[instance.status]  # Maps the status to a progress percentage.
        }

# Django signal that triggers whenever an order is updated.
@receiver(post_save, sender=Order)
def order_status_handler(sender, instance, created, **kwargs):
    # This signal handler is triggered after an Order is saved.
    # It sends updated order data to the corresponding WebSocket group.
    
    if not created:  # Only send updates for existing orders (not newly created ones).
        channel_layer = get_channel_layer()  # Get the channel layer to send the message through WebSocket.
        
        # Prepare the data to be sent, which includes order details and progress percentage.
        data = {
            'order_id': str(instance.order_id),
            'amount': instance.amount,
            'status': instance.status,
            'date': str(instance.created_at),
            'progress_percentage': order_mapper[instance.status]
        }

        # Send the updated order data to the specific WebSocket group corresponding to the order_id.
        async_to_sync(channel_layer.group_send)(
            f'orders_{instance.order_id}',  # The group name tied to the order_id.
            {
                'type': 'order_status',  # The type of the message (calls the 'order_status' method in MyConsumer).
                'value': json.dumps(data)  # The data being sent, serialized as JSON.
            }
        )
