from helper import config, statuses

def get_enabled_services():
    return config['options']['services'].keys()

#ugly
def get_status_name(code):
    for key, val in statuses.items():
        if code == val:
            return key

def init_counter():
    res = {}
    for k in config['resources'].keys():
        res[k] = []
    return res

t = init_counter()

