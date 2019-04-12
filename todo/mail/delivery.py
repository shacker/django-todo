import importlib


def _declare_backend(backend_path):
    backend_path = backend_path.split(".")
    backend_module_name = ".".join(backend_path[:-1])
    class_name = backend_path[-1]

    def backend(*args, headers={}, from_address=None, **kwargs):
        def _backend():
            backend_module = importlib.import_module(backend_module_name)
            backend = getattr(backend_module, class_name)
            return backend(*args, **kwargs)

        if from_address is None:
            raise ValueError("missing from_address")

        _backend.from_address = from_address
        _backend.headers = headers
        return _backend

    return backend


smtp_backend = _declare_backend("django.core.mail.backends.smtp.EmailBackend")
console_backend = _declare_backend("django.core.mail.backends.console.EmailBackend")
locmem_backend = _declare_backend("django.core.mail.backends.locmem.EmailBackend")
