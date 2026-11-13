from io import BytesIO
from types import SimpleNamespace

from PIL import Image, ImageDraw

from thumbor.config import Config
from thumbor.engines.pil import Engine


def make_palette_gif_source():
    # Palette GIF: index 0 is the transparent background, index 1 is blue.
    img = Image.new("P", (40, 40), 0)
    img.putpalette([255, 255, 255, 0, 0, 255] + [0] * (256 * 3 - 6))
    ImageDraw.Draw(img).ellipse([8, 8, 31, 31], fill=1)
    buffer = BytesIO()
    img.save(buffer, "GIF", transparency=0)
    return buffer.getvalue()


def make_engine():
    config = Config()
    config.PILLOW_PRESERVE_INDEXED_MODE = True
    config.ALLOW_ANIMATED_GIFS = False
    context = SimpleNamespace(config=config, modules=None)
    engine = Engine(context)
    engine.extension = ".gif"
    return engine


def test_resized_palette_gif_keeps_transparent_background():
    engine = make_engine()
    engine.image = engine.create_image(make_palette_gif_source())
    engine.resize(80, 80)

    result = engine.read(".gif")
    out = Image.open(BytesIO(result)).convert("RGBA")

    # The corner was transparent in the source and must stay transparent.
    assert out.getpixel((0, 0))[3] == 0
