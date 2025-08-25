# /app/pollers/wolkvox.py
import json, datetime as dt, time, threading
from urllib.request import Request, urlopen
from config import URL_AGENTES, URL_LATENCIA, HEADERS, POLL_SECONDS

_stop_flag = False
_thread = None

def _get_json(url, headers, timeout=30):
    req = Request(url, headers=headers, method="GET")
    with urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))

def _to_int(x, default=0):
    try:
        return int(str(x).strip())
    except Exception:
        return default

def _loop(agentes_writer, lat_writer):
    global _stop_flag
    while not _stop_flag:
        ts_now = dt.datetime.now(dt.timezone.utc)
        ts_str = ts_now.isoformat() + "Z"

        # --- agentes ---
        try:
            data = _get_json(URL_AGENTES, HEADERS)
            rows = data if isinstance(data, list) else data.get("data", [])
            for a in rows:
                agentes_writer.write_row(
                    ts_str,
                    str(a.get("agent_id","")),
                    str(a.get("agent_name","")),
                    str(a.get("agent_status","")),
                    _to_int(a.get("calls",0)),
                    _to_int(a.get("inbound",0)),
                    _to_int(a.get("outbound",0)),
                    _to_int(a.get("internal",0)),
                    _to_int(a.get("time_state_now",0)),
                    _to_int(a.get("ready_time",0)),
                    _to_int(a.get("inbound_time",0)),
                    _to_int(a.get("outbound_time",0)),
                    _to_int(a.get("acw_time",0)),
                    _to_int(a.get("ring_time",0)),
                    str(a.get("login_time","")),
                    _to_int(a.get("aht_time",0)),
                    _to_int(a.get("ocupation",0)),  # la API lo nombra así
                    _to_int(a.get("aux_time",0))
                )
        except Exception as e:
            print("Error agentes:", repr(e))

        # --- latencia ---
        try:
            dlat = _get_json(URL_LATENCIA, HEADERS)
            por_agente = dlat.get("por_agente", dlat.get("data", dlat if isinstance(dlat, list) else []))
            for r in por_agente:
                lat_writer.write_row(
                    ts_str,
                    str(r.get("agent_id", r.get("id_agente",""))),
                    str(r.get("agent_status", r.get("estado",""))),
                    str(r.get("IP", r.get("ip",""))),
                    str(r.get("version", r.get("versión",""))),
                    str(r.get("platform", r.get("plataforma",""))),
                    str(r.get("connection_type", r.get("tipo_de_conexión",""))),
                    _to_int(r.get("latency_ms", r.get("latencia_ms",0))),
                    _to_int(r.get("jitter_tx", r.get("fluctuación de transmisión",0))),
                    _to_int(r.get("jitter_rx", r.get("fluctuación de rx",0))),
                    _to_int(r.get("tx_ploss", 0)),
                    _to_int(r.get("rx_ploss", 0)),
                    _to_int(r.get("network_reject_pct", r.get("rechazo de red",0))),
                    str(r.get("last_seen", r.get("última fecha","")))
                )
        except Exception as e:
            print("Error latencia:", repr(e))

        time.sleep(POLL_SECONDS)

def start(agentes_writer, lat_writer):
    """Arranca el hilo del poller usando writers inyectados."""
    global _thread, _stop_flag
    if _thread and _thread.is_alive():
        print("Poller ya está corriendo")
        return
    _stop_flag = False
    _thread = threading.Thread(target=_loop, args=(agentes_writer, lat_writer), daemon=True)
    _thread.start()
    print("Poller Wolkvox iniciado")

def stop():
    global _stop_flag
    _stop_flag = True
    print("Poller Wolkvox detenido (se detendrá al final del ciclo)")