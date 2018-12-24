from bottle import route, run, request, error
import sentences
import json

demo = sentences.Demo()

@error(404)
def mistake404(code):
    return 'something error2!'

@route('/speech', method=['GET', 'POST'])
def do_post():
    params = request.body.read()
    try:
        params = eval(params.decode('utf-8'))
    except:
        params = {}
    sent = params['speech']

    global demo
    answer, ticket_info, total_nums, cur_flight, temp, day = demo.booking(sent)

    result = {}
    result['answer'] = answer
    result['speech'] = str(ticket_info)
    if cur_flight != []:
        result['total'] = total_nums
        result['flights'] = cur_flight[:1]
    else:
        result['total'] = 0
        result['flights'] = {}
    result['message'] = "SUCCESS"
    result['temp'] = temp
    result['day'] = day
    return json.dumps(result)

# run(host='192.168.2.152', port=8080)
run(host='127.0.0.1', port=8080)


# @route('/hello/<name>')
# def index(name):
#     return dict(name=name)
