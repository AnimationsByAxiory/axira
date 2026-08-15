from .temporal import DefaultTimeInterval


class _SpectralOpacityBaseFunction:
    def __init__(
        self,
        DurationScalarMetric=DefaultTimeInterval,
        TargetFunctionEntity=None,
    ):
        duration = float(DurationScalarMetric)

        if duration < 0:
            raise ValueError("DurationScalarMetric cannot be negative.")

        self.duration = duration
        self.target = TargetFunctionEntity


class SpectralOpacityFadeOutFunction(_SpectralOpacityBaseFunction):
    """Smoothly animate the active entity opacity to zero."""


class SpectralOpacityFadeInFunction(_SpectralOpacityBaseFunction):
    """Smoothly animate the active entity opacity to one."""
