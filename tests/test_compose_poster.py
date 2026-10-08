import importlib.util
import tempfile
import unittest
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills" / "creating-instagram-product-posters" / "scripts" / "compose_poster.py"
FONT_DIR = ROOT / "skills" / "creating-instagram-product-posters" / "assets" / "fonts"


def load_module():
    spec = importlib.util.spec_from_file_location("compose_poster", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ComposePosterTests(unittest.TestCase):
    def test_rejects_font_outside_bundled_allowlist(self):
        module = load_module()
        with tempfile.TemporaryDirectory() as temp_dir:
            fake_font = Path(temp_dir) / "UnknownFont.ttf"
            fake_font.write_bytes(b"not-a-font")
            with self.assertRaisesRegex(ValueError, "approved bundled font"):
                module.validate_font(fake_font)

    def test_pretendard_requires_its_license_file(self):
        module = load_module()
        font = FONT_DIR / "Pretendard-Bold.otf"
        license_file = FONT_DIR / "Pretendard-OFL.txt"
        self.assertTrue(font.exists(), "Pretendard test font fixture is missing")
        self.assertTrue(license_file.exists(), "Pretendard OFL license is missing")
        self.assertEqual(module.validate_font(font), font.resolve())

    def test_composes_exact_1080_by_1350_poster(self):
        module = load_module()
        with tempfile.TemporaryDirectory() as temp_dir:
            source = Path(temp_dir) / "background.png"
            output = Path(temp_dir) / "poster.png"
            Image.new("RGB", (1122, 1402), "#183F39").save(source)

            module.compose_poster(
                background_path=source,
                output_path=output,
                title="한 방울의\n수분 루틴",
                subtitle="가볍게 스며드는 데일리 세럼",
                title_font_path=FONT_DIR / "Pretendard-Bold.otf",
                subtitle_font_path=FONT_DIR / "Pretendard-Regular.otf",
            )

            with Image.open(output) as result:
                self.assertEqual(result.size, (1080, 1350))
                self.assertEqual(result.mode, "RGB")

    def test_supports_bottom_typography_zone(self):
        module = load_module()
        with tempfile.TemporaryDirectory() as temp_dir:
            source = Path(temp_dir) / "background.png"
            output = Path(temp_dir) / "poster.png"
            Image.new("RGB", (1080, 1350), "#101312").save(source)

            module.compose_poster(
                background_path=source,
                output_path=output,
                title="한 방울의\n수분 루틴",
                subtitle="가볍게 스며드는 데일리 세럼",
                title_font_path=FONT_DIR / "Pretendard-Bold.otf",
                subtitle_font_path=FONT_DIR / "Pretendard-Regular.otf",
                placement="bottom",
            )

            with Image.open(output).convert("RGB") as result:
                light_pixels_top = 0
                light_pixels_bottom = 0
                pixels = result.load()
                for y in range(result.height):
                    for x in range(result.width):
                        r, g, b = pixels[x, y]
                        if r > 180 and g > 180 and b > 180:
                            if y < result.height // 2:
                                light_pixels_top += 1
                            else:
                                light_pixels_bottom += 1
                self.assertGreater(light_pixels_bottom, 1000)
                self.assertLess(light_pixels_top, light_pixels_bottom // 10)

    def test_adds_optional_editorial_metadata(self):
        module = load_module()
        with tempfile.TemporaryDirectory() as temp_dir:
            source = Path(temp_dir) / "background.png"
            output = Path(temp_dir) / "poster.png"
            Image.new("RGB", (1080, 1350), "#101312").save(source)

            module.compose_poster(
                background_path=source,
                output_path=output,
                title="한 방울의\n수분 루틴",
                subtitle="가볍게 스며드는 데일리 세럼",
                title_font_path=FONT_DIR / "Pretendard-Bold.otf",
                subtitle_font_path=FONT_DIR / "Pretendard-Regular.otf",
                placement="bottom",
                eyebrow="DEWDROP / SERUM 01",
                feature_text="산뜻한 수분감",
                footer="EDITORIAL STUDY · 4:5",
            )

            with Image.open(output).convert("RGB") as result:
                pixels = result.load()
                top_band_light = sum(
                    1
                    for y in range(40, 160)
                    for x in range(60, 1020)
                    if min(pixels[x, y]) > 180
                )
                lower_band_light = sum(
                    1
                    for y in range(820, 1320)
                    for x in range(60, 1020)
                    if min(pixels[x, y]) > 180
                )
                self.assertGreater(top_band_light, 100)
                self.assertGreater(lower_band_light, 2000)

    def test_eyebrow_does_not_inject_unapproved_right_label(self):
        """Catches hard-coded editorial copy that was never supplied by the user."""
        module = load_module()
        with tempfile.TemporaryDirectory() as temp_dir:
            source = Path(temp_dir) / "background.png"
            output = Path(temp_dir) / "poster.png"
            Image.new("RGB", (1080, 1350), "#101312").save(source)

            module.compose_poster(
                background_path=source,
                output_path=output,
                title="제목",
                subtitle="서브타이틀",
                title_font_path=FONT_DIR / "Pretendard-Bold.otf",
                subtitle_font_path=FONT_DIR / "Pretendard-Regular.otf",
                eyebrow="USER APPROVED",
            )

            with Image.open(output).convert("RGB") as result:
                injected_pixels = sum(
                    1
                    for y in range(50, 105)
                    for x in range(700, 1020)
                    if min(result.getpixel((x, y))) > 180
                )
                self.assertLess(injected_pixels, 10)

    def test_custom_subtitle_size_increases_rendered_text_footprint(self):
        """Catches a compositor that ignores the mobile-legibility size override."""
        module = load_module()
        with tempfile.TemporaryDirectory() as temp_dir:
            source = Path(temp_dir) / "background.png"
            small_output = Path(temp_dir) / "small.png"
            large_output = Path(temp_dir) / "large.png"
            Image.new("RGB", (1080, 1350), "#101312").save(source)

            common = {
                "background_path": source,
                "title": "",
                "subtitle": "UV PLUS · SPF 50/PA++++",
                "title_font_path": FONT_DIR / "Pretendard-Bold.otf",
                "subtitle_font_path": FONT_DIR / "Pretendard-Regular.otf",
            }
            module.compose_poster(output_path=small_output, subtitle_size=28, **common)
            module.compose_poster(output_path=large_output, subtitle_size=52, **common)

            def light_pixels(path):
                with Image.open(path).convert("RGB") as result:
                    return sum(
                        1
                        for y in range(80, 230)
                        for x in range(60, 1020)
                        if min(result.getpixel((x, y))) > 180
                    )

            self.assertGreater(light_pixels(large_output), light_pixels(small_output) * 1.5)

    def test_custom_title_spacing_separates_multiline_headline(self):
        """Catches a compositor that ignores the requested headline leading."""
        module = load_module()
        with tempfile.TemporaryDirectory() as temp_dir:
            source = Path(temp_dir) / "background.png"
            tight_output = Path(temp_dir) / "tight.png"
            open_output = Path(temp_dir) / "open.png"
            Image.new("RGB", (1080, 1350), "#101312").save(source)

            common = {
                "background_path": source,
                "title": "가\n가",
                "subtitle": "",
                "title_font_path": FONT_DIR / "Pretendard-Bold.otf",
                "subtitle_font_path": FONT_DIR / "Pretendard-Regular.otf",
            }
            module.compose_poster(output_path=tight_output, title_spacing=-10, **common)
            module.compose_poster(output_path=open_output, title_spacing=30, **common)

            def bottommost_title_pixel(path):
                with Image.open(path).convert("RGB") as result:
                    rows = [
                        y
                        for y in range(80, 420)
                        if any(min(result.getpixel((x, y))) > 180 for x in range(60, 420))
                    ]
                    return max(rows)

            self.assertGreaterEqual(
                bottommost_title_pixel(open_output) - bottommost_title_pixel(tight_output),
                35,
            )

    def test_default_multiline_title_uses_open_leading(self):
        """Catches a default that makes stacked Korean headline lines look cramped."""
        module = load_module()
        with tempfile.TemporaryDirectory() as temp_dir:
            source = Path(temp_dir) / "background.png"
            default_output = Path(temp_dir) / "default.png"
            tight_output = Path(temp_dir) / "tight.png"
            Image.new("RGB", (1080, 1350), "#101312").save(source)

            common = {
                "background_path": source,
                "title": "매일의 UV 루틴,\n클라랑스",
                "subtitle": "",
                "title_font_path": FONT_DIR / "Pretendard-Bold.otf",
                "subtitle_font_path": FONT_DIR / "Pretendard-Regular.otf",
            }
            module.compose_poster(output_path=default_output, **common)
            module.compose_poster(output_path=tight_output, title_spacing=-10, **common)

            def bottommost_title_pixel(path):
                with Image.open(path).convert("RGB") as result:
                    rows = [
                        y
                        for y in range(80, 440)
                        if any(min(result.getpixel((x, y))) > 180 for x in range(60, 1020))
                    ]
                    return max(rows)

            self.assertGreaterEqual(
                bottommost_title_pixel(default_output) - bottommost_title_pixel(tight_output),
                15,
            )


if __name__ == "__main__":
    unittest.main()
