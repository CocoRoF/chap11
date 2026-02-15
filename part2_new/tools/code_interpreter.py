from langchain_core.tools import tool
from pydantic import BaseModel, Field


# 모듈 레벨 변수 - LangGraph가 별도 스레드에서 tool을 실행하므로
# st.session_state 대신 이 변수를 통해 client에 접근
_code_interpreter_client = None


def set_code_interpreter_client(client):
    """main.py에서 세션 초기화 시 호출하여 client를 설정"""
    global _code_interpreter_client
    _code_interpreter_client = client


class ExecPythonInput(BaseModel):
    """타입을 지정하기 위한 클래스"""

    code: str = Field()


@tool(args_schema=ExecPythonInput)
def code_interpreter_tool(code):
    """
    Code Interpreter를 사용하여 Python 코드를 실행합니다.
    - 아래와 같은 작업에 적합합니다.
      - pandas 및 matplotlib 등의 라이브러리를 사용한 데이터 가공 및 시각화
      - 수식 계산 및 통계 분석
      - 자연어 처리 라이브러리를 활용한 텍스트 데이터 분석도 가능
    - Code Interpreter는 인터넷에 연결되지 않습니다
      - 외부 웹사이트 정보를 읽거나 새 라이브러리를 설치할 수 없습니다
    - Code Interpreter가 작성한 코드를 함께 출력하도록 요구하면 좋습니다
      - 결과 검증을 사용자가 더 쉽게 할 수 있습니다
    - 어느 정도 코드가 틀려도 자동으로 수정해줄 때가 있습니다

    Returns:
    - text: Code Interpreter가 출력한 텍스트 (주로 코드 실행 결과)
    - files: Code Interpreter가 저장한 파일의 경로
        - 파일은 `./files/` 아래에 저장됩니다.
    """
    print("\n\n=== Executing Code ===")
    print(code)
    print("=====================\n\n")
    return _code_interpreter_client.run(code)
