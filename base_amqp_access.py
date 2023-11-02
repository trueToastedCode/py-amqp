def build_make_amqp_access(asyncio, datetime, aio_pika, Id):
    async def make_amqp_access(loop, url, queue, default_timeout_ms=30000):
        futures = {}

        def on_response(message):
            future = futures.pop(message.correlation_id)
            future.set_result(message.body)

        connection = await aio_pika.connect(url, loop=loop)
        channel = await connection.channel()
        callback_queue = await channel.declare_queue(exclusive=True)
        await callback_queue.consume(on_response)

        async def send_rpc_message(message, timeout_ms=default_timeout_ms):
            correlation_id = Id.create_id()
            future = loop.create_future()
            futures[correlation_id] = future
            expiration_dt = None \
                if timeout_ms is None or timeout_ms <= 0 \
                else datetime.datetime.now() + datetime.timedelta(milliseconds=timeout_ms)
            await channel.default_exchange.publish(
                aio_pika.Message(
                    message.encode(),
                    content_type='text/plain',
                    correlation_id=correlation_id,
                    reply_to=callback_queue.name,
                    expiration=expiration_dt
                ),
                routing_key=queue
            )
            if expiration_dt is None:
                return await future
            return await asyncio.wait_for(
                future,
                timeout=(expiration_dt - datetime.datetime.now()).total_seconds()
            )

        async def close():
            await channel.close()
            await connection.close()

        return send_rpc_message, close

    return make_amqp_access
