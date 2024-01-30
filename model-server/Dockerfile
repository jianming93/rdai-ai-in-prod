ARG TRITON_VERSION=24.01
ARG TRITON_BACKEND=vllm
ARG MODEL_URL
ARG REVISION
FROM nvcr.io/nvidia/tritonserver:${TRITON_VERSION}-${TRITON_BACKEND}-python-py3



RUN echo ${REVISION}

RUN pip install --upgrade huggingface_hub

RUN huggingface-cli download $MODEL_URL --local-dir Mixtral-8x7B-Instruct-v0.1-GPTQ --local-dir-use-symlinks False