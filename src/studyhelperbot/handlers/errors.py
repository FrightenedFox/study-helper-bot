import sys


def error_info():
    info = (f"{sys.exc_info()[0]}:   {sys.exc_info()[1]};"
            f"   LINE: {sys.exc_info()[2].tb_lineno},"
            f"   FILE: {sys.exc_info()[2].tb_frame.f_code.co_filename}")
    return info
