"""エージェントの配線テスト。

TestModel は実際のLLMを呼ばない偽モデルで、登録されたツールを全部呼んでから
ダミーの回答を返す。APIキーも利用枠も使わずに、
「ツールが登録され、呼ばれ、結果がモデルに戻るか」を確かめられる。
"""

from pydantic_ai import DeferredToolRequests
from pydantic_ai.messages import ToolCallPart, ToolReturnPart
from pydantic_ai.models.test import TestModel

from app import tools
from app.agent import agent

BASE_TOOLS = {"search_glossary", "get_lecture_summary", "make_quiz", "save_learning_log"}


def _parts(result, kind):
    return [p for m in result.all_messages() for p in m.parts if isinstance(p, kind)]


def test_base_tools_are_registered_and_called():
    model = TestModel()
    with agent.override(model=model):
        result = agent.run_sync("LoRAとは？")

    offered = {t.name for t in model.last_model_request_parameters.function_tools}
    assert BASE_TOOLS <= offered  # 演習でツールを足しても壊れないよう「含む」で判定

    called = {p.tool_name for p in _parts(result, ToolCallPart)}
    assert BASE_TOOLS <= called
    # 承認が必要なツール（requires_approval=True）は、実行されずに承認待ちになるので戻り値が無い
    waiting = len(result.output.approvals) if isinstance(result.output, DeferredToolRequests) else 0
    assert len(_parts(result, ToolReturnPart)) + waiting == len(_parts(result, ToolCallPart))
    assert isinstance(result.output, DeferredToolRequests)
    assert any(call.tool_name == "save_learning_log" for call in result.output.approvals)
    assert result.output


def test_glossary_result_reaches_the_model():
    model = TestModel(call_tools=["search_glossary"])
    with agent.override(model=model):
        result = agent.run_sync("RAGとは？")
    returns = _parts(result, ToolReturnPart)
    assert returns and returns[0].tool_name == "search_glossary"


def test_approved_learning_log_result_reaches_resumed_model(tmp_path, monkeypatch):
    monkeypatch.setattr(tools, "LEARNING_LOG_DIR", tmp_path / "learning_log")
    initial_model = TestModel(call_tools=["save_learning_log"])
    with agent.override(model=initial_model):
        pending = agent.run_sync("今日の学習を記録して")

    assert isinstance(pending.output, DeferredToolRequests)
    assert not tools.LEARNING_LOG_DIR.exists()
    approved = pending.output.build_results(
        approvals={call.tool_call_id: True for call in pending.output.approvals}
    )
    resumed_model = TestModel(call_tools=[])
    with agent.override(model=resumed_model):
        resumed = agent.run_sync(
            None,
            message_history=pending.all_messages(),
            deferred_tool_results=approved,
        )

    returns = [
        part for part in _parts(resumed, ToolReturnPart)
        if part.tool_name == "save_learning_log"
    ]
    assert tools.LEARNING_LOG_DIR.joinpath("learning_log.md").exists()
    assert returns and "保存しました" in returns[0].content
