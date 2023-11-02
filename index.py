import asyncio
import aio_pika
import datetime
from Id.index import Id

from .base_amqp_access import build_make_amqp_access

make_amqp_access = build_make_amqp_access(asyncio, datetime, aio_pika, Id)
