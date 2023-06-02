import re
import sys
import pandas
from helper.FileHelper import FileHelper


class CreateFiwareSDM():
    '''
    Class to generate FIWARE Smart Data Model from
    output of script 1
    '''

    def __init__(self, configparser):
        # section name in config
        self.section_name_2 = '2_create_fiware_smart_data_model'

        # section name section before
        self.section_name_1 = '1_group_tags_and_assign_meaning'

        # config parser
        self.configparser = configparser

        # file handler
        self.filehelper = FileHelper()

        # mandatory columns
        self.column_name = self.configparser.returnElementValue(self.section_name_1,
                                                                'input_column_attribute_name')
        self.column_type = self.configparser.returnElementValue(self.section_name_1,
                                                                'input_column_attribute_type')
        self.column_kks_0 = self.configparser.returnElementValue(self.section_name_1,
                                                                 'output_column_attribute_kks_0')
        self.column_kks_1 = self.configparser.returnElementValue(self.section_name_1,
                                                                 'output_column_attribute_kks_1')
        self.column_kks_1_nr = self.configparser.returnElementValue(self.section_name_1,
                                                                    'output_column_attribute_kks_1_nr')
        self.column_kks_2 = self.configparser.returnElementValue(self.section_name_1,
                                                                 'output_column_attribute_kks_2')
        self.column_kks_2_nr = self.configparser.returnElementValue(self.section_name_1,
                                                                    'output_column_attribute_kks_2_nr')
        self.column_kks_3 = self.configparser.returnElementValue(self.section_name_1,
                                                                 'output_column_attribute_kks_3')
        self.column_ending = self.configparser.returnElementValue(self.section_name_1,
                                                                  'output_column_attribute_ending')
        self.column_entity = self.configparser.returnElementValue(self.section_name_1,
                                                                  'output_column_attribute_entity')
        self.column_entity_other_lang = self.configparser.returnElementValue(
            self.section_name_1, 'output_column_attribute_entity_other_lang')
        self.column_meaning = self.configparser.returnElementValue(self.section_name_1,
                                                                   'output_column_attribute_meaning')

    def create_comment_header(self, filehandler_output, entity):
        '''
        Create initial comment to structure model document
        :param filehandler_output:
        :param entity:
        :return:
        '''
        # -> create comment header
        comment_header = "    "
        for i in range(1, len(str(entity)) + 7):
            comment_header += "#"
        comment_header += "\n"

        # write to file
        filehandler_output.write("\n")
        filehandler_output.write(comment_header)
        filehandler_output.write("    ## {} ##\n".format(entity))
        filehandler_output.write(comment_header)

    def create_entity_handler(self, filehandler_output, cleaned_entity_name, entity_name, entity_name_ol, function):
        '''
        create a new entity for data model
        :param filehandler_output:
        :param entity_name:
        :param function:
        :return:
        '''
        # beginning of entity
        filehandler_output.write("    {}:\n".format(cleaned_entity_name))

        # create description based on configuration
        entitiy_description = self.configparser.returnElementValue(
            self.section_name_2, 'entitiy_description')
        description = entitiy_description.replace("ENTITY_NAME", self.remove_umlauts_and_spaces(entity_name)).replace(
            "FUNCTION_CODE", function).replace("ALT_ENT_NAME", self.remove_umlauts_and_spaces(entity_name_ol))
        filehandler_output.write(
            "      description: \"{}\"\n".format(description))
  
        # create mandatory parameters
        self.create_mandatory_parameter(filehandler_output)

        # begining of properties section
        filehandler_output.write("      properties:\n")

    def create_mandatory_parameter(self, filehandler_output):
        '''
        Create list of mandatory parameters for Smart Data Model
        Mandatory values can be configures in mandatory_properties
        '''
        # get all mandatory properties
        mandatory_properties = self.configparser.returnElementValue(self.section_name_2, 'mandatory_properties')

        # create list of mandatory properties
        filehandler_output.write("      required:\n")
        for property in mandatory_properties:
            filehandler_output.write("        - \"{}\"\n".format(property))

    def create_default_relation_to_PLS(self, filehandler_output):
        '''
        This method appends a default relationship to PLS
        :param filehandler_output:
        :return:
        '''
        # get description from configuration
        subsystem_description = self.configparser.returnElementValue(
            self.section_name_2, 'subsystem_description')

        filehandler_output.write("        {}:\n".format("isSubsystemOf"))
        filehandler_output.write(
            "          description: \"{}\"\n".format(subsystem_description))
        filehandler_output.write("          type: string\n")
        filehandler_output.write("          x-ngsi:\n")
        filehandler_output.write("            model: https://schema.org/URL\n")
        filehandler_output.write("            type: Relationship\n")

    def create_fiware_id_property(self, filehandler_output):
        '''
        Create static, mandatory id field as entity property
        '''
        filehandler_output.write("        id:\n")
        filehandler_output.write("          anyOf:\n")
        filehandler_output.write("            - description: \"Property. Identifier format of any NGSI entity\"\n")
        filehandler_output.write("              maxLength: 256\n")
        filehandler_output.write("              minLength: 1\n")
        filehandler_output.write("              pattern: '^[\w\-\.\{\}\$\+\*\[\]`|~^@!,:\\\]+$'\n")
        filehandler_output.write("              type: \"string\"\n")
        filehandler_output.write("            - description: \"Property. Identifier format of any NGSI entity\"\n")
        filehandler_output.write("              format: \"uri\"\n")
        filehandler_output.write("              type: \"string\"\n")
        filehandler_output.write("          description: \"Unique identifier of the entity\"\n")
        filehandler_output.write("          x-ngsi:\n")
        filehandler_output.write("            type: \"Property\"\n")

    def create_fiware_type_property(self, filehandler_output, entity_type):
        '''
        Create static, mandatory id field as entity property
        '''
        filehandler_output.write("        type:\n")
        filehandler_output.write("          description: \"NGSI Entity type. it has to be {} \
                                 (a specific PCS part)\"\n".format(entity_type))
        filehandler_output.write("          enum:\n")
        filehandler_output.write("            - \"{}\"\n".format(entity_type))
        filehandler_output.write("          type: \"string\"\n")
        filehandler_output.write("          x-ngsi:\n")
        filehandler_output.write("            type: \"Property\"\n")

    def create_static_tag_with_function_name(self, filehandler_output):
        '''
        This method appends a static tag with KKS function name eg. GCN (Chemikalienversorgung, Dosierung)
        :param filehandler_output:
        :return:
        '''
        filehandler_output.write("        {}:\n".format("KksFunction"))
        filehandler_output.write(
            "          description: \"{}\"\n".format("KKS function for property (level 1)"))
        filehandler_output.write("          type: \"string\"\n")
        filehandler_output.write("          x-ngsi:\n")
        filehandler_output.write("            type: \"Property\"\n")

    def create_static_tag(self, filehandler_output, name, description, type):
        '''
        This method appends a static tag with given name / desc / type
        :param filehandler_output:
        :return:
        '''
        filehandler_output.write("        {}:\n".format(name))
        filehandler_output.write(
            "          description: \"{}\"\n".format(description))
        filehandler_output.write("          type: \"{}\"\n".format(type))
        filehandler_output.write("          x-ngsi:\n")
        filehandler_output.write("            type: \"Property\"\n")

    def remove_umlauts_and_spaces(self, name):
        '''
        Remove umlauts from (german) attribute names
        :param name:
        :return:
        '''
        # remove all special chars besides letters, numbers or whitespace
        if name and isinstance(name, str):
            # remove leading whitespaces
            name_without_ws = name.strip()
            # remove special chars
            name_without_special_chars = re.sub(
                '[^a-zA-ZÜÖÄäöü0-9 ß().]', '', name_without_ws)
            # replace ö, ä, ... with oe, ae, ...
            name_without_umlaute = name_without_special_chars.replace("ä", "ae").replace("Ä", "Ae").replace(
                "ö", "oe").replace("Ö", "Oe").replace("ü", "ue").replace("Ü", "Ue").replace("ß", "ss")
        else:
            print("\n\nError: Name is empty or not of type String: '{}'".format(name))
            sys.exit(1)

        return name_without_umlaute

    def clean_entity_name(self, name):
        '''
        Clean entity names so that these are written in camel case for entity names
        :param name:
        :return:
        '''
        name_without_umlauts_and_spaces = self.remove_umlauts_and_spaces(
            name).replace(".", "")
        # split word by whitespace
        new_name_parts = name_without_umlauts_and_spaces.split(" ")
        new_name = ""
        for i in range(1, len(new_name_parts)+1):
            first_letter = new_name_parts[i-1][:1]
            other_letters = new_name_parts[i-1][1:]
            new_name += "{}{}".format(first_letter.upper(), other_letters)

        return new_name

    def append_property_to_entity(self, filehandler_output, property_name, property_meaning, property_type):
        '''
        Append new property to entity
        :param filehandler_output:
        :param property_name:
        :param property_meaning:
        :param property_type:
        :return:
        '''
        filehandler_output.write("        {}:\n".format(property_name))
        filehandler_output.write(
            "          description: \"{}\"\n".format(property_meaning))
        openAPI3_type = "number" if property_type == "32-Bit IEEE 754" else "boolean"
        ngsi_model = "https://schema.org/Number" if openAPI3_type == "number" else "https://schema.org/Boolean"
        filehandler_output.write(
            "          type: \"{}\"\n".format(openAPI3_type))
        filehandler_output.write("          x-ngsi:\n")
        filehandler_output.write(
            "            model: \"{}\"\n".format(ngsi_model))
        filehandler_output.write(
            "            type: \"{}\"\n".format("Property"))

    def create_default_properties(self, filehandler_output, entity_name):
        '''
        Create default properties for FIWARE Smart Data Model:
        - id
        - type
        - dateObserved
        - isSubsystemOf
        - kksFunction
        '''
        # --> mandatory FIWARE fields
        self.create_fiware_id_property(filehandler_output)
        self.create_fiware_type_property(filehandler_output, entity_name)
        self.create_static_tag(filehandler_output,
                               "dateObserved", "Date of the observed entity defined by the user.", "string")
        # --> reference to PLS
        self.create_default_relation_to_PLS(filehandler_output)
        # --> create default static tags KKS function
        self.create_static_tag(
            filehandler_output, "kksFunction", "KKS function of property (level 1)", "string")

    def create_fiware_sdm(self):
        '''
        Controller for resource creation
        '''        
        # DEFINE VARIABLES
        # File to parse
        filepath_input = self.configparser.returnElementValue(
            self.section_name_2, 'filepath_input')
        # File to export
        filepath_output = self.configparser.returnElementValue(
            self.section_name_2, 'filepath_output')
        # collection of all entities
        all_entities = []
        # collection of non-kks entities
        non_kks_entities = []
        # collection of duplicate entitty attributes
        duplicate_entitiy_attributes = []

        # 1) Check if file exists
        print("\na) Check if input / output file exist")
        self.filehelper.check_file_exists(filepath_input)
        self.filehelper.check_file_exists(filepath_output)
        # delete all lines after configured line number
        self.filehelper.clear_file_from_line(self.configparser.returnElementValue
                                             (self.section_name_2, 'clear_existing_file_from_line'), filepath_output)
        filehandler_output = open(filepath_output, "a")

        # 2) Read as dataframe and sort by entity
        print("\nb) Read as dataframe and sort by entity")
        df = pandas.read_excel(filepath_input)
        # df.sort_values(self.column_entity)

        # 3) Loop through entities and create entity + attributes for all functions
        print("\nc) Loop through entities and create entity + attributes for all functions")
        entitiy_attributes = []
        for index, row in df.iterrows():
            if row[self.column_entity] and isinstance(row[self.column_entity], str):
                # Case 1: Valid KKS name
                # clean name for entity
                cleaned_entity_name = self.clean_entity_name(
                    row[self.column_entity])
                cleaned_attribute_name = row[self.column_name].strip()

                # Check if new entity
                # if not append a property to existing entity
                if cleaned_entity_name in all_entities:
                    # Duplicate attribute name (normally because of missing suffix from text export error)
                    if cleaned_attribute_name in entitiy_attributes:
                        # duplicate
                        print(
                            "-> DUPLICATE PROPERTY: {}".format(cleaned_attribute_name))
                        duplicate_entitiy_attributes.append(
                            cleaned_attribute_name)
                    else:
                        # add new attribute to entity
                        print("-> Property: {}".format(cleaned_attribute_name))
                        cleaned_attribute_meaning = self.remove_umlauts_and_spaces(
                            row[self.column_meaning])
                        self.append_property_to_entity(filehandler_output, cleaned_attribute_name,
                                                       cleaned_attribute_meaning, row[self.column_type])
                        entitiy_attributes.append(cleaned_attribute_name)
                # if yes create new entity
                else:
                    print("\n New entitiy: {}".format(cleaned_entity_name))
                    entitiy_attributes = []
                    all_entities.append(cleaned_entity_name)

                    # -> create comment header
                    self.create_comment_header(
                        filehandler_output, cleaned_entity_name)
                    # -> create entity
                    self.create_entity_handler(filehandler_output, cleaned_entity_name, row[self.column_entity],
                                               row[self.column_entity_other_lang], row[self.column_kks_1])
                    # -> create default properties 
                    self.create_default_properties(filehandler_output, cleaned_entity_name)
                    # -> create first property
                    cleaned_attribute_meaning = self.remove_umlauts_and_spaces(
                        row[self.column_meaning])
                    self.append_property_to_entity(
                        filehandler_output, cleaned_attribute_name, cleaned_attribute_meaning, row[self.column_type])
                    print("-> Property: {}".format(cleaned_attribute_name))
                    entitiy_attributes.append(cleaned_attribute_name)
            else:
                # Case 2: No a valid KKS name
                print("\nError: Element {} has no valid KKS name!".format(row[self.column_name]))
                non_kks_entities.append(cleaned_attribute_name)

        # print results
        print("\n\nCreated {} entities.".format(len(all_entities)))

        print("\nLeft out {} not valid attributes".format(len(non_kks_entities)))
        print("These are: {}".format(non_kks_entities))
        print("PLEASE CORRECT THEM MANUALLY!")

        print("\nFound {} duplicate attributes of an entity".format(
            len(duplicate_entitiy_attributes)))
        print("These are: {}".format(duplicate_entitiy_attributes))
        print("PLEASE CORRECT THEM MANUALLY!")
