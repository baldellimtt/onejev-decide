# onejev-decide

Typed visual decisions with [OneJev](https://github.com/OmniJev/OneJev): YAML → calibrated answers → alert.  
Package Python atomico `onejev_decide` + Docker GPU + playground.

Warm latency tipica (RTX 3050): **~0.3–0.7 s** (IQ4_XS, vision cap 128, warmup al boot).

---

## Install

### A) Docker GPU (consigliato)

**Requisiti:** Docker Desktop + NVIDIA.

```bash
git clone https://github.com/YOUR_USER/onejev-decide.git
cd onejev-decide
docker compose up -d --build
```

| | |
|---|---|
| API | http://127.0.0.1:8000 |
| UI | http://127.0.0.1:7860 |

All’avvio il container fa **warmup** (prima inferenza automatica). Poi:

```bash
docker compose run --rm infer data/incident/incident_01.jpg --pretty
```

### B) Windows nativo

**Requisiti:** [uv](https://docs.astral.sh/uv/), `llama-server`.

```powershell
git clone https://github.com/YOUR_USER/onejev-decide.git
cd onejev-decide
.\scripts\setup.ps1
.\scripts\serve.ps1
```

```powershell
.\.venv\Scripts\python.exe -m onejev_decide.warmup
.\.venv\Scripts\python.exe scripts\ui.py
.\.venv\Scripts\python.exe scripts\infer.py data\incident\incident_01.jpg --pretty
```

### C) Ubuntu nativo

```bash
git clone https://github.com/YOUR_USER/onejev-decide.git
cd onejev-decide
chmod +x scripts/*.sh
./scripts/setup.sh
./scripts/serve.sh
```

```bash
./.venv/bin/python -m onejev_decide.warmup
./.venv/bin/python scripts/ui.py
```

### Sample images

```bash
python scripts/fetch_samples.py
```

---

## Package

```text
onejev_decide/
  decide.py      # API pubblica
  client.py      # HTTP pooled
  media.py       # resize JPEG
  answers.py     # normalize + soglie
  questions.py   # YAML → System One
  warmup.py      # cold-start killer
config.yaml      # modello + latenza + domande
```

```python
from onejev_decide import decide
print(decide(Path("foto.jpg")))
```

---

## Config (latenza)

[`config.yaml`](config.yaml): `IQ4_XS`, `max_image_side: 320`, `image_max_tokens: 128`, `warmup: true`, una sola domanda `overflow`.

---

## License

Apache-2.0
