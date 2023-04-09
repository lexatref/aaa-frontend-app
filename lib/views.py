from io import BytesIO

from aiohttp.web import Response
from aiohttp.web import View
from aiohttp_jinja2 import render_template

from lib.image import image_to_img_src
from lib.image import PolygonDrawer
from lib.image import open_image


class IndexView(View):
    async def get(self) -> Response:
        return render_template("index.html", self.request, {})

    async def post(self) -> Response:
        try:
            form = await self.request.post()
            image = open_image(form["image"].file)
            temp = BytesIO()
            image.save(temp, format="jpeg")
            image = open_image(temp)
            draw = PolygonDrawer(image)
            try:
                language = form["language"]
                if language == "ru":
                    model = self.request.app["modelru"]
                else:
                    model = self.request.app["model"]
            except Exception:
                model = self.request.app["model"]
            words = []
            for coords, word, accuracy in model.readtext(image):
                draw.highlight_word(coords, word)
                cropped_img = draw.crop(coords)
                cropped_img_b64 = image_to_img_src(cropped_img)
                try:
                    min_acc = float(form["accuracy"])/100
                except Exception:
                    min_acc = 0.
                if accuracy > min_acc:
                    words.append(
                        {
                            "image": cropped_img_b64,
                            "word": word,
                            "accuracy": accuracy,
                        }
                    )
            image_b64 = image_to_img_src(draw.get_highlighted_image())
            ctx = {"image": image_b64, "words": words}
            return render_template("index.html", self.request, ctx)
        except Exception as err:
            ctx = {
                    "error": str(err),
                    'errortype': str(type(err))[8:-2]
                    }
            return render_template("index.html", self.request, ctx)
