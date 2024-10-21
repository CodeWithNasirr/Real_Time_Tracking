# Real-time Pizza Order Tracking System

This is a Django-based project for tracking pizza orders in real-time using **WebSockets**, **Django Channels**, and **Redis**. The project also includes **static file handling**, **templates**, and **Tailwind CSS** for front-end styling. It allows users to view the progress of their pizza order in real-time and updates the order status dynamically.

## Features
- Real-time pizza order tracking using WebSockets
- Redis-powered channel layers for real-time data transfer
- Signal-based event triggers on order status changes
- Tailwind CSS for a modern UI design

## Prerequisites

Before setting up this project, ensure that you have the following installed on your machine:

- Python 3.12
- Redis server
- Node.js and npm (for Tailwind CSS)
- Django 5 
- Django Channels
- Channels Redis

## Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/realtimetracking.git
cd realtimetracking
```

### 2. Create a Virtual Environment

Set up a virtual environment for Python dependencies:

```bash
python3 -m venv venv
source venv/bin/activate  # For Linux/Mac
# OR
venv\Scripts\activate  # For Windows
```

### 3. Install Dependencies

Install the required Python packages:

```bash
pip install -r requirements.txt
```

The `requirements.txt` file should contain:
```
Django==4.2
channels==4.0.0
channels-redis==4.0.0
```

### 4. Install and Configure Redis

Make sure Redis is installed and running:

- For **Linux**:  
  ```bash
  sudo apt install redis
  sudo service redis-server start
  ```

- For **Mac**:  
  Install via Homebrew:
  ```bash
  brew install redis
  brew services start redis
  ```

- For **Windows**:  
  Download Redis for Windows from the official repository [here](https://github.com/microsoftarchive/redis/releases).

### 5. Configure Django Settings

In `realtimetracking/settings.py`, ensure the following settings are added for **Channels** and **Redis**:

```python
INSTALLED_APPS = [
    # Other installed apps...
    'pizzatracker',
    'channels',
]

ASGI_APPLICATION = 'realtimetracking.asgi.application'

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [("127.0.0.1", 6379)],
        },
    },
}
```

### 6. Setup Database and Migrate

Run the following commands to create the database and migrate the models:

```bash
python manage.py makemigrations pizzatracker
python manage.py migrate
```

### 7. Tailwind CSS Installation

To style the frontend, install **Tailwind CSS** using npm:

```bash
npm install -D tailwindcss
npx tailwindcss init
```

Update the `tailwind.config.js` file to point to your templates:

```js
module.exports = {
  content: ['./pizzatracker/templates/**/*.html'],
  theme: {
    extend: {},
  },
  plugins: [],
}
```

Run Tailwind CSS to watch for changes:

```bash
npx tailwindcss -i ./pizzatracker/static/input.css -o ./pizzatracker/static/output.css --watch
```

### 8. Run the Redis Server

Make sure Redis is running on your local machine:

```bash
redis-server
```

### 9. Run Django Development Server

Run the Django development server:

```bash
python manage.py runserver
```

### 10. WebSocket Testing

Use a WebSocket client like **WebSocket King** or **Postman** to test the real-time order status tracking. You can hit the WebSocket URL in the format:

```bash
ws://127.0.0.1:8000/ws/pizza/<order_id>/
```

For testing, add a pizza order and track its status through WebSockets.

## Application Overview

### Directory Structure

```
realtimetracking/
│
├── pizzatracker/               # Django App for Pizza tracking
│   ├── migrations/             # Django migrations
│   ├── static/                 # Static files (CSS, JS, Images)
│   ├── templates/              # HTML templates for the frontend
│   ├── consumers.py            # WebSocket consumer for real-time order tracking
│   ├── models.py               # Order and Pizza models
│   ├── views.py                # View logic (if any)
│   └── urls.py                 # URL routing for the app
│
├── realtimetracking/           # Main project folder
│   ├── asgi.py                 # ASGI configuration for Channels
│   ├── settings.py             # Project settings
│   └── urls.py                 # Main project URL routing
│
└── manage.py                   # Django management script
```

### WebSocket Consumer

In `pizzatracker/consumers.py`, the logic for handling WebSocket connections:

```python
from channels.generic.websocket import WebsocketConsumer
from .models import Order
from asgiref.sync import async_to_sync
import json

class OrderProgess(WebsocketConsumer):
    def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['order_id']
        self.room_group_name = f'order_{self.room_name}' 

        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )

        order = Order.give_order_details(self.room_name)
        self.accept()
        self.send(text_data=json.dumps({"payload": order}))

    def order_status(self, event):
        data = json.loads(event['value'])
        self.send(text_data=json.dumps({'payload': data}))

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )
```

### Signal for Order Status Updates

In `pizzatracker/models.py`, add Django signals to trigger WebSocket updates:

```python
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Order
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import json

@receiver(post_save, sender=Order)
def order_status_handler(sender, instance, created, **kwargs):
    if not created:
        channel_layer = get_channel_layer()
        data = {
            "order_id": str(instance.order_id),
            "amount": instance.amount,
            "status": instance.status,
        }
        async_to_sync(channel_layer.group_send)(
            f'order_{instance.order_id}',
            {
                'type': 'order_status',
                'value': json.dumps(data)
            }
        )
```

## Testing

1. Add an order using the Django admin interface or Django shell.
2. Open a WebSocket client and connect to the WebSocket URL with the order ID.
3. Change the order status from the admin panel or shell and see real-time updates reflected in the WebSocket client.