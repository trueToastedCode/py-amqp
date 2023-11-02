import aio_pika
import inspect
import json

from .amqp_callback import build_make_amqp_callback

make_amqp_callback = build_make_amqp_callback(aio_pika, inspect, json)
