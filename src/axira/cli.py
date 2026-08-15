import argparse
import importlib.util
import sys
from pathlib import Path

from .renderer import Renderer
from .scene import Scene


QUALITY = {
    "-l": {"width": 848, "height": 480, "fps": 30, "name": "Low"},
    "-m": {"width": 1280, "height": 720, "fps": 30, "name": "Medium"},
    "-b": {"width": 1920, "height": 1080, "fps": 60, "name": "Big"},
    "-k": {"width": 3840, "height": 2160, "fps": 60, "name": "4K"},
}


def load_scene(file_path, scene_name):
    file_path = Path(file_path).resolve()

    if not file_path.exists():
        raise RuntimeError(f"Scene file was not found: {file_path}")

    spec = importlib.util.spec_from_file_location("axira_user_scene", file_path)

    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load scene file: {file_path}")

    module = importlib.util.module_from_spec(spec)
    sys.modules["axira_user_scene"] = module
    spec.loader.exec_module(module)

    if not hasattr(module, scene_name):
        available = [
            name for name, value in vars(module).items()
            if isinstance(value, type)
            and issubclass(value, Scene)
            and value is not Scene
        ]
        suffix = f" Available scenes: {', '.join(available)}" if available else ""
        raise RuntimeError(
            f"Scene '{scene_name}' was not found in '{file_path.name}'.{suffix}"
        )

    scene_class = getattr(module, scene_name)

    if not isinstance(scene_class, type) or not issubclass(scene_class, Scene):
        raise RuntimeError(
            f"'{scene_name}' exists, but it is not an Axira Scene. "
            f"Use: class {scene_name}(Scene):"
        )

    return scene_class


def build_parser():
    parser = argparse.ArgumentParser(
        prog="axira",
        description="Axira mathematical animation engine",
    )

    parser.add_argument("file", help="Python file containing the scene")
    parser.add_argument("scene", help="Scene class name")

    quality = parser.add_mutually_exclusive_group()
    quality.add_argument("-l", "--low", action="store_const", const="-l", dest="quality", help="848x480, 30 FPS")
    quality.add_argument("-m", "--medium", action="store_const", const="-m", dest="quality", help="1280x720, 30 FPS (default)")
    quality.add_argument("-b", "--big", action="store_const", const="-b", dest="quality", help="1920x1080, 60 FPS")
    quality.add_argument("-k", "--4k", action="store_const", const="-k", dest="quality", help="3840x2160, 60 FPS")

    parser.add_argument("-o", "--output", default=None, help="Output MP4 filename")
    parser.add_argument("--fps", type=int, default=None, help="Override preset FPS")

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()

    quality_key = args.quality or "-m"
    preset = QUALITY[quality_key]
    fps = args.fps if args.fps is not None else preset["fps"]

    if fps <= 0:
        parser.error("--fps must be greater than 0")

    output = args.output or f"{args.scene}.mp4"
    if not output.lower().endswith(".mp4"):
        output += ".mp4"

    try:
        scene_class = load_scene(args.file, args.scene)
        scene = scene_class()

        renderer = Renderer(
            width=preset["width"],
            height=preset["height"],
            fps=fps,
        )

        print(
            f"Axira | {args.scene} | {preset['name']} "
            f"{preset['width']}x{preset['height']} @ {fps} FPS"
        )

        renderer.render(scene, output)

    except Exception as error:
        print(f"Axira error: {error}", file=sys.stderr)
        raise SystemExit(1)


if __name__ == "__main__":
    main()
