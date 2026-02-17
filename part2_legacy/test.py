"""
part2_regecy - Assistants API Code Interpreter 테스트
(part1_regacy에서 검증된 코드를 기반으로 동일하게 테스트)

테스트 항목:
1. 간단한 수학 코드 실행 (2+2)
2. matplotlib 차트 생성 및 파일 다운로드 (savefig)
3. LangChain 도구 JSON 반환 형식 확인
"""

import os
import sys
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.code_interpreter import CodeInterpreterClient


def test_simple_math():
    """테스트 1: 간단한 수학 코드 실행"""
    print("=" * 60)
    print("테스트 1: 간단한 수학 코드 실행 (2+2)")
    print("=" * 60)

    code = "result = 2 + 2\nprint(f'2 + 2 = {result}')"

    print(f"[실행 코드]\n{code}\n")
    text_result, file_names = client.run(code)

    print(f"[텍스트 결과] {text_result}")
    print(f"[생성된 파일] {file_names}")

    assert text_result is not None, "텍스트 결과가 None입니다"
    assert "4" in text_result, f"결과에 '4'가 포함되어야 합니다. 실제: {text_result}"

    print("\n✅ 테스트 1 통과: 수학 코드 실행 성공\n")
    return True


def test_chart_generation():
    """테스트 2: matplotlib 차트 생성 및 파일 다운로드"""
    print("=" * 60)
    print("테스트 2: matplotlib 차트 생성 및 파일 다운로드")
    print("=" * 60)

    code = """
import matplotlib.pyplot as plt
import numpy as np

x = np.linspace(0, 2 * np.pi, 100)
y = np.sin(x)

fig, ax = plt.subplots(figsize=(8, 5))
ax.plot(x, y, 'b-', linewidth=2)
ax.set_title('Sine Wave')
ax.set_xlabel('x')
ax.set_ylabel('sin(x)')
ax.grid(True)
plt.savefig('/mnt/data/sine_wave.png', dpi=100, bbox_inches='tight')
plt.close()
print("차트를 /mnt/data/sine_wave.png 에 저장했습니다")
"""

    print(f"[실행 코드]\n{code}\n")
    text_result, file_names = client.run(code)

    print(f"[텍스트 결과] {text_result}")
    print(f"[생성된 파일] {file_names}")

    assert text_result is not None, "텍스트 결과가 None입니다"
    assert file_names is not None and len(file_names) > 0, \
        f"다운로드된 파일이 없습니다. file_names: {file_names}"

    for f in file_names:
        assert os.path.exists(f), f"파일이 존재하지 않습니다: {f}"
        file_size = os.path.getsize(f)
        assert file_size > 0, f"파일 크기가 0입니다: {f}"
        print(f"  📁 {f} ({file_size:,} bytes)")

    image_files = [f for f in file_names if f.endswith(('.png', '.jpeg', '.gif', '.webp'))]
    assert len(image_files) > 0, \
        f"이미지 파일이 없습니다. 다운로드된 파일: {file_names}"

    print(f"\n✅ 테스트 2 통과: 차트 생성 및 다운로드 성공 ({len(image_files)}개 이미지)\n")
    return True


def test_tools_json_return():
    """테스트 3: tools/code_interpreter.py의 JSON 반환 형식 확인"""
    print("=" * 60)
    print("테스트 3: LangChain 도구 JSON 반환 형식 확인")
    print("=" * 60)

    from tools.code_interpreter import code_interpreter_tool, set_code_interpreter_client

    set_code_interpreter_client(client)

    result = code_interpreter_tool.invoke({"code": "print(10 * 5)"})

    print(f"[도구 반환값] {result}")
    print(f"[반환 타입] {type(result)}")

    assert isinstance(result, str), \
        f"LangChain 도구는 문자열을 반환해야 합니다. 실제 타입: {type(result)}"

    parsed = json.loads(result)
    assert isinstance(parsed, list), f"JSON 파싱 결과가 list여야 합니다. 실제: {type(parsed)}"
    assert len(parsed) == 2, f"[text, files] 형태여야 합니다. 실제 길이: {len(parsed)}"

    text_result, file_names = parsed
    assert "50" in text_result, f"결과에 '50'이 포함되어야 합니다. 실제: {text_result}"
    assert isinstance(file_names, list), f"file_names가 list여야 합니다. 실제: {type(file_names)}"

    print(f"  text_result: {text_result}")
    print(f"  file_names: {file_names}")
    print("\n✅ 테스트 3 통과: JSON 반환 형식 정상\n")
    return True


if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    print(f"작업 디렉토리: {os.getcwd()}\n")

    print("🚀 Assistants API Code Interpreter 테스트 시작 (part2_regecy)")
    print(f"{'=' * 60}\n")

    print("CodeInterpreterClient 생성 중 (Assistant + Thread 생성)...")
    client = CodeInterpreterClient()
    print(f"  Assistant ID: {client.assistant_id}")
    print(f"  Thread ID: {client.thread_id}\n")

    results = {}
    tests = [
        ("간단한 수학 코드 실행", test_simple_math),
        ("차트 생성 및 다운로드", test_chart_generation),
        ("LangChain 도구 JSON 반환", test_tools_json_return),
    ]

    for name, test_func in tests:
        try:
            results[name] = test_func()
        except Exception as e:
            print(f"\n❌ 테스트 실패 [{name}]: {e}")
            import traceback
            traceback.print_exc()
            results[name] = False

    # 결과 요약
    print("\n" + "=" * 60)
    print("📊 테스트 결과 요약")
    print("=" * 60)
    for name, passed in results.items():
        status = "✅ 통과" if passed else "❌ 실패"
        print(f"  {status} - {name}")

    total = len(results)
    passed = sum(1 for v in results.values() if v)
    print(f"\n결과: {passed}/{total} 통과")

    try:
        client.openai_client.beta.assistants.delete(client.assistant_id)
        print(f"\n🧹 Assistant 정리 완료 (ID: {client.assistant_id})")
    except Exception as e:
        print(f"\n⚠️ Assistant 정리 실패: {e}")

    if passed < total:
        sys.exit(1)
