import asyncio
import logging
import json
import websockets
from typing import Any, Callable, Sequence

from .constants import ChannelType

WEBSOCKET_URL = "wss://www.avanza.se/_push/cometd"

logger = logging.getLogger("avanza_socket")


class AvanzaSocket:
    def __init__(self, push_subscription_id, cookies):
        self._socket = None
        self._client_id = None
        self._message_count = 1
        self._push_subscription_id = push_subscription_id
        self._connected = False
        self._subscriptions = {}
        self._cookies = cookies

    async def init(self):
        asyncio.ensure_future(self.__create_socket())
        await self.__wait_for_websocket_to_be_connected()

    async def __wait_for_websocket_to_be_connected(self):
        timeout_count = 40
        timeout_value = 0.250

        # Waits for a maximum of 10 seconds for the connection to be complete
        for _ in range(0, timeout_count):
            if self._connected:
                return
            await asyncio.sleep(timeout_value)

        raise TimeoutError(
            "\
            We weren't able to connect \
            to the websocket within the expected timeframe \
        "
        )

    async def __create_socket(self):
        async with websockets.connect(
            WEBSOCKET_URL, extra_headers={"Cookie": self._cookies}
        ) as self._socket:
            await self.__send_handshake_message()
            await self.__socket_message_handler()

    async def __send_handshake_message(self):
        await self.__send(
            {
                "advice": {"timeout": 60000, "interval": 0},
                "channel": "/meta/handshake",
                "ext": {"subscriptionId": self._push_subscription_id},
                "minimumVersion": "1.0",
                "supportedConnectionTypes": [
                    "websocket",
                    "long-polling",
                    "callback-polling",
                ],
                "version": "1.0",
            }
        )

    async def __send_connect_message(self):
        await self.__send(
            {
                "channel": "/meta/connect",
                "clientId": self._client_id,
                "connectionType": "websocket",
                "id": self._message_count,
            }
        )

    async def __socket_subscribe(
        self, subscription_string, callback: Callable[[str, dict], Any]
    ):
        self._subscriptions[subscription_string] = {"callback": callback}

        await self.__send(
            {
                "channel": "/meta/subscribe",
                "clientId": self._client_id,
                "subscription": subscription_string,
            }
        )

    async def __send(self, message):
        wrapped_message = [{**message, "id": str(self._message_count)}]

        logger.info(f"Outgoing message: {wrapped_message}")

        await self._socket.send(json.dumps(wrapped_message))

        self._message_count = self._message_count + 1

    async def __handshake(self, message: dict):
        if message.get("successful", False):
            self._client_id = message.get("clientId")
            await self.__send(
                {
                    "advice": {"timeout": 0},
                    "channel": "/meta/connect",
                    "clientId": self._client_id,
                    "connectionType": "websocket",
                }
            )
            return

        advice = message.get("advice")
        if advice and advice.get("reconnect") == "handshake":
            await self.__send_handshake_message()

    async def __connect(self, message: dict):
        successful = message.get("successful", False)
        advice = message.get("advice", {})
        reconnect = advice.get("reconnect") == "retry"
        interval = advice.get("interval")

        connect_successful = successful and (
            not advice or (reconnect and interval >= 0)
        )

        if connect_successful:
            await self.__send(
                {
                    "channel": "/meta/connect",
                    "clientId": self._client_id,
                    "connectionType": "websocket",
                }
            )

            if not self._connected:
                self._connected = True
                await self.__resubscribe_existing_subscriptions()

        elif self._client_id:
            await self.__send_connect_message()

    async def __resubscribe_existing_subscriptions(self):
        for key, value in self._subscriptions.items():
            if value.get("client_id") != self._client_id:
                await self.__socket_subscribe(key, value["callback"])

    async def __disconnect(self, message):
        await self.__send_handshake_message()

    async def __register_subscription(self, message):
        subscription = message.get("subscription")
        if subscription is None:
            raise ValueError("No subscription channel found on subscription message")

        self._subscriptions[subscription]["client_id"] = self._client_id

    async def __socket_message_handler(self):
        message_action = {
            "/meta/disconnect": self.__disconnect,
            "/meta/handshake": self.__handshake,
            "/meta/connect": self.__connect,
            "/meta/subscribe": self.__register_subscription,
        }

        async for message in self._socket:
            message = json.loads(message)[0]
            message_channel = message.get("channel")
            error = message.get("error")

            logger.info(f"Incoming message: {message}")

            if error:
                logger.error(error)

            action = message_action.get(message_channel)
            # Use user subscribed action
            if action is None:
                callback = self._subscriptions[message_channel]["callback"]
                callback(message)
            else:
                await action(message)

    async def subscribe_to_id(
        self, channel: ChannelType, id: str, callback: Callable[[str, dict], Any]
    ):
        return await self.subscribe_to_ids(channel, [id], callback)

    async def subscribe_to_ids(
        self,
        channel: ChannelType,
        ids: Sequence[str],
        callback: Callable[[str, dict], Any],
    ):
        valid_channels_for_multiple_ids = [
            ChannelType.ORDERS,
            ChannelType.DEALS,
            ChannelType.POSITIONS,
        ]

        if len(ids) > 1 and channel not in valid_channels_for_multiple_ids:
            raise ValueError(
                f"Multiple ids is not supported for channels other than {valid_channels_for_multiple_ids}"
            )

        subscription_string = f'/{channel.value}/{",".join(ids)}'
        await self.__socket_subscribe(subscription_string, callback)
