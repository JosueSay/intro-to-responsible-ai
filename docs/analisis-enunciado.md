# Análisis del enunciado

Lectura crítica de `instrucciones.md`: contradicciones internas, ambigüedades,
supuestos que asumió esta implementación y dudas abiertas para el instructor.

> El PDF original llega OCR-garbled ("jos"→fijos, "condence"→confidence,
> "oat"→float, "calica"→califica). El contrato se entiende igual.

## 1. Incoherencias internas del documento

| # | Incoherencia                                                        | Detalle                                                                 |
| - | ------------------------------------------------------------------- | ----------------------------------------------------------------------- |
| 1 | "muestra verdict y reason" vs. el ejemplo muestra 3 campos          | El ejemplo de salida incluye `Confidence`, que la descripción no menciona. |
| 2 | `verdict` en minúscula vs. `BLOCKED` en mayúscula                   | El JSON exige minúscula; el display del cliente usa mayúscula.           |
| 3 | El 400 define un mensaje exacto, pero hay más causas de 400          | Solo se especifica `text is required`; Content-Type/JSON inválido quedan sin mensaje definido. |
| 4 | Frontera 400 vs 500 sin definir                                     | Content-Type equivocado o JSON malformado: ¿error del cliente (400) o interno (500)? |

## 2. Supuestos asumidos por esta implementación

Decisiones tomadas donde el enunciado no es explícito. Todas son revisables si
el instructor aclara.

| Tema                         | Supuesto asumido                                              |
| ---------------------------- | ------------------------------------------------------------ |
| Puerto                       | `8000` por defecto (config), configurable en `config.yml`.   |
| Content-Type no JSON         | Responde **400** (`{"error": "Content-Type must be application/json"}`). |
| Body no parseable como JSON  | Responde **400** (`{"error": "invalid JSON body"}`).         |
| `text` no-string (ej. número)| Responde **400** `text is required`.                         |
| `text` solo espacios         | Cuenta como vacío → **400** (`strip()`).                     |
| `reason` en `allowed`        | Se incluye siempre (transparencia).                          |
| `confidence` en `allowed`    | Valor fijo `allowed_confidence` (0.95).                      |
| Salida del cliente           | Muestra `Verdict | Confidence | Reason` (formato del ejemplo). |
| Endpoint extra               | Se agrega `GET /health` para pruebas rápidas (no exigido).   |
| Lenguaje                     | Python 3.12, solo stdlib.                                     |
| Log del servidor             | Formato `[POST /moderate] IP -> code {...}` con IP del cliente. |

La frontera 400/500 se resolvió a favor de **400 para todo error atribuible al
cliente** (Content-Type, JSON, text); el **500** queda solo para excepciones no
controladas. Ver [contrato-api.md](contrato-api.md).

## 3. Dudas abiertas (priorizadas por impacto en la interoperabilidad)

Las 1–5 son las que de verdad rompen que las apps se hablen entre compañeros.

| # | Duda                                                                 | Por qué importa                                        |
| - | -------------------------------------------------------------------- | ------------------------------------------------------ |
| 1 | ¿Puerto fijo acordado (8000) o cada quien elige el suyo?             | Sin acuerdo, nadie sabe a qué puerto pegarle.          |
| 2 | ¿El formato de args del cliente (`host X port Y text Z`) es obligatorio y exacto, o vale `--host`? | El ejemplo usa un formato posicional inusual.          |
| 3 | ¿`reason` es obligatorio también en `allowed`?                       | No hay ejemplo de un `allowed`.                        |
| 4 | ¿Se evalúa la *lógica* de `confidence` o solo que sea float en [0,1]? | Con keywords no hay un score natural.                  |
| 5 | ¿Los mensajes de falla del cliente deben ser textuales exactos?      | Aparecen como "ejemplo", no como contrato.             |
| 6 | ¿`text` con solo espacios cuenta como vacío?                         | Caso borde no definido.                                |
| 7 | ¿Lenguaje libre o Python obligatorio?                                | Cambia qué es "correcto".                              |
| 8 | ¿Se exige el log del servidor con ese formato exacto?                | Está en "ejemplo de output".                           |
| 9 | ¿Encoding de `reason` (UTF-8/acentos)? ¿Límite de longitud de `text`? | Interop y robustez.                                    |
| 10| ¿Endpoints extra permitidos o solo `/moderate`?                      | Se agregó `/health`.                                   |

## 4. Hipótesis del objetivo real

El enunciado se presenta como "hacé una API", pero el diseño sugiere que lo
evaluado es otra cosa. El repo se llama **responsible-ai**.

1. **Disciplina de contrato / interoperabilidad.** El estándar es "no
   negociable" con enums y mensajes exactos. El test real parece ser: *¿tu app
   habla con la de un desconocido sin coordinar más que el contrato?* Premia
   respetar el spec al pie de la letra.

2. **Moderación responsable (ángulo responsible-ai).** Moderar por keywords es
   deliberadamente frágil: falsos positivos ("no puedo *matar* el tiempo"),
   falsos negativos (typos/leet), sesgo idiomático, censura excesiva. El schema
   fuerza `reason` (explicabilidad) y `confidence` (incertidumbre). Probable que
   se espere una reflexión sobre estas limitaciones.

3. **Robustez y seguridad.** El énfasis en 400/500/timeout y en exponer a
   `0.0.0.0` **sin auth** puede medir manejo de errores y conciencia de riesgo:
   servicio abierto a la red, inyección vía `reason`, DoS con payloads grandes.

## 5. Limitaciones conocidas del moderador por keywords

Para tener lista la defensa del ángulo "responsible AI":

- **Falsos positivos por contexto**: una keyword dentro de una frase inocente
  bloquea igual (no hay análisis semántico).
- **Falsos negativos triviales**: `id10ta`, `1d1ota` o acentos raros evaden la
  lista.
- **Sesgo de idioma/cultura**: la lista es estática y en español; no cubre otros
  idiomas ni jerga nueva.
- **Sin trazabilidad de decisión más allá de `reason`**: no hay auditoría ni
  apelación.
- **Mantenimiento**: la lista de keywords envejece y puede sobre/infra-bloquear.

Estas limitaciones son inherentes al enfoque por reglas; un sistema de
producción usaría modelos + revisión humana + métricas de error.
