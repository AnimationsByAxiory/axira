class ExecuteSceneOperator:

    def __init__(
        self,
        MathPlayTransform=None,
        MathWaitTransform=None,
    ):
        supplied = [
            MathPlayTransform is not None,
            MathWaitTransform is not None,
        ]

        if sum(supplied) != 1:
            raise ValueError(
                "ExecuteSceneOperator requires exactly one transform: "
                "MathPlayTransform or MathWaitTransform."
            )

        if MathPlayTransform is not None:
            self.transform = MathPlayTransform
            self.operator_type = "play"
        else:
            self.transform = MathWaitTransform
            self.operator_type = "wait"
