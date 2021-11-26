class Logger:
    def __init__(self, head):
        self.__head = head

    def debug(self, msg):
        print("[D] {}: {}".format(self.__head, msg))

    def error(self, msg):
        print('\033[91m' + "[E] {}: {}".format(self.__head, msg) + '\033[0m')

    def info(self, msg):
        print("[I] {}: {}".format(self.__head, msg))
