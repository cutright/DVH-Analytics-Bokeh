from DVH_SQL import *


class QuerySQL:
    def __init__(self, table_name, condition_str):

        if table_name in {'Beams', 'DVHs', 'Plans', 'Rxs'}:
            create_properties = True
        else:
            create_properties = False

        if create_properties:
            self.table_name = table_name
            self.condition_str = condition_str
            self.cnx = DVH_SQL()

            # column names, use as property names
            column_cursor = self.cnx.get_column_names(table_name)

            for row in column_cursor:
                column = str(row[0]).strip()
                self.cursor = self.cnx.query(self.table_name,
                                             column,
                                             self.condition_str)
                rtn_list = get_unique_list(self.cursor_to_list())
                setattr(self, column, rtn_list)
        else:
            print 'Table name in valid. Please select from Beams, DVHs, Plans, or Rxs.'

    def cursor_to_list(self):
        rtn_list = {}
        i = 0
        for row in self.cursor:
            rtn_list[i] = str(row[0])
            i += 1
        return rtn_list


def get_unique_list(input_list):
    inverted = dict()
    rtn_list_unique = dict()
    i = 0
    for (a, b) in input_list.iteritems():
        if b not in inverted:
            inverted[b] = a
    for c in inverted.iterkeys():
        rtn_list_unique[i] = c
        i += 1

    return rtn_list_unique
