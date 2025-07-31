from functools import reduce


class include:
    def __init__(self, module: str):
        self.module = module

    def load(self, ppath: str):
        module = __import__(self.module, fromlist=["urls"])
        murls: list[path] = getattr(module, "urls", [])

        for url in murls:
            url.path = self._normalize_path(ppath, url.path)

        return murls

    def _normalize_path(self, *path_segments: str):
        combined = reduce(lambda x, y: x + y, path_segments)
        return "/".join(filter(None, combined.split("/")))

    def __repr__(self):
        return f"<include module={self.module}>"


class path:
    def __init__(self, path: str, view: type | include):
        self.path = path
        self.view = view if isinstance(view, type) else view.load(path)

    def __repr__(self):
        return f"<path path={self.path} view={self.view}>"
