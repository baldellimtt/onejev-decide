# onejev-decide

Typed visual decisions with [OneJev](https://github.com/OmniJev/OneJev): YAML → calibrated answers → alert.  
Lean Python package `onejev_decide` + GPU Docker + playground UI.

Typical warm latency (RTX 3050): **~0.3–0.7 s** (IQ4_XS, vision cap 128, boot warmup).

---

## Install

### A) Docker GPU (recommended)

**Requirements:** Docker Desktop + NVIDIA.

```bash
git clone https://github.com/baldellimtt/onejev-decide.git
cd onejev-decide
./scripts/up.sh          # Linux/macOS
# .\scripts\up.ps1       # Windows
```

After compose finishes healthy, the script prints:

```text
 API   http://127.0.0.1:8000
 UI    http://127.0.0.1:7860
```

On start the container runs a **warmup** inference. Then:

```bash
docker compose run --rm infer data/incident/incident_01.jpg --pretty
```

### B) Native Windows

**Requirements:** [uv](https://docs.astral.sh/uv/), `llama-server`.

```powershell
git clone https://github.com/baldellimtt/onejev-decide.git
cd onejev-decide
.\scripts\setup.ps1
.\scripts\serve.ps1
```

```powershell
.\.venv\Scripts\python.exe -m onejev_decide.warmup
.\.venv\Scripts\python.exe scripts\ui.py
.\.venv\Scripts\python.exe scripts\infer.py data\incident\incident_01.jpg --pretty
```

### C) Native Ubuntu

```bash
git clone https://github.com/baldellimtt/onejev-decide.git
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
  decide.py      # public API
  client.py      # pooled HTTP
  media.py       # JPEG resize
  answers.py     # normalize + thresholds
  questions.py   # YAML → System One
  warmup.py      # cold-start killer
config.yaml      # model + latency + questions
```

```python
from pathlib import Path
from onejev_decide import decide

print(decide(Path("photo.jpg")))
```

---

## Config (latency)

[`config.yaml`](config.yaml): `IQ4_XS`, `max_image_side: 320`, `image_max_tokens: 128`, `warmup: true`, single `overflow` question.

---

## License

Apache-2.0
