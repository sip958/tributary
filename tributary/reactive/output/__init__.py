from pprint import pprint
from functools import partial

from ..base import _wrap, FunctionWrapper
from .kafka import Kafka as KafkaSink  # noqa: F401
from .http import HTTP as HTTPSink  # noqa: F401


def Print(foo, foo_kwargs=None):
    foo = _wrap(foo, foo_kwargs or {})

    def _print(foo):
        for r in foo():
            print(r)

    return _wrap(_print, dict(foo=foo), name='Print', wraps=(foo,), share=foo)


def Graph(f_wrap):
    if not isinstance(f_wrap, FunctionWrapper):
        raise Exception('ViewGraph expects tributary')
    return f_wrap.view(0)[0]


def PPrint(f_wrap):
    pprint(Graph(f_wrap))


def GraphViz(f_wrap, name='Graph'):
    d = Graph(f_wrap)
    from graphviz import Digraph
    dot = Digraph(name, strict=True)
    dot.format = 'png'

    def rec(nodes, parent):
        for d in nodes:
            if not isinstance(d, dict):
                dot.node(d)
                dot.edge(d, parent)

            else:
                for k in d:
                    dot.node(k)
                    rec(d[k], k)
                    dot.edge(k, parent)

    for k in d:
        dot.node(k)
        rec(d[k], k)

    return dot


def Perspective(foo, foo_kwargs=None, **psp_kwargs):
    foo = _wrap(foo, foo_kwargs or {})

    from perspective import PerspectiveWidget
    p = PerspectiveWidget([], **psp_kwargs)

    def _perspective(foo):
        for r in foo():
            p.update(r)
            yield r

    from IPython.display import display
    display(p)

    return _wrap(_perspective, dict(foo=foo), name='Perspective', wraps=(foo,), share=foo)


def FunctionalSink(f_wrap, callback, callback_kwargs):
    if not isinstance(f_wrap, FunctionWrapper):
        raise Exception('Functional expects tributary')

    callback = partial(callback, **callback_kwargs)

    def _foo(foo, callback_):
        for x in foo():
            yield callback(foo)

    return _wrap(_foo, dict(foo=f_wrap), name='Functional', wraps=(f_wrap,))
