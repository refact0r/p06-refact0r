# Regression test for issue #2: transparent round_corner must not leave a dark ring.

import asyncio
import types
from io import BytesIO

from PIL import Image

from thumbor.config import Config
from thumbor.context import Context
from thumbor.engines.pil import Engine
from thumbor.filters.round_corner import Filter


def build_engine_and_filter(params):
    context = Context(config=Config())
    source = Image.new("RGBA", (100, 100), (255, 255, 255, 255))
    buffer = BytesIO()
    source.save(buffer, format="PNG")
    engine = Engine(context)
    engine.load(buffer.getvalue(), ".png")
    context.modules = types.SimpleNamespace(engine=engine)
    Filter.pre_compile()
    instance = Filter.init_if_valid(params, context)
    return instance, engine


def test_transparent_round_corner_has_no_dark_opaque_pixels():
    instance, engine = build_engine_and_filter(
        "round_corner(60,255,255,255,true)"
    )
    asyncio.run(instance.run())
    result = engine.image.convert("RGBA")
    dark = []
    for x in range(result.width):
        for y in range(result.height):
            r, g, b, a = result.getpixel((x, y))
            if a == 255 and (r, g, b) != (255, 255, 255):
                dark.append((x, y, (r, g, b)))
    assert dark == [], f"opaque pixels differ from the white fill: {dark[:5]}"
