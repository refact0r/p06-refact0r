from types import SimpleNamespace

from PIL import Image

from thumbor.config import Config
from thumbor.engines.pil import Engine
from thumbor.point import FocalPoint
from thumbor.transformer import Transformer


def test_auto_crop_on_1x1_source_to_wide_target_keeps_pixels():
    # Issue #4: a 1x1 source asked for 50x25 (ratio 2:1) computes a crop
    # height of round(0.5) == 0, so the crop is empty and the picture vanishes.
    config = Config()
    engine = Engine(SimpleNamespace(config=config, modules=None))
    engine.extension = ".png"
    engine.image = Image.new("RGBA", (1, 1), (255, 0, 0, 255))

    context = SimpleNamespace(
        config=config,
        modules=None,
        request=SimpleNamespace(engine=engine),
    )
    transformer = Transformer(context)
    transformer.target_width = 50.0
    transformer.target_height = 25.0
    transformer.focal_points = [
        FocalPoint.from_alignment("center", "middle", 1, 1)
    ]

    transformer.auto_crop()

    width, height = engine.size
    assert width > 0
    assert height > 0


def _fit_in_transformer(target_width, target_height, request_width, request_height):
    engine = Engine(SimpleNamespace(config=Config(), modules=None))
    engine.extension = ".png"
    engine.image = Image.new("RGBA", (940, 2), (255, 0, 0, 255))
    request = SimpleNamespace(
        engine=engine,
        adaptive=False,
        full=False,
        width=request_width,
        height=request_height,
    )
    context = SimpleNamespace(
        config=Config(), modules=None, request=request
    )
    transformer = Transformer(context)
    transformer.target_width = target_width
    transformer.target_height = target_height
    return transformer, engine


def test_fit_in_1x1_on_wide_source_returns_1x1():
    # Issue #4: /unsafe/fit-in/1x1/940x2.png rounds the height to 0.
    transformer, engine = _fit_in_transformer(1.0, 1.0, 1, 1)

    transformer.fit_in_resize()

    assert engine.size == (1, 1)


def test_fit_in_width_only_on_wide_source_returns_100x1():
    # Issue #4: /unsafe/fit-in/100x0/940x2.png rounds the height to 0.
    transformer, engine = _fit_in_transformer(None, None, 100, 0)
    transformer._calculate_target_dimensions()

    transformer.fit_in_resize()

    assert engine.size == (100, 1)
