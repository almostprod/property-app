import pathlib
import json

import jinja2

from starlette.templating import Jinja2Templates


@jinja2.contextfunction
def asset_url(context: dict, name: str, dist_root=None):
    if dist_root is None:
        from property_app.config import get_config

        config = get_config()
        dist_root = config.DIST_ROOT

    dist_path = pathlib.Path(dist_root)
    manifest_path = dist_path / pathlib.Path("assets/manifest.json")
    with open(manifest_path, "rb") as manifest_file:
        manifest = json.load(manifest_file)

    asset_name = pathlib.Path(manifest[name])

    request = context["request"]

    return request.url_for("assets", path=asset_name.as_posix())


def get_templates(template_root=None):
    from property_app.config import get_config

    if template_root is None:
        config = get_config()
        template_root = pathlib.Path(config.TEMPLATE_ROOT)

    template_dir = template_root / pathlib.Path("templates")

    templates = Jinja2Templates(directory=template_dir.as_posix())

    jinja_env = templates.env
    jinja_env.globals["asset_url"] = asset_url

    return templates
