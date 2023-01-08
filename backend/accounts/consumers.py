import time
import json
from django.http import HttpResponse
from django.shortcuts import render
from channels.generic.websocket import AsyncWebsocketConsumer, WebsocketConsumer
from asgiref.sync import async_to_sync

# Django Channels consumer that listens for websocket connections and process start events
class ProgressConsumers(AsyncWebsocketConsumer):
    async def connect(self):
        # Accept the websocket connection
        await self.accept()
    
    async def disconnect(self, close_code):
        # Close the websocket connection
        await self.close()
    
    async def receive(self, text_data):
        # Parse the incoming message
        data = json.loads(text_data)
        if data['type'] == 'start':
            # Start the process and send progress update events over the websocket connection
            await self.send_progress_updates()
    
    async def send_progress_updates(self):
        for i in range(100):
            # Do some work
            time.sleep(0.1)
            # Send progress update over websocket connection
            await self.send(text_data=json.dumps({
                'type': 'update',
                'progress': i
            }))
        # Send completion event over websocket connection
        await self.send(text_data=json.dumps({
            'type': 'complete'
        }))


class ProgressConsumer(WebsocketConsumer):
    def connect(self):
        self.accept()

    def disconnect(self, close_code):
        pass

    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]

        self.send(text_data=json.dumps({"message": message}))
    
    def send(self, text_data):
        async_to_sync(self.channel_layer.group_send)(
            "progress",
            {
                "type": "progress.update",
                "text": text_data,
            },
        )




