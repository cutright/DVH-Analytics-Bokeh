#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sun Feb 26 11:06:28 2017

@author: nightowl
"""


import mysql.connector
from mysql.connector import Error
import getpass


def Send_String_to_SQL(SQL_String):
    """ Connect to MySQL database """

    SQL_UserName = raw_input('User Name: ')
    SQL_Password = getpass.getpass()
    SQL_Database = raw_input('Database Name: ')
    SQL_TableName = raw_input('Table Name: ')

    config = {'user': SQL_UserName,
              'password': SQL_Password,
              'host': 'localhost',
              'database': SQL_Database,
              'raise_on_warnings': True,
              }

    try:
        print('Connecting to MySQL database...')
        cnx = mysql.connector.connect(**config)

        if cnx.is_connected():
            print('connection established.')
        else:
            print('connection failed.')

    except Error as error:
        print(error)

    finally:
        cnx.close()
        print('Connection closed.')


if __name__ == '__main__':
    Send_String_to_SQL()
