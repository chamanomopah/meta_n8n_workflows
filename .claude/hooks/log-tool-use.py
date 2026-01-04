#!/usr/bin/env python3
import json
import sys
import os
from datetime import datetime

# Criar pasta logs se não existir
log_dir = "./logs"
os.makedirs(log_dir, exist_ok=True)

# Ler input do stdin (JSON com dados da tool)
input_data = json.load(sys.stdin)

# Extrair informações
log_entry = {
    "timestamp": datetime.now().isoformat(),
    "tool_name": input_data.get("tool_name", "unknown"),
    "tool_input": input_data.get("tool_input", {}),
    "session_id": input_data.get("session_id", ""),
}

# Salvar no arquivo de log
log_file = os.path.join(log_dir, "tool-usage.jsonl")
with open(log_file, "a") as f:
    f.write(json.dumps(log_entry) + "\n")

# Exit code 0 = sucesso
sys.exit(0)