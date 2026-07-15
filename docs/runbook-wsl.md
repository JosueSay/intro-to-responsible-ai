# Runbook — correr el lab en WSL2

Guía paso a paso para levantar el Provider, abrir el puerto y consumir/atender a
compañeros en la misma red (hotspot). Pensada para WSL2 en modo *mirrored*.

## Concepto clave: qué IP se usa

| IP                         | Ejemplo           | ¿Se usa en el lab? |
| -------------------------- | ----------------- | ------------------ |
| Pública (la de "cuál es mi IP") | `190.14.133.227` | **No** (CGNAT, no alcanzable). |
| Local / LAN (en el hotspot)| `192.168.x.x`     | **Sí**: esta compartís. |

Averiguá tu IP local siempre con:

```bash
hostname -I | awk '{print $1}'
```

## Paso a paso

### 1. Conectarse al hotspot

Conectá **Windows** a la WiFi del teléfono. WSL2 (mirrored) hereda la red.

### 2. Prender el servidor (Provider)

```bash
cd ~/uvg/responsible-ai
.venv/bin/python server.py        # o: make serve
```

Debe imprimir `Servidor escuchando en 0.0.0.0:8000`. Dejá la terminal abierta.
Para reiniciarlo: `pkill -f server.py` y volvé a correrlo.

### 3. Abrir el puerto 8000 en el Firewall de Windows

Requiere **PowerShell como administrador**:

1. Tecla Windows → escribí `PowerShell`.
2. Clic derecho → **Ejecutar como administrador** → aceptar UAC.
3. Correr:

```powershell
New-NetFirewallRule -DisplayName "Moderation 8000" -Direction Inbound -LocalPort 8000 -Protocol TCP -Action Allow
```

Alternativa (auto-eleva desde una PowerShell normal):

```powershell
Start-Process powershell -Verb RunAs -ArgumentList '-NoExit','-Command','New-NetFirewallRule -DisplayName "Moderation 8000" -Direction Inbound -LocalPort 8000 -Protocol TCP -Action Allow'
```

Verificar que quedó:

```powershell
Get-NetFirewallRule -DisplayName "Moderation 8000"
```

### 4. Probar tu propio server

```bash
.venv/bin/python client.py --host $(hostname -I | awk '{print $1}') --port 8000 --text "eres un idiota"
```

Esperado: `Verdict: BLOCKED | Confidence: 0.7 | Reason: ...`

### 5. Consumir a un compañero (sos Consumer)

Pedile su IP local y su puerto:

```bash
.venv/bin/python client.py --host <IP_DEL_COMPANERO> --port 8000 --text "hola mundo"
```

### 6. Que un compañero te consuma (sos Provider)

Pasale tu IP local (`hostname -I | awk '{print $1}'`) y el puerto `8000`. Él corre
el paso 5 apuntando a vos.

## Troubleshooting

| Síntoma                          | Significado                          | Acción                                   |
| -------------------------------- | ------------------------------------ | ---------------------------------------- |
| `No route to host`               | Distinta red / IP de otra subred     | Ambos en el hotspot; comparar prefijo de IP. |
| `timeout` con ping OK            | Firewall bloquea el 8000             | Paso 3 (regla de firewall).              |
| `Connection refused`             | El server no está prendido           | El dueño corre el paso 2.                |
| Funciona por `127.0.0.1` pero no por la IP | Firewall o red equivocada  | Paso 3 + revisar `hostname -I`.          |
| `Acceso denegado / Error 5` en PowerShell | PowerShell sin admin        | Abrir PowerShell como administrador.     |

## Comandos de referencia

```bash
make serve                                         # prender el server
make moderate TEXT="idiota" HOST=<ip> PORT=8000    # cliente rápido
make test-docker                                   # 29 pruebas en contenedores
hostname -I | awk '{print $1}'                     # tu IP local del momento
pkill -f server.py                                 # apagar el server
```
