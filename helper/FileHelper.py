import os


class FileHelper(object):
    '''
    Some useful file operations
    '''

    def check_file_exists(self, filename):
        '''
        check if given file exists
        :param filename:
        :return:
        '''
        if os.path.isfile(filename):
            print("The text file {} can be found.".format(filename))
        else:
            raise Exception("The file doesn't exist or cannot be found.")

    def print_key_value(self, key, value):
        '''
        print parsed line as key-value-pair
        :param key:
        :param value:
        :return:
        '''
        print("Key: {}; Value: {}".format(key, value))

    def clear_file_from_line(self, line_number, filepath_output):
        '''
        Delete all lines after a given line 
        '''
        # read all lines
        with open(filepath_output, 'r') as f:
            data = f.readlines()
            f.close()

        # delete all lines after given lines
        counter = 0
        with open(filepath_output, 'w') as f:
            for line in data:
                counter = counter + 1
                # only write lines before max line number
                if not counter >= line_number:
                    f.write(line)
            f.close()
