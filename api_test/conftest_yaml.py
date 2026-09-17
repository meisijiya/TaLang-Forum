"""YAML 数据驱动 pytest fixture

约定：testcases/test_<name>_yaml.py 自动加载 data/<name>.yaml
通过 conftest_yaml 注入 `case` 参数。
"""
from pathlib import Path

import pytest
import yaml


def load_yaml_cases(yaml_file: str) -> list:
    """从 data/<yaml_file> 加载 cases 列表"""
    yaml_path = Path(__file__).parent / "data" / yaml_file
    if not yaml_path.exists():
        return []
    with open(yaml_path, encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    return data.get("cases", [])


def pytest_generate_tests(metafunc):
    """自动 parametrize test_*_yaml.py 的 `case` 参数"""
    if "case" not in metafunc.fixturenames:
        return
    module = metafunc.module.__name__
    if not (module.startswith("test_") and module.endswith("_yaml")):
        return
    yaml_name = module[5:-5] + ".yaml"  # test_login_yaml → login.yaml
    cases = load_yaml_cases(yaml_name)
    if not cases:
        return
    ids = [c.get("id", f"case-{i}") for i, c in enumerate(cases)]
    metafunc.parametrize("case", cases, ids=ids)
