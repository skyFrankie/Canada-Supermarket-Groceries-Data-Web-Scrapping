mapping = {
    'HMart': {
        'params': {
            'environment': [
                {
                    'name': 'STORE',
                    'value': 'HMart'
                },
                {
                    'name': 'EVENT_NUM'
                },
            ]
        }
        ,
        'loop_info': [1, 2, 3] + list(range(5, 14))
    },
    'Loblaws': {
        'params': {
            'environment': [
                {
                    'name': 'STORE',
                    'value': 'Loblaws'
                },
                {
                    'name': 'EVENT_NUM'
                },
            ]
        },
        'loop_info': list(range(2, 16))
    },
    'Metro': {
        'params': {
            'environment': [
                {
                    'name': 'STORE',
                    'value': 'Metro'
                },
                {
                    'name': 'EVENT_NUM'
                },
            ]
        },
        'loop_info': list(range(16))
    }
}
