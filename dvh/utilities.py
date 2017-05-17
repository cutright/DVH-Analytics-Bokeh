from SQL_to_Python import QuerySQL
from DVH_SQL import DVH_SQL
from datetime import datetime
from dateutil.relativedelta import relativedelta


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