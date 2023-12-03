# Chat Website with Django and Django Channels

This tutorial will guide you through creating a chat website using Django and Django Channels.

## Getting Started

### 1. Setting up a Django Project

1. Create and enter the desired directory for project setup.

2. Create a virtual environment using pipenv or other means:

    ```shell
    pipenv shell
    ```

3. Install Django:

    ```shell
    pip install django
    ```

4. Create a Django project called ChatPrj:

    ```shell
    django-admin startproject ChatPrj
    ```

5. Create an app called ChatApp:

    ```shell
    python manage.py startapp ChatApp
    ```

6. Open the project in your code editor.

7. Create a templates folder and register it in the project's settings.

8. Register the app in the project's settings.

9. Create URLs for the app and register them in the project's URLs.

### 2. Installing Libraries

1. Install Django Channels:

    ```shell
    pip install django-channels
    ```

2. Install Daphne:

    ```shell
    pip install daphne
    ```
3. Add  ChatApp, daphne and channels to `installed_apps` in `settings.py` file: 
    ```python
    INSTALLED_APPS = [
        'daphne',
        'django.contrib.admin',
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.messages',
        'django.contrib.staticfiles',
        'ChatApp',
        'channels',
    ]
    ```
### 3. Create Important Files in the App Folder

1. Create `routing.py`.

2. Create `consumers.py`.

### 4. Creating Models

1. Create a model called `Room`:

    ```python
    class Room(models.Model):
        room_name = models.CharField(max_length=255)

        def __str(self):
            return self.room_name
    ```

2. Create another model called `Message`:

    ```python
    class Message(models.Model):
        room = models.ForeignKey(Room, on_delete=models.CASCADE)
        sender = models.CharField(max_length=255)
        message = models.TextField()

        def __str(self):
            return str(self.room)
    ```

3. Make migrations and migrate:

    ```shell
    python manage.py makemigrations
    python manage.py migrate
    ```

4. Register the models in the `admin.py` file:

    ```python
    from .models import *

    admin.site.register(Room)
    admin.site.register(Message)
    ```


# 5. Getting Template Files from GitHub

   - Download the following HTML templates from GitHub:
     - `index.html`
     - `message.html`



### 6. Create Views

   1. CreateRoom view:

        ```python
        def CreateRoom(request):
            return render(request, 'index.html')
        ```

   2. Message view:

        ```python
        def MessageView(request, room_name, username):
            return render(request, 'message.html')
        ```

### 7. Map Views to URLs:

```python
from . import views
from django.urls import path

urlpatterns = [
    path('', views.CreateRoom, name='create-room'),
    path('<str:room_name>/<str:username>/', views.MessageView, name='room'),
]
```

### 8. View CreateRoom view in browser to make sure setup works

### 9. Allow users to login or create chat rooms in CreateRoom view

In your `index.html` file, make sure to include a CSRF token in form:

```html
{% csrf_token %}
```

In your Django `CreateRoom` view, check for incoming POST requests:

```python
if request.method == 'POST':
```

Retrieve user-entered data:

```python
if request.method == 'POST':
    username = request.POST['username']
    room = request.POST['room']
```

Create try and except blocks to either get the room object or create it if it does not exist:

```python
try:
    get_room = Room.objects.get(room_name=room)
except Room.DoesNotExist:
    new_room = Room(room_name=room)
    new_room.save()
```

Test the code to see if it works.

Next, redirect users to `MessageView`:

```python
try:
    get_room = Room.objects.get(room_name=room)
    return redirect('room', room_name=room, username=username)
except Room.DoesNotExist:
    new_room = Room(room_name=room)
    new_room.save()
    return redirect('room', room_name=room, username=username)
```

### 10. Displaying Messages Created in a Room

1. Getting the room object and returning it as well as room name and username in the context

```python
def MessageView(request, room_name, username):
    get_room = Room.objects.get(room_name=room_name)
    get_messages = Message.objects.filter(room=get_room)
    
    context = {
        "messages": get_messages,
        "user": username,
        "room_name": room_name,
    }
    
    return render(request, 'message.html', context)
```

2. Display Messages from the Query Set in `message.html`:

```html
<div class="message" id="chatContainer">
    <!-- Received messages are displayed here -->
    {% for i in messages %}
        {% if i.sender != user %}
            <div class="receive">
                <p style="color: #000;"> {{i.message}}<strong>-{{i.sender}}</strong></p>
            </div>
        {% else %}
            <div class="send">
                <p style="color: #000;">{{i.message}}</p>
            </div>
        {% endif %}
    {% endfor %}
    <!-- End of received messages -->
</div>
```

This code is part of your `messages.html` file and is responsible for rendering the messages in the chat room. Messages are displayed differently based on whether the sender is the current user or another user.

### 11. Creating Consumers
Head over to your `consumers.py` file
1. Importing Modules:

```python
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from ChatApp.models import *
```
2. Creating `ChatConsumer`:

```python
class ChatConsumer(AsyncWebsocketConsumer):
```

3. Create `connect` Method:

```python
class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.room_name = f"room_{self.scope['url_route']['kwargs']['room_name']}"
        await self.channel_layer.group_add(self.room_name, self.channel_name)
        await self.accept()
```

4. Create `disconnect` Method:

```python
class ChatConsumer(AsyncWebsocketConsumer):
    
    async def connect(self):
        self.room_name = f"room_{self.scope['url_route']['kwargs']['room_name']}"
        await self.channel_layer.group_add(self.room_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_name, self.channel_name)
```

In this code section, you're creating a Django Channels consumer called `ChatConsumer`. It includes the `connect` method for WebSocket connection setup and the `disconnect` method for WebSocket disconnection handling. These consumers are essential for real-time communication in your Django application.

### 12. Creating URL for `ChatConsumer`

 Head to your `routing.py` File and Add the Following:

```python
from django.urls import path
from .consumers import ChatConsumer

websocket_urlpatterns = [
    path('ws/notification/<str:room_name>/', ChatConsumer.as_asgi()),
]
```

### 13.  Register routing url in `asgi.py` file in project
Head to your `asgi.py` file in project folder
1. Importing Modules:

```python
import os
from django.core.asgi import get_asgi_application

# imports
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
from ChatApp import routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'movie.settings')

application = get_asgi_application()
```

2. Rename `application` to `django_asgi_app`:

```python
django_asgi_app = get_asgi_application()
```

3. Add the Following:

```python
application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": URLRouter(
        routing.websocket_urlpatterns
    )
})
```

4. The Final Code:

```python
import os
from django.core.asgi import get_asgi_application

# imports
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
from ChatApp import routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'movie.settings')

django_asgi_app = get_asgi_application()

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": URLRouter(
        routing.websocket_urlpatterns
    )
})
```

### 14. Adding `asgi.py` Configurations and `channel_layers` to Settings
Head to `settings.py` file
1. Update `ASGI_APPLICATION` in your Settings:

```python
ASGI_APPLICATION = "ChatProject.asgi.application"
```

2. Add `channel_layers` Configuration:

```python
CHANNEL_LAYERS = {
    "default": {"BACKEND": "channels.layers.InMemoryChannelLayer"},
}
```

Here's the provided content in markdown format for your `readme.md` file:


### 15. Creating a New WebSocket

1. Head to `message.html` File and Create Script Tags:

```html
<script>

</script>
```

This step involves adding script tags to your `message.html` file to embed JavaScript code for handling WebSocket connections.

2. Create a New WebSocket:

```javascript
<script>
    const websocketProtocol = window.location.protocol === "https:" ? "wss" : "ws";
    const wsEndpoint = `${websocketProtocol}://${window.location.host}/ws/notification/{{room_name}}/`;
    const socket = new WebSocket(wsEndpoint);
</script>
```

In this part of the code, you're creating a new WebSocket connection in your `message.html` file. It determines the WebSocket protocol based on whether the application is served over HTTPS or HTTP and establishes a connection to the WebSocket endpoint for the specific chat room.

###  16. Creating Event Handlers for WebSocket Connection

Handling WebSocket Connection Events:

```javascript
<script>
    // Determine the WebSocket protocol based on the application's URL
    const websocketProtocol = window.location.protocol === "https:" ? "wss" : "ws";
    const wsEndpoint = `${websocketProtocol}://${window.location.host}/ws/notification/{{room_name}}/`;

    // Create a new WebSocket connection
    const socket = new WebSocket(wsEndpoint);

    // Successful connection event
    socket.onopen = (event) => {
        console.log("WebSocket connection opened!");
    };

    // Socket disconnect event
    socket.onclose = (event) => {
        console.log("WebSocket connection closed!");
    };
</script>
```

### 17. Creating an Event Listener for Sending Messages


```javascript
<script>
    // Determine the WebSocket protocol based on the application's URL
    const websocketProtocol = window.location.protocol === "https:" ? "wss" : "ws";
    const wsEndpoint = `${websocketProtocol}://${window.location.host}/ws/notification/{{room_name}}/`;

    // Create a new WebSocket connection
    const socket = new WebSocket(wsEndpoint);

    // Successful connection event
    socket.onopen = (event) => {
        console.log("WebSocket connection opened!");
    };

    // Socket disconnect event
    socket.onclose = (event) => {
        console.log("WebSocket connection closed!");
    };

    // Form submit listener
    document.getElementById('message-form').addEventListener('submit', function(event){
        event.preventDefault();
        const message = document.getElementById('msg').value;
        socket.send(
            JSON.stringify({
                'message': message,
                'room_name': '{{room_name}}',
                'sender': '{{user}}',
            })
        );
    });
</script>
```

###  18. Creating Methods in Consumers to Receive and Send New Messages

1. Creating a `ChatConsumer` with `receive` Method:

```python
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from ChatApp.models import *

class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.room_name = f"room_{self.scope['url_route']['kwargs']['room_name']}"
        await self.channel_layer.group_add(self.room_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_name, self.channel_name)

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json
```

2. Adding a `send_message` Method:

```python
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from ChatApp.models import *

class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.room_name = f"room_{self.scope['url_route']['kwargs']['room_name']}"
        await this.channel_layer.group_add(self.room_name, self.channel_name)
        await this.accept()

    async def disconnect(self, close_code):
        await this.channel_layer.group_discard(self.room_name, self.channel_name)

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json

    async def send_message(self, event):
        data = event['message']
        await self.create_message(data=data)
        response_data = {
            'sender': data['sender'],
            'message': data['message']
        }
        await self.send(text_data=json.dumps({'message': response_data}))
```

3. Creating the `create_message` Method to Create and Save Messages:

```python
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from ChatApp.models import *

class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.room_name = f"room_{self.scope['url_route']['kwargs']['room_name']}"
        await self.channel_layer.group_add(self.room_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_name, self.channel_name)

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json

    async def send_message(self, event):
        data = event['message']
        await self.create_message(data=data)
        response_data = {
            'sender': data['sender'],
            'message': data['message']
        }
        await self.send(text_data=json.dumps({'message': response_data}))

    @database_sync_to_async
    def create_message(self, data):
        get_room_by_name = Room.objects.get(room_name=data['room_name'])
        if not Message.objects.filter(message=data['message']).exists():
            new_message = Message(room=get_room_by_name, sender=data['sender'], message=data['message'])
            new_message.save()
```

In this code section, you're defining methods in your Django Channels `ChatConsumer` to receive, send, and create messages. These methods handle WebSocket communication and message storage in your Django application.

#### 19. Adding a Socket Event Listener for Server Responses:

```javascript
<script>
    // Determine the WebSocket protocol based on the application's URL
    const websocketProtocol = window.location.protocol === "https:" ? "wss" : "ws";
    const wsEndpoint = `${websocketProtocol}://${window.location.host}/ws/notification/{{room_name}}/`;

    // Create a new WebSocket connection
    const socket = new WebSocket(wsEndpoint);

    // Successful connection event
    socket.onopen = (event) => {
        console.log("WebSocket connection opened!");
    };

    // Socket disconnect event
    socket.onclose = (event) => {
        console.log("WebSocket connection closed!");
    };

    // Form submit listener
    document.getElementById('message-form').addEventListener('submit', function(event){
        event.preventDefault();
        const message = document.getElementById('msg').value;
        socket.send(
            JSON.stringify({
                'message': message,
                'room_name': '{{room_name}}',
                'sender': '{{user}}',
            })
        );
    });

    // Response from consumer on the server
    socket.addEventListener("message", (event) => {
        const messageData = JSON.parse(event.data)['message'];
        console.log(messageData);

        var sender = messageData['sender'];
        var message = messageData['message'];

        // Empty the message input field after the message has been sent
        if (sender == '{{user}}'){
            document.getElementById('msg').value = '';
        }

        // Append the message to the chatbox
        var messageDiv = document.querySelector('.message');
        if (sender != '{{user}}') { // Assuming you have a variable `currentUser` to hold the current user's name
            messageDiv.innerHTML += '<div class="receive"><p style="color: #000;">' + message + '<strong>-' + sender + '</strong></p></div>';
        } else {
            messageDiv.innerHTML += '<div class="send"><p style="color: #000;">' + message + '</p></div>';
        }
        scrollToBottom();
    });
</script>
```

2.  Adding a Function for Automatic Scrolling to the Bottom:

```javascript
<script>
    function scrollToBottom() {
        var chatContainer = document.getElementById("chatContainer");
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }
</script>
```

### 20. Testing the Code

In this section, you're creating a JavaScript event listener to handle responses from the server through the WebSocket connection. It updates the chat interface with incoming messages and automatically scrolls to the bottom to display the latest messages.