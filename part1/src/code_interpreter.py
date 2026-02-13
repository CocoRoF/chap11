import os

import mimetypes
import traceback
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()


class CodeInterpreterClient:
    """
    OpenAI의 Assistants API의 Code Interpreter Tool을 사용하여
    Python 코드를 실행하거나 파일을 읽고 분석을 수행하는 클래스

    이 클래스는 다음 기능을 제공합니다：
    1. OpenAI Assistants API를 사용한 Python 코드 실행
    2. 파일 업로드 및 Assistants API로의 등록
    3. 업로드한 파일을 사용한 데이터 분석 및 그래프 생성

    주요 메서드：
    - upload_file(file_content): 파일을 업로드하여 Assistants API에 등록한다
    - run(prompt): Assistants API를 사용해 Python 코드를 실행하거나 파일 분석을 수행한다

    Example:
    ===============
    from src.code_interpreter import CodeInterpreter
    code_interpreter = CodeInterpreter()
    code_interpreter.upload_file(open('file.csv', 'rb').read())
    code_interpreter.run("file.csv의 내용을 읽어서 그래프를 그려주세요")
    """

    def __init__(self):
        self.file_ids = []
        self.openai_client = OpenAI()
        self.assistant_id = self._create_assistant_agent()
        self.thread_id = self._create_thread()
        self._create_file_directory()
        self.code_intepreter_instruction = """
        제공된 데이터 분석용 Python 코드를 실행해주세요.
        실행한 결과를 반환해주세요. 당신의 분석 결과는 필요하지 않습니다.
        다시 한 번 반복합니다, 실행한 결과를 반환해주세요.
        파일 경로 등이 조금 틀려 있을 경우에는 적절히 수정해주세요.
        수정한 경우에는 수정 내용을 설명해주세요.
        """

    def _create_file_directory(self):
        directory = "./files/"
        os.makedirs(directory, exist_ok=True)

    def _create_assistant_agent(self):
        self.assistant = self.openai_client.beta.assistants.create(
            name="Python Code Runner",
            instructions="You are a python code runner. Write and run code to answer questions.",
            tools=[{"type": "code_interpreter"}],
            model="gpt-4o",
            tool_resources={"code_interpreter": {"file_ids": self.file_ids}},
        )
        return self.assistant.id

    def _create_thread(self):
        thread = self.openai_client.beta.threads.create()
        return thread.id

    def upload_file(self, file_content):
        """
        Upload file to assistant agent
        Args:
            file_content (_type_): open('file.csv', 'rb').read()
        """
        file = self.openai_client.files.create(file=file_content, purpose="assistants")
        self.file_ids.append(file.id)
        # Assistant에 새로운 파일을 추가하여 업데이트한다
        self._add_file_to_assistant_agent()
        return file.id

    def _add_file_to_assistant_agent(self):
        self.assistant = self.openai_client.beta.assistants.update(
            assistant_id=self.assistant_id,
            tool_resources={"code_interpreter": {"file_ids": self.file_ids}},
        )

    def run(self, code):

        prompt = f"""
        다음 코드를 실행하고 결과를 반환해 주세요. 
        ```python
        {code}
        ```
        **중요 규칙**:
        - 생성된 이미지나 파일을 언급할 때 경로(/mnt/data/xxx.png)를 사용하지 마세요
        - 대신 "이미지를 생성했습니다" 정도로만 언급하고, 파일은 자동으로 첨부됩니다
        - 코드 실행 결과만 반환해주세요
        """

        # add message to thread
        self.openai_client.beta.threads.messages.create(
            thread_id=self.thread_id, role="user", content=prompt
        )

        # run assistant to get response
        run = self.openai_client.beta.threads.runs.create_and_poll(
            thread_id=self.thread_id,
            assistant_id=self.assistant_id,
            instructions=self.code_intepreter_instruction,
        )
        if run.status == "completed":
            message = self.openai_client.beta.threads.messages.list(
                thread_id=self.thread_id, limit=1  # Get the last message
            )
            try:
                file_ids = []
                for content in message.data[0].content:
                    if content.type == "text":
                        text_content = content.text.value
                        for annotation in content.text.annotations:
                            file_path = getattr(annotation, "file_path", None)
                            file_id = getattr(file_path, "file_id", None)
                            if file_id:
                                file_ids.append(file_id)
                    elif content.type == "image_file":
                        image_file_id = getattr(content.image_file, "file_id", None)
                        if image_file_id:
                            file_ids.append(image_file_id)
                    else:
                        raise ValueError("Unknown content type")
            except:
                print(traceback.format_exc())
                return None, None
        else:
            raise ValueError("Run failed")

        file_names = []
        if file_ids:
            for file_id in file_ids:
                if not file_id:
                    continue
                file_names.append(self._download_file(file_id))

        return text_content, file_names

    def _download_file(self, file_id):
        data = self.openai_client.files.content(file_id)
        data_bytes = data.read()

        mime_type = mimetypes.guess_type(file_id)[0] or "application/octet-stream"

        # MIME 타입에서 확장자를 가져옴
        extension = mimetypes.guess_extension(mime_type)

        # 확장자를 가져올 수 없는 경우 기본 확장자를 사용
        if not extension:
            extension = ""

        file_name = f"./files/{file_id}{extension}"
        with open(file_name, "wb") as file:
            file.write(data_bytes)

        return file_name
