# onejev-decide — GPU CUDA 12.8 (Ubuntu 24.04 / GLIBC ≥ 2.38)
FROM nvidia/cuda:12.8.0-runtime-ubuntu24.04

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DECISION_CONFIG=/app/config.yaml \
    HF_HOME=/cache/huggingface \
    UV_SYSTEM_PYTHON=1 \
    UV_BREAK_SYSTEM_PACKAGES=1 \
    LD_LIBRARY_PATH=/opt/llama:/usr/local/nvidia/lib64:/usr/local/cuda/lib64:${LD_LIBRARY_PATH}

RUN apt-get update && apt-get install -y --no-install-recommends \
      python3 curl ca-certificates tar \
      libgomp1 libstdc++6 \
    && rm -rf /var/lib/apt/lists/*

ARG LLAMA_TAG=b12038
ARG LLAMA_URL=https://github.com/ggml-org/llama.cpp/releases/download/${LLAMA_TAG}/llama-${LLAMA_TAG}-bin-ubuntu-cuda-12.8-x64.tar.gz
ARG CUDART_URL=https://github.com/ggml-org/llama.cpp/releases/download/${LLAMA_TAG}/cudart-llama-${LLAMA_TAG}-bin-ubuntu-cuda-12.8-x64.tar.gz
RUN mkdir -p /opt/llama && \
    curl -fsSL -o /tmp/llama.tgz "$LLAMA_URL" && \
    tar -xzf /tmp/llama.tgz -C /opt/llama --strip-components=1 && \
    rm /tmp/llama.tgz && \
    curl -fsSL -o /tmp/cudart.tgz "$CUDART_URL" && \
    tar -xzf /tmp/cudart.tgz -C /opt/llama --strip-components=1 && \
    rm /tmp/cudart.tgz && \
    ln -sf /opt/llama/llama-server /usr/local/bin/llama-server && \
    test -x /opt/llama/llama-server

WORKDIR /app
COPY requirements.txt scripts/patch_qev.py ./
RUN uv pip install -r requirements.txt \
 && curl -fsSL -o /tmp/onejev.tgz https://github.com/OmniJev/OneJev/archive/refs/heads/main.tar.gz \
 && tar -xzf /tmp/onejev.tgz -C /tmp \
 && uv pip install /tmp/OneJev-main \
 && rm -rf /tmp/onejev.tgz /tmp/OneJev-main \
 && command -v qev \
 && python3 patch_qev.py

COPY config.yaml ./
COPY onejev_decide ./onejev_decide
COPY scripts ./scripts
COPY ui ./ui

EXPOSE 8000
VOLUME ["/cache/huggingface", "/app/data", "/app/outputs"]

COPY scripts/docker-entrypoint.sh /docker-entrypoint.sh
RUN sed -i 's/\r$//' /docker-entrypoint.sh scripts/*.sh \
 && chmod +x /docker-entrypoint.sh scripts/*.sh

ENTRYPOINT ["/docker-entrypoint.sh"]
CMD ["serve"]
