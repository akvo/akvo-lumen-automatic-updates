import requests as r
import time
import sys
import os

base_url = 'https://unicef.akvolumen.org'
dataset_api_url = base_url + '/api/datasets/{}'
update_api_url = dataset_api_url + '/update'
job_status_url = base_url + '/api/job_executions/dataset/{}'
max_attempts = 120
wait_time = 5

token_url = 'https://akvofoundation.eu.auth0.com/oauth/token'

token_data = {
    'client_id': os.environ['CLIENT_ID'],
    'client_secret': os.environ['CLIENT_SECRET'],
    'username': os.environ['AUTH0_USER'],
    'password': os.environ['AUTH0_PWD'],
    'grant_type': 'password',
    'scope': 'openid email'
}

# Form - dataset mapping
table_dataset = {
    'f1': '60b67338-ca0b-4d2f-9209-44bdcc244a9c',
    'f3':'60a6a4d9-020c-4b4f-a8b3-791d4b2f4f02',
    'f4':'60b7c400-7095-41e4-ad6c-fc898f880948',
    'f6':'60a63134-0fbf-4209-b185-e5071b37cf4f',
    'f7':'60a631ad-6fac-44af-b098-bc7e363b0d51',
    'f8':'60a63218-b323-43a9-a70e-01a61eef21cc',
    'f9':'60a6327b-0ab8-4194-a277-8d8e2caefd9a',
    'f10':'60aff888-bfd7-4840-a977-56234b27b192',
    'f12':'60b8bdac-5faf-4aef-b12b-279b2164f23b',
}



def get_token():
    response = r.post(token_url, token_data)
    if response.ok:
        return response.json()['id_token']
    raise RuntimeError('Unable to get access token: HTTP {} - {}'.format(response.status_code, response.text))


def headers(token):
    return {
        'Authorization': 'Bearer ' + token,
        'Host': 'unicef.akvolumen.org',
        'Origin': 'https://unicef.akvolumen.org',
        'Content-Type': 'application/json',
    }


def wait_for_update(token, job_id):
    for i in range(max_attempts):
        url = job_status_url.format(job_id)
        update_response = r.get(url, headers=headers(token))
        if update_response.ok and update_response.json()['status'] == 'OK':
            print(' - done')
            return True
        print('#', end='')
        time.sleep(wait_time)
    return False


def update_dataset(token, dataset_id):
    print('Updating dataset {}'.format(dataset_id))
    url = update_api_url.format(dataset_id)
    job = r.post(url, headers=headers(token))

    if not job.ok:
        sys.stderr.write('Error updating dataset {} - HTTP {} - '.format(dataset_id, job.status_code, job.text))
        return False

    job_id = job.json()['updateId']

    if not wait_for_update(token, job_id):
        sys.stderr.write('Error updated dataset {}, max attempts reached'.format(dataset_id))
        return False

    return True



if __name__ == '__main__':
    prefix = int(time.time())

    for d in table_dataset:
        print('Processing: ' + d)
        dataset_id = table_dataset[d]
        token = get_token()
        update_dataset(token, dataset_id)
