import sys
import logging


def exception_info():
    info = (f"{sys.exc_info()[0]}:   {sys.exc_info()[1]};\n"
            f"   LINE: {sys.exc_info()[2].tb_lineno},\n"
            f"   FILE: {sys.exc_info()[2].tb_frame.f_code.co_filename}")
    return info


def log_exception():
    logging.exception(exception_info())
