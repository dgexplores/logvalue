"""Small AST rules that produce auditable source findings, never auto-fixes."""

from __future__ import annotations

import ast
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass(frozen=True)
class StaticFinding:
    rule: str
    line: int
    message: str


class _Visitor(ast.NodeVisitor):
    def __init__(self) -> None:
        self.findings: list[StaticFinding] = []

    def visit_Call(self, node: ast.Call) -> None:
        name = node.func.id if isinstance(node.func, ast.Name) else getattr(node.func, "attr", "")
        if name == "print":
            self.findings.append(StaticFinding("print-instead-of-logger", node.lineno, "Use the application logger instead of print."))
        if name in {"debug", "info", "warning", "warn", "error", "exception", "critical"} and node.args:
            first = node.args[0]
            if isinstance(first, ast.JoinedStr):
                self.findings.append(StaticFinding("interpolated-log-message", node.lineno, "Prefer parameterised log messages over f-strings."))
            elif isinstance(first, ast.BinOp) and isinstance(first.op, ast.Add):
                self.findings.append(StaticFinding("concatenated-log-message", node.lineno, "Prefer parameterised log messages over string concatenation."))
        self.generic_visit(node)


def scan_python(path: Path) -> list[StaticFinding]:
    """Return findings for a Python source file; invalid syntax is surfaced."""
    visitor = _Visitor()
    visitor.visit(ast.parse(path.read_text(encoding="utf-8"), filename=str(path)))
    return visitor.findings


def findings_as_dicts(findings: list[StaticFinding]) -> list[dict[str, object]]:
    return [asdict(finding) for finding in findings]
