import os
import json
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
from dotenv import load_dotenv

load_dotenv()
key = os.environ.get('GROQ_API_KEY')
model = os.environ.get('GROQ_MODEL', 'groq2o-mini')
url = f'https://api.groq.ai/v1/models/{model}/infer'
print('KEY SET:', bool(key))
print('MODEL:', model)
print('URL:', url)

payload = json.dumps({
    'input': 'Hola, responde OK.',
    'max_output_tokens': 50,
    'temperature': 0.3,
}).encode('utf-8')
headers = {
    'Authorization': f'Bearer {key}',
    'Content-Type': 'application/json',
}
req = Request(url, data=payload, headers=headers, method='POST')
try:
    with urlopen(req, timeout=30) as resp:
        body = resp.read().decode('utf-8')
        print('STATUS:', resp.status)
        print('BODY:', body)
        data = json.loads(body)
        print('PARSED:', data)
except HTTPError as e:
    print('HTTPERROR', e.code)
    try:
        print(e.read().decode('utf-8'))
    except Exception:
        pass
except URLError as e:
    print('URLERROR', e)
except Exception as e:
    print('ERROR', e)
