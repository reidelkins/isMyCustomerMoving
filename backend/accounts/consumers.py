# import time
# import json
# from django.http import HttpResponse
# from django.shortcuts import render
# from channels.generic.websocket import AsyncWebsocketConsumer, WebsocketConsumer
# from asgiref.sync import async_to_sync

# # Django Channels consumer that listens for websocket connections and process start events
# class ProgressConsumers(AsyncWebsocketConsumer):
#     async def connect(self):
#         # Accept the websocket connection
#         await self.accept()
    
#     async def disconnect(self, close_code):
#         # Close the websocket connection
#         await self.close()
    
#     async def receive(self, text_data):
#         # Parse the incoming message
#         data = json.loads(text_data)
#         if data['type'] == 'start':
#             # Start the process and send progress update events over the websocket connection
#             await self.send_progress_updates()
    
#     async def send_progress_updates(self):
#         for i in range(100):
#             # Do some work
#             time.sleep(0.1)
#             # Send progress update over websocket connection
#             await self.send(text_data=json.dumps({
#                 'type': 'update',
#                 'progress': i
#             }))
#         # Send completion event over websocket connection
#         await self.send(text_data=json.dumps({
#             'type': 'complete'
#         }))


# class ProgressConsumer(WebsocketConsumer):
#     def connect(self):
#         self.accept()

#     def disconnect(self, close_code):
#         pass

#     def receive(self, text_data):
#         text_data_json = json.loads(text_data)
#         message = text_data_json["message"]

#         self.send(text_data=json.dumps({"message": message}))
    
#     def send(self, text_data):
#         async_to_sync(self.channel_layer.group_send)(
#             "progress",
#             {
#                 "type": "progress.update",
#                 "text": text_data,
#             },
#         )


from channels.generic.websocket import JsonWebsocketConsumer


class ChatConsumer(JsonWebsocketConsumer):
    """
    This consumer is used to show user's online status,
    and send notifications.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.room_name = None

    def connect(self):
        print("Connected!")
        self.room_name = "home"
        self.accept()
        self.send_json(
            {
                "type": "welcome_message",
                "message": "Hey there! You've successfully connected!",
            }
        )

    def disconnect(self, code):
        print("Disconnected!")
        return super().disconnect(code)

    def receive(self, text_data=None, bytes_data=None):
        print("Received!")
        return super().receive(text_data, bytes_data)
    
    def send(self, text_data=None, bytes_data=None, close=False):
        print("Sent!")
        return super().send(text_data, bytes_data, close)

    def receive_json(self, content, **kwargs):
        print(content)
        return super().receive_json(content, **kwargs)



