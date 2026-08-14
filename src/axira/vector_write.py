from pathlib import Path
import re
import xml.etree.ElementTree as ET

from PIL import Image, ImageDraw
from svgpathtools import parse_path


XLINK = "{http://www.w3.org/1999/xlink}href"


class VectorWriteRenderer:
    """
    Axira LaTeX vector writer.

    Important:
    - Finished glyphs are copied from the real dvipng LaTeX image.
    - The active glyph is drawn from the real dvisvgm SVG path.
    - Disconnected subpaths are animated separately, so Axira does not draw
      false connector lines between unrelated contours inside one glyph.
    """

    def __init__(
        self,
        stroke_width=2,
        samples_per_subpath=180,
    ):
        self.stroke_width = int(stroke_width)
        self.samples_per_subpath = int(samples_per_subpath)

    def _number(self, value, default=0.0):
        if value is None:
            return default

        match = re.search(
            r"[-+]?(?:\d+(?:\.\d*)?|\.\d+)",
            str(value),
        )

        if match is None:
            return default

        return float(match.group(0))

    # =========================================================
    # SVG PARSING
    # =========================================================

    def _path_definitions(self, root):
        definitions = {}

        for element in root.iter():
            tag = element.tag.split("}")[-1]

            if tag != "path":
                continue

            path_id = element.attrib.get("id")
            path_data = element.attrib.get("d")

            if path_id and path_data:
                definitions[path_id] = path_data

        return definitions

    def _drawables(self, root, definitions):
        page = None

        for element in root.iter():
            if (
                element.tag.split("}")[-1] == "g"
                and element.attrib.get("id") == "page1"
            ):
                page = element
                break

        container = page if page is not None else root

        result = []

        for element in list(container):
            tag = element.tag.split("}")[-1]

            # -------------------------------------------------
            # LaTeX glyph
            # -------------------------------------------------

            if tag == "use":
                href = (
                    element.attrib.get(XLINK)
                    or element.attrib.get("href")
                )

                if not href or not href.startswith("#"):
                    continue

                path_data = definitions.get(
                    href[1:]
                )

                if not path_data:
                    continue

                result.append(
                    {
                        "kind": "path",
                        "d": path_data,
                        "x": self._number(
                            element.attrib.get("x"),
                            0.0,
                        ),
                        "y": self._number(
                            element.attrib.get("y"),
                            0.0,
                        ),
                    }
                )

            # -------------------------------------------------
            # Fraction bar etc.
            # -------------------------------------------------

            elif tag == "rect":
                result.append(
                    {
                        "kind": "rect",
                        "x": self._number(
                            element.attrib.get("x"),
                            0.0,
                        ),
                        "y": self._number(
                            element.attrib.get("y"),
                            0.0,
                        ),
                        "width": self._number(
                            element.attrib.get("width"),
                            0.0,
                        ),
                        "height": self._number(
                            element.attrib.get("height"),
                            0.0,
                        ),
                    }
                )

        return result

    # =========================================================
    # BOUNDING BOXES
    # =========================================================

    def _path_bbox(self, drawable):
        try:
            path = parse_path(
                drawable["d"]
            )

            xmin, xmax, ymin, ymax = (
                path.bbox()
            )

            return (
                xmin + drawable["x"],
                ymin + drawable["y"],
                xmax + drawable["x"],
                ymax + drawable["y"],
            )

        except Exception:
            return None

    def _drawable_svg_bbox(self, drawable):
        if drawable["kind"] == "path":
            return self._path_bbox(drawable)

        return (
            drawable["x"],
            drawable["y"],
            drawable["x"]
            + drawable["width"],
            drawable["y"]
            + drawable["height"],
        )

    def _all_svg_bbox(self, drawables):
        boxes = []

        for drawable in drawables:
            bbox = self._drawable_svg_bbox(
                drawable
            )

            if bbox is not None:
                boxes.append(bbox)

        if not boxes:
            raise RuntimeError(
                "Axira could not calculate "
                "the LaTeX SVG bounding box."
            )

        return (
            min(box[0] for box in boxes),
            min(box[1] for box in boxes),
            max(box[2] for box in boxes),
            max(box[3] for box in boxes),
        )

    def _visible_png_bbox(
        self,
        final_formula,
    ):
        alpha = final_formula.getchannel(
            "A"
        )

        bbox = alpha.getbbox()

        if bbox is None:
            raise RuntimeError(
                "Axira could not find visible "
                "pixels in the final LaTeX PNG."
            )

        return bbox

    # =========================================================
    # COORDINATE MAPPING
    # =========================================================

    def _svg_to_png(
        self,
        x,
        y,
        svg_bbox,
        png_bbox,
    ):
        sx0, sy0, sx1, sy1 = svg_bbox
        px0, py0, px1, py1 = png_bbox

        svg_width = max(
            1e-9,
            sx1 - sx0,
        )

        svg_height = max(
            1e-9,
            sy1 - sy0,
        )

        png_width = (
            px1 - px0
        )

        png_height = (
            py1 - py0
        )

        px = (
            px0
            + (x - sx0)
            / svg_width
            * png_width
        )

        py = (
            py0
            + (y - sy0)
            / svg_height
            * png_height
        )

        return (
            int(round(px)),
            int(round(py)),
        )

    def _drawable_png_bbox(
        self,
        drawable,
        svg_bbox,
        png_bbox,
        image_size,
    ):
        bbox = self._drawable_svg_bbox(
            drawable
        )

        if bbox is None:
            return None

        x0, y0, x1, y1 = bbox

        px0, py0 = self._svg_to_png(
            x0,
            y0,
            svg_bbox,
            png_bbox,
        )

        px1, py1 = self._svg_to_png(
            x1,
            y1,
            svg_bbox,
            png_bbox,
        )

        image_width, image_height = (
            image_size
        )

        left = max(
            0,
            min(px0, px1) - 2,
        )

        right = min(
            image_width,
            max(px0, px1) + 3,
        )

        top = max(
            0,
            min(py0, py1) - 2,
        )

        bottom = min(
            image_height,
            max(py0, py1) + 3,
        )

        if (
            right <= left
            or bottom <= top
        ):
            return None

        return (
            left,
            top,
            right,
            bottom,
        )

    # =========================================================
    # FINISHED GLYPHS
    # =========================================================

    def _paste_completed_drawable(
        self,
        result,
        final_formula,
        drawable,
        svg_bbox,
        png_bbox,
    ):
        bbox = self._drawable_png_bbox(
            drawable,
            svg_bbox,
            png_bbox,
            final_formula.size,
        )

        if bbox is None:
            return

        crop = final_formula.crop(
            bbox
        )

        result.paste(
            crop,
            (
                bbox[0],
                bbox[1],
            ),
            crop,
        )

    # =========================================================
    # ACTIVE GLYPH: SUBPATH WRITE
    # =========================================================

    def _continuous_subpaths(
        self,
        path_data,
    ):
        """
        Split one SVG glyph path into physically disconnected contours.

        This is the key fix for the visual artifacts:
        Axira no longer joins the end of one contour to the start of another.
        """

        try:
            path = parse_path(
                path_data
            )
        except Exception:
            return []

        if len(path) == 0:
            return []

        try:
            subpaths = (
                path.continuous_subpaths()
            )
        except Exception:
            # Safe fallback: treat each SVG segment separately.
            subpaths = [
                type(path)(segment)
                for segment in path
            ]

        return [
            subpath
            for subpath in subpaths
            if len(subpath) > 0
        ]

    def _sample_subpath(
        self,
        subpath,
        progress,
        drawable,
        svg_bbox,
        png_bbox,
    ):
        progress = max(
            0.0,
            min(1.0, float(progress)),
        )

        if progress <= 0.0:
            return []

        sample_count = max(
            2,
            int(
                self.samples_per_subpath
                * progress
            ),
        )

        points = []

        for index in range(
            sample_count
        ):
            t = (
                progress
                * index
                / (sample_count - 1)
            )

            try:
                point = subpath.point(t)
            except Exception:
                continue

            x = (
                point.real
                + drawable["x"]
            )

            y = (
                point.imag
                + drawable["y"]
            )

            points.append(
                self._svg_to_png(
                    x,
                    y,
                    svg_bbox,
                    png_bbox,
                )
            )

        return points

    def _draw_active_path(
        self,
        draw,
        drawable,
        progress,
        svg_bbox,
        png_bbox,
    ):
        subpaths = self._continuous_subpaths(
            drawable["d"]
        )

        if not subpaths:
            return

        # Each disconnected contour gets its own part of the animation.
        position = (
            progress
            * len(subpaths)
        )

        completed_subpaths = min(
            len(subpaths),
            int(position),
        )

        active_progress = (
            position
            - completed_subpaths
        )

        # Draw complete subpaths without joining them.
        for index in range(
            completed_subpaths
        ):
            points = self._sample_subpath(
                subpaths[index],
                1.0,
                drawable,
                svg_bbox,
                png_bbox,
            )

            if len(points) >= 2:
                draw.line(
                    points,
                    fill=(
                        255,
                        255,
                        255,
                        255,
                    ),
                    width=self.stroke_width,
                    joint="curve",
                )

        # Draw only the currently active subpath.
        if (
            completed_subpaths
            < len(subpaths)
            and active_progress > 0.0
        ):
            points = self._sample_subpath(
                subpaths[
                    completed_subpaths
                ],
                active_progress,
                drawable,
                svg_bbox,
                png_bbox,
            )

            if len(points) >= 2:
                draw.line(
                    points,
                    fill=(
                        255,
                        255,
                        255,
                        255,
                    ),
                    width=self.stroke_width,
                    joint="curve",
                )

    # =========================================================
    # FRAME
    # =========================================================

    def render_pil_frame(
        self,
        svg_file,
        final_png_file,
        progress,
    ):
        progress = max(
            0.0,
            min(1.0, float(progress)),
        )

        root = ET.fromstring(
            Path(svg_file).read_text(
                encoding="utf-8"
            )
        )

        definitions = (
            self._path_definitions(root)
        )

        drawables = self._drawables(
            root,
            definitions,
        )

        if not drawables:
            raise RuntimeError(
                "Axira could not find drawable "
                "LaTeX elements in the dvisvgm SVG."
            )

        final_formula = Image.open(
            final_png_file
        ).convert("RGBA")

        svg_bbox = self._all_svg_bbox(
            drawables
        )

        png_bbox = self._visible_png_bbox(
            final_formula
        )

        result = Image.new(
            "RGBA",
            final_formula.size,
            (0, 0, 0, 0),
        )

        draw = ImageDraw.Draw(
            result
        )

        animation_position = (
            progress
            * len(drawables)
        )

        complete_count = min(
            len(drawables),
            int(animation_position),
        )

        active_progress = (
            animation_position
            - complete_count
        )

        for index, drawable in enumerate(
            drawables
        ):
            # ---------------------------------------------
            # Finished mathematical element
            # ---------------------------------------------

            if index < complete_count:
                self._paste_completed_drawable(
                    result,
                    final_formula,
                    drawable,
                    svg_bbox,
                    png_bbox,
                )

                continue

            # ---------------------------------------------
            # Not yet started
            # ---------------------------------------------

            if index > complete_count:
                continue

            if active_progress <= 0.0:
                continue

            # ---------------------------------------------
            # Active glyph
            # ---------------------------------------------

            if drawable["kind"] == "path":
                self._draw_active_path(
                    draw,
                    drawable,
                    active_progress,
                    svg_bbox,
                    png_bbox,
                )

            # ---------------------------------------------
            # Fraction line / rectangle
            # ---------------------------------------------

            else:
                bbox = (
                    self._drawable_png_bbox(
                        drawable,
                        svg_bbox,
                        png_bbox,
                        final_formula.size,
                    )
                )

                if bbox is None:
                    continue

                (
                    left,
                    top,
                    right,
                    bottom,
                ) = bbox

                active_right = (
                    left
                    + int(
                        (right - left)
                        * active_progress
                    )
                )

                if active_right > left:
                    crop = (
                        final_formula.crop(
                            (
                                left,
                                top,
                                active_right,
                                bottom,
                            )
                        )
                    )

                    result.paste(
                        crop,
                        (
                            left,
                            top,
                        ),
                        crop,
                    )

        return result
