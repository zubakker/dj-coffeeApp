import json
from channels.generic.websocket import AsyncWebsocketConsumer, WebsocketConsumer
from channels import auth
from . import models

class MyConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        
        await self.channel_layer.group_add('chat1', self.channel_name)
        await self.accept()
        # await auth.login(self.scope, models.CoffeeDrinker)
        print(self.scope['headers'])
        print(self.scope['user'])

    async def receive(self, text_data=None):
        await self.channel_layer.group_send(
            'chat1', {"type": "chat_message", "message": text_data*2}
        )

    async def chat_message(self, event):
        message = event["message"]

        await self.send(text_data=message)


    async def disconnect(self, close_code):
        await self.channel_layer.group_discard('chat1', self.channel_name)
        await self.close()
