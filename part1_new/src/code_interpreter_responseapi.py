import os
import mimetypes
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()


class CodeInterpreterClient:
    """
    Responses API 기반 Code Interpreter Client
    (단발성 예제용, 컨테이너 1회 생성)
    """

    def __init__(self):
        self.client = OpenAI()
        self._create_file_directory()

        # 컨테이너 1회 생성
        container = self.client.containers.create(name="code-interpreter-example")
        self.container_id = container.id  # cntr_XXXX

    def _create_file_directory(self):
        os.makedirs("./files/", exist_ok=True)

    def upload_file(self, file_content):
        file = self.client.files.create(
            file=file_content,
            purpose="assistants",
        )
        return file.id

    def run(self, code: str):
        response = self.client.responses.create(
            model="gpt-4.1",
            input=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "input_text",
                            "text": f"""
아래 Python 코드를 실행하고 결과만 반환하세요.
설명이나 해석은 하지 마세요.

```python
{code}
```
""",
                        }
                    ],
                }
            ],
            tools=[
                {
                    "type": "code_interpreter",
                    "container": self.container_id,
                }
            ],
            tool_choice="auto",
        )

        text_output = ""
        file_paths = []

        for item in response.output:
            if item.type == "message":
                for c in item.content:
                    if c.type == "output_text":
                        text_output += c.text

            if item.type == "tool_result" and item.tool_name == "code_interpreter":
                for f in item.files or []:
                    file_paths.append(self._save_file(f))

        return text_output, file_paths

    def _save_file(self, file_obj):
        file_id = file_obj["file_id"]
        data = self.client.files.content(file_id).read()

        mime_type = mimetypes.guess_type(file_id)[0] or "application/octet-stream"
        ext = mimetypes.guess_extension(mime_type) or ""

        path = f"./files/{file_id}{ext}"
        with open(path, "wb") as f:
            f.write(data)

        return path
