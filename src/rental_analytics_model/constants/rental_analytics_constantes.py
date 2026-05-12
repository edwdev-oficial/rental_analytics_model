MODELOS_ROMPEDOR_VALIDOS = [
    "te500",
    "te600",
    "te700",
    "te800",
    "te1000",
    "te2000",
    "te3000",
]

COL_RENAME_REPAROS = {
    "Custo de Reparos": "custo_total",
    "Pagado pelo Cliente": "custo_cliente",
    "Economia": "economia",
    "# Notif.": "falhas",
}

COLS_REPAROS_FINAL = [
    "modelo",
    "Número de Série",
    "Idade em Anos",
    "idade_int",
    "falhas",
    "# Reparos",
    "custo_total",
    "custo_cliente",
    "economia",
]