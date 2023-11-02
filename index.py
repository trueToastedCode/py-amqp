import aio_pika
from ..id import Id

from base_amqp_access import build_make_amqp_access

make_amqp_access = build_make_amqp_access(aio_pika, Id)
