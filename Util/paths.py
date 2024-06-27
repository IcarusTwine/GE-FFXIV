import configparser

config = {
    'init': None
}

def get_ffxiv_path():
    global config
    if config['init'] is None:
        config_parser = configparser.ConfigParser()
        config_parser.read('./config.ini')
        if 'Paths' in config_parser and 'ffxiv_path' in config_parser['Paths']:
            ffxiv_path = config_parser['Paths']['ffxiv_path'].strip('"')  # Remove any surrounding quotes
            config['init'] = True
            config['ffxiv_path'] = ffxiv_path
            return ffxiv_path
        else:
            raise KeyError("The key 'ffxiv_path' is missing in the 'Paths' section of the config.ini file.")
    else:
        return config['ffxiv_path']
