import imageio.v2 as imageio

from PIL import Image, ImageDraw, ImageFont

from .latex import LatexRenderer
from .vector_write import VectorWriteRenderer
from .scene.temporal import DefaultTimeInterval


class Renderer:

    def __init__(
        self,
        width=1280,
        height=720,
        fps=30,
    ):
        self.width = width
        self.height = height
        self.fps = fps

        self.latex_renderer = LatexRenderer()

        self.vector_write_renderer = (
            VectorWriteRenderer()
        )

    def render(
        self,
        scene,
        output="axira_output.mp4",
    ):
        frames = []

        for operator in scene.operators:
            transform = operator.transform

            # =================================================
            # TEMPORAL HOLD / WAIT
            # =================================================

            if getattr(operator, "operator_type", "play") == "wait":
                duration = getattr(
                    transform,
                    "duration",
                    DefaultTimeInterval,
                )

                frame_count = max(
                    1,
                    int(duration * self.fps),
                )

                if frames:
                    hold_frame = frames[-1]
                else:
                    hold_frame = Image.new(
                        "RGB",
                        (self.width, self.height),
                        "black",
                    )

                for _ in range(frame_count):
                    frames.append(
                        hold_frame.copy()
                    )

                continue

            # =================================================
            # LATEX WRITE ANIMATION
            # =================================================

            if self.is_latex_write(
                transform
            ):
                frames.extend(
                    self.render_latex_write(
                        transform
                    )
                )
                continue

            duration = getattr(
                transform,
                "duration",
                1.0,
            )

            frame_count = max(
                1,
                int(duration * self.fps),
            )

            frame = self.render_operator(
                operator
            )

            for _ in range(frame_count):
                frames.append(
                    frame.copy()
                )

        if not frames:
            raise ValueError(
                "Scene contains no operators."
            )

        imageio.mimsave(
            output,
            frames,
            fps=self.fps,
        )

        print(
            f"Rendered: {output}"
        )

    def is_latex_write(
        self,
        transform,
    ):
        return (
            transform.__class__.__name__
            == "LatexSymbolicMathWriteFunction"
        )

    def render_latex_write(
        self,
        transform,
    ):
        expression = (
            transform.target.expression
        )

        duration = getattr(
            transform,
            "duration",
            2.0,
        )

        frame_count = max(
            2,
            int(duration * self.fps),
        )

        svg_file = (
            self.latex_renderer.render_svg(
                expression
            )
        )

        final_png_file = (
            self.latex_renderer.render_png(
                expression
            )
        )

        frames = []

        for frame_number in range(
            frame_count
        ):
            progress = (
                frame_number
                / (frame_count - 1)
            )

            formula = (
                self.vector_write_renderer
                .render_pil_frame(
                    svg_file,
                    final_png_file,
                    progress,
                )
            )

            frame = Image.new(
                "RGB",
                (
                    self.width,
                    self.height,
                ),
                "black",
            )

            x = (
                self.width
                - formula.width
            ) // 2

            y = (
                self.height
                - formula.height
            ) // 2

            frame.paste(
                formula,
                (x, y),
                formula,
            )

            frames.append(frame)

        return frames

    def render_operator(
        self,
        operator,
    ):
        image = Image.new(
            "RGB",
            (
                self.width,
                self.height,
            ),
            "black",
        )

        transform = operator.transform

        if self.is_latex_write(
            transform
        ):
            expression = (
                transform.target.expression
            )

            png_file = (
                self.latex_renderer
                .render_png(expression)
            )

            formula = Image.open(
                png_file
            ).convert("RGBA")

            x = (
                self.width
                - formula.width
            ) // 2

            y = (
                self.height
                - formula.height
            ) // 2

            image.paste(
                formula,
                (x, y),
                formula,
            )

            return image

        draw = ImageDraw.Draw(
            image
        )

        text = (
            transform.target.expression
        )

        try:
            font = ImageFont.truetype(
                "arial.ttf",
                60,
            )
        except OSError:
            font = ImageFont.load_default()

        bbox = draw.textbbox(
            (0, 0),
            text,
            font=font,
        )

        text_width = (
            bbox[2] - bbox[0]
        )

        text_height = (
            bbox[3] - bbox[1]
        )

        x = (
            self.width
            - text_width
        ) / 2

        y = (
            self.height
            - text_height
        ) / 2

        draw.text(
            (x, y),
            text,
            fill="white",
            font=font,
        )

        return image
