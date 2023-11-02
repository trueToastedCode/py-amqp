def build_make_amqp_access(aio_pika, Id):
    async def make_amqp_access(loop, url, queue):
        futures = {}

        def on_response(message):
            future = futures.pop(message.correlation_id)
            future.set_result(message.body)

        connection = await aio_pika.connect(url, loop=loop)
        channel = await connection.channel()
        callback_queue = await channel.declare_queue(exclusive=True)
        await callback_queue.consume(on_response)

        async def send_rpc_message(message):
            correlation_id = Id.createId()
            future = loop.create_future()
            futures[correlation_id] = future
            await channel.default_exchange.publish(
                aio_pika.Message(
                    message.encode(),
                    content_type='text/plain',
                    correlation_id=correlation_id,
                    reply_to=callback_queue.name,
                ),
                routing_key=queue
            )
            return await future

        async def close():
            await connection.close()

        return send_rpc_message, close

    return make_amqp_access
