import streamlit as st
from langchain_core.tools import tool
from pydantic import BaseModel, Field


class ExecPythonInput(BaseModel):
    """타입을 지정하기 위한 클래스"""

    code: str = Field()


@tool(args_schema=ExecPythonInput)
def code_interpreter_tool(code):
    """
    Code Interpreter를 사용해 Python 코드를 실행합니다.

    - 데이터 가공, 시각화, 수식 계산, 통계 분석, 텍스트 분석에 적합합니다.
    - 인터넷 연결이 없어 외부 사이트 접근이나 라이브러리 설치는 불가합니다.
    - 코드 실행 결과와 생성 파일을 함께 확인할 수 있습니다.

    Returns:
    - text: Code Interpreter의 코드 실행 결과
    - files: Code Interpreter가 생성한 파일 경로 (`./files/` 이하)
    """

    print("\n\n=== Executing Code ===")
    print(code)
    print("=====================\n\n")
    return st.session_state.code_interpreter_client.run(code)
