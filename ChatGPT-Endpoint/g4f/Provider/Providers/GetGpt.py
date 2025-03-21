import os
import json
import uuid
import requests
from ...typing import sha256, Dict, get_type_hints

url = 'https://chat.getgpt.world/'
model = ['gpt-3.5-turbo']
supports_stream = True
needs_auth = False

def _create_completion(model: str, messages: list, stream: bool, **kwargs):
    headers = {
        'Content-Type': 'application/json',
        'Referer': 'https://chat.getgpt.world/',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'
    }

    data = json.dumps({
        'messages': messages,
        'frequency_penalty': kwargs.get('frequency_penalty', 0),
        'max_tokens': kwargs.get('max_tokens', 4000),
        'model': 'gpt-3.5-turbo',
        'presence_penalty': kwargs.get('presence_penalty', 0),
        'temperature': kwargs.get('temperature', 1),
        'top_p': kwargs.get('top_p', 1),
        'stream': True,
        'uuid': str(uuid.uuid4())
    })

    res = requests.post('https://chat.getgpt.world/api/chat/stream', 
                        headers=headers, json={'signature': data}, stream=True)

    for line in res.iter_lines():
        if b'content' in line:
            line_json = json.loads(line.decode('utf-8').split('data: ')[1])
            yield (line_json['choices'][0]['delta']['content'])


params = f'g4f.Providers.{os.path.basename(__file__)[:-3]} supports: ' + \
    '(%s)' % ', '.join(
        [f'{name}: {get_type_hints(_create_completion)[name].__name__}' for name in _create_completion.__code__.co_varnames[:_create_completion.__code__.co_argcount]])
