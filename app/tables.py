
# ---------- WRITERS (usar dict en 0.39.7) ----------
# === Tabla AGENTES (alineada 1:1 con el API) ===
from deephaven import DynamicTableWriter
from deephaven import dtypes as dht

agentes_writer = DynamicTableWriter({
    "ts": dht.string,          # timestamp local en ISO: "2025-08-22T21:20:00Z"
    "agent_id": dht.string,
    "agent_name": dht.string,
    "agent_status": dht.string,
    "calls": dht.int32,
    "inbound": dht.int32,
    "outbound": dht.int32,
    "internal": dht.int32,
    "time_state_now": dht.long,
    "ready_time": dht.long,
    "inbound_time": dht.long,
    "outbound_time": dht.long,
    "acw_time": dht.long,
    "ring_time": dht.long,
    "login_time": dht.string,
    "aht_time": dht.long,
    "ocupation": dht.long,
    "aux_time": dht.long,
})
agentes_live = agentes_writer.table

lat_writer = DynamicTableWriter({
    "ts": dht.string,           # timestamp ISO string, e.g. "2025-08-22T21:20:00Z"
    "agent_id": dht.string,
    "agent_state": dht.string,  # API: agent_status / estado
    "ip": dht.string,           # API: IP
    "version": dht.string,
    "platform": dht.string,     # "app" o "web"
    "connection_type": dht.string,  # "Ethernet" o "Wi‑Fi"
    "latency_ms": dht.int32,
    "jitter_tx": dht.int32,
    "jitter_rx": dht.int32,
    "tx_ploss_pct": dht.int32,  # API: tx_ploss (%)
    "rx_ploss_pct": dht.int32,  # API: rx_ploss (%)
    "network_reject_pct": dht.int32,
    "last_seen_str": dht.string,
})
latencia_live = lat_writer.table

# ---------- VISTAS / KPIs ----------
def build_views():
    from deephaven import ui

    winA = agentes_live.where("ts >= now() - MINUTES(15)")
    kpi_calls_15m = winA.group_by("agent_id","agent_name").update([
        "Llamadas = max(calls)",
        "Entrantes = max(inbound)",
        "Salientes = max(outbound)",
        "Internas = max(internal)",
    ])

    winL = latencia_live.where("ts >= now() - MINUTES(5)")
    salud_red_5m = winL.group_by("agent_id").update([
        "lat_ms_avg = avg(latency_ms)",
        "tx_ploss_avg = avg(tx_ploss_pct)",
        "rx_ploss_avg = avg(rx_ploss_pct)",
    ])

    kpi_lat_prom = salud_red_5m.group_by().update(["LatenciaProm5m = avg(lat_ms_avg)"])

    agentes_con_problemas = (
        winL.where("latency_ms > 150 || tx_ploss_pct > 1 || rx_ploss_pct > 1")
            .group_by("agent_id").update(["_one = 1"]).group_by()
            .update(["AgentesConProblemas = sum(_one)"])
            .drop_columns("_one")
    )

    top_calls = (
        kpi_calls_15m.update("ord = -Llamadas")
                     .sort("ord")
                     .update_view("rank = (int) i")
                     .where("rank < 10")
    )
    chart_calls = ui.plot_xy("Top llamadas (15m)", top_calls, x="agent_name", y="Llamadas")

    return dict(
        kpi_calls_15m=kpi_calls_15m,
        salud_red_5m=salud_red_5m,
        kpi_lat_prom=kpi_lat_prom,
        agentes_con_problemas=agentes_con_problemas,
        chart_calls=chart_calls,
    )