import os


class Logger(object):

    def __init__(self, filename):
        self.filename = filename
        self.items = []
        # print('Loading logfile {0}'.format(filename))

        if not os.path.isfile(self.filename):
            f = open(self.filename, 'w')
            f.close()
            print('Created logfile {0}'.format(self.filename))
        else:
            self.load_items()

    def load_items(self):
        try:
            with open(self.filename, 'r') as f:
                self.items = f.read().splitlines()
        except IOError as e:
            print('Error reading history logfile: {0}'.format(e.message))

    def __write(self, mode, data):
        try:
            with open(self.filename, mode) as f:
                f.write('{0}\n'.format(data))
        except IOError as e:
            print('Error saving history logfile: {0}'.format(e.message))

    def write(self, data):
        self.__write('w', data)

    def append(self, data):
        self.__write('a', data)
