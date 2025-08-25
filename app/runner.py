# /app/runner.py
_views = None

def start():
    """Arranca el poller y construye las vistas/KPIs. Devuelve un dict."""
    global _views
    import tables
    from pollers import wolkvox

    # pasar los writers al poller (evita circular imports)
    wolkvox.start(tables.agentes_writer, tables.lat_writer)

    _views = tables.build_views()
    return _views

def stop():
    from pollers import wolkvox
    wolkvox.stop()