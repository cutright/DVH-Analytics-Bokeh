from DVH_SQL import *


class QuerySQL:
    def __init__(self, table_name, condition_str, *unique):

        table_name = table_name.lower()

        if table_name in {'beams', 'dvhs', 'plans', 'rxs'}:
            self.table_name = table_name
            self.condition_str = condition_str
            self.cnx = DVH_SQL()

            # column names, use as property names
            column_cursor = self.cnx.get_column_names(table_name)

            for row in column_cursor:
                column = str(row).strip()
                self.cursor = self.cnx.query(self.table_name,
                                             column,
                                             self.condition_str)
                if unique:
                    rtn_list = get_unique_list(self.cursor_to_list())
                else:
                    rtn_list = self.cursor_to_list()
                setattr(self, column, rtn_list)
        else:
            print 'Table name in valid. Please select from Beams, DVHs, Plans, or Rxs.'

    def cursor_to_list(self):
        rtn_list = []
        for row in self.cursor:
            if isinstance(row[0], (int, long, float)):
                rtn_list.append(row[0])
            else:
                rtn_list.append(str(row[0]))
        return rtn_list


def get_unique_list(input_list):
    rtn_list_unique = []

    for value in input_list:
        if value not in rtn_list_unique:
            rtn_list_unique.append(value)

    return rtn_list_unique
