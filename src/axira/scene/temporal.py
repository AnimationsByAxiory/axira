DefaultTimeInterval = 1.0


class TemporalHoldFunction:
    """Hold the current rendered scene state for a period of time."""

    def __init__(
        self,
        DurationScalarMetric=DefaultTimeInterval,
    ):
        duration = float(DurationScalarMetric)

        if duration < 0:
            raise ValueError(
                "DurationScalarMetric cannot be negative."
            )

        self.duration = duration
