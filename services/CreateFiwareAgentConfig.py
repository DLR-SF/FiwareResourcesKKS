import re
import sys
import pandas
from helper.FileHelper import FileHelper


class CreateFiwareAgentConfig():
    '''
    Class to generate FIWARE IoT-Agent
    configuration
    '''

    def __init__(self, configparser):
        # section name in config
        self.section_name_1 = '1_group_tags_and_assign_meaning'
        self.section_name = '3_create_fiware_iotagent_configuration'

        # config parser
        self.configparser = configparser

        # file handler
        self.filehelper = FileHelper()

        # collection of all entities
        self.all_entities = []
        # collection of non-kks entities
        self.non_kks_entities = []
        # collection of duplicate entitty attributes
        self.duplicate_entitiy_attributes = []

        # mandatory columns
        self.opc_ua_ns = self.configparser.returnElementValue(
            self.section_name, 'opc_ua_namespace')
        self.column_name = self.configparser.returnElementValue(
            self.section_name_1, 'input_column_attribute_name')
        self.column_type = self.configparser.returnElementValue(
            self.section_name_1, 'input_column_attribute_type')
        self.column_kks_1_nr = self.configparser.returnElementValue(
            self.section_name_1, 'output_column_attribute_kks_1_nr')
        self.column_entity = self.configparser.returnElementValue(
            self.section_name_1, 'output_column_attribute_entity')
        self.column_type_map1 = self.configparser.returnElementValue(
            self.section_name_1, 'output_column_attribute_type_1')
        self.column_type_map2 = self.configparser.returnElementValue(
            self.section_name_1, 'output_column_attribute_type_2')

    def clean_name(self, name):
        '''
        Clean entity names so that these are written
        in camel case as entity names
        :param name:
        :return:
        '''
        # remove all special chars besides letters, numbers or whitespace
        if name and isinstance(name, str):
            # remove special chars
            name_without_special_chars = re.sub(
                '[^a-zA-ZÜÖÄäöü0-9 ]', '', name)
            # replace ö, ä, ... with oe, ae, ...
            name_without_umlaute = name_without_special_chars.replace(
                "ä", "ae").replace("Ä", "Äe").replace("ö", "oe").replace(
                "Ö", "oe").replace("ü", "ue").replace("Ü", "ue")
            # split word by whitespace
            new_name_parts = name_without_umlaute.split(" ")
            new_name = ""
            for i in range(1, len(new_name_parts)+1):
                first_letter = new_name_parts[i-1][:1]
                other_letters = new_name_parts[i-1][1:]
                new_name += "{}{}".format(first_letter.upper(), other_letters)
        else:
            print("\n\nError: Name is empty \
                  or not of type String: '{}'".format(name))
            sys.exit(1)

        return new_name

    def check_if_last_element(self, df, entity, index):
        '''
        Check if the last property of the entity in the sorted dataframe
        Return True is it is the last and False if it is not the last element
        :param entity:
        :param index:
        :return:
        '''
        try:
            # there is another property if the next row has the same entity
            return 0 if df.iloc[index + 1][self.column_entity] == entity else 1
        except IndexError:
            # last element as there is no next element
            return None

    def create_context_section(self, filehandler_output, df, section_name):
        '''
        Create config section context / contextSubscriptions from input file
        Format:
        contexts: [
            {
                id: '<Entity-ID>',
                type: '<Entity-Type>',
                mappings: [
                    {
                        ocb_id: '<Attribute-Name>',
                        opcua_id: 'ns=<OPC Namespace>;s=<Attribute-OPC-Tag>',
                        object_id: 'ns=<OPC Namespace>;s=<Attribute-OPC-Tag>',
                        inputArguments: []
                    },
                    {
                        ocb_id: '<Attribute-Name2>',
                        opcua_id: 'ns=<OPC Namespace>;s=<Attribute-OPC-Tag2>',
                        object_id: 'ns=<OPC Namespace>;s=<Attribute-OPC-Tag2>',
                        inputArguments: []
                    },
                    ...
                ]
            }
        ],

        :param filehandler_output:
        :param df:
        :return:
        '''

        entitiy_attributes = []
        all_entities = []
        entity_counter = 0
        filehandler_output.write("    {}: [\n".format(section_name))
        for index, row in df.iterrows():
            if row[self.column_entity] and isinstance(
                    row[self.column_entity], str):

                # Case 1: Valid KKS name
                # clean name for entity
                cleaned_entity_name = self.clean_name(row[self.column_entity])

                # Check if new entity
                if cleaned_entity_name in all_entities:
                    # Duplicate attribute name
                    if row[self.column_name] in entitiy_attributes:
                        # duplicate
                        self.duplicate_entitiy_attributes.append(
                            row[self.column_name])
                    else:
                        # add new attribute to entity property list
                        last_element_property = self.check_if_last_element(
                            df, row[self.column_entity], index)
                        self.level_3_context_append_property(
                            filehandler_output, row[self.column_name],
                            last_element_property)
                        entitiy_attributes.append(row[self.column_name])
                        print("-> Property: {}".format(row[self.column_name]))

                else:
                    # create new entity
                    entity_counter = entity_counter + 1
                    print("\n New entitiy: {}".format(cleaned_entity_name))
                    entitiy_attributes = []
                    all_entities.append(cleaned_entity_name)

                    # -> create level 2 entity id, type and mapping start
                    entity_id = "urn:ngsi-ld:PCS-STJ:{}:{}".format(
                        cleaned_entity_name, row[self.column_kks_1_nr])
                    filehandler_output.write("        {\n")
                    filehandler_output.write(
                        '            id: "{}",\n'.format(entity_id))
                    filehandler_output.write(
                        '            type: "{}",\n'.format(cleaned_entity_name))
                    filehandler_output.write('            mappings: [\n')

                    # -> create level 3 mappings (property)
                    last_element_property = self.check_if_last_element(
                        df, row[self.column_entity], index)
                    self.level_3_context_append_property(
                        filehandler_output, row[self.column_name],
                        last_element_property)

                    entitiy_attributes.append(row[self.column_name])
                    print("-> Property: {}".format(row[self.column_name]))
            else:
                # Case 2: No a valid KKS name
                print("\nError: Element {} has no valid KKS name!".format(
                    row[self.column_name]))
                self.non_kks_entities.append(row[self.column_name])

    def transform_opc_da_to_ua_name(self, name):
        '''
        Transform original name to actual name used
        Reformat special characters
        :param name:
        :return:
        '''
        cleaned_name = name.replace("/", "//")
        return cleaned_name

    def level_3_context_append_property(self, filehandler_output, name, last_entity_property):
        '''
        Create new property for context section type
        :param name:
        :param last_entity_property:
        :return:
        '''
        # transform name
        opcua_name = self.transform_opc_da_to_ua_name(name)

        filehandler_output.write("                {\n")
        filehandler_output.write(
            '                    ocb_id: "{}",\n'.format(name))
        filehandler_output.write('                    opcua_id: "ns={};s={}",\n'.format(
            self.opc_ua_ns, opcua_name))
        filehandler_output.write('                    object_id: "ns={};s={}",\n'.format(
            self.opc_ua_ns, opcua_name))
        filehandler_output.write("                    inputArguments: []\n")
        filehandler_output.write("                }")

        if last_entity_property == 0:
            # if there is another property add comma
            filehandler_output.write(",\n")
        else:
            # there is no other property so no comma
            filehandler_output.write("\n")
            filehandler_output.write("            ]\n")
            filehandler_output.write("        }")

            if last_entity_property is None:
                filehandler_output.write("\n")
                filehandler_output.write("    ],\n")
            else:
                # Not last element
                filehandler_output.write(",\n")

    def create_types_section(self, filehandler_output, df):
        '''
        Create config section types from input file
        Format:
            types: {
              EntityType1: {
                active: [
                    {
                        name: 'PropertyName1',
                        type: 'Number'
                    },
                    {
                        name: 'PropertyName2',
                        type: 'Number'
                    },
                    ...
                ],
                lazy: [],
                commands: []
            },

        :param filehandler_output:
        :param df:
        :return:
        '''
        entitiy_attributes = []
        entity_counter = 0
        filehandler_output.write("    types: {\n")
        for index, row in df.iterrows():
            if row[self.column_entity] and isinstance(row[self.column_entity], str):
                # Case 1: Valid KKS name
                # clean name for entity
                cleaned_entity_name = self.clean_name(row[self.column_entity])

                # Check if new entity
                if cleaned_entity_name in self.all_entities:
                    # Duplicate attribute name (normally because of missing suffix from text export error)
                    if row[self.column_name] in entitiy_attributes:
                        # duplicate
                        print(
                            "-> DUPLICATE PROPERTY: {}".format(row[self.column_name]))
                        self.duplicate_entitiy_attributes.append(
                            row[self.column_name])
                    else:
                        # add new attribute to entity property list
                        last_element = self.check_if_last_element(
                            df, row[self.column_entity], index)
                        self.level_4_types_append_property(
                            filehandler_output, row[self.column_type_map2], row[self.column_name], last_element)
                        entitiy_attributes.append(row[self.column_name])

                else:
                    # create new entity
                    entity_counter = entity_counter + 1
                    print("\n New entitiy: {}".format(cleaned_entity_name))
                    entitiy_attributes = []
                    self.all_entities.append(cleaned_entity_name)

                    # -> create level 2 entity name
                    filehandler_output.write(
                        "        {}: {{\n".format(cleaned_entity_name))
                    # -> start active block
                    filehandler_output.write("            active: [\n")

                    # -> create first property
                    last_element = self.check_if_last_element(
                        df, row[self.column_entity], index)
                    self.level_4_types_append_property(
                        filehandler_output, row[self.column_type_map2], row[self.column_name], last_element)

                    entitiy_attributes.append(row[self.column_name])
            else:
                # Case 2: No a valid KKS name
                print("\nError: Element {} has no valid KKS name!".format(
                    row[self.column_name]))
                self.non_kks_entities.append(row[self.column_name])

        # close types section
        filehandler_output.write("    },")

    def level_4_types_append_property(self, filehandler_output, fiware_type, name, last_entity_property):
        '''
        append an element to the types property section at fourth level
        of nested types-json-object
        :param datatype:
        :param name:
        :param last_entity_property:
        :return:
        '''
        filehandler_output.write("                {\n")
        filehandler_output.write(
            '                    name: "{}",\n'.format(name))
        filehandler_output.write(
            '                    type: "{}"\n'.format(fiware_type))
        filehandler_output.write("                }")
        print("-> Property: {}".format(name))

        # add comma if the property is not the last of the entity
        if last_entity_property == 0:
            filehandler_output.write(",\n")
        elif last_entity_property == 1 or last_entity_property is None:
            # close entity section
            filehandler_output.write("\n            ],\n")
            filehandler_output.write("            lazy: [],\n")
            filehandler_output.write("            commands: []\n")
            filehandler_output.write("        }")

            # add comma behind entity if another entity will follow
            if last_entity_property is not None:
                filehandler_output.write(",\n")
            else:
                # No additional comma for last element
                filehandler_output.write("\n")

    def create_fiware_agent_config(self):
        '''
        Controller for resource creation
        '''
        # DEFINE VARIABLES
        # File to parse
        filepath_input = self.configparser.returnElementValue(
            self.section_name, 'filepath_input')
        # File to export
        filepath_output_types = self.configparser.returnElementValue(
            self.section_name, 'filepath_output_types')
        filepath_output_context = self.configparser.returnElementValue(
            self.section_name, 'filepath_output_context')

        # 1) Check if file exists and empty it if if contains content
        print("\na) Check if input file exist and clear old content")
        self.filehelper.check_file_exists(filepath_input)
        filehandler_output_types = open(filepath_output_types, "a")
        filehandler_output_types.truncate(0)
        filehandler_output_context = open(filepath_output_context, "a")
        filehandler_output_context.truncate(0)

        # 2) Read as dataframe and sort by entity
        print("\nc) Read as dataframe and sort by entity")
        df = pandas.read_excel(filepath_input)
        # todo somehow the last value is not sorted ...
        # actual workaround: Sort by excel
        # Even the hex values of the strings are the same -> Excel can sort them correctly (pandas bug?)
        # -> LAST:                  53:74:72:61:68:6c:75:6e:67:73:6d:65:73:73:73:79:73:74:65:6d
        # -> OTHER WITH SAME VALUE: 53:74:72:61:68:6c:75:6e:67:73:6d:65:73:73:73:79:73:74:65:6d
        df.sort_values(by=self.column_entity)

        # 3) Start to create output file
        print("\nc) Start to create output file")
        # -> create types
        filehandler_output_types.write("\n#################\n")
        filehandler_output_types.write("# TYPES SECTION #")
        print("\n# TYPES SECTION #")
        filehandler_output_types.write("\n#################\n")
        self.create_types_section(filehandler_output_types, df)
        # -> create context
        filehandler_output_context.write("\n\n\n###################\n")
        filehandler_output_context.write("# CONTEXT SECTION #")
        print("\n\n# CONTEXT SECTION #")
        filehandler_output_context.write("\n###################\n")
        self.create_context_section(filehandler_output_context, df, "contexts")
        # -> create contextSubscriptions
        # todo

        # print results
        print("\n\nCreated {} entities.".format(len(self.all_entities)))

        print("\nLeft out {} not valid attributes".format(
            len(self.non_kks_entities)))
        print("These are: {}".format(self.non_kks_entities))
        print("PLEASE CORRECT THEM MANUALLY!")

        print("\nFound {} duplicate attributes of an entity".format(len(self.duplicate_entitiy_attributes)))
        print("These are: {}".format(self.duplicate_entitiy_attributes))
        print("PLEASE CORRECT THEM MANUALLY!")
