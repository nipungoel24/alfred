const BASE=import.meta.env.VITE_ALFRED_API_URL ?? 'http://127.0.0.1:8765';
export async function api<T>(path:string, init?:RequestInit):Promise<T>{const r=await fetch(BASE+path,init);if(!r.ok){const body=await r.json().catch(()=>null);throw new Error(body?.error?.message||body?.detail||'Request failed');}return r.json();}
