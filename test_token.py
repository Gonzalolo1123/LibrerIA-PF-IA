from llama_cpp import Llama

# Ruta al modelo .gguf
llm = Llama(model_path="models/llama-2-7b.Q4_K_M.gguf")

prompt = "Responde de manera formal y cordial: ¿Cuál es el horario de atención?"
output = llm(prompt, max_tokens=100)

print(output['choices'][0]['text'])