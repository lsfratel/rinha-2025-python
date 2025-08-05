import traceback
from collections import abc, defaultdict
from inspect import getmembers, isfunction

from ..constants import METHODS, STATUS_CODE
from ..http import Request, on_exception
from ..urls import exec_it, match_it, parse_it, path


class Application:
    def __init__(
        self,
        urls: list[path],
        on_exception: abc.Callable[
            [Request, Exception], tuple[int, dict[str, str], bytes]
        ] = on_exception,
    ):
        self.routes = defaultdict(list)
        self.on_exception = on_exception
        self.process_urls(urls)

    def process_urls(self, urls: list[path]):
        for p in urls:
            if isinstance(p.view, list):
                self.process_urls(p.view)
                continue
            for name, _ in getmembers(p.view, isfunction):
                method_name = name.upper()
                if method_name not in METHODS:
                    continue
                rules = parse_it(p.path)
                rules[0].update({"view": p.view, "handler": name})
                self.routes[method_name].append(rules)
                if (
                    method_name == "GET"
                    and not hasattr(p.view, "head")
                    and not hasattr(p.view, "HEAD")
                ):
                    self.routes["HEAD"].append(rules)

    def __call__(self, environ: dict, start_response):
        http_method = environ.get("REQUEST_METHOD", "get").upper()
        request_path = environ.get("PATH_INFO", "/")
        matched_routes = match_it(request_path, self.routes.get(http_method, []))
        if not matched_routes:
            start_response(STATUS_CODE[404], (("Content-Length", "0"),))
            return []
        req = Request(environ)
        params = exec_it(req.path, matched_routes)
        req.path_params = params
        route, *_ = matched_routes
        view_instance = None
        try:
            view_instance = route["view"]()
            view_instance.ctx = {"request": req}
            handler = getattr(view_instance, route["handler"])
            status_c, headers, body = handler(req)
        except Exception as ex:
            traceback.print_exc()
            if view_instance and hasattr(view_instance, "on_exception"):
                handler = view_instance.on_exception
            else:
                handler = self.on_exception
            status_c, headers, body = handler(req, ex)
        if "content-length" not in headers:
            headers["content-length"] = str(len(body))
        start_response(STATUS_CODE[status_c], list(headers.items()))
        if req.method == "HEAD":
            return []
        return [body]
