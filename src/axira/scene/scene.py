from .operator import ExecuteSceneOperator


class SceneMeta(type):

    @classmethod
    def __prepare__(metaclass, name, bases):
        namespace = {}
        operators = []

        def register_operator(**kwargs):
            operator = ExecuteSceneOperator(**kwargs)
            operators.append(operator)
            return operator

        namespace["ExecuteSceneOperator"] = register_operator
        namespace["_axira_operators"] = operators
        return namespace

    def __new__(metaclass, name, bases, namespace):
        own_operators = list(namespace.get("_axira_operators", []))
        inherited_operators = []

        for base in bases:
            inherited_operators.extend(getattr(base, "operators", []))

        cls = super().__new__(metaclass, name, bases, namespace)
        cls.operators = inherited_operators + own_operators
        return cls


class Scene(metaclass=SceneMeta):
    """Base class for an Axira scene."""

    def __init__(self):
        # Each instance receives its own copy of the operators declared
        # in the class body by SceneMeta.
        self.operators = list(type(self).operators)

    def execute(self, operator):
        self.operators.append(operator)
        return operator
