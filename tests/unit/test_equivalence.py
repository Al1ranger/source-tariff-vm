"""Pure-function tests: equality may not tolerate consequential differences."""
import ast
from pathlib import Path


def test_validator_rejects_operand_and_decision_disagreement():
    source = Path("contracts/SourceTariffVM.py").read_text(encoding="utf-8")
    function = next(node for node in ast.parse(source).body
                    if isinstance(node, ast.FunctionDef) and node.name == "compilation_equal")
    namespace = {}
    exec(compile(ast.Module(body=[function], type_ignores=[]), "equivalence", "exec"), namespace)
    equal = namespace["compilation_equal"]
    leader = {"state": "COMPILED", "code": {"scope": "EACH", "rate": 12000}}
    assert equal(leader, leader.copy())
    assert not equal(leader, {**leader, "state": "UNSUPPORTED"})
    assert not equal(leader, {**leader, "code": {"scope": "TOTAL", "rate": 12000}})
    assert not equal(leader, {**leader, "code": {"scope": "EACH", "rate": 12001}})
    assert not equal(None, None)
