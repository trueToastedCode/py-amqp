def make_listen_react_amqp(logging, aio_pika, functools, make_amqp_callback):
    async def listen_react_amqp(loop, url, queue, controllers, healthy_callback=None):
        logging.info('Connecting server...')

        connection = await aio_pika.connect(url, loop=loop)
        channel = await connection.channel()
        queue = await channel.declare_queue(queue)

        amqp_callback = make_amqp_callback(controllers)

        if healthy_callback:
            healthy_callback()

        logging.info(f'Server is listening on queue {queue}')

        await queue.consume(
            functools.partial(
                amqp_callback,
                channel.default_exchange
            )
        )

    return listen_react_amqp
