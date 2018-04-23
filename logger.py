# -*- encoding:utf-8 -*-
import logging
import random
import string

# # create logger
# logger_name = "example"
# logger = logging.getLogger(logger_name)
# logger.setLevel(logging.DEBUG)
#
# # create file handler
#
# log_path = "./log/log.log"
# fh = logging.FileHandler(log_path)
# fh.setLevel(logging.WARN)
#
# # create formatter
# fmt = "%(asctime)-15s %(levelname)s %(filename)s %(lineno)d %(process)d %(message)s"
# datefmt = "%a %d %b %Y %H:%M:%S"
# formatter = logging.Formatter(fmt, datefmt)
#
# # add handler and formatter to logger
# fh.setFormatter(formatter)
# logger.addHandler(fh)

# print log info
# logger.debug('debug message')
# logger.info('info message')
# logger.warn('warn message')
# logger.error('error message')
# logger.critical('critical message')

def generate_activation_code(len=16, n=1):
    '''生成n个长度为len的随机序列码'''
    random.seed()
    chars = string.ascii_letters + string.digits
    return [''.join([random.choice(chars) for _ in range(len)]) for _ in range(n)]

print generate_activation_code(10)