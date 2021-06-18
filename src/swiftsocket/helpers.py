import yaml



typing_map = {
    'integer': int,
    'float': float,
    'string': str,
    'list': list,
    'dict': dict,
    'boolean': bool,
}

def read_config(config):
    settings = {}

    # general must-have settings
    settings['host'] = str(config['host'])
    settings['port'] = str(config['port'])

    # defined requests
    settings['requests'] = []
    if 'requests' in config:
        for request in config['requests']:

            # ensure command is a string
            cmd = str(request['command'])

            # collect the data definitions
            data = {}
            if 'data' in request:
                for key, typing in request['data'].items():
                    if typing not in typing_map:
                        raise TypeError(f"Unknown type definition in config: '{typing}'. Allowed are {typing_map.keys()}.")
                    else:
                        data[key] = typing_map[typing]

            # collect the enabled response definitons
            responses = []
            if 'responses' in request:
                responses = [str(r) for r in request['responses']]

            # save the compiled request            
            settings['requests'].append({'command': cmd, 'data': data, 'responses': responses})

    # defined responses
    settings['responses'] = []
    if 'responses' in config:
        for response in config['responses']:

            # ensure command is a string
            cmd = str(response['command'])

            # collect the data definitions
            data = {}
            if 'data' in response:
                for key, typing in response['data'].items():
                    if typing not in typing_map:
                        raise TypeError(f"Unknown type definition in config: '{typing}'. Allowed are {typing_map.keys()}.")
                    else:
                        data[key] = typing_map[typing]

            # collect the enabled response definitons
            requests = []
            if 'requests' in response:
                requests = [str(r) for r in response['requests']]

            # save the compiled request            
            settings['responses'].append({'command': cmd, 'data': data, 'requests': requests})
    
    # return the completely compiled settings dict
    return settings



def read_yaml_config(filepath):
    with open(filepath, 'r') as stream:
        config = yaml.safe_load(stream)
        return read_config(config)

