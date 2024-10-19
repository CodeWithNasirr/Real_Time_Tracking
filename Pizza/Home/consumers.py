from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync, sync_to_async
import json
from .models import *

class MyConsumer(WebsocketConsumer):
    def connect(self):
        # Extract the order_id from the URL route parameters and set room names.
        # self.room_name stores the unique order_id, which is passed via the URL.
        self.room_name = self.scope['url_route']['kwargs']['order_id']
        
        # self.room_group_name is the group identifier for WebSocket connections related to this specific order.
        # This allows us to broadcast messages to all WebSocket clients tracking this order.
        self.room_group_name = f"orders_{self.room_name}"

        # Join the WebSocket connection to this group using the channel layer.
        # This ensures that messages sent to this group are received by all clients in the group.
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )

        # Fetch the order details from the model using the static method 'give_order_details'.
        # This sends the order data to the connected WebSocket client upon connection.
        orders = Order.give_order_details(self.room_name)

        # Accept the WebSocket connection
        self.accept()

        # Send the order details as JSON to the connected WebSocket client.
        self.send(text_data=json.dumps({
            'order': orders
        }))

    def order_status(self, event):
        # print(event)
        # This method is triggered whenever the 'group_send' method is called in the signal handler.
        # The 'event' parameter contains the message data broadcasted to the group.

        # Deserialize the JSON value from the event, which contains order status updates.
        data = json.loads(event['value'])

        # Send the updated order data back to the client via WebSocket.
        self.send(text_data=json.dumps({
            'order': data
        }))

    def receive(self, text_data=None, bytes_data=None):
        # This method can be used to receive messages from the WebSocket client.
        # For now, it just prints any received text data.
        print(text_data)

    def disconnect(self, code):
        # When the WebSocket connection is closed, this method is called.
        # You could perform any cleanup here if needed.
        return super().disconnect(code)
