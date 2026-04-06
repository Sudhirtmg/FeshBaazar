from channels.generic.websocket import AsyncWebsocketConsumer
import json

class OrderConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        print("🟢 WS CONNECT ATTEMPT") 
        self.group_name = "orders"

        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

        await self.accept()
        print("✅ WS CONNECTED")

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def send_order_update(self, event):
        await self.send(text_data=json.dumps(event["data"]))
        


class LedgerConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.group_name = "ledger"

        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

        await self.accept()
        print("✅ Ledger WS Connected")

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def send_ledger_update(self, event):
        await self.send(text_data=json.dumps(event["data"]))