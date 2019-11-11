from __future__ import annotations

from flask import Flask
from flask import request as flask_request
from flask.globals import _request_ctx_stack

from open_horadric_lib.base.context import Context
from open_horadric_lib.proxy.request import ProxyRequest


class ProxyApplication(Flask):
    request_class = ProxyRequest
    context_class = Context

    def dispatch_request(self):
        """
        Copied and fixed for context using
        :return:
        """
        req = _request_ctx_stack.top.request
        if req.routing_exception is not None:
            self.raise_routing_exception(req)
        rule = req.url_rule
        # if we provide automatic options for this URL and the
        # request came with the OPTIONS method, reply automatically
        if getattr(rule, "provide_automatic_options", False) and req.method == "OPTIONS":
            return self.make_default_options_response()
        # otherwise dispatch to the handler for that endpoint
        return self.view_functions[rule.endpoint](request=flask_request, context=self.context_class(), **req.view_args)
