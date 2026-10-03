from urllib.request import Request, urlopen
import json


def generate(model: str, prompt: str, endpoint: str = "http://127.0.0.1:11434") -> dict:
    body = json.dumps({"model": model, "prompt": prompt, "stream": False}).encode()
    req = Request(endpoint.rstrip("/") + "/api/generate", data=body,
                  headers={"Content-Type": "application/json"}, method="POST")
    with urlopen(req, timeout=600) as response:
        return json.load(response)
