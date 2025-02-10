from dataclasses import dataclass
from typing import List, Union, Dict, Any
from enum import Enum


class Operator(Enum):
    EQUALS = "eq"
    NOT_EQUALS = "ne"
    CONTAINS = "contains"
    NOT_CONTAINS = "not_contains"
    GREATER_THAN = "gt"
    LESS_THAN = "lt"
    IN = "in"
    NOT_IN = "not_in"
    STARTS_WITH = "starts_with"
    ENDS_WITH = "ends_with"


class LogicalOperator(Enum):
    AND = "and"
    OR = "or"


@dataclass
class Condition:
    field: str
    operator: Operator
    value: Any


class Filter:
    def __init__(self, rules):
        """
        初始化过滤器
        :param rules: 过滤规则列表或JSON字符串
        """
        self.rules = rules if isinstance(rules, list) else []

    def check(self, target_obj=None):
        """
        检查目标对象是否符合过滤规则
        :param target_obj: 要检查的目标对象
        :return: bool
        """
        if not self.rules:
            return True

        for rule in self.rules:
            key = rule.get('key')
            operator = rule.get('operator')
            value = rule.get('value')
            logic = rule.get('logic')

            if not all([key, operator, value]):
                continue

            # 从目标对象获取要检查的值
            target_value = target_obj.get(key) if isinstance(target_obj, dict) else getattr(target_obj, key, None)

            result = self._compare(target_value, operator, value)

            if logic == 'and' and not result:
                return False
            if logic == 'or' and result:
                return True

        return True

    def _compare(self, target_value, operator, value):
        """
        比较逻辑实现
        :param target_value: 目标值
        :param operator: 操作符
        :param value: 比较值
        :return: bool
        """
        if target_value is None:
            return False

        if operator == 'contains':
            return str(value).lower() in str(target_value).lower()
        elif operator == 'not_contains':
            return str(value).lower() not in str(target_value).lower()
        elif operator == 'eq':
            return str(target_value).lower() == str(value).lower()
        elif operator == 'ne':
            return str(target_value).lower() != str(value).lower()
        elif operator == 'starts_with':
            return str(target_value).lower().startswith(str(value).lower())
        elif operator == 'ends_with':
            return str(target_value).lower().endswith(str(value).lower())

        return False