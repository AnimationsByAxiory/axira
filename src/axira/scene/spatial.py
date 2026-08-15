from numbers import Real

from .temporal import DefaultTimeInterval


class DirectionalVector:
    """A small immutable 2D vector used by Axira spatial transforms."""

    __slots__ = ("_x", "_y")

    def __init__(self, direction):
        if isinstance(direction, DirectionalVector):
            x = direction.x
            y = direction.y
        elif isinstance(direction, (tuple, list)) and len(direction) == 2:
            x, y = direction
        else:
            raise TypeError(
                "DirectionalVector expects Up, Down, Left, Right, "
                "another DirectionalVector, or a two-value tuple/list."
            )

        if not isinstance(x, Real) or not isinstance(y, Real):
            raise TypeError("DirectionalVector components must be real numbers.")

        self._x = float(x)
        self._y = float(y)

    @property
    def x(self):
        return self._x

    @property
    def y(self):
        return self._y

    def __iter__(self):
        yield self._x
        yield self._y

    def __mul__(self, scalar):
        if not isinstance(scalar, Real):
            return NotImplemented

        return DirectionalVector(
            (
                self._x * float(scalar),
                self._y * float(scalar),
            )
        )

    def __rmul__(self, scalar):
        return self.__mul__(scalar)

    def __add__(self, other):
        if not isinstance(other, DirectionalVector):
            return NotImplemented

        return DirectionalVector(
            (
                self._x + other.x,
                self._y + other.y,
            )
        )

    def __sub__(self, other):
        if not isinstance(other, DirectionalVector):
            return NotImplemented

        return DirectionalVector(
            (
                self._x - other.x,
                self._y - other.y,
            )
        )

    def __neg__(self):
        return DirectionalVector((-self._x, -self._y))

    def __repr__(self):
        return f"DirectionalVector(x={self._x:g}, y={self._y:g})"

    def __eq__(self, other):
        if not isinstance(other, DirectionalVector):
            return False

        return self._x == other.x and self._y == other.y


# Logical scene directions. Positive Y points upward; the renderer converts
# that convention to screen pixels internally.
Up = DirectionalVector((0.0, 1.0))
Down = DirectionalVector((0.0, -1.0))
Left = DirectionalVector((-1.0, 0.0))
Right = DirectionalVector((1.0, 0.0))


class SpatialVectorTranslationFunction:
    """Smoothly translate the active Axira entity by a directional vector."""

    def __init__(
        self,
        TargetPositionVector,
        DurationScalarMetric=DefaultTimeInterval,
        TargetFunctionEntity=None,
    ):
        if not isinstance(TargetPositionVector, DirectionalVector):
            TargetPositionVector = DirectionalVector(TargetPositionVector)

        duration = float(DurationScalarMetric)

        if duration < 0:
            raise ValueError("DurationScalarMetric cannot be negative.")

        self.vector = TargetPositionVector
        self.target_position_vector = TargetPositionVector
        self.duration = duration
        self.target = TargetFunctionEntity
