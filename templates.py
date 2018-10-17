import constants
import utilities as utils


def get_json_template():
    return {
        'source': None,
        'sourceUrl': None,
        'sourceStatus': constants.STATUS_GOOD,
        'timestamp': utils.get_timestamp(),
        'hostname': utils.get_hostname(),
        'services': []
    }
