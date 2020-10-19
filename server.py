import flask
import re
import os
import hashlib
import binascii
from datetime import datetime, timedelta
import constant as const
import dblayer as database
from flask import request, jsonify, make_response


app = flask.Flask(__name__)
app.config["DEBUG"] = True



@app.route('/users', methods=['POST'])
def signup():
    """
    signup method to create the entry for an user in the database
    It handle the failure case if you try to add the same info multiple times.
    :return: HTTP Response
    """

    postdata= request.get_json()
    email=postdata.get("email",None)
    password=postdata.get("password",None)
    if not _validate_email(email):
        invalid_error="Invalid email id %s" %email
        return make_response(jsonify(invalid_error),
                             const.HTTP_404_INVALID_ARGUMENT)
    if not _check_passwordComplexity(password):
        invalid_error = "Password length is not appropriate %s" % password
        return make_response(jsonify(invalid_error),
                             const.HTTP_404_INVALID_ARGUMENT)

    current_time=_get_current_time_string()
    isUserInfoAdded, value = database.insert_data_to_table(email,password,current_time)

    result = {}
    if not isUserInfoAdded:
        result['error']=str(value)
        return make_response(jsonify(result),
                             const.HTTP_400_BADREQUEST)

    result['id']=value[0][0]
    result['email']=value[0][1]
    result['password']=value[0][2]
    result['created_at']=value[0][3]
    result['updated_at']=value[0][4]
    return make_response(jsonify(result),
                             const.HTTP_SUCCESS)

@app.route('/login', methods=['POST'])
def login():
    """
    login api to validate the email and password and provide the token in case of success.
    :return: HTTP Response
    """
    postdata = request.get_json()
    email = postdata.get("email", None)
    password = postdata.get("password", None)
    if not _validate_email(email):
        invalid_error = "Invalid email id %s" % email
        return make_response(jsonify(invalid_error),
                             const.HTTP_404_INVALID_ARGUMENT)
    if not _check_passwordComplexity(password):
        invalid_error = "Password length is not appropriate %s" % password
        return make_response(jsonify(invalid_error),
                             const.HTTP_404_INVALID_ARGUMENT)


    user_data = database.verify_user_details(postdata)
    if  not len(user_data):
        error_response = "Invalid user creadential"
        return make_response(jsonify(error_response),
                             const.HTTP_401_UNAUTHRISED)


    update_dict={}
    update_dict['token']=_generate_md5based_token()
    update_dict['token_created_on']=_get_current_time_string()
    database.update_data_to_table(update_dict,user_data[0][0])


    return make_response(jsonify({"token":update_dict['token']}),
                         const.HTTP_SUCCESS)


@app.route('/secret',methods=['GET'])
def secret():
    """
    secret API to validate the token. It also check the token is expired of not.
    Incase of valid token returns the user id and message.
    :return:
    """
    headers = request.headers
    # print headers
    request_token = headers.get('Authorization', None)

    isExpired, user_data= isTokenExpired(request_token)
    if not isExpired:
        result={
            "user_id": user_data[0][0],
            "secret": "All your base are belong to us"
        }
        return make_response(jsonify(result),
                             const.HTTP_SUCCESS)
    else:
        result={
            "error": "token invalid"
        }
        return make_response(jsonify(result),
                             const.HTTP_401_UNAUTHRISED)


@app.route('/users/<id>',methods=['Patch'])
def update(id):
    """
    Update API to update the user information such as email , password.
    Handle the case if you provide the email, password, both or none.
    It also check validate the token as well user id and return the appropriate response.
    :param id:
    :return:
    """
    postdata = request.get_json()
    if postdata:
        email = postdata.get("email", None)
        password = postdata.get("password", None)


        if email and not _validate_email(email):
            invalid_error = "Invalid email id %s" % email
            return make_response(jsonify(invalid_error),
                                 const.HTTP_404_INVALID_ARGUMENT)
        if password and not _check_passwordComplexity(password):
            invalid_error = "Password length is not appropriate %s" % password
            return make_response(jsonify(invalid_error),
                                 const.HTTP_404_INVALID_ARGUMENT)

    user_info = database.find_userby_email_uid(userid=id)

    if not len(user_info):
        invalid_error = "Invalid userid  %s" % id
        return make_response(jsonify(invalid_error),
                             const.HTTP_401_UNAUTHRISED)
    else:
        token=user_info[0][5]
        headers = request.headers
        request_token = headers.get('Authorization', None)
        if token !=request_token.split( )[-1]:
            result = {
                "error": "access denied"
            }
            return make_response(jsonify(result),
                                 const.HTTP_401_UNAUTHRISED)

        isExpired, user_data = isTokenExpired(token)
        if isExpired:
            result={
                "error": "token expired"
            }
            return make_response(jsonify(result),
                                 const.HTTP_401_UNAUTHRISED)

        updateTime = _get_current_time_string()
        if not postdata:
            postdata={}
        postdata["updated_on"]=updateTime
        database.update_data_to_table(postdata,id)
        user_info = database.find_userby_email_uid(userid=id)

        result = {}
        result['id'] = user_info[0][0]
        result['email'] = user_info[0][1]
        result['password'] = user_info[0][2]
        result['created_at'] = user_info[0][3]
        result['updated_at'] = user_info[0][4]
        return make_response(jsonify(result),
                             const.HTTP_SUCCESS)


@app.route('/shutdown',methods=['POST'])
def shutdown():
    """
    Created a API to shutdown the server
    It also delete the table.
    :return:
    """
    database.delete_table()
    os._exit(0)


def _get_current_time_string():
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

def isTokenExpired(token):
    """
    Validate the token is valid or not.
    Assumping token life is 10 mins
    :param token:
    :return:
    """
    token=token.split()[-1]

    user_info={'token':token}
    user_entry_in_database = database.verify_user_details(user_info)
    if not len(user_entry_in_database):
        return True, None
    else:
        token_created=user_entry_in_database[0][6]
        token_time_obj = datetime.strptime(str(token_created), '%Y-%m-%d %H:%M:%S')
        current_time_obj = datetime.now()
        if token_time_obj + timedelta(minutes=const.TOKEN_EXPIRED) < current_time_obj:
            return True, None
        else:
            return False, user_entry_in_database


def _generate_md5based_token():
    """
    Method to generate token
    :return: string
    """
    randkey=binascii.hexlify(os.urandom(16))
    return hashlib.md5(randkey).hexdigest()

def _validate_email(email):
    """
    Method to validate the email id string
    :param email: string
    :return: boolean
    """
    regex='^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'
    return re.search(regex,email)

def _check_passwordComplexity(password):
    """
    Method to validate the password length
    :param password: string
    :return: boolean
    """
    if len(password)<8:
        return False
    else:
        return True


database.create_database_table()
app.run(port=9001)

