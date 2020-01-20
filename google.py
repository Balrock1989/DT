import httplib2
import apiclient.discovery
from oauth2client.service_account import ServiceAccountCredentials
from auth import CREDENTIALS_FILE

credentials = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE,
                                                               ['https://www.googleapis.com/auth/spreadsheets',
                                                                'https://www.googleapis.com/auth/drive'])
httpAuth = credentials.authorize(httplib2.Http())
service = apiclient.discovery.build('sheets', 'v4', http=httpAuth)
spreadsheet = service.spreadsheets().create(body={
    'properties': {'title': 'Акции', 'locale': 'ru_RU'},
    'sheets': [{'properties': {'sheetType': 'GRID',
                               'sheetId': 0,
                               'title': 'Акции',
                               'gridProperties': {'columnCount': 9}}}]
}).execute()
driveService = apiclient.discovery.build('drive', 'v3', http=httpAuth)
shareRes = driveService.permissions().create(
    fileId=spreadsheet['spreadsheetId'],
    body={'type': 'anyone', 'role': 'reader'},  # доступ на чтение кому угодно
    fields='id'
).execute()

print(spreadsheet)
