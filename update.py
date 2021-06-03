import requests as r
import time
import sys
import os

base_url = 'https://<LUMEN_INSTANCE>.akvolumen.org'
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
    '<LUMEN_DATASET_TITLE>': '<LUMEN_DATASET_ID>',
}



def get_token():
    response = r.post(token_url, token_data)
    if response.ok:
        return response.json()['id_token']
    raise RuntimeError('Unable to get access token: HTTP {} - {}'.format(response.status_code, response.text))


def headers(token):
    return {
        'Authorization': 'Bearer ' + token,
        'Host': '<LUMEN_INSTANCE>.akvolumen.org',
        'Origin': 'https://<LUMEN_INSTANCE>.akvolumen.org',
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
