import httplib2
import googleapiclient.discovery
from oauth2client.service_account import ServiceAccountCredentials
import requests
import datetime
from unicodedata import normalize
from dotenv import load_dotenv
import os


load_dotenv()
CREDENTIALS_FILE = 'task-olya-b54fe20f574b.json'
credentials = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE,
                                                               ['https://www.googleapis.com/auth/spreadsheets',
                                                                'https://www.googleapis.com/auth/drive'])
SPREADSHEETID = os.environ.get('SPREADSHEETID')
TOKEN = os.environ.get('TOKEN')
CHAT = os.environ.get('CHAT')

httpAuth = credentials.authorize(httplib2.Http())  # autorization
service = googleapiclient.discovery.build('sheets', 'v4',
                                          http=httpAuth)  # choose working with tables and version 4 of API


def make_message(data: list) -> str:
    """format data for reading rules"""
    date = datetime.date.today()
    sms = f'{date}\n' \
          f'{data[0]}\n{data[1]} - {data[4]}/{data[7]}\n' \
          f'{data[2]} - {data[5]}/{data[8]}\n' \
          f'{data[3]} - {data[6]}/{data[9]}\n\n' \
          f'{data[10]}\n{data[11]} - {data[14]}/{data[17]}\n' \
          f'{data[12]} - {data[15]}/{data[18]}\n' \
          f'{data[13]} - {data[16]}/{data[19]}\n'
    return sms


def read_sheet() -> str:
    ranges = ["Для отправки!A1:C9"]
    spreadsheet = service.spreadsheets().values().batchGet(spreadsheetId=SPREADSHEETID,
                                                           ranges=ranges,
                                                           valueRenderOption='FORMATTED_VALUE',
                                                           ).execute()
    sheet_values = spreadsheet['valueRanges'][0]['values']
    all_data = []
    for i in sheet_values:
        all_data += [normalize('NFKD', x) for x in i]
    cooking_text = make_message(all_data)
    return cooking_text


# '''use this piece for getting access to a table for another user/email'''
# driveService = googleapiclient.discovery.build('drive', 'v3', http=httpAuth)  # choose working with \
#                                                                              # Google Drive and version 3 of API
# access = driveService.permissions().create(
#     fileId=spreadsheetId,
#     body={'type': 'user', 'role': 'writer', 'emailAddress': '.....@gmail.com'},  # open access for edit
#     fields='id'
# ).execute()


def message(sms):
    """send data to the telegram channel"""
    URL = (
        'https://api.telegram.org/bot{token}/sendMessage'.format(
            token=TOKEN))
    data = {'chat_id': CHAT,
            'text': sms
            }
    requests.post(URL, data=data)
    #print(sms)


if __name__ == "__main__":
    message(read_sheet())
