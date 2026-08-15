import httpx
class OllamaUnavailable(Exception): pass
class OllamaClient:
 def __init__(self, base_url, client=None): self.base_url=base_url.rstrip('/'); self.client=client or httpx.AsyncClient(timeout=90)
 async def health(self):
  try: r=await self.client.get(self.base_url+'/api/tags'); r.raise_for_status(); return r.json()
  except httpx.HTTPError as e: raise OllamaUnavailable('Ollama is not currently reachable.') from e
 async def generate(self, model, prompt, schema=None, temperature=0.0):
  try:
   payload={'model':model,'prompt':prompt,'stream':False,'think':False,'options':{'temperature':temperature}}
   if schema: payload['format']=schema
   r=await self.client.post(self.base_url+'/api/generate',json=payload); r.raise_for_status()
   response_text = r.json()['response']
   import re
   clean_text = re.sub(r'<(think|thinking)>.*?</\1>', '', response_text, flags=re.IGNORECASE | re.DOTALL).strip()
   return clean_text
  except httpx.HTTPError as e: raise OllamaUnavailable('Ollama inference failed.') from e
