import configparser


class WrongFileFormatException(Exception):
    pass


class CodeSequenceConverter:
    def __init__(self, config_file_name):
        self.config_file_name = config_file_name
        self._parse_config()
        self.coded_groups = []
        self.decoded_groups = []

    def _parse_config(self):
        config = configparser.ConfigParser()
        config.read(self.config_file_name)
        self.delimiter = config['Settings']['delimiter']
        self.not_found_value = config['Settings']['not_found_value']
        self.coded_group_id_to_file_names = dict()
        for group_id in range(1, 9):
            table_numbers = config['GroupNumberToTables'][str(group_id)].split(',')
            self.coded_group_id_to_file_names[group_id] = []
            for num in table_numbers:
                file_path = config['TableNumberToFileName'][num]
                self.coded_group_id_to_file_names[group_id].append(file_path)

    def convert(self, coded_string):
        self.coded_groups = self._break_to_groups(coded_string)
        self.decoded_groups = [self.not_found_value for i in range(len(self.coded_groups))]
        group_id = 0
        print('Scanning for matches...')
        for coded_group in self.coded_groups:
            group_id += 1
            is_found = False
            for file_name in self.coded_group_id_to_file_names[group_id]:
                with open(file_name, 'r', encoding='utf8') as file:
                    line_number = 0
                    for line in file:
                        line_number += 1
                        line = line.strip()
                        try:
                            self._check_correctness(line)
                        except WrongFileFormatException as e:
                            print("[ERROR]: Wrong file format. Line skipped. File: {0}, Line number: {1}, Message: {2}"
                                  .format(file_name, line_number, e))
                            continue
                        key, translation = line.split(self.delimiter)
                        if key == coded_group:
                            self.decoded_groups[group_id - 1] = translation
                            is_found = True
                            break
                if is_found:
                    break

    def _break_to_groups(self, coded_string):
        coded_parts = []
        is_quotation_open = False
        current_part = ''
        for c in coded_string:
            if c == '"':
                is_quotation_open = not is_quotation_open
                continue
            if c == '-' and not is_quotation_open:
                coded_parts.append(current_part)
                current_part = ''
            else:
                current_part += c
        coded_parts.append(current_part)
        return coded_parts

    def _check_correctness(self, line):
        if line == '\n':
            raise WrongFileFormatException('Empty line')
        if self.delimiter not in line:
            raise WrongFileFormatException('There is no delimiter in line')
        if len(line.split(self.delimiter)) != 2:
            raise WrongFileFormatException('Unable to split on 2 parts')
        if len(line.split(self.delimiter)[1]) == 0:
            raise WrongFileFormatException('Empty content of line')

    def print_converted_string(self):
        print('Decoded sequence:')
        for i in range(len(self.coded_groups)):
            print('[{0}] {1} = {2}'.format(i + 1, self.coded_groups[i], self.decoded_groups[i]))


if __name__ == '__main__':
    converter = CodeSequenceConverter('./config.ini')
    coded_sequence = input('Enter dash-separated code sequence...\n'
                           '(Use "" for grouping names containing dash, e.g. "ЭнИ-100")\n')
    converter.convert(coded_sequence)
    converter.print_converted_string()
