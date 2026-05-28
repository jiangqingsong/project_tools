import importlib
import pkgutil
from pathlib import Path

from fastapi import FastAPI


def register_routers(app: FastAPI):
    modules_path = Path(__file__).parent.parent / "modules"
    if not modules_path.exists():
        return
    for module_info in pkgutil.iter_modules([str(modules_path)]):
        try:
            mod = importlib.import_module(f"app.modules.{module_info.name}.router")
        except ModuleNotFoundError:
            continue
        if hasattr(mod, "router"):
            prefix = f"/api/{module_info.name}"
            app.include_router(mod.router, prefix=prefix)
