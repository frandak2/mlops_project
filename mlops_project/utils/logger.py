def get_logging_config(transaction_id):
    """create the log

    Args:
        transaction_id (_type_): _description_

    Returns:
        _type_: _description_
    """
    logging_config = {
        'version': 1,
        'disable_existing_loggers': True,
        'formatters': {
            'standard': {
                "datefmt": '%Y-%m-%d %H:%M:%S %p',
                'format': f'%(asctime)s | %(levelname)s | SWORD | %(module)s >> {transaction_id} | %(message)s'
            },
        },
        'handlers': {
            'default': {
                'formatter': 'standard',
                'class': 'logging.StreamHandler',
            },
        },
        'loggers': {
            '': {
                'handlers': ['default'],
                'level': 'INFO',
                'propagate': False
            }
        }
    }
    return logging_config