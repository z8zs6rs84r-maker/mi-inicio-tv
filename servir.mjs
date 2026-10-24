// Servidor mínimo para ver la pantalla de inicio en la Mac: node servir.mjs [puerto]
import { createServer } from 'node:http';
import { readFile } from 'node:fs/promises';
import { extname, join, normalize } from 'node:path';
import { fileURLToPath } from 'node:url';

const carpeta = fileURLToPath(new URL('.', import.meta.url));
const puerto = Number(process.argv[2] || 8080);
const tipos = { '.html': 'text/html; charset=utf-8', '.js': 'text/javascript', '.css': 'text/css',
  '.png': 'image/png', '.svg': 'image/svg+xml', '.json': 'application/json' };

createServer(async (req, res) => {
  const ruta = normalize(decodeURIComponent(new URL(req.url, 'http://x').pathname)).replace(/^(\.\.[/\\])+/, '');
  const archivo = join(carpeta, ruta.endsWith('/') ? ruta + 'index.html' : ruta);
  if (!archivo.startsWith(carpeta)) { res.writeHead(403).end(); return; }
  try {
    const datos = await readFile(archivo);
    res.writeHead(200, { 'Content-Type': tipos[extname(archivo)] || 'application/octet-stream' }).end(datos);
  } catch {
    res.writeHead(404).end('No encontrado');
  }
}).listen(puerto, () => console.log(`Pantalla de inicio en http://localhost:${puerto}/`));
