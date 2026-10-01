import hashlib
import json

BODY = b"Jobs use whole minutes; round each partial job UP. Linux costs USD 0.012 per minute."
SOURCE_HASH = hashlib.sha256(BODY).hexdigest()
ARGS = ("github", "docs", "a" * 40, "content/rates.md", SOURCE_HASH, "linux_4_core")
ANSWER = {"supported": True, "unit_seconds": 60, "rounding": "CEIL", "scope": "EACH",
          "minimum_units": 0, "rates": [{"sku": "linux_4_core", "microusd_per_unit": 12000}]}


def compiler(vm, answer=ANSWER, status=200, body=BODY):
    vm.mock_web(r".*raw\.githubusercontent\.com.*", {"status": status, "body": body})
    vm.mock_llm(r"(?s).*Compile a metered USD tariff.*", json.dumps(answer))


def installed(c, vm, sender):
    vm.sender = sender
    compiler(vm)
    key = c.compile_program(*ARGS)
    report = json.loads(c.get_compilation(key))
    return key, report["program_root"]


def test_compilation_affects_rounding_and_quote(direct_vm, direct_deploy, direct_alice):
    c = direct_deploy("contracts/SourceTariffVM.py")
    key, root = installed(c, direct_vm, direct_alice)
    result = json.loads(c.quote(root, "linux_4_core", "61,61"))
    assert result["billed_units"] == [2, 2]
    assert result["charge_microusd"] == 48000
    assert json.loads(c.get_compilation(key))["state"] == "COMPILED"
    assert c.history_count() == 1


def test_total_scope_is_different_executable_program(direct_vm, direct_deploy, direct_alice):
    c = direct_deploy("contracts/SourceTariffVM.py")
    direct_vm.sender = direct_alice
    compiler(direct_vm, {**ANSWER, "scope": "TOTAL"})
    key = c.compile_program(*ARGS)
    root = json.loads(c.get_compilation(key))["program_root"]
    assert json.loads(c.quote(root, "linux_4_core", "61,61"))["charge_microusd"] == 36000


def test_source_hash_mismatch_installs_nothing(direct_vm, direct_deploy, direct_alice):
    c = direct_deploy("contracts/SourceTariffVM.py")
    direct_vm.sender = direct_alice
    compiler(direct_vm, body=b"Manipulated rate schedule")
    key = c.compile_program(*ARGS)
    report = json.loads(c.get_compilation(key))
    assert report["state"] == "HASH_MISMATCH" and report["program_root"] == ""
    with direct_vm.expect_revert("no installed program"):
        c.quote(report["report_root"], "linux_4_core", "61")


def test_semantic_unsupported_has_no_executable_artifact(direct_vm, direct_deploy, direct_alice):
    c = direct_deploy("contracts/SourceTariffVM.py")
    direct_vm.sender = direct_alice
    compiler(direct_vm, {"supported": False})
    key = c.compile_program(*ARGS)
    report = json.loads(c.get_compilation(key))
    assert report["state"] == "UNSUPPORTED" and report["artifact"]["code"] is None
    with direct_vm.expect_revert("compilation is terminal"):
        c.compile_program(*ARGS)


def test_unavailable_retries_preserve_attempt_history(direct_vm, direct_deploy, direct_alice):
    c = direct_deploy("contracts/SourceTariffVM.py")
    direct_vm.sender = direct_alice
    compiler(direct_vm, status=503)
    key = c.compile_program(*ARGS)
    assert json.loads(c.get_compilation(key))["state"] == "UNAVAILABLE"
    direct_vm.clear_mocks()
    compiler(direct_vm)
    assert c.compile_program(*ARGS) == key
    assert c.history_count() == 2
    assert json.loads(c.get_history(0))["state"] == "UNAVAILABLE"
    assert json.loads(c.get_history(1))["attempt"] == 2


def test_terminal_artifact_cannot_be_resampled(direct_vm, direct_deploy, direct_alice):
    c = direct_deploy("contracts/SourceTariffVM.py")
    installed(c, direct_vm, direct_alice)
    with direct_vm.expect_revert("compilation is terminal"):
        c.compile_program(*ARGS)


def test_quote_receipts_are_principal_bound_and_replay_safe(direct_vm, direct_deploy, direct_alice, direct_bob):
    c = direct_deploy("contracts/SourceTariffVM.py")
    _, root = installed(c, direct_vm, direct_alice)
    alice_root = c.record_quote(root, "linux_4_core", "61,61", "quote-one")
    original = c.get_receipt(direct_alice, "quote-one")
    with direct_vm.expect_revert("receipt nonce already used"):
        c.record_quote(root, "linux_4_core", "1", "quote-one")
    direct_vm.sender = direct_bob
    bob_root = c.record_quote(root, "linux_4_core", "1", "quote-one")
    assert alice_root != bob_root
    assert c.get_receipt(direct_alice, "quote-one") == original


def test_unknown_sku_and_invalid_durations_cannot_quote(direct_vm, direct_deploy, direct_alice):
    c = direct_deploy("contracts/SourceTariffVM.py")
    _, root = installed(c, direct_vm, direct_alice)
    with direct_vm.expect_revert("SKU absent"):
        c.quote(root, "invented", "1")
    for bad in ("0", "-1", "1.5", "2592001", ",", "1," * 33 + "1"):
        with direct_vm.expect_revert("[EXPECTED]"):
            c.quote(root, "linux_4_core", bad)


def test_malformed_model_cannot_install_unsafe_opcodes(direct_vm, direct_deploy, direct_alice):
    c = direct_deploy("contracts/SourceTariffVM.py")
    direct_vm.sender = direct_alice
    compiler(direct_vm, {**ANSWER, "rounding": "EXEC_PYTHON"})
    with direct_vm.expect_revert("unsupported opcode"):
        c.compile_program(*ARGS)


def test_duplicate_skus_and_path_escape_rejected(direct_vm, direct_deploy, direct_alice):
    c = direct_deploy("contracts/SourceTariffVM.py")
    direct_vm.sender = direct_alice
    with direct_vm.expect_revert("distinct exact SKU"):
        c.compile_program(*ARGS[:-1], "linux_4_core,linux_4_core")
    with direct_vm.expect_revert("invalid pinned source"):
        c.compile_program("github", "docs", "a" * 40, "../private", SOURCE_HASH, "linux_4_core")
