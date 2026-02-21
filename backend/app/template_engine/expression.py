from __future__ import annotations

import ast
from collections.abc import Mapping
from typing import Any


class UnsafeExpressionError(ValueError):
    pass


_ALLOWED_COMPARE_NODES = (ast.Eq, ast.NotEq, ast.In, ast.NotIn, ast.Gt, ast.GtE, ast.Lt, ast.LtE)


class SafeBooleanEvaluator:
    """Evaluate a restricted boolean expression against a context mapping."""

    def evaluate(self, expression: str | None, context: Mapping[str, Any]) -> bool:
        if expression is None or expression.strip() == "":
            return False
        tree = ast.parse(expression, mode="eval")
        return bool(self._eval_node(tree.body, context))

    def _eval_node(self, node: ast.AST, context: Mapping[str, Any]) -> Any:
        if isinstance(node, ast.BoolOp):
            values = [self._eval_node(value, context) for value in node.values]
            if isinstance(node.op, ast.And):
                return all(values)
            if isinstance(node.op, ast.Or):
                return any(values)
            raise UnsafeExpressionError(f"Unsupported boolean operator: {ast.dump(node.op)}")

        if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.Not):
            return not bool(self._eval_node(node.operand, context))

        if isinstance(node, ast.Compare):
            left = self._eval_node(node.left, context)
            for op, comparator in zip(node.ops, node.comparators):
                if not isinstance(op, _ALLOWED_COMPARE_NODES):
                    raise UnsafeExpressionError(f"Unsupported comparison operator: {ast.dump(op)}")
                right = self._eval_node(comparator, context)
                if isinstance(op, ast.Eq):
                    ok = left == right
                elif isinstance(op, ast.NotEq):
                    ok = left != right
                elif isinstance(op, ast.In):
                    ok = left in right
                elif isinstance(op, ast.NotIn):
                    ok = left not in right
                elif isinstance(op, ast.Gt):
                    ok = left > right
                elif isinstance(op, ast.GtE):
                    ok = left >= right
                elif isinstance(op, ast.Lt):
                    ok = left < right
                else:
                    ok = left <= right

                if not ok:
                    return False
                left = right
            return True

        if isinstance(node, ast.Name):
            if node.id in {"True", "False", "None"}:
                return {"True": True, "False": False, "None": None}[node.id]
            return context.get(node.id)

        if isinstance(node, ast.Constant):
            return node.value

        if isinstance(node, ast.List):
            return [self._eval_node(elt, context) for elt in node.elts]

        if isinstance(node, ast.Tuple):
            return tuple(self._eval_node(elt, context) for elt in node.elts)

        raise UnsafeExpressionError(f"Unsupported expression node: {ast.dump(node)}")
