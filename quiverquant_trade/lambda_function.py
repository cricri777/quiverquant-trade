import main


def lambda_handler(event, context):
    main.run(is_secret_manager=True)

    return {
        'statusCode': 200,
        'body': 'Run Complete'
    }