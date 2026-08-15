from dataclasses import dataclass

from PIL import Image


@dataclass
class RenderEntityState:
    entity: object
    image: Image.Image
    x: float = 0.0
    y: float = 0.0
    opacity: float = 1.0
    visible: bool = True


class SceneRenderState:
    """Mutable visual state owned by one Renderer.render() call."""

    def __init__(self):
        self._states = {}
        self._order = []
        self.active_entity = None

    def contains(self, entity):
        return id(entity) in self._states

    def get(self, entity):
        try:
            return self._states[id(entity)]
        except KeyError as error:
            raise RuntimeError(
                "The requested entity is not active in the rendered scene yet."
            ) from error

    def activate(self, entity, image):
        key = id(entity)

        if key not in self._states:
            self._states[key] = RenderEntityState(
                entity=entity,
                image=image.convert("RGBA"),
            )
            self._order.append(key)
        else:
            self._states[key].image = image.convert("RGBA")
            self._states[key].visible = True

        self.active_entity = entity
        return self._states[key]

    def resolve_target(self, explicit_target=None):
        target = explicit_target

        if target is None:
            target = self.active_entity

        if target is None:
            raise RuntimeError(
                "This transform needs an active entity. "
                "Write or show an entity before moving/fading it."
            )

        return self.get(target)

    def ordered_states(self):
        return [self._states[key] for key in self._order]
