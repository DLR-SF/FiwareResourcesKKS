from helper.ConfigParser import ConfigParser
from services.GroupTagsAndAssignMeaning import GroupTagsAndAssignMeaning
from services.CreateFiwareSDM import CreateFiwareSDM
from services.CreateFiwareAgentConfig import CreateFiwareAgentConfig


class Main:
    def __init__(self):
        # section name in config
        self.section_name = '0_general'

    def print_intro(self):
        print("")
        print("CREATE FIWARE DATAMODEL AND CONFIGURATION FROM GIVEN KKS ATTRIBUTE LIST")
        print("Start tool to:")
        print("1) group tags to entities and assign meaningful property names")
        print("2) create FIWARE smart data model from entities and properties")
        print("3) create FIWARE OPC UA IoT-Agent configuration")

    def start_tool(self):
        '''
        tool controller that executes the scripts
        :return:
        '''
        # Beginning
        self.print_intro()

        # 1) Parse config
        print("\n Read tool configuration...")
        configparser = ConfigParser("config.yaml")
        configparser.readConfig()
        language = configparser.returnElementValue(
            self.section_name, 'language')

        # Execute script 1
        print("\n**********************\n* 1) Execute Script 1 *\n**********************")
        if configparser.returnElementValue(self.section_name, 'execute_script_1') == "true":
            groupTagsAndAssignMeaning_service = GroupTagsAndAssignMeaning(
                configparser, language)
            groupTagsAndAssignMeaning_service.group_tags_and_assign_meaning()
            print("-> Success.")
        else:
            print("-> skip step 1 configured in configuration.")

        # Execute script 2
        print("\n**********************\n* 2) Execute Script 2 *\n**********************")
        if configparser.returnElementValue(self.section_name, 'execute_script_2') == "true":
            createFiwareSDM_service = CreateFiwareSDM(configparser)
            createFiwareSDM_service.create_fiware_sdm()
            print("-> Success.")
        else:
            print("-> skip step 2 configured in configuration.")

        # Execute script 3
        print("\n**********************\n* 3) Execute Script 3 *\n**********************")
        if configparser.returnElementValue(self.section_name, 'execute_script_3') == "true":
            createFiwareAgentConfig_service = CreateFiwareAgentConfig(
                configparser)
            createFiwareAgentConfig_service.create_fiware_agent_config()
            print("-> Success.")
        else:
            print("-> skip step 3 configured in configuration.")

        # End of script
        print("\n\nDone.")


if __name__ == "__main__":
    main = Main()
    main.start_tool()
