from datetime import datetime, timedelta

def getMessageData(messages, period):
    message_chunks = []
    start = datetime.now()
    end = datetime.now()-timedelta(days=period)
    for i in range(5):
        message_chunks.append([message.correct for message in messages if message.timestamp > end and message.timestamp < start])
        start = end
        end = start-timedelta(days=period)

    return message_chunks[::-1]

def getDateChunks(period):
	date_chunks = []
	current = datetime.now()
	for i in range(5):
	    date_chunks.append("{}/{}".format(current.month, current.day))
	    current = current-timedelta(hours=24*period)
	return date_chunks[::-1]