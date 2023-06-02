import re
import sys
import pandas
from helper.FileHelper import FileHelper


class GroupTagsAndAssignMeaning():
    '''
    Class to 
    - parse KKS attribute names
    - group them into entities
    - assign meaning to attributes
    - map OpenAPI 3.0 / FIWARE datatypes
    '''

    def __init__(self, configparser, language):
        # section name in config
        self.section_name = '1_group_tags_and_assign_meaning'

        # config parser
        self.configparser = configparser

        # file handler
        self.filehelper = FileHelper()

        # important files
        self.filepath_kks_meanings = self.configparser.returnElementValue(
            self.section_name, 'filepath_kks_meanings')

        # language
        self.langugage = language

        # columns
        self.column_name = self.configparser.returnElementValue(self.section_name, 'input_column_attribute_name')
        self.column_type = self.configparser.returnElementValue(self.section_name, 'input_column_attribute_type')
        self.column_kks_0 = self.configparser.returnElementValue(self.section_name, 'output_column_attribute_kks_0')
        self.column_kks_1 = self.configparser.returnElementValue(self.section_name, 'output_column_attribute_kks_1')
        self.column_kks_1_nr = self.configparser.returnElementValue(self.section_name,
                                                                    'output_column_attribute_kks_1_nr')
        self.column_kks_2 = self.configparser.returnElementValue(self.section_name, 'output_column_attribute_kks_2')
        self.column_kks_2_nr = self.configparser.returnElementValue(self.section_name,
                                                                    'output_column_attribute_kks_2_nr')
        self.column_kks_3 = self.configparser.returnElementValue(self.section_name, 'output_column_attribute_kks_3')
        self.column_ending = self.configparser.returnElementValue(self.section_name, 'output_column_attribute_ending')
        self.column_entity = self.configparser.returnElementValue(self.section_name, 'output_column_attribute_entity')
        self.column_entity_other_lang = self.configparser.returnElementValue(
            self.section_name, 'output_column_attribute_entity_other_lang')
        self.column_meaning = self.configparser.returnElementValue(self.section_name, 'output_column_attribute_meaning')
        self.column_type_map1 = self.configparser.returnElementValue(self.section_name,
                                                                     'output_column_attribute_type_1')
        self.column_type_map2 = self.configparser.returnElementValue(self.section_name,
                                                                     'output_column_attribute_type_2')

        # columns meanings
        self.column_meaning_kks_1_f_de = 'function_de'
        self.column_meaning_kks_1_f_en = 'function_en'
        self.column_meaning_kks_2_g = 'group_de' if self.langugage == "de" else "group_en"
        self.column_meaning_kks_2_d = 'description_de' if self.langugage == "de" else "description_en"
        self.column_meaning_ending = 'meaning_de' if self.langugage == "de" else "meaning_en"
        self.column_abbreviation = self.configparser.returnElementValue(
            self.section_name, 'mapping_column_abbreviation')
        self.column_aggregate = self.configparser.returnElementValue(
            self.section_name, 'mapping_column_aggregate')
        self.column_type_name = self.configparser.returnElementValue(
            self.section_name, 'mapping_column_type_name')
        self.column_map_type1 = self.configparser.returnElementValue(
            self.section_name, 'mapping_column_map_type_name')

    def split_name(self, name):
        '''
        split name by / if possible
        otherwise stop tool (check weird non kks name!)
        :param name:
        :return:
        '''
        try:
            return name.split('/')[0]
        except Exception:
            print(
                "Error: Failed to split name '{}'. Please correct it in input file.".name)
            sys.exit(1)

    def create_columns_for_name_parts(self, df):
        '''
        Loop through variable names and parse them (split by kks meaning)
        :param df:
        :return:
        '''
        list_of_additions = []
        df_meaning_function = pandas.read_excel(
            self.filepath_kks_meanings, "functions")
        df_meaning_aggregate = pandas.read_excel(
            self.filepath_kks_meanings, "aggregates")
        df_meaning_ending = pandas.read_excel(
            self.filepath_kks_meanings, "endings")

        for name in df[self.column_name]:
            print('\n Variable name is: {}'.format(name))

            # split name to only use kks prefix
            kks_name = self.split_name(name)

            # parse for model and append to dictionary
            parsed_values = self.parse_tagname(kks_name)
            print(parsed_values)

            # parse ending and append to dictionary
            parsed_values_with_ending = self.parse_ending(name, parsed_values)

            # generate name from parsed values
            parsed_values_with_name = self.assign_meaning(
                parsed_values_with_ending, df_meaning_function, df_meaning_aggregate, df_meaning_ending, name)

            # append to collection
            list_of_additions.append(parsed_values_with_name)
        return list_of_additions

    def parse_ending(self, name, append_values):
        '''
        get suffix from kks-filename
        :param name:
        :param append_values:
        :return:
        '''
        # parse ending
        ending_regex = "\..*$"
        ending_match = re.search(ending_regex, name)
        ending_var = ending_match.group(0)
        append_values.append(ending_var.strip())
        print("Ending: {}".format(ending_var))

        return append_values

    def parse_tagname(self, name):
        '''
        Take name, split in relevant parts and add to variable
        Naming is done by 'Kraftwerk-Kennzeichensystem'
        see ref here: https://de.wikipedia.org/wiki/Kraftwerk-Kennzeichensystem

        outline levels parsed:
        1. outline level 0: Overall Plant => 0
        2. outline level 1: Function => 3 letters, 2 numbers
        3. outline level 2: Aggregate => 2 letters, 3 numbers
        4. outline level 3: Operational Resources (optional) => can be EOF, three letters, digit in brackets, ...
           single letter, or underscore followed by a term
        :return:
        '''

        kks_outline_levels = []
        kks_outline_regex = "^(.{1})([A-Z]{3})(\d{3}|\d{2})([A-Z]{2}|[A-Z]{1})(\d{3})($|[A-Z]{3}|_.*|\(\d+\)|[A-Z])"
        output = re.match(kks_outline_regex, name)

        # first letter (should always be '0' in JL)
        if output.group(0) != name:
            # we might have a weird element and didn't parse all parts correctly
            print(
                "\nError: kks name regex doesn't meet all parts of name: {}".format(name))
            sys.exit()

        # append all functional levels splitted in numbers and letters from group 1-5
        for i in range(1, 7):
            kks_outline_levels.append(output.group(i))

        return kks_outline_levels

    def assign_meaning(self, list_of_additions, df_meaning_function,
                       df_meaning_aggregate, df_meaning_ending, element_name):
        '''
        Assign meaning to kks name
        :param list_of_additions:
        :param df_meaning_function:
        :param df_meaning_aggregate:
        :param df_meaning_ending:
        :param element_name:
        :return:
        '''
        if list_of_additions[0] == '0':

            # get meaning to function (level 1)
            function_value = list_of_additions[1]
            relevant_row = df_meaning_function.loc[df_meaning_function[self.column_abbreviation] == function_value]
            function_element_de = relevant_row[self.column_meaning_kks_1_f_de].values[0].strip(
            )
            function_element_en = relevant_row[self.column_meaning_kks_1_f_en].values[0].strip(
            )
            function_nr = list_of_additions[2]
            # assign as entity
            function_element = function_element_de if self.langugage == "de" else function_element_en
            function_element_other_lang = function_element_de if self.langugage == "en" else function_element_en
            list_of_additions.append(function_element)
            list_of_additions.append(function_element_other_lang)

            # get meaning of aggregate (level 2)
            aggregate_value = list_of_additions[3]
            relevant_row = df_meaning_aggregate.loc[df_meaning_aggregate[self.column_aggregate] == aggregate_value]
            aggregate_element = "{} {}".format(
                relevant_row[self.column_meaning_kks_2_g].values[0],
                relevant_row[self.column_meaning_kks_2_d].values[0])
            aggregate_nr = list_of_additions[4]

            # append operating resources
            operating_resources = list_of_additions[5]

            # parse ending
            ending_value = list_of_additions[6]
            relevant_row = df_meaning_ending.loc[df_meaning_ending[self.column_abbreviation] == ending_value]
            if not relevant_row[self.column_meaning_ending].empty:
                # assign meaning
                ending_element = relevant_row[self.column_meaning_ending].values[0]
            else:
                # No meaning can be found
                ending_element = ending_value

            # create name
            name = "{} Nr. {} {} Nr. {} {} ({})".format(
                function_element, function_nr, aggregate_element, aggregate_nr, operating_resources, ending_element)
            print("Meaning Tag: {}".format(name))
            if not name:
                # weird element -> use name
                name = element_name
            # assign meaning for tag
            list_of_additions.append(name)

        else:
            # weird non-kkks element
            print("No Meaning can be found to tag: {}".format(element_name))
            list_of_additions.append("")
            list_of_additions.append("")

        return list_of_additions

    def create_columns_for_types(self, df_input):
        '''
        Parse given types and map types for script 2 and 3 to assign valid openapi 3.0, ngsi-ld and
        possible also other types
        :param df_input:
        :return:
        '''
        df_meaning_datatype = pandas.read_excel(
            self.filepath_kks_meanings, "datatypes")
        list_of_types = []
        for datatype in df_input[self.column_type]:
            relevant_row = df_meaning_datatype.loc[df_meaning_datatype[self.column_type_name] == datatype]
            if not relevant_row[self.column_type_map1].empty:
                type_openapi = relevant_row[self.column_type_map1].values[0]
            else:
                type_openapi = ""
                print("No type found that can be mapped to data type: {}. Please configure types"
                      " in mapping file for all data types or empty value will be used".format(relevant_row))

            if not relevant_row[self.column_type_map2].empty:
                type_ngsild = relevant_row[self.column_type_map2].values[0]
            else:
                type_ngsild = ""
                print("No type found that can be mapped to data type: {}. Please configure types"
                      "in mapping file for all data types or empty value will be used".format(relevant_row))
            list_of_types.append([type_openapi, type_ngsild])

        return list_of_types

    def group_tags_and_assign_meaning(self):
        '''
        Controller for resource creation
        '''
        # DEFINE VARIABLES
        # File to parse
        filepath_input = self.configparser.returnElementValue(
            self.section_name, 'filepath_input')
        # File to export
        filepath_output = self.configparser.returnElementValue(
            self.section_name, 'filepath_output')

        # 1) Check if file exists
        print("\na) Check if input files exist")
        self.filehelper.check_file_exists(filepath_input)
        self.filehelper.check_file_exists(self.filepath_kks_meanings)

        # 2) Parse variables from excel file
        print("\nb) Read input file as dataframe")
        df = pandas.read_excel(filepath_input, index_col=0)

        # 3) loop through all variables and split name
        print("\nc) Parse KKS name parts and assign meaning to name")
        list_of_additions = self.create_columns_for_name_parts(df)

        print("\nd) Assign OpenAPI and NGSI-LD datatypes to types")
        # map datatype
        list_of_types = self.create_columns_for_types(df)

        # 4) Export to excel
        print("\ne) Export relevant elements excel")
        # add column to dataframe
        df_additions = pandas.DataFrame(list_of_additions,
                                        columns=[self.column_kks_0, self.column_kks_1, self.column_kks_1_nr,
                                                 self.column_kks_2, self.column_kks_2_nr, self.column_kks_3,
                                                 self.column_ending, self.column_entity, self.column_entity_other_lang,
                                                 self.column_meaning])
        df_types = pandas.DataFrame(list_of_types,
                                    columns=[self.column_type_map1, self.column_type_map2])
        df_all_cols = pandas.concat([df, df_additions, df_types], axis=1)
        # write to excel
        df_all_cols = df_all_cols.loc[:, ~
                                      df_all_cols.columns.str.contains("Unnamed")]
        df_all_cols.sort_values(by=self.column_entity).to_excel(
            filepath_output, index=False)
        print("\n\nDone.")
