import imageio.v2 as imageio

from PIL import Image, ImageDraw, ImageFont

from .latex import LatexRenderer
from .state import SceneRenderState
from .scene import (
    MathematicalFunctionTransform,
    MathematicalWriteFunction,
    LatexSymbolicMathFunction,
    LatexSymbolicMathWriteFunction,
    SpatialVectorTranslationFunction,
    SpectralOpacityFadeOutFunction,
    SpectralOpacityFadeInFunction,
)
from .scene.temporal import DefaultTimeInterval


class Renderer:

    def __init__(
        self,
        width=1280,
        height=720,
        fps=30,
    ):
        self.width = int(width)
        self.height = int(height)
        self.fps = int(fps)

        if self.width <= 0 or self.height <= 0:
            raise ValueError("Renderer width and height must be positive.")

        if self.fps <= 0:
            raise ValueError("Renderer fps must be positive.")

        self.latex_renderer = LatexRenderer()
        self._vector_write_renderer = None

    # =========================================================
    # PUBLIC RENDER
    # =========================================================

    def render(
        self,
        scene,
        output="axira_output.mp4",
    ):
        frames = []
        state = SceneRenderState()

        for operator in scene.operators:
            transform = operator.transform

            if getattr(operator, "operator_type", "play") == "wait":
                frames.extend(
                    self._render_wait(
                        transform,
                        state,
                    )
                )
                continue

            if isinstance(transform, LatexSymbolicMathWriteFunction):
                frames.extend(
                    self._render_latex_write(
                        transform,
                        state,
                    )
                )
                continue

            if isinstance(transform, MathematicalWriteFunction):
                frames.extend(
                    self._render_text_write(
                        transform,
                        state,
                    )
                )
                continue

            if isinstance(transform, SpatialVectorTranslationFunction):
                frames.extend(
                    self._render_translation(
                        transform,
                        state,
                    )
                )
                continue

            if isinstance(transform, SpectralOpacityFadeOutFunction):
                frames.extend(
                    self._render_opacity(
                        transform,
                        state,
                        target_opacity=0.0,
                    )
                )
                continue

            if isinstance(transform, SpectralOpacityFadeInFunction):
                frames.extend(
                    self._render_opacity(
                        transform,
                        state,
                        target_opacity=1.0,
                    )
                )
                continue

            raise TypeError(
                "Unsupported Axira transform: "
                f"{transform.__class__.__name__}"
            )

        if not frames:
            raise ValueError("Scene contains no operators.")

        imageio.mimsave(
            output,
            frames,
            fps=self.fps,
        )

        print(f"Rendered: {output}")

    # =========================================================
    # TIMING / EASING
    # =========================================================

    def _frame_count(self, duration, minimum=1):
        duration = float(duration)

        if duration < 0:
            raise ValueError("Animation duration cannot be negative.")

        if duration == 0:
            return 1

        return max(
            minimum,
            int(round(duration * self.fps)),
        )

    @staticmethod
    def _smooth_progress(progress):
        """Smoothstep easing: soft start and soft stop."""
        progress = max(0.0, min(1.0, float(progress)))
        return progress * progress * (3.0 - 2.0 * progress)

    @staticmethod
    def _progress(frame_number, frame_count):
        if frame_count <= 1:
            return 1.0

        return frame_number / (frame_count - 1)

    # =========================================================
    # SCENE COMPOSITION
    # =========================================================

    @property
    def pixels_per_scene_unit(self):
        # Eight logical vertical scene units fit in the frame height.
        # This makes DirectionalVector movement resolution-independent.
        return self.height / 8.0

    def _blank_frame(self):
        return Image.new(
            "RGB",
            (self.width, self.height),
            "black",
        )

    def _apply_opacity(self, image, opacity):
        opacity = max(0.0, min(1.0, float(opacity)))
        overlay = image.convert("RGBA").copy()

        if opacity >= 1.0:
            return overlay

        alpha = overlay.getchannel("A")
        alpha = alpha.point(
            lambda value: int(round(value * opacity))
        )
        overlay.putalpha(alpha)
        return overlay

    def _entity_pixel_position(self, entity_state, image):
        offset_x = entity_state.x * self.pixels_per_scene_unit
        offset_y = -entity_state.y * self.pixels_per_scene_unit

        x = int(round(
            (self.width - image.width) / 2 + offset_x
        ))

        y = int(round(
            (self.height - image.height) / 2 + offset_y
        ))

        return x, y

    def _paste_entity(
        self,
        frame,
        entity_state,
        image_override=None,
        opacity_override=None,
    ):
        if not entity_state.visible:
            return

        opacity = (
            entity_state.opacity
            if opacity_override is None
            else opacity_override
        )

        if opacity <= 0.0:
            return

        image = (
            entity_state.image
            if image_override is None
            else image_override
        ).convert("RGBA")

        overlay = self._apply_opacity(
            image,
            opacity,
        )

        x, y = self._entity_pixel_position(
            entity_state,
            overlay,
        )

        frame.paste(
            overlay,
            (x, y),
            overlay,
        )

    def _compose_scene(
        self,
        state,
        exclude_entity=None,
    ):
        frame = self._blank_frame()

        for entity_state in state.ordered_states():
            if (
                exclude_entity is not None
                and entity_state.entity is exclude_entity
            ):
                continue

            self._paste_entity(
                frame,
                entity_state,
            )

        return frame

    # =========================================================
    # ASSETS
    # =========================================================

    def _render_text_asset(self, entity):
        text = entity.expression

        try:
            font = ImageFont.truetype(
                "arial.ttf",
                60,
            )
        except OSError:
            font = ImageFont.load_default()

        probe = Image.new(
            "RGBA",
            (1, 1),
            (0, 0, 0, 0),
        )
        draw = ImageDraw.Draw(probe)

        bbox = draw.textbbox(
            (0, 0),
            text,
            font=font,
        )

        padding = 6
        width = max(1, bbox[2] - bbox[0] + padding * 2)
        height = max(1, bbox[3] - bbox[1] + padding * 2)

        image = Image.new(
            "RGBA",
            (width, height),
            (0, 0, 0, 0),
        )

        draw = ImageDraw.Draw(image)
        draw.text(
            (
                padding - bbox[0],
                padding - bbox[1],
            ),
            text,
            fill="white",
            font=font,
        )

        return image

    def _render_entity_asset(self, entity):
        if isinstance(entity, LatexSymbolicMathFunction):
            png_file = self.latex_renderer.render_png(
                entity.expression
            )
            return Image.open(png_file).convert("RGBA")

        if isinstance(entity, MathematicalFunctionTransform):
            return self._render_text_asset(entity)

        raise TypeError(
            "Unsupported Axira entity: "
            f"{entity.__class__.__name__}"
        )

    # =========================================================
    # WRITE
    # =========================================================

    def _get_vector_write_renderer(self):
        if self._vector_write_renderer is None:
            try:
                from .vector_write import VectorWriteRenderer
            except ModuleNotFoundError as error:
                if error.name == "svgpathtools":
                    raise RuntimeError(
                        "LaTeX vector writing requires svgpathtools. "
                        "Install Axira dependencies with: pip install axira"
                    ) from error
                raise

            self._vector_write_renderer = VectorWriteRenderer()

        return self._vector_write_renderer

    def _render_latex_write(
        self,
        transform,
        state,
    ):
        entity = transform.target
        duration = getattr(transform, "duration", 2.0)
        frame_count = self._frame_count(duration, minimum=2)

        final_image = self._render_entity_asset(entity)
        svg_file = self.latex_renderer.render_svg(entity.expression)

        if state.contains(entity):
            entity_state = state.get(entity)
            old_x = entity_state.x
            old_y = entity_state.y
            old_opacity = entity_state.opacity
        else:
            entity_state = state.activate(entity, final_image)
            old_x = 0.0
            old_y = 0.0
            old_opacity = 1.0

        # Do not show the full entity behind the vector write animation.
        entity_state.visible = False

        frames = []
        vector_renderer = self._get_vector_write_renderer()
        final_png_file = self.latex_renderer.render_png(entity.expression)

        for frame_number in range(frame_count):
            progress = self._progress(frame_number, frame_count)

            formula = vector_renderer.render_pil_frame(
                svg_file,
                final_png_file,
                progress,
            )

            frame = self._compose_scene(
                state,
                exclude_entity=entity,
            )

            temporary_state = state.get(entity)
            temporary_state.x = old_x
            temporary_state.y = old_y
            temporary_state.opacity = old_opacity
            temporary_state.visible = True

            self._paste_entity(
                frame,
                temporary_state,
                image_override=formula,
            )

            temporary_state.visible = False
            frames.append(frame)

        entity_state.image = final_image
        entity_state.x = old_x
        entity_state.y = old_y
        entity_state.opacity = old_opacity
        entity_state.visible = True
        state.active_entity = entity

        return frames

    def _render_text_write(
        self,
        transform,
        state,
    ):
        entity = transform.target
        duration = getattr(transform, "duration", 2.0)
        frame_count = self._frame_count(duration, minimum=2)
        final_image = self._render_entity_asset(entity)

        if state.contains(entity):
            entity_state = state.get(entity)
        else:
            entity_state = state.activate(entity, final_image)

        entity_state.image = final_image
        entity_state.visible = False
        frames = []

        for frame_number in range(frame_count):
            progress = self._smooth_progress(
                self._progress(frame_number, frame_count)
            )
            visible_width = int(round(final_image.width * progress))

            partial = Image.new(
                "RGBA",
                final_image.size,
                (0, 0, 0, 0),
            )

            if visible_width > 0:
                crop = final_image.crop(
                    (0, 0, visible_width, final_image.height)
                )
                partial.paste(crop, (0, 0), crop)

            frame = self._compose_scene(
                state,
                exclude_entity=entity,
            )

            entity_state.visible = True
            self._paste_entity(
                frame,
                entity_state,
                image_override=partial,
            )
            entity_state.visible = False

            frames.append(frame)

        entity_state.visible = True
        entity_state.opacity = 1.0
        state.active_entity = entity

        return frames

    # =========================================================
    # SPATIAL TRANSLATION
    # =========================================================

    def _render_translation(
        self,
        transform,
        state,
    ):
        entity_state = state.resolve_target(
            getattr(transform, "target", None)
        )

        state.active_entity = entity_state.entity

        start_x = entity_state.x
        start_y = entity_state.y

        delta_x = transform.vector.x
        delta_y = transform.vector.y

        frame_count = self._frame_count(
            transform.duration,
            minimum=2,
        )

        frames = []

        for frame_number in range(frame_count):
            progress = self._smooth_progress(
                self._progress(frame_number, frame_count)
            )

            entity_state.x = start_x + delta_x * progress
            entity_state.y = start_y + delta_y * progress

            frames.append(
                self._compose_scene(state)
            )

        entity_state.x = start_x + delta_x
        entity_state.y = start_y + delta_y

        return frames

    # =========================================================
    # SPECTRAL OPACITY
    # =========================================================

    def _render_opacity(
        self,
        transform,
        state,
        target_opacity,
    ):
        entity_state = state.resolve_target(
            getattr(transform, "target", None)
        )

        state.active_entity = entity_state.entity
        start_opacity = entity_state.opacity
        target_opacity = max(0.0, min(1.0, float(target_opacity)))

        frame_count = self._frame_count(
            transform.duration,
            minimum=2,
        )

        frames = []

        for frame_number in range(frame_count):
            progress = self._smooth_progress(
                self._progress(frame_number, frame_count)
            )

            entity_state.opacity = (
                start_opacity
                + (target_opacity - start_opacity) * progress
            )

            frames.append(
                self._compose_scene(state)
            )

        entity_state.opacity = target_opacity
        return frames

    # =========================================================
    # TEMPORAL HOLD
    # =========================================================

    def _render_wait(
        self,
        transform,
        state,
    ):
        duration = getattr(
            transform,
            "duration",
            DefaultTimeInterval,
        )

        frame_count = self._frame_count(duration)
        hold_frame = self._compose_scene(state)

        return [
            hold_frame.copy()
            for _ in range(frame_count)
        ]
