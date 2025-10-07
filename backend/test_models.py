#!/usr/bin/env python3
"""
Quick test script to find working HuggingFace models
"""

import os
import requests
import time
from dotenv import load_dotenv

load_dotenv()

def test_single_model(model_name):
    """Test a single model"""
    token = os.getenv('HUGGINGFACE_API_TOKEN')
    if not token:
        print("No API token found!")
        return False

    url = f"https://api-inference.huggingface.co/models/{model_name}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    try:
        print(f"Testing {model_name}...")
        response = requests.post(
            url,
            headers=headers,
            json={"inputs": "Hello world", "parameters": {"max_new_tokens": 10}},
            timeout=15
        )

        print(f"  Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            if isinstance(result, list) and len(result) > 0:
                text = result[0].get('generated_text', '')
                print(f"  SUCCESS! Generated: {text[:100]}...")
                return True
        elif response.status_code == 503:
            print("  Model is loading (503) - might work after waiting")
            return "loading"
        else:
            print(f"  Failed: {response.text[:200]}")

    except Exception as e:
        print(f"  Error: {str(e)[:100]}")

    return False

def main():
    """Test multiple models to find one that works"""
    print("Testing HuggingFace models...")
    print("=" * 50)

    # Test models one by one
    models = [
        "gpt2",
        "distilgpt2",
        "gpt2-medium",
        "EleutherAI/gpt-neo-125M",
        "google/flan-t5-small",
        "facebook/opt-125m"
    ]

    working_models = []

    for model in models:
        result = test_single_model(model)
        if result == True:
            working_models.append(model)
        elif result == "loading":
            print(f"  {model} might work after loading...")
            working_models.append(model)

        print()  # Empty line between tests
        time.sleep(1)  # Brief pause

    print("SUMMARY:")
    print(f"Found {len(working_models)} potentially working models:")
    for model in working_models:
        print(f"  - {model}")

    if not working_models:
        print("No working models found. The system will use template-based generation.")
        print("This is still effective for creating ads!")

if __name__ == "__main__":
    main()
