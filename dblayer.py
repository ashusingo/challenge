import psycopg2
import os
from psycopg2 import OperationalError, errorcodes, errors
import constant as const


def create_connection_todb():
    """
    Create the Database connection return the connection pointer.
    :return:
    """
    try:

        #Trying to fetch the variable from environment variable.
        env_variable=os.environ
        host=env_variable.get("DB_HOST",None)
        user=env_variable.get("DB_USER",None)
        password=env_variable.get("DB_PASS",None)
        dbname=env_variable.get("DB_NAME",None)

        # If environment variable not available read values from constant file.
        if not host:
            host=const.DB_HOST
        if not user:
            user=const.DB_USER
        if not password:
            password=const.DB_PASS
        if not dbname:
            dbname=const.DB_NAME

        connection = psycopg2.connect(user=user,
                                      password=password,
                                      host=host,
                                      port="5432",
                                      database=dbname)
        return connection
    except OperationalError as err:
        raise

    except psycopg2.Error as err:
        raise


def create_database_table():
    """
    Create the table.
    Before creating the databse deleting the existing table
    :return:
    """
    try:
        conn = create_connection_todb()
        cursor = conn.cursor()

        #Check if table is alrady present.
        droptable_ifExist= "DROP TABLE IF EXISTS %s;" %const.DB_TABLE
        cursor.execute(droptable_ifExist) # This execution for the safe side if table exists
        conn.commit()

        createdb_query="CREATE TABLE %s ( userid BIGSERIAL  PRIMARY KEY, email VARCHAR(50) UNIQUE NOT NULL, password VARCHAR(50) NOT NULL, created_on VARCHAR(50) NOT NULL,updated_on VARCHAR(50), token VARCHAR(100), token_created_on TIMESTAMP);"%const.DB_TABLE
        cursor.execute(createdb_query)
        conn.commit()

        cursor.close()
        conn.close()
    except OperationalError as err:
        raise
    except psycopg2.Error as err:
        raise

def insert_data_to_table(email, password, createdTime):
    """
    Insert the user information into the table
    :param email:
    :param password:
    :param createdTime:
    :return:
    """
    try:
        conn = create_connection_todb()
        curr = conn.cursor()
        insert_statment = "INSERT INTO %s (email, password,created_on) VALUES ('%s','%s','%s');" %(const.DB_TABLE,email,password,createdTime)
        curr.execute(insert_statment)
        conn.commit()

        select_statment = "SELECT * FROM %s WHERE email='%s';"%(const.DB_TABLE,email)
        curr.execute(select_statment)
        added_date=curr.fetchall()
        return True, added_date

    except OperationalError as err:
        return False, err
    except psycopg2.Error as err:
        return  False, err


def update_data_to_table(updatedict,key):

    conn = create_connection_todb()
    cursor = conn.cursor()

    update = ""
    for k,v in updatedict.iteritems():
        if len(update) !=0:
            update = update+","
        temp= k+ "="+"'%s'"%v
        update=update+temp
    update_query = "UPDATE %s SET %s WHERE userid = %s;" %(const.DB_TABLE,update,key)
    cursor.execute(update_query)
    conn.commit()
    cursor.close()
    conn.close()



def find_userby_email_uid(email=None,userid=None):
    
    conn = create_connection_todb()
    cursor = conn.cursor()
    if userid:
        selectQuery="SELECT * FROM %s WHERE userid=%s"%(const.DB_TABLE,userid)
    if email:
        selectQuery = "SELECT * FROM %s WHERE email='%s'" % (const.DB_TABLE, email)
    cursor.execute(selectQuery)
    data=cursor.fetchall()
    cursor.close()
    conn.close()
    return data


def verify_user_details(userinfo):
    """
    verify that provided user information is available in databse
    :param userinfo:
    :return:
    """
    conn = create_connection_todb()
    cursor = conn.cursor()

    sql_condition = ""
    for k, v in userinfo.iteritems():
        if len(sql_condition) != 0:
            sql_condition = sql_condition + " AND "
        temp = k + "=" + "'%s'" % v
        sql_condition = sql_condition + temp
    selectQuery="SELECT * FROM %s WHERE %s"%(const.DB_TABLE,sql_condition)

    cursor.execute(selectQuery)
    user_info=cursor.fetchall()
    cursor.close()
    conn.close()
    return user_info


def delete_table():
    """
    Delete the table if exists
    :return:
    """
    conn=create_connection_todb()
    cursor=conn.cursor()
    drop_table_query="DROP TABLE IF EXISTS %s;"%const.DB_TABLE
    cursor.execute(drop_table_query)
    conn.commit()
    cursor.close()
    conn.close()



create_database_table()
# from datetime import datetime
# k=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
# print k
# insert_data_to_table("ashutoshdd@domain.com","Password",str(k))
# print find_user_byid(1)
# updatedict={'email':'ashutosh100ankit@gmail.com','password':'Password123!'}
# update_data_to_table(updatedict,1)
