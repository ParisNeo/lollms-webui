
__author__ = "parisneo"
__github__ = "https://github.com/ParisNeo/lollms-webui"
__copyright__ = "Copyright 2023, "
__license__ = "Apache 2.0"

def compare_lists(list1, list2):
    if len(list1) != len(list2):
        return False
    else:
        return list1 == list2
