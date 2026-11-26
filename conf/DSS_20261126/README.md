# DSS 2026 — LLMRouter w praktyce: lokalne LLM-y dla Codex i Claude Code

Materiały do tutoriala prowadzonego podczas **Data Science Summit 2026** (online, 26.11.2026, 09:00–10:15).

> **Tytuł tutoriala:** *LLMRouter w praktyce: lokalne LLM-y dla Codex i Claude Code — Od uruchomienia routera i
> konfiguracji modeli po działających agentów AI korzystających z Ollama, llama.cpp i vLLM.*

Ten katalog zbiera materiały konferencyjne: prezentację, konfiguracje routingu oraz skrypty pomocnicze do budowy decka.
Poniżej znajdziesz opis zawartości, mapę repozytoriów i linki do dokumentacji potrzebnej do odtworzenia demo.

---

## Spis treści

- [Co jest w tym katalogu](#co-jest-w-tym-katalogu)
- [O czym jest tutorial](#o-czym-jest-tutorial)
- [Jak nawigować po materiałach](#jak-nawigować-po-materiałach)
- [Szybki start — odtworzenie demo](#szybki-start--odtworzenie-demo)
- [Konfiguracje w `configs/`](#konfiguracje-w-configs)
- [Mapa repozytoriów i narzędzi](#mapa-repozytoriów-i-narzędzi)
- [Dokumentacja pluginów i kluczowe funkcje](#dokumentacja-pluginów-i-kluczowe-funkcje)
- [Materiały źródłowe i lektura](#materiały-źródłowe-i-lektura)
- [Co dalej / roadmapa](#co-dalej--roadmapa)

---

## Co jest w tym katalogu

| Ścieżka                                                                                  | Opis                                                                            |
|------------------------------------------------------------------------------------------|---------------------------------------------------------------------------------|
| [`LLMRouter_DSS2026_tutorial.pptx`](./LLMRouter_DSS2026_tutorial.pptx)                   | Prezentacja tutoriala (PowerPoint).                                             |
| [`LLMRouter_DSS2026_tutorial.pdf`](./LLMRouter_DSS2026_tutorial.pdf)                     | Eksport prezentacji do PDF.                                                     |
| [`dock/`](./dock/)                                                                       | Materiały robocze decka: skrypty budujące slajdy i wersja markdown prezentacji. |
| [`dock/presentation.md`](./dock/presentation.md)                                         | Prezentacja w formie Markdown — slajdy + notatki prelegenta.                    |
| [`dock/build_deck.py`](./dock/build_deck.py)                                             | Skrypt generujący deck PPTX.                                                    |
| [`dock/deck_content.py`](./dock/deck_content.py)                                         | Treść slajdów (wydzielona z builda).                                            |
| [`dock/deck_layout.py`](./dock/deck_layout.py)                                           | Layout/styl slajdów.                                                            |
| [`configs/`](./configs/)                                                                 | Przykładowe konfiguracje routingu używane w demo.                               |
| [`configs/models-config.json`](./configs/models-config.json)                             | Konfiguracja modeli/providerów dla LLM Routera.                                 |
| [`configs/agentic_routing_codex.json`](./configs/agentic_routing_codex.json)             | Konfiguracja pluginu `agentic_routing_codex`.                                   |
| [`configs/agentic_routing_claude_code.json`](./configs/agentic_routing_claude_code.json) | Konfiguracja pluginu `agentic_routing_claude_code`.                             |

---

## O czym jest tutorial

Tutorial pokazuje, jak zbudować praktyczną warstwę routingu dla lokalnych agentów kodujących:

1. **Uruchomić LLM Router** jako jeden punkt wejścia API.
2. **Skonfigurować modele i providery** (Ollama / llama.cpp / vLLM) w `models.json`.
3. **Włączyć pluginy routingu agentowego**:
    - `agentic_routing_codex` — wybór modelu dla faz pracy Codex CLI (plan/implement/test/debug/...),
    - `agentic_routing_claude_code` — centralne mapowanie tierów Claude Code na lokalne modele.
4. **Podpiąć klientów**: Codex CLI (`/v1/responses`) i Claude Code (`/v1/messages`).
5. **Obserwować decyzje routingu w logach** i diagnozować typowe problemy.

### Kluczowa idea

W tej architekturze są **dwie osobne decyzje**:

- **Plugin routingu** decyduje: *jaki model logiczny ma obsłużyć request?*
- **Strategia load balancingu** decyduje: *który provider/slot ma wolną pojemność?*

Dzięki temu klient (Codex/Claude Code) pozostaje prosty, a polityka routingu i wykorzystanie infrastruktury są
zarządzane centralnie.

---

## Jak nawigować po materiałach

### Chcę szybko obejrzeć prezentację

- Otwórz [`LLMRouter_DSS2026_tutorial.pdf`](./LLMRouter_DSS2026_tutorial.pdf) lub [
  `LLMRouter_DSS2026_tutorial.pptx`](./LLMRouter_DSS2026_tutorial.pptx).
- Wersja tekstowa z notatkami: [`dock/presentation.md`](./dock/presentation.md).

### Chcę odtworzyć konfigurację routingu

- Zacznij od [`configs/models-config.json`](./configs/models-config.json).
- Potem zobacz [`configs/agentic_routing_codex.json`](./configs/agentic_routing_codex.json) i [
  `configs/agentic_routing_claude_code.json`](./configs/agentic_routing_claude_code.json).
- Porównaj z dokumentacją pluginów (linki niżej).

### Chcę zobaczyć live-wizualizację decyzji routingu

- Użyj repo: [llm-router-log-viz](https://github.com/radlab-dev-group/llm-router-log-viz) — dashboard do oglądania
  `Codex routing: ...` na żywo.

---

## Szybki start — odtworzenie demo

> Poniżej minimalna ścieżka „labowa”. Dostosuj hosty, porty, nazwy modeli i klucze do swojego środowiska.

### 1. Przygotuj backend LLM

Uruchom lokalny backend (np. llama.cpp, Ollama lub vLLM) i sprawdź **bez routera**:

- zwykłą odpowiedź,
- streaming,
- tool calling (żądanie narzędzia → wynik narzędzia → odpowiedź).

### 2. Zainstaluj router i pluginy

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install 'radlab-llm-router[api,metrics]'
python -m pip install 'llm-router-plugins[memory]'
# opcjonalnie semantyka Codexa:
# python -m pip install 'llm-router-plugins[ml,memory]'
```

### 3. Skonfiguruj router

- Skopiuj/dostosuj [`configs/models-config.json`](./configs/models-config.json).
- Ustaw zmienne środowiskowe (przykład):

```bash
export LLM_ROUTER_MODELS_CONFIG="$PWD/configs/models-config.json"
export LLM_ROUTER_UTILS_PLUGINS_PIPELINE='agentic_routing_codex,agentic_routing_claude_code'
export LLM_ROUTER_BALANCE_STRATEGY='first_available_optim_nworkers'
```

- Wskaż pliki konfiguracyjne pluginów (ścieżki dostosuj do swojego wdrożenia):

```bash
export LLM_ROUTER_ROUTING_SEMANTIC_AGENTIC_CODEX_CONFIG="$PWD/configs/agentic_routing_codex.json"
export LLM_ROUTER_ROUTING_SEMANTIC_AGENTIC_CLAUDE_CODE_CONFIG="$PWD/configs/agentic_routing_claude_code.json"
```

### 4. Uruchom router

Uruchom router zgodnie z dokumentacją `llm-router` (np. skrypt `run-rest-api-gunicorn.sh` / CLI
`llm-router server start`).

### 5. Podłącz klientów

**Codex CLI (`~/.codex/config.toml`):**

```toml
model = "auto_codex"
model_provider = "llm_router"
model_context_window = 256000
model_max_output_tokens = 32768

[model_providers.llm_router]
name = "LLM Router"
base_url = "http://127.0.0.1:8081/v1"
wire_api = "responses"
env_key = "LLM_ROUTER_API_KEY"
```

**Claude Code:**

```bash
export ANTHROPIC_BASE_URL='http://127.0.0.1:8081'
export ANTHROPIC_AUTH_TOKEN="$LLM_ROUTER_API_KEY"
claude
```

### 6. Obserwuj routing

W logach routera szukaj:

- `Codex routing: mode=... source=... model=... similarity=... class=...`
- `Claude Code model swap: ... -> ... (mode=..., match_type=...)`

Do wizualizacji live użyj [llm-router-log-viz](https://github.com/radlab-dev-group/llm-router-log-viz).

---

## Konfiguracje w `configs/`

### `models-config.json`

Definiuje modele logiczne, providerów, `api_type`, `api_host`, `model_path`, `tool_calling`, `input_size`, `nworkers`,
`fallback_model` i aktywne modele. To główny plik, który mówi routerowi *jakie modele istnieją i gdzie są*.

### `agentic_routing_codex.json`

Polityka routingu Codexa: trigger `auto_codex`, klasy requestów (`main`, `aux_title`, `compaction`), tryby (`plan`,
`implement`, `review`, `debug`, `test`, `git_review`, ...), reguły/heurystyki, opcjonalna semantyka i pamięć faz.

### `agentic_routing_claude_code.json`

Mapowanie nazw/tierów Claude Code na lokalne modele logiczne. W domyślnej konfiguracji nie ma magicznego `auto_claude`;
plugin dopasowuje nazwy/rodziny modeli.

> **Uwaga:** Konfiguracje w tym katalogu są materiałem demonstracyjnym. Przed użyciem produkcyjnym dostosuj hosty, nazwy
> modeli, limity kontekstu, Redis, auth i sekrety.

---

## Mapa repozytoriów i narzędzi

### Rdzeń ekosystemu

| Repozytorium            | Rola                                                                                | Linki                                                                                                                                                                       |
|-------------------------|-------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **llm-router**          | Brama/gateway: REST API, routing do providerów, load balancing, auth, metryki, CLI. | [GitHub](https://github.com/radlab-dev-group/llm-router) • [PyPI](https://pypi.org/project/radlab-llm-router/) • [Strona produktu](https://radlab.dev/products/llm-router/) |
| **llm-router-plugins**  | Pluginy pipeline: maskery, guardraile, routing agentowy, knowledge.                 | [GitHub](https://github.com/radlab-dev-group/llm-router-plugins) • [PyPI](https://pypi.org/project/radlab-llm-router-plugins/)                                              |
| **llm-router-web**      | Gotowe UI (Config Manager, Anonymizer UI).                                          | [GitHub](https://github.com/radlab-dev-group/llm-router-web)                                                                                                                |
| **llm-router-services** | Usługi HTTP wspierające pluginy (guardraile, masker).                               | [GitHub](https://github.com/radlab-dev-group/llm-router-services)                                                                                                           |
| **llm-router-utils**    | Narzędzia CLI, deploy/config helpers.                                               | [GitHub](https://github.com/radlab-dev-group/llm-router-utils)                                                                                                              |

### Narzędzia demo / roadmapy

| Repozytorium           | Rola                                                                    | Linki                                                            |
|------------------------|-------------------------------------------------------------------------|------------------------------------------------------------------|
| **llm-router-log-viz** | Live dashboard do wizualizacji decyzji `Codex routing` z logów routera. | [GitHub](https://github.com/radlab-dev-group/llm-router-log-viz) |
| **ak-bench**           | Benchmark/evaluacja agentów, routerów, modeli i pluginów.               | [GitHub](https://github.com/radlab-dev-group/ak-bench)           |

### Materiały konferencyjne

| Zasób          | Opis                               | Link                                                                                  |
|----------------|------------------------------------|---------------------------------------------------------------------------------------|
| Ten katalog    | Prezentacja, PDF, configi, dock.   | [DSS_20261126](https://github.com/radlab-dev-group/varia/tree/main/conf/DSS_20261126) |
| Prezentacja MD | Wersja tekstowa slajdów + notatki. | [dock/presentation.md](./dock/presentation.md)                                        |
| DSS 2026       | Strona konferencji.                | [main.dssconf.pl](https://main.dssconf.pl/pl#agenda)                                  |

---

## Dokumentacja pluginów i kluczowe funkcje

### Routing agentowy

| Temat                        | Co warto przeczytać                                                                     | Link                                                                                                                                                             |
|------------------------------|-----------------------------------------------------------------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Codex routing — plugin       | Opis triggera `auto_codex`, klas requestów, kaskady decyzji, konfiguracji, pamięci faz. | [codex/README.md](https://github.com/radlab-dev-group/llm-router-plugins/blob/main/llm_router_plugins/utils/routing/agentic_routing/codex/README.md)             |
| Claude Code routing — plugin | Mapowanie nazw/tierów Claude Code na lokalne modele, normalizacja, wildcardy.           | [claude_code/README.md](https://github.com/radlab-dev-group/llm-router-plugins/blob/main/llm_router_plugins/utils/routing/agentic_routing/claude_code/README.md) |
| Agentic routing — overview   | Szerszy kontekst routingu agentowego w pluginach.                                       | [agentic_routing/](https://github.com/radlab-dev-group/llm-router-plugins/tree/main/llm_router_plugins/utils/routing/agentic_routing)                            |

### Konfiguracja i operacje LLM Routera

| Temat                       | Po co                                                 | Link                                                                                                                  |
|-----------------------------|-------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------|
| Schemat konfiguracji modeli | Pola `models-config.json`, provider/model, aktywacja. | [MODELS_CONFIG.md](https://github.com/radlab-dev-group/llm-router/blob/main/llm_router_api/docs/MODELS_CONFIG.md)     |
| Strategie load balancingu   | `balanced`, `first_available_optim_nworkers`, itp.    | [LB_STRATEGIES.md](https://github.com/radlab-dev-group/llm-router/blob/main/llm_router_api/docs/LB_STRATEGIES.md)     |
| Zmienne środowiskowe        | Pełna lista env vars routera.                         | [ENV_DEFINITIONS.md](https://github.com/radlab-dev-group/llm-router/blob/main/llm_router_api/docs/ENV_DEFINITIONS.md) |
| Autoryzacja                 | Klucze, magazyny, polityki dostępu.                   | [AUTHENTICATION.md](https://github.com/radlab-dev-group/llm-router/blob/main/llm_router_api/docs/AUTHENTICATION.md)   |
| Dokumentacja llm-router-api | Endpointy, zachowanie API, deployment.                | [llm_router_api](https://github.com/radlab-dev-group/llm-router/tree/main/llm_router_api)                             |

### Funkcje, które warto znać przy demo

- **`auto_codex`** — stały alias modelu dla Codexa; plugin podmienia go na model docelowy zgodnie z fazą/klasą requestu.
- **Kaskada decyzji Codexa** — jawny tryb → klasa requestu → Plan Mode → faza z tool calls → pamięć faz → heurystyki →
  semantyka → fallback.
- **Claude Code tier mapping** — normalizacja nazwy, literal, wildcard, rodzina; brak domyślnego `auto_claude`.
- **`nworkers`** — limit slotów providera w strategii `first_available_optim_nworkers`, nie liczba workerów Gunicorna.
- **Redis** — osobne role: load balancing, auth, pamięć faz Codexa (różne prefiksy/konfiguracje).
- **Fail-open pluginów routingu** — niepasujący payload nie powinien blokować całego requestu; błędy
  konfiguracji/rozwiązania modelu i tak trzeba diagnozować.

---

## Materiały źródłowe i lektura

- Wpis
  RadLab: [Lokalni agenci, wspólna infrastruktura — auto_codex i routing Claude Code](https://radlab.dev/2026-10-27/lokalni-agenci-auto-codex-auto-claude/)
- LLM Router — strona produktu: [radlab.dev/products/llm-router](https://radlab.dev/products/llm-router/)
- Dokumentacja/README
  repo: [llm-router](https://github.com/radlab-dev-group/llm-router), [llm-router-plugins](https://github.com/radlab-dev-group/llm-router-plugins)
- Pakiety
  PyPI: [radlab-llm-router](https://pypi.org/project/radlab-llm-router/), [radlab-llm-router-plugins](https://pypi.org/project/radlab-llm-router-plugins/)

---

## Co dalej / roadmapa

Kierunek pokazywany w tutorialu można podsumować jako:

1. **Route** — LLM Router wybiera model logiczny i provider/slot.
2. **Augment** — `agentic_knowledge` (w `llm-router-plugins`) dostarcza agentowi kontekst/procedury i może uczyć się z
   feedbacku.
3. **Measure** — `ak-bench` pozwala mierzalnie porównywać agentów, routery, modele i pluginy.

Repozytoria do śledzenia:

- [llm-router-log-viz](https://github.com/radlab-dev-group/llm-router-log-viz) — obserwowalność decyzji routingu.
- [ak-bench](https://github.com/radlab-dev-group/ak-bench) — powtarzalna ewaluacja.
- [llm-router-plugins](https://github.com/radlab-dev-group/llm-router-plugins) — routing, knowledge, guardraile,
  maskery.
