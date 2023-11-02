import logging
import aio_pika
import functools

from amqp_callback.index import make_amqp_callback

from .listen_react_amqp import make_listen_react_amqp

listen_react_amqp = make_listen_react_amqp(logging, aio_pika, functools, make_amqp_callback)
