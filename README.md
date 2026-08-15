# Axira

Axira is a Python library and rendering engine for creating mathematical animations programmatically.

The project is designed around a declarative scene description model. Instead of describing an animation as a sequence of imperative method calls, Axira represents mathematical objects, transformations, timing operations, and scene actions as explicit Python objects.

Axira is currently focused on mathematical typesetting, LaTeX rendering, vector-based writing animations, scene execution, video rendering, and a command-line interface for producing animations at different output qualities.

The project is under active development.

---

## Overview

Mathematical animations often consist of several different concepts:

- mathematical expressions;
- objects displayed on a scene;
- transformations applied to those objects;
- timing;
- animation operators;
- rendering;
- video encoding.

Axira attempts to represent these concepts explicitly.

For example, a LaTeX expression can be represented as a mathematical entity:

```python
eq = LatexSymbolicMathFunction(
    LaTeXScalarExpression=r"\frac{1}{2}x^2"
)
```

Writing that expression is represented separately:

```python
LatexSymbolicMathWriteFunction(
    TargetFunctionEntity=eq,
    duration=3.0
)
```

The transformation is then executed by a scene operator:

```python
ExecuteSceneOperator(
    MathPlayTransform=LatexSymbolicMathWriteFunction(
        TargetFunctionEntity=eq,
        duration=3.0
    )
)
```

Timing operations are represented in the same way.

For example:

```python
ExecuteSceneOperator(
    MathWaitTransform=TemporalHoldFunction(
        DurationScalarMetric=DefaultTimeInterval
    )
)
```

This structure is one of the main ideas behind Axira.

Rather than treating every operation as an unrelated scene method, Axira builds a structured description of what exists in a scene and what should happen to it.

---

# Features

The current version of Axira includes:

- Python-based mathematical scene definitions;
- LaTeX mathematical expressions;
- LaTeX rendering through a TeX distribution;
- DVI generation;
- SVG conversion using `dvisvgm`;
- PNG rendering using `dvipng`;
- vector-based LaTeX writing animations;
- scene operators;
- mathematical transformations;
- temporal hold operations;
- resolution-independent directional vectors (`Up`, `Down`, `Left`, `Right`);
- smooth spatial translation with `SpatialVectorTranslationFunction`;
- fade-in and fade-out opacity transforms;
- persistent scene state across write, move, fade, and wait operations;
- configurable animation duration;
- video generation;
- multiple rendering quality presets;
- command-line rendering;
- custom output filenames;
- configurable frame rates;
- a cache for generated LaTeX assets.

Axira is still in an early stage of development. The API may change significantly between releases.

---

# Installation

Axira requires Python 3.10 or newer.

Install Axira using pip:

```bash
pip install axira
```

For development, clone the repository and install it in editable mode:

```bash
git clone https://github.com/Animationsbyaxiory/axira.git
cd axira
python -m pip install -e .
```

Editable installation allows changes made inside the source directory to be immediately available to Python without rebuilding and reinstalling the package after every modification.

---

# External Requirements

Axira uses LaTeX to typeset mathematical expressions.

A working TeX distribution is therefore required for LaTeX-based mathematical rendering.

On Windows, MiKTeX can be used.

Axira expects the following commands to be available from the system command line:

```text
latex
dvisvgm
dvipng
```

You can check them with:

```bash
latex --version
dvisvgm --version
dvipng --version
```

If these commands cannot be found, make sure your TeX distribution is installed correctly and its executable directory is available through the system `PATH`.

These programs are external system dependencies. They are not installed automatically by `pip install axira`.

---

# Basic Example

Create a file named `main.py`:

```python
from axira import *


class Demo(Scene):

    eq = LatexSymbolicMathFunction(
        LaTeXScalarExpression=r"\frac{1}{2}x^2"
    )

    ExecuteSceneOperator(
        MathPlayTransform=LatexSymbolicMathWriteFunction(
            TargetFunctionEntity=eq,
            duration=3.0
        )
    )

    ExecuteSceneOperator(
        MathWaitTransform=TemporalHoldFunction(
            DurationScalarMetric=DefaultTimeInterval
        )
    )
```

Render the scene using:

```bash
axira main.py Demo -l
```

Axira will load `main.py`, find the `Demo` scene, execute its operators, render the frames, and encode the result as a video.

---

# Command-Line Interface

Axira provides a command-line interface.

The general syntax is:

```text
axira <python-file> <scene-name> [options]
```

For example:

```bash
axira main.py Demo -l
```

The first argument specifies the Python file containing the scene.

The second argument specifies the scene class that should be rendered.

The remaining arguments control rendering options.

---

# Rendering Quality

Axira provides several quality presets.

Low quality:

```bash
axira main.py Demo -l
```

Medium quality:

```bash
axira main.py Demo -m
```

High quality:

```bash
axira main.py Demo -b
```

4K quality:

```bash
axira main.py Demo -k
```

These presets allow the same scene source code to be rendered at different resolutions and frame rates without modifying the Python scene itself.

Lower-quality rendering is useful during development because it reduces rendering time.

Higher-quality rendering can then be used for the final video.

---

# Output Files

By default, Axira generates an MP4 video based on the rendered scene.

A custom output filename can also be specified:

```bash
axira main.py Demo -b -o result.mp4
```

This renders the `Demo` scene and writes the result to:

```text
result.mp4
```

---

# Custom Frame Rate

The frame rate can be overridden from the command line.

For example:

```bash
axira main.py Demo -m --fps 60
```

This allows the resolution preset and frame rate to be controlled independently when necessary.

---

# Scenes

A scene is the main container for an Axira animation.

Scenes inherit from:

```python
Scene
```

For example:

```python
from axira import *


class Example(Scene):
    pass
```

A scene can contain mathematical entities and execution operators.

The scene definition describes the sequence of operations that the renderer will process.

---

# Mathematical Entities

Axira distinguishes mathematical objects from transformations.

A mathematical expression can first be declared:

```python
eq = LatexSymbolicMathFunction(
    LaTeXScalarExpression=r"x^2 + y^2 = r^2"
)
```

This object represents the mathematical expression itself.

It does not automatically describe how that expression should appear.

The animation is represented separately.

For example:

```python
LatexSymbolicMathWriteFunction(
    TargetFunctionEntity=eq,
    duration=2.0
)
```

This represents a writing transformation targeting the mathematical entity `eq`.

---

# Scene Operators

Transformations are executed through scene operators.

For example:

```python
ExecuteSceneOperator(
    MathPlayTransform=LatexSymbolicMathWriteFunction(
        TargetFunctionEntity=eq,
        duration=2.0
    )
)
```

The separation between an entity, a transformation, and an operator is intentional.

Conceptually:

```text
Mathematical Entity
        |
        v
Transformation
        |
        v
Scene Operator
        |
        v
Renderer
        |
        v
Frames
        |
        v
Video
```

This gives Axira a structured internal representation that can be expanded as the project develops.

---

# LaTeX Support

Mathematical expressions in Axira can be written using standard LaTeX syntax.

For example:

```python
eq = LatexSymbolicMathFunction(
    LaTeXScalarExpression=r"\frac{a+b}{c}"
)
```

Another example:

```python
eq = LatexSymbolicMathFunction(
    LaTeXScalarExpression=r"\int_0^\infty e^{-x^2}\,dx"
)
```

Or:

```python
eq = LatexSymbolicMathFunction(
    LaTeXScalarExpression=r"\sum_{n=1}^{\infty}\frac{1}{n^2}"
)
```

Axira does not attempt to reproduce mathematical typography using a normal operating-system font.

Instead, mathematical expressions are processed by an actual LaTeX toolchain.

This allows the final mathematical notation to use genuine LaTeX typesetting.

---

# LaTeX Rendering Pipeline

Axira's mathematical rendering pipeline uses several stages.

Conceptually:

```text
LaTeX expression
       |
       v
.tex source
       |
       v
LaTeX compiler
       |
       v
DVI
       |
       +------------------+
       |                  |
       v                  v
   dvisvgm              dvipng
       |                  |
       v                  v
     SVG                 PNG
       |                  |
       +--------+---------+
                |
                v
        Axira Renderer
                |
                v
             Frames
                |
                v
              MP4
```

The SVG representation is useful for vector information and animation.

The PNG representation provides the final rasterized appearance of the LaTeX expression.

Axira combines these representations during rendering.

---

# LaTeX Write Animation

Axira includes a writing animation for mathematical expressions.

Example:

```python
ExecuteSceneOperator(
    MathPlayTransform=LatexSymbolicMathWriteFunction(
        TargetFunctionEntity=eq,
        duration=3.0
    )
)
```

The `duration` parameter controls how long the writing animation takes.

For example:

```python
duration=1.0
```

produces a faster animation, while:

```python
duration=5.0
```

produces a slower animation.

Internally, Axira uses vector information generated from the LaTeX output to progressively reveal mathematical glyphs.

The current implementation is an early version of the vector writing system and will continue to be improved.

---

# Spatial Translation

Axira can smoothly translate the currently active scene entity using directional vectors.

The four built-in directions are:

```python
Up
Down
Left
Right
```

Directions support ordinary vector-style arithmetic. For example:

```python
DirectionalVector(Up * 2)
DirectionalVector(Right * 3)
DirectionalVector(Up * 2 + Right * 3)
DirectionalVector(Left - Down)
```

A spatial translation is represented by `SpatialVectorTranslationFunction`:

```python
ExecuteSceneOperator(
    MathPlayTransform=SpatialVectorTranslationFunction(
        TargetPositionVector=DirectionalVector(Right * 2),
        DurationScalarMetric=2.0
    )
)
```

If `TargetFunctionEntity` is omitted, the transformation is applied to the most recently active entity. This allows a scene to be written as a sequence of operations without repeating the target for every transform.

Axira uses smooth interpolation for translations, so an entity accelerates softly at the beginning of the movement and decelerates near the end rather than moving at a visually abrupt constant rate.

Directional units are independent of output resolution. One logical scene unit corresponds to one eighth of the frame height, so the same scene keeps approximately the same composition when rendered at low, medium, high, or 4K quality.

---

# Spectral Opacity Transforms

Axira provides opacity-based fade operations for the active entity.

Fade out:

```python
ExecuteSceneOperator(
    MathPlayTransform=SpectralOpacityFadeOutFunction(
        DurationScalarMetric=1.0
    )
)
```

Fade in:

```python
ExecuteSceneOperator(
    MathPlayTransform=SpectralOpacityFadeInFunction(
        DurationScalarMetric=1.0
    )
)
```

`SpectralOpacityFadeOutFunction` smoothly changes the entity opacity from its current value to zero. The entity remains part of the scene state, which means it can later be moved or restored with `SpectralOpacityFadeInFunction`.

As with spatial transforms, an explicit `TargetFunctionEntity` can be supplied when necessary, while the default behavior operates on the most recently active entity.

---

# Temporal Operations

Axira represents waiting as an explicit temporal transformation.

For example:

```python
ExecuteSceneOperator(
    MathWaitTransform=TemporalHoldFunction(
        DurationScalarMetric=DefaultTimeInterval
    )
)
```

`DefaultTimeInterval` represents the default waiting interval.

A custom duration can also be supplied:

```python
ExecuteSceneOperator(
    MathWaitTransform=TemporalHoldFunction(
        DurationScalarMetric=5.0
    )
)
```

This holds the current scene state for five seconds.

The renderer does not replace the scene with an empty frame during a temporal hold. It preserves the most recently rendered scene state for the requested duration.

For example:

```python
from axira import *


class Demo(Scene):

    eq = LatexSymbolicMathFunction(
        LaTeXScalarExpression=r"E = mc^2"
    )

    ExecuteSceneOperator(
        MathPlayTransform=LatexSymbolicMathWriteFunction(
            TargetFunctionEntity=eq,
            duration=2.0
        )
    )

    ExecuteSceneOperator(
        MathWaitTransform=TemporalHoldFunction(
            DurationScalarMetric=3.0
        )
    )
```

Conceptually, this scene performs:

```text
Write E = mc²
      |
      | 2 seconds
      v
Expression completed
      |
      | 3 seconds
      v
Hold final scene
```

---

# Rendering

Axira's renderer converts scene operations into a sequence of frames.

The basic process is:

```text
Scene
  |
  v
Scene operators
  |
  v
Transformations
  |
  v
Frame generation
  |
  v
Frame sequence
  |
  v
Video encoder
  |
  v
MP4
```

Animation duration and frame rate determine how many frames are generated.

For example, a two-second animation rendered at 30 FPS contains approximately:

```text
2 × 30 = 60 frames
```

A three-second temporal hold at the same frame rate adds approximately:

```text
3 × 30 = 90 frames
```

The renderer then combines these frames into the final video.

---

# LaTeX Cache

Compiling LaTeX repeatedly can be expensive.

Axira therefore maintains a cache for generated mathematical assets.

Cached files are stored under the Axira cache directory.

This allows identical mathematical expressions to reuse previously generated output rather than recompiling the same expression every time.

The cache is an implementation detail and should generally not be committed to source control.

A typical `.gitignore` should include:

```gitignore
.axira/
```

---

# Example: Quadratic Formula

```python
from axira import *


class QuadraticFormula(Scene):

    formula = LatexSymbolicMathFunction(
        LaTeXScalarExpression=
        r"x=\frac{-b\pm\sqrt{b^2-4ac}}{2a}"
    )

    ExecuteSceneOperator(
        MathPlayTransform=LatexSymbolicMathWriteFunction(
            TargetFunctionEntity=formula,
            duration=4.0
        )
    )

    ExecuteSceneOperator(
        MathWaitTransform=TemporalHoldFunction(
            DurationScalarMetric=2.0
        )
    )
```

Render:

```bash
axira main.py QuadraticFormula -m
```

---

# Example: Integral

```python
from axira import *


class IntegralExample(Scene):

    integral = LatexSymbolicMathFunction(
        LaTeXScalarExpression=
        r"\int_a^b f(x)\,dx"
    )

    ExecuteSceneOperator(
        MathPlayTransform=LatexSymbolicMathWriteFunction(
            TargetFunctionEntity=integral,
            duration=3.0
        )
    )

    ExecuteSceneOperator(
        MathWaitTransform=TemporalHoldFunction(
            DurationScalarMetric=2.0
        )
    )
```

---

# Example: Summation

```python
from axira import *


class SummationExample(Scene):

    formula = LatexSymbolicMathFunction(
        LaTeXScalarExpression=
        r"\sum_{k=1}^{n} k = \frac{n(n+1)}{2}"
    )

    ExecuteSceneOperator(
        MathPlayTransform=LatexSymbolicMathWriteFunction(
            TargetFunctionEntity=formula,
            duration=4.0
        )
    )

    ExecuteSceneOperator(
        MathWaitTransform=TemporalHoldFunction(
            DurationScalarMetric=3.0
        )
    )
```

---

# Project Philosophy

Axira is being developed around several ideas.

## Mathematical objects should be explicit

A mathematical expression is represented as an object rather than being hidden inside rendering code.

## Transformations should be explicit

Writing, waiting, and future animation operations are represented as transformations.

## Execution should be explicit

`ExecuteSceneOperator` describes when a transformation becomes part of the scene execution sequence.

## Rendering should be separate from scene description

A scene describes what should happen.

The renderer determines how that description becomes frames and video.

This separation is intended to make the engine easier to extend as more mathematical objects and animation systems are introduced.

---

# Current Architecture

A simplified representation of Axira's current architecture is:

```text
axira
|
+-- Scene
|
+-- Mathematical entities
|   |
|   +-- LatexSymbolicMathFunction
|
+-- Mathematical transformations
|   |
|   +-- LatexSymbolicMathWriteFunction
|
+-- Temporal transformations
|   |
|   +-- TemporalHoldFunction
|
+-- Scene operators
|   |
|   +-- ExecuteSceneOperator
|
+-- LaTeX renderer
|   |
|   +-- latex
|   +-- dvisvgm
|   +-- dvipng
|
+-- Vector writing renderer
|
+-- Video renderer
|
+-- Command-line interface
```

The architecture is expected to evolve as Axira gains additional features.

---

# Development Status

Axira is currently an early-stage project.

The current release should be considered experimental.

The following areas are expected to evolve:

- scene composition;
- positioning;
- multiple simultaneous mathematical objects;
- object transformations;
- vector animation quality;
- text rendering;
- colors;
- camera controls;
- timing systems;
- animation interpolation;
- scene state management;
- caching;
- rendering performance;
- error reporting;
- command-line options;
- cross-platform support.

Backward compatibility is not guaranteed during early development.

---

# Planned Direction

Axira is intended to grow beyond rendering a single mathematical expression.

Possible future areas include:

- multiple objects in one scene;
- object positioning;
- coordinate systems;
- graphs;
- geometric primitives;
- transformations between mathematical expressions;
- object movement;
- scaling;
- rotation;
- color controls;
- camera movement;
- equations with individually addressable components;
- synchronized animations;
- custom easing functions;
- improved vector writing;
- text objects;
- reusable scene components;
- audio support;
- improved rendering performance;
- additional output formats.

These items describe the intended direction of the project and should not be interpreted as features already available in the current release.

---

# Development Installation

Clone the repository:

```bash
git clone https://github.com/Animationsbyaxiory/axira.git
```

Enter the directory:

```bash
cd axira
```

Install in editable mode:

```bash
python -m pip install -e .
```

Check the CLI:

```bash
axira --help
```

Then render a test scene:

```bash
axira main.py Demo -l
```

---

# Building the Package

Install the Python build tools:

```bash
python -m pip install --upgrade build twine
```

Build Axira:

```bash
python -m build
```

The generated distributions will be placed in:

```text
dist/
```

Typically:

```text
dist/
├── axira-1.1.0-py3-none-any.whl
└── axira-1.1.0.tar.gz
```

Check the distributions:

```bash
python -m twine check dist/*
```

---

# Contributing

Axira is under active development.

Contributions, bug reports, experiments, suggestions, and discussions about the architecture are welcome.

When reporting a rendering problem, useful information includes:

- operating system;
- Python version;
- Axira version;
- TeX distribution;
- `latex --version`;
- `dvisvgm --version`;
- `dvipng --version`;
- complete error traceback;
- minimal scene that reproduces the issue.

This information makes rendering and LaTeX problems significantly easier to reproduce.

---

# Bug Reports

If Axira fails while rendering a scene, include the complete traceback when opening an issue.

For LaTeX-specific failures, first verify:

```bash
latex --version
dvisvgm --version
dvipng --version
```

If one of these commands cannot be found, the issue is likely related to the local TeX installation or system `PATH`.

---

# Platform Support

Axira is currently being developed and tested primarily with Python on Windows.

Support for additional platforms may improve as the project develops.

Because the LaTeX pipeline depends on external programs, behavior may differ depending on the installed TeX distribution and operating system.

---

# Why Axira?

Axira exists as an experiment in building a mathematical animation engine with a structured Python representation of scenes.

A mathematical animation contains more information than just pixels.

It contains mathematical entities, transformations, timing relationships, execution order, and visual state.

Axira attempts to preserve these concepts in its API rather than immediately reducing everything to drawing commands.

For example:

```python
ExecuteSceneOperator(
    MathWaitTransform=TemporalHoldFunction(
        DurationScalarMetric=2.0
    )
)
```

does not merely mean "duplicate some frames."

At the scene-description level, it represents a temporal operation that holds the current state for a defined interval.

Similarly:

```python
ExecuteSceneOperator(
    MathPlayTransform=LatexSymbolicMathWriteFunction(
        TargetFunctionEntity=eq,
        duration=3.0
    )
)
```

represents an animation transformation applied to a particular mathematical entity.

This structured approach is the foundation on which the rest of Axira can be developed.

---

# Version

Current early release:

```text
Axira 1.1.0
```

---

# License

See the `LICENSE` file included with the project.

---

# Authors and Project

Axira is an independent mathematical animation engine written in Python.

Repository:

```text
https://github.com/Animationsbyaxiory/axira
```

The project is under active development. New mathematical objects, transformations, rendering capabilities, and scene operations are expected to be introduced in future releases.