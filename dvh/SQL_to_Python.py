from DVH_SQL import *
import datetime
from dateutil.relativedelta import relativedelta


class QuerySQL:
    def __init__(self, table_name, condition_str, *unique):

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


def recalculate_ages():

    dvh_data = QuerySQL('Plans', "mrn != ''")
    cnx = DVH_SQL()

    for i in range(0, len(dvh_data.mrn)):
        uid = dvh_data.study_instance_uid[i]
        sim_study_date = dvh_data.sim_study_date[i].split('-')
        birth_date = dvh_data.birth_date[i].split('-')

        birth_year = int(birth_date[0])
        birth_month = int(birth_date[1])
        birth_day = int(birth_date[2])
        birth_date_obj = datetime.datetime(birth_year, birth_month, birth_day)

        sim_study_year = int(sim_study_date[0])
        sim_study_month = int(sim_study_date[1])
        sim_study_day = int(sim_study_date[2])
        sim_study_date_obj = datetime.datetime(sim_study_year,
                                               sim_study_month,
                                               sim_study_day)

        if sim_study_date == '1800-01-01':
            age = '(NULL)'
        else:
            age = relativedelta(sim_study_date_obj, birth_date_obj).years

        condition = "study_instance_uid = '" + uid + "'"
        cnx.update('Plans', 'age', str(age), condition)

    cnx.cnx.close()
