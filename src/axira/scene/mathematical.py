class MathematicalFunctionTransform:

    def __init__(
        self,
        MathScalarExpression,
    ):
        self.expression = MathScalarExpression


class MathematicalWriteFunction:

    def __init__(
        self,
        TargetFunctionEntity,
        duration=2.0,
    ):
        self.target = TargetFunctionEntity
        self.duration = duration


class LatexSymbolicMathFunction:

    def __init__(
        self,
        LaTeXScalarExpression,
    ):
        self.expression = LaTeXScalarExpression


class LatexSymbolicMathWriteFunction:

    def __init__(
        self,
        TargetFunctionEntity,
        duration=2.0,
    ):
        self.target = TargetFunctionEntity
        self.duration = duration