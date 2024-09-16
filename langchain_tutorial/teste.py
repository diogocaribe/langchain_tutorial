from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama.llms import OllamaLLM

template = """Question: {question}

Answer: Let's think step by step."""

prompt = ChatPromptTemplate.from_template(template)

# Configure a URL do Ollama
ollama_url = "http://localhost:11434"

model = OllamaLLM(model="llama3", base_url=ollama_url)

chain = prompt | model

response = chain.invoke({"question": "What is LangChain?"})
print(response)