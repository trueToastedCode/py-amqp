def build_make_amqp_callback(aio_pika, inspect, json):
    def make_amqp_callback(controllers):
        async def amqp_callback(exchange, rabbit_message):
            async with rabbit_message.process():
                result = None
                try:
                    # parse controller and args from message
                    message = rabbit_message.body.decode()
                    i = message.find('{')
                    function_name = message if i == -1 else message[:i]
                    # get controller
                    try:
                        if isinstance(controllers, list):
                            chosen = next(f for f in controllers if f.__name__ == function_name)
                        else:
                            chosen = controllers[function_name]
                        # parse arguments
                        try:
                            params = {} if i == -1 else json.loads(message[i:])
                            # call controller
                            try:
                                result = await chosen(**params) \
                                    if inspect.iscoroutinefunction(chosen) \
                                    else chosen(**params)
                            except:
                                # controller failed
                                result = {
                                    'statusCode': 500,
                                    'body': {'error': 'An unknown error occurred'}
                                }
                        except json.decoder.JSONDecodeError:
                            # failed to parse arguments
                            result = {
                                'statusCode': 400,
                                'body': {'error': 'Invalid controller parameters'}
                            }
                    except (StopIteration, KeyError):
                        # controller doesn't exist
                        result = {
                            'statusCode': 400,
                            'body': {'error': f'Invalid controller function: {function_name}'}
                        }
                except:
                    result = {
                        'statusCode': 400,
                        'body': {'error': 'Invalid message'}
                    }
                # send result
                await exchange.publish(
                    aio_pika.Message(
                        body=json.dumps(result).encode(),
                        correlation_id=rabbit_message.correlation_id
                    ),
                    routing_key=rabbit_message.reply_to
                )

        return amqp_callback

    return make_amqp_callback
