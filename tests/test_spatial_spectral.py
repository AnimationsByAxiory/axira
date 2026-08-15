import tempfile
import unittest
from pathlib import Path

import imageio.v2 as imageio

from axira import (
    Scene,
    MathematicalFunctionTransform,
    MathematicalWriteFunction,
    ExecuteSceneOperator,
    TemporalHoldFunction,
    DirectionalVector,
    Up,
    Down,
    Left,
    Right,
    SpatialVectorTranslationFunction,
    SpectralOpacityFadeOutFunction,
    SpectralOpacityFadeInFunction,
    Renderer,
)


class VectorTests(unittest.TestCase):
    def test_directional_vector_arithmetic(self):
        vector = DirectionalVector(Right * 3 + Up * 2 - Left)
        self.assertEqual(vector, DirectionalVector((4.0, 2.0)))
        self.assertEqual(DirectionalVector(Down * 2), DirectionalVector((0.0, -2.0)))
        self.assertEqual(2 * Right, DirectionalVector((2.0, 0.0)))

    def test_invalid_vector(self):
        with self.assertRaises(TypeError):
            DirectionalVector("Up")


class TransformTests(unittest.TestCase):
    def test_spatial_transform(self):
        transform = SpatialVectorTranslationFunction(
            TargetPositionVector=DirectionalVector(Up * 2),
            DurationScalarMetric=1.5,
        )
        self.assertEqual(transform.vector, DirectionalVector((0.0, 2.0)))
        self.assertEqual(transform.duration, 1.5)
        self.assertIsNone(transform.target)

    def test_fade_transform_defaults(self):
        self.assertEqual(SpectralOpacityFadeOutFunction().duration, 1.0)
        self.assertEqual(SpectralOpacityFadeInFunction().duration, 1.0)

    def test_negative_duration_is_rejected(self):
        with self.assertRaises(ValueError):
            SpatialVectorTranslationFunction(
                DirectionalVector(Right),
                DurationScalarMetric=-1,
            )

        with self.assertRaises(ValueError):
            SpectralOpacityFadeOutFunction(
                DurationScalarMetric=-1,
            )


class RendererIntegrationTests(unittest.TestCase):
    def test_write_move_fade_wait_fadein(self):
        class MotionScene(Scene):
            text = MathematicalFunctionTransform(
                MathScalarExpression="AXIRA"
            )

            ExecuteSceneOperator(
                MathPlayTransform=MathematicalWriteFunction(
                    TargetFunctionEntity=text,
                    duration=0.2,
                )
            )

            ExecuteSceneOperator(
                MathPlayTransform=SpatialVectorTranslationFunction(
                    TargetPositionVector=DirectionalVector(Right * 2),
                    DurationScalarMetric=0.4,
                )
            )

            ExecuteSceneOperator(
                MathPlayTransform=SpectralOpacityFadeOutFunction(
                    DurationScalarMetric=0.3,
                )
            )

            ExecuteSceneOperator(
                MathWaitTransform=TemporalHoldFunction(
                    DurationScalarMetric=0.2,
                )
            )

            ExecuteSceneOperator(
                MathPlayTransform=SpectralOpacityFadeInFunction(
                    DurationScalarMetric=0.3,
                )
            )

        renderer = Renderer(
            width=320,
            height=240,
            fps=10,
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            output = Path(temp_dir) / "motion.mp4"
            renderer.render(MotionScene(), str(output))
            self.assertTrue(output.exists())
            self.assertGreater(output.stat().st_size, 0)

            reader = imageio.get_reader(str(output))
            frames = [frame for frame in reader]
            reader.close()

        # 0.2*10 + 0.4*10 + 0.3*10 + 0.2*10 + 0.3*10 = 14 frames.
        self.assertEqual(len(frames), 14)

        def bright_center_x(frame):
            # Ignore compression noise and find bright text pixels.
            mask = frame.mean(axis=2) > 100
            ys, xs = mask.nonzero()
            if len(xs) == 0:
                return None
            return float(xs.mean())

        start_x = bright_center_x(frames[1])
        moved_x = bright_center_x(frames[5])

        self.assertIsNotNone(start_x)
        self.assertIsNotNone(moved_x)
        self.assertGreater(moved_x, start_x + 40)

        # Fade-out completes at frame 8, then wait frames 9-10 remain dark.
        self.assertLess(frames[8].mean(), 8.0)
        self.assertLess(frames[9].mean(), 8.0)
        self.assertLess(frames[10].mean(), 8.0)

        # Fade-in returns the entity at its translated position.
        final_x = bright_center_x(frames[-1])
        self.assertIsNotNone(final_x)
        self.assertGreater(final_x, start_x + 40)


class LatexStateIntegrationTests(unittest.TestCase):
    def test_latex_write_then_move_and_fade_without_external_tex(self):
        from PIL import Image
        from axira import LatexSymbolicMathFunction, LatexSymbolicMathWriteFunction

        class FakeLatexRenderer:
            def __init__(self, directory):
                self.directory = Path(directory)
                self.png = self.directory / "fake_formula.png"
                image = Image.new("RGBA", (80, 30), (0, 0, 0, 0))
                for x in range(10, 70):
                    for y in range(10, 20):
                        image.putpixel((x, y), (255, 255, 255, 255))
                image.save(self.png)

            def render_png(self, expression):
                return self.png

            def render_svg(self, expression):
                return self.directory / "fake.svg"

        class FakeVectorRenderer:
            def render_pil_frame(self, svg_file, png_file, progress):
                full = Image.open(png_file).convert("RGBA")
                width = int(round(full.width * progress))
                out = Image.new("RGBA", full.size, (0, 0, 0, 0))
                if width > 0:
                    crop = full.crop((0, 0, width, full.height))
                    out.paste(crop, (0, 0), crop)
                return out

        class LatexMotionScene(Scene):
            equation = LatexSymbolicMathFunction(
                LaTeXScalarExpression=r"E=mc^2"
            )

            ExecuteSceneOperator(
                MathPlayTransform=LatexSymbolicMathWriteFunction(
                    TargetFunctionEntity=equation,
                    duration=0.2,
                )
            )

            ExecuteSceneOperator(
                MathPlayTransform=SpatialVectorTranslationFunction(
                    TargetPositionVector=DirectionalVector(Up),
                    DurationScalarMetric=0.2,
                )
            )

            ExecuteSceneOperator(
                MathPlayTransform=SpectralOpacityFadeOutFunction(
                    DurationScalarMetric=0.2,
                )
            )

        with tempfile.TemporaryDirectory() as temp_dir:
            renderer = Renderer(width=240, height=160, fps=10)
            renderer.latex_renderer = FakeLatexRenderer(temp_dir)
            renderer._vector_write_renderer = FakeVectorRenderer()

            output = Path(temp_dir) / "latex_state.mp4"
            renderer.render(LatexMotionScene(), str(output))

            reader = imageio.get_reader(str(output))
            frames = [frame for frame in reader]
            reader.close()

        self.assertEqual(len(frames), 6)

        def bright_center_y(frame):
            mask = frame.mean(axis=2) > 100
            ys, xs = mask.nonzero()
            if len(ys) == 0:
                return None
            return float(ys.mean())

        before_move_y = bright_center_y(frames[1])
        after_move_y = bright_center_y(frames[3])

        self.assertIsNotNone(before_move_y)
        self.assertIsNotNone(after_move_y)
        self.assertLess(after_move_y, before_move_y - 10)
        self.assertLess(frames[-1].mean(), 8.0)


if __name__ == "__main__":
    unittest.main()
