import json
try:
    import openai
except ImportError:  # openai might not be installed in environment
    openai = None


def call_large_model_api(system_prompt: str, text: str) -> dict:
    """Call a large model API with a prompt and text.
    This is a placeholder using OpenAI's API if available.
    Returns a dictionary with parsed result.
    """
    if openai is None:
        # Return dummy data when openai package not available
        return {
            'chinese': '示例',
            'english': 'example',
            'ppt_pages': '1-3',
            'description': 'dummy description'
        }

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": text},
    ]
    response = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=messages)
    content = response.choices[0].message.content
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        # fallback to raw text
        return {'raw': content}

