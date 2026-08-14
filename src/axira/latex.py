from pathlib import Path
import hashlib
import subprocess
import tempfile


class LatexRenderer:

    def __init__(
        self,
        latex_compiler="latex",
        svg_converter="dvisvgm",
        png_converter="dvipng",
        cache_directory=".axira/cache/latex",
    ):
        self.latex_compiler = latex_compiler
        self.svg_converter = svg_converter
        self.png_converter = png_converter

        self.cache_directory = Path(cache_directory)
        self.cache_directory.mkdir(
            parents=True,
            exist_ok=True,
        )

    def _expression_hash(self, expression):
        return hashlib.sha256(
            expression.encode("utf-8")
        ).hexdigest()[:16]

    def _tex_source(self, expression):
        return rf"""
\documentclass[preview]{{standalone}}

\begin{{document}}

\[
{expression}
\]

\end{{document}}
"""

    def _compile_dvi(self, expression, temp_dir):
        temp_dir = Path(temp_dir)

        tex_file = temp_dir / "formula.tex"
        dvi_file = temp_dir / "formula.dvi"

        tex_file.write_text(
            self._tex_source(expression),
            encoding="utf-8",
        )

        latex_process = subprocess.run(
            [
                self.latex_compiler,
                "-interaction=nonstopmode",
                "-halt-on-error",
                "formula.tex",
            ],
            cwd=temp_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        if latex_process.returncode != 0:
            print("=== LaTeX ERROR ===")
            print(latex_process.stdout)
            print(latex_process.stderr)
            print("===================")

            raise RuntimeError(
                "LaTeX compilation failed with exit code "
                f"{latex_process.returncode}"
            )

        return dvi_file

    def render_svg(self, expression):
        expression_hash = self._expression_hash(expression)

        svg_file = (
            self.cache_directory
            / f"{expression_hash}.svg"
        )

        if svg_file.exists():
            return svg_file

        with tempfile.TemporaryDirectory() as temp_dir:
            dvi_file = self._compile_dvi(
                expression,
                temp_dir,
            )

            svg_process = subprocess.run(
                [
                    self.svg_converter,
                    str(dvi_file),
                    "-n",
                    "-o",
                    str(svg_file),
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )

            if svg_process.returncode != 0:
                print("=== dvisvgm ERROR ===")
                print(svg_process.stdout)
                print(svg_process.stderr)
                print("=====================")

                raise RuntimeError(
                    "dvisvgm conversion failed with exit code "
                    f"{svg_process.returncode}"
                )

        return svg_file

    def render_png(self, expression):
        expression_hash = self._expression_hash(expression)

        png_file = (
            self.cache_directory
            / f"{expression_hash}.png"
        )

        if png_file.exists():
            return png_file

        with tempfile.TemporaryDirectory() as temp_dir:
            dvi_file = self._compile_dvi(
                expression,
                temp_dir,
            )

            dvipng_process = subprocess.run(
                [
                    self.png_converter,
                    "-D",
                    "300",
                    "-T",
                    "tight",
                    "-bg",
                    "Transparent",
                    "-fg",
                    "White",
                    "-o",
                    str(png_file),
                    str(dvi_file),
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )

            if dvipng_process.returncode != 0:
                print("=== dvipng ERROR ===")
                print(dvipng_process.stdout)
                print(dvipng_process.stderr)
                print("====================")

                raise RuntimeError(
                    "dvipng conversion failed with exit code "
                    f"{dvipng_process.returncode}"
                )

        return png_file
