from __future__ import print_function
from tools.io.database.sql_to_python import QuerySQL
from tools.io.database.sql_connector import DVH_SQL
from datetime import datetime
from dateutil.relativedelta import relativedelta


def recalculate_ages(*custom_condition):

    if custom_condition:
        custom_condition = " AND " + custom_condition[0]
    else:
        custom_condition = ''

    dvh_data = QuerySQL('Plans', "mrn != ''" + custom_condition)
    cnx = DVH_SQL()

    for i in range(len(dvh_data.mrn)):
        mrn = dvh_data.mrn[i]
        uid = dvh_data.study_instance_uid[i]
        sim_study_date = dvh_data.sim_study_date[i].split('-')
        birth_date = dvh_data.birth_date[i].split('-')

        try:
            birth_year = int(birth_date[0])
            birth_month = int(birth_date[1])
            birth_day = int(birth_date[2])
            birth_date_obj = datetime(birth_year, birth_month, birth_day)

            sim_study_year = int(sim_study_date[0])
            sim_study_month = int(sim_study_date[1])
            sim_study_day = int(sim_study_date[2])
            sim_study_date_obj = datetime(sim_study_year, sim_study_month, sim_study_day)

            if sim_study_date == '1800-01-01':
                age = '(NULL)'
            else:
                age = relativedelta(sim_study_date_obj, birth_date_obj).years

            condition = "study_instance_uid = '" + uid + "'"
            cnx.update('Plans', 'age', str(age), condition)
        except:
            print("Update Failed for", mrn, "sim date:", sim_study_date, "birthdate", birth_date, sep=' ')

    cnx.close()


def recalculate_total_mu(*custom_condition):

    if custom_condition:
        custom_condition = " AND " + custom_condition[0]
    else:
        custom_condition = ''

    # Get entire table
    beam_data = QuerySQL('Beams', "mrn != ''" + custom_condition)
    cnx = DVH_SQL()

    plan_mus = {}
    for i in range(len(beam_data.study_instance_uid)):
        uid = beam_data.study_instance_uid[i]
        beam_mu = beam_data.beam_mu[i]
        fxs = float(beam_data.fx_count[i])
        if uid not in list(plan_mus):
            plan_mus[uid] = 0.

        plan_mus[uid] += beam_mu * fxs

    for uid in list(plan_mus):
        cnx.update('Plans', 'total_mu', str(round(plan_mus[uid], 1)), "study_instance_uid = '%s'" % uid)

    cnx.close()
