from bottle import route, run, template, request, error

import json

# @route('/hello/<name>')
# def index(name):
#     return dict(name=name)
@error(403)
def mistake403(code):
    return 'The parameter you passed has the wrong format!'

@error(404)
def mistake404(code):
    return 'Sorry, this page does not exist!'

@route('/speech', method=['GET', 'POST'])
def Login():
    params = request.body.read()
    try:
        params = eval(params.decode('utf-8')) # json.loads(params)
    except:
        params = {}
    #  print(params.get("phone", None))
    print(params)
    print(type(params))
    ret = {}

    ret["status"] = 1  # 返回成功状态码
    ret["token"] = u'test' # 返回token 只要你登陆成功，服务端就返回一个token(就是密钥) 与服务器交流就把这个token带上
    return json.dumps(ret)   # dict->str   loads str->dict

run(host='localhost', port=8080)
