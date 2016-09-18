#!/usr/bin/env python
#
# Exports all TPM passwords to an AWS S3 bucket.
#
# @author tblong
# @version 2016-09-18
# @license MIT
#

import requests
import json
import boto3
import tpmPasswordsToS3Config as Config

#####################
# Globals
#####################
PWD_FILE = Config.general['password_file']
NUM_PWDS_URL = Config.tpm_api['passwords_count']
BASE_PWD_PAGE_URL = Config.tpm_api['passwords_page']
BASE_PWD_URL = Config.tpm_api['password_page']

# bot credentials
HEADERS = Config.tpm_api['header']


def get_pwd_pages():
    """
    Get the number pages of passwords

    :returns number of password pages found, zero otherwise.
    """
    response = requests.request("GET", NUM_PWDS_URL, headers=HEADERS)
    page_count = json.loads(response.content).get('num_pages')

    return page_count if page_count > 0 else 0


def get_pwd_ids(num_pages):
    """
    Get the list of password IDs.

    :param num_pages: the number of pages of passwords
    :return: a list of password IDs sorted by ascending ID
    """

    pwd_ids = []

    # get list of IDs in each page
    for page in range(1, num_pages + 1):
        url = BASE_PWD_PAGE_URL + str(page) + ".json"
        response = requests.request("GET", url, headers=HEADERS)
        passwords = json.loads(response.content)

        # iterate through all password IDs for this page
        for pwd in passwords:
            pwd_id = pwd.get('id')
            if pwd_id is not None:
                pwd_ids.append(pwd_id)

    # in-place sort by password ID
    pwd_ids.sort()

    return pwd_ids


def write_passwords(pwd_ids):
    """
    Given the list of passwords IDs, write the passwords to a file.

    :param pwd_ids: list of password IDs
    :return: None
    """

    with open(PWD_FILE, mode='w') as pwd_file:
        # beginning of json file
        pwd_file.write("[\n")

        for id in pwd_ids:
            url = BASE_PWD_URL + str(id) + ".json"
            response = requests.request("GET", url, headers=HEADERS)
            pwd_content = json.loads(response.content)
            password = pwd_content.get("password")

            # only write if password prop not empty
            if password:
                pwd_file.write(json.dumps(pwd_content, indent=4, sort_keys=True))
                # add comma and new line if not last in list
                if id is not pwd_ids[-1]:
                    pwd_file.write(',\n')

        # end of json file
        pwd_file.write("\n]\n")


def upload_to_s3():
    """
    Send json password file to S3.

    :return: None
    """

    # get the json password file
    pwd_file = open(PWD_FILE, mode='rb')
    pwd_list = json.load(pwd_file)  # calls read() on file object

    # only upload if json password file not empty
    if len(pwd_list) > 0:
        # reset file object to beginning
        pwd_file.seek(0)

        # setup s3 connection
        s3 = boto3.resource('s3', region_name=Config.connection['region_name'],
                            aws_access_key_id=Config.connection['aws_access_key'],
                            aws_secret_access_key=Config.connection['aws_secret_key'])

        s3_object_path = Config.s3['key_prefix'] + PWD_FILE
        s3.Bucket(Config.s3['bucket_name']).put_object(Key=s3_object_path, Body=pwd_file)


def main():
    pages = get_pwd_pages()
    ids = get_pwd_ids(pages)
    write_passwords(ids)
    upload_to_s3()

if __name__ == '__main__':
    main()
