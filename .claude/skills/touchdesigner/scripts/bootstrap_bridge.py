# Claude <-> TouchDesigner HTTP 橋接 bootstrap
# 用法：在 TD 的 Textport（Alt+T）貼上全文執行一次，
# 然後 File > Save 存成 claude_bridge.toe，之後可直接用該檔啟動 TD。
#
# 建立 /claude_bridge (Base COMP)：
#   - webserver1 (WebServer DAT, port 9981)
#   - handler   (Text DAT, callbacks)
# Claude 端 POST {"code": "..."} 到 http://127.0.0.1:9981/exec，
# 程式碼於 TD 全域執行，變數 result 會被序列化回傳。

HANDLER_CODE = '''
import json
import traceback

def onHTTPRequest(webServerDAT, request, response):
    if request['uri'] != '/exec' or request['method'] != 'POST':
        response['statusCode'] = 404
        response['statusReason'] = 'Not Found'
        response['data'] = json.dumps({'ok': False, 'error': 'POST /exec only'})
        return response
    try:
        payload = json.loads(request['data'])
        scope = {'result': None}
        exec(payload['code'], globals(), scope)
        response['statusCode'] = 200
        response['statusReason'] = 'OK'
        response['data'] = json.dumps({'ok': True, 'result': repr(scope.get('result'))})
    except Exception:
        response['statusCode'] = 200
        response['statusReason'] = 'OK'
        response['data'] = json.dumps({'ok': False, 'error': traceback.format_exc()})
    return response
'''

root = op('/')
bridge = root.op('claude_bridge') or root.create(baseCOMP, 'claude_bridge')

handler = bridge.op('handler') or bridge.create(textDAT, 'handler')
handler.text = HANDLER_CODE

ws = bridge.op('webserver1') or bridge.create(webserverDAT, 'webserver1')
ws.par.port = 9981
ws.par.callbacks = 'handler'
ws.par.active = False
ws.par.active = True

print('[claude_bridge] ready on http://127.0.0.1:9981/exec')
