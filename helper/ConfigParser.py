import yaml


class ConfigParser(object):
    '''
    Configuration Handling
    '''

    def __init__(self, path_to_config):
        # path to config
        self.config_path = path_to_config

        # parsed configuration
        self.data = []

    def readConfig(self):
        '''
        Read configuration and parse it into dictionary
        :return:
        '''
        with open(self.config_path, "r") as stream:
            self.data = yaml.safe_load(stream)

    def returnElementValue(self, section, element):
        '''
        return configuration value based on configuration
        section and element
        :param section:
        :param element:
        :return:
        '''
        return self.data[section][element]
