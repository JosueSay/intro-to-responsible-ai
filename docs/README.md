# Documentación — Servicio de Moderación de Contenido

Punto de entrada a la documentación del laboratorio. Un **Provider** (API REST
`POST /moderate`) y un **Consumer** (CLI) que consume el endpoint de cualquier
compañero en la misma red o vía túnel Cloudflare.

## Índice

| Documento                          | Contenido                                              |
| ---------------------------------- | ------------------------------------------------------ |
| [analisis-enunciado.md](analisis-enunciado.md) | Incoherencias, supuestos, dudas y objetivo del lab. |
| [arquitectura.md](arquitectura.md) | Componentes, flujo de una request y diagrama.          |
| [contrato-api.md](contrato-api.md) | Contrato exacto de `POST /moderate` (request/respuesta/errores). |
| [librerias.md](librerias.md)       | Stack y librerías usadas (solo stdlib + PyYAML opcional). |
| [ejecucion.md](ejecucion.md)       | Requisitos, dónde corre, puertos y comandos desglosados. |
| [modulos.md](modulos.md)           | Desglose archivo por archivo del código.               |
| [pruebas.md](pruebas.md)           | Set de pruebas dockerizado (pytest, unit + integration). |
| [runbook-wsl.md](runbook-wsl.md)   | Paso a paso para correr el lab en WSL2 (server, firewall, cliente). |
| [tunel-cloudflare.md](tunel-cloudflare.md) | Exposición pública vía Cloudflare Tunnel.      |

## Resumen rápido

| Componente | Archivo         | Rol                                        |
| ---------- | --------------- | ------------------------------------------ |
| Provider   | `server.py`     | Expone `POST /moderate` en `0.0.0.0:8010`. |
| Consumer   | `client.py`     | CLI que hace el POST y muestra el veredicto. |
| Lógica     | `moderation.py` | Reglas por keywords + carga de config.     |
| Config     | `config.yml`    | Todos los valores ajustables.              |
