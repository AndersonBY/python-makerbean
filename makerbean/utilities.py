# -*- coding: utf-8 -*-
# @Author: ander
# @Date:   2020-12-22 16:15:28
# @Last Modified by:   ander
# @Last Modified time: 2020-12-22 16:26:03
import re
import os


def validate_title(title):
    rstr = r"[\/\\\:\*\?\"\<\>\|\%]"
    new_title = re.sub(rstr, "_", title)
    return new_title


def mkdir(folder):
    if not os.path.exists(folder):
        os.mkdir(folder)
