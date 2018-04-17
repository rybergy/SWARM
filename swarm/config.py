"""
simple configuration loader including default values.
"""
import yaml

default = {
    'xbee': {
        'port': '/dev/ttyUSB0', 'baud': 57600, 'addresses': []
    },
    'arduino': {
        'port': '/dev/ttyUSB0', 'baud': 115200
    }
}


def load(location='config.yml'):
    config = default.copy()  # copy default so it doesn't get changed

    # attempt to load config file
    try:
        with open(location, mode='r') as c:
            config.update(yaml.load(c, Loader=yaml.Loader))
    except FileNotFoundError:
        print('{} not found, created using default values.'.format(location))

    # update file in case new defaults were added
    with open(location, mode='w') as c:
        yaml.dump(config, c)

    return config
