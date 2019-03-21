#coding:utf-8
from flask_table import Table, Col
# Declare your table
class RecycleTable(Table):
    name = Col('名称')
    description = Col('操作')

# Get some objects
class RecycleItem(object):
    def __init__(self, name, description):
        self.name = name
        self.description=description
