# coding:utf-8
from bottle import route, run, request, error
import sentences
import json

demo = sentences.Demo()

@error(404)
def mistake404(code):
    return 'something error2!'

@route('/speechprocessing', method=['GET', 'POST'])
def do_post():
    global demo
    params = request.body.read()
    try:
        params = eval(params.decode('utf-8'))
    except:
        params = {}
    sent = params['speech']

    answer, ticket_info, total_nums, cur_flight, temp, day = demo.booking(sent)

    try:
        result = {}
#	ss = "{'nticket':}"
        result['answer'] = answer
        result['speech'] = json.JSONEncoder().encode(ticket_info)
        result['message'] = "SUCCESS"
        # result['temp'] = temp
        # result['day'] = day

        if cur_flight != []:
            result['total'] = total_nums
            result['flights'] = cur_flight
        else:
            result['total'] = 0
            result['flights'] = {}
# 	print(result)
    except:
        result = {}

    return json.dumps(result)

# run(host='192.168.2.152', port=8080)
run(host='172.31.27.214', port=80)
