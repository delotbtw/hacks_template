from pathlib import Path

from scripts.export_openapi import CONTRACT_PATH, render


def test_openapi_contract_is_up_to_date():
    assert Path(CONTRACT_PATH).exists(), "contracts/openapi.json отсутствует: make contracts"
    assert Path(CONTRACT_PATH).read_text() == render(), (
        "Контракт устарел: выполните `make contracts`"
    )
