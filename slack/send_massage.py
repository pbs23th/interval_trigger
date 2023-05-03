import json
import datetime
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

slack_token = 'xoxb-2952903029057-4087212464261-tEfPQI531QHQCSXIPArMdjVH' # Bot OAuth Token
client = WebClient(token=slack_token)


def send_message(data):
    try:
        msg = dataphase(data)
        response = client.chat_postMessage(
            channel="dantaro_perpetual", # Channel ID
            text='perpetual 에러',
            blocks=msg,
        )

    except SlackApiError as e:
        print('Error: {}'.format(e.response['error']))
        assert e.response["error"]

def dataphase(data):
    time = str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    data = [
		{
			"type": "header",
			"text": {
				"type": "plain_text",
				"text": "트리거 발동",
				"emoji": True
			}
		},
		{
			"type": "section",
			"text": {
				"type": "mrkdwn",
				"text": "발생 시간 : "+ time
			}
		},
		{
			"type": "section",
			"text": {
				"type": "mrkdwn",
				"text": "거래소 : " + data['exchange']
			}
		},
		{
			"type": "section",
			"text": {
				"type": "mrkdwn",
				"text": "모드 : " + data['mode']
			}
		},
		{
			"type": "section",
			"text": {
				"type": "mrkdwn",
				"text": "마켓 : " + data['market']
			}
		},
		{
			"type": "section",
			"text": {
				"type": "mrkdwn",
				"text": "간격 : " + str(data['interval']) + '%'
			}
		},
		{
			"type": "section",
			"text": {
				"type": "mrkdwn",
				"text": "현재가격 : " + str(data['price'])
			}
		},
		{
			"type": "divider"
		}
	]
    return data


if __name__ == '__main__':
	respone_data = {
		'exchange': 'upbit',
		'mode': 'spot',
		'market': 'KRW-BTC',
		'interval': '1',
		'price': '132165', }

	send_message(respone_data)
