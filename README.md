# Overview
This repo use opensource Vision - Large Language Model (vLLM) served by Ollama to create interactive chat. This project aims to quickly test the capability of vLLM locally in you personal PC laptop/desktop.

# Preprequisite

1. **Python** with pip.

2. **Pytorch** with CUDA (Optional) to leverage the GPU for faster inference of Ollama.

3. **[Ollama](https://ollama.com/)**. We use Ollama to serve the REST API server. 

# Installation

1. Clone this repository.

```
git clone https://github.com/tiencapham/ollama-vllm.git
cd ollama-vllm/
```

2. Install requirement.

```
pip install -r requirements.txt
```

3. Pull the Ollama model. (**Note** You only need to pull the first time). You can pull other models from **[Vision Model of Ollama](https://ollama.com/search?c=visionhttps://ollama.com/search?c=vision)**. 


```
ollama pull openbmb/minicpm-o2.6:8b
```

# Inference

1. Run the Streamlit app.

```
streamlit run main.py
```

2. Open the web using local URL: http://localhost:8501 or Network URL: http://your_ip:8501.

3. Enjoy an interactive chat.

# Demo
[![Watch the video](https:/img.youtube.com/watch?v=GzIvpj-MrjA)](https://www.youtube.com/watch?v=GzIvpj-MrjA)

# Troubleshoot

1. Ollama server still running after you terminate the process of this app. To stop the ollama server and release the GPU VRAM or CPU RAM, we have to stop the server using:

```
ollama stop openbmb/minicpm-o2.6:8b
```

You can list all of running models using ```ollama ps```.

2. GPU or CPU usage. Ollama will automaticly detect you GPU and will prioritize running on GPU if you have enough VRAM to run the model. Or it can be offloading to allow efficient inference.

