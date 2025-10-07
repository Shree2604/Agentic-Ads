#!/usr/bin/env python3
import requests

# Test without authentication
print('Testing without authentication...')
try:
    response = requests.post('https://api-inference.huggingface.co/models/gpt2',
                           json={'inputs': 'Hello'}, timeout=10)
    print(f'Status: {response.status_code}')
    print(f'Response: {response.text[:200]}')
except Exception as e:
    print(f'Error: {e}')

print()

# Test if the model exists on the Hub
print('Testing model existence on Hub...')
try:
    response = requests.get('https://huggingface.co/api/models/gpt2', timeout=10)
    print(f'Hub Status: {response.status_code}')
    if response.status_code == 200:
        data = response.json()
        print(f'Model exists: {data.get("id", "unknown")}')
        print(f'Private: {data.get("private", True)}')
        print(f'Pipeline: {data.get("pipeline_tag", "none")}')
except Exception as e:
    print(f'Error: {e}')
