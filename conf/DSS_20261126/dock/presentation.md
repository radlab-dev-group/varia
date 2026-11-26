# LLMRouter w praktyce: lokalne LLM-y dla Codex i Claude Code

**Data Science Summit 2026 — warsztat online**  
**Prowadzący:** Paweł Kędzia  
**Data:** 26 listopada 2026

> Od uruchomienia routera i konfiguracji modeli po działających agentów AI korzystających z Ollama, llama.cpp i vLLM.

---

## Jak korzystać z tego dokumentu

To tekstowa wersja prezentacji `LLMRouter_DSS2026_tutorial.pptx` z katalogu `conf/DSS_20261126`. Każdy rozdział
odpowiada slajdowi. Pod treścią znajdują się **notatki prelegenta** oparte na notatkach ze slajdów oraz wskazówki do
prowadzenia demo.

Źródło treści: [`dock/deck_content.py`](./deck_content.py), [`dock/build_deck.py`](./build_deck.py), [
`dock/deck_layout.py`](./deck_layout.py).

---

## Slajd 1 — Tytuł

**LLMRouter w praktyce: lokalne LLM-y dla Codex i Claude Code**

*Od uruchomienia routera i konfiguracji modeli po działających agentów AI korzystających z Ollama, llama.cpp i vLLM.*

- Prowadzący: **Paweł Kędzia**
- Data Science Summit 2026 / warsztat online

**Notatki prelegenta:**

- Po warsztacie uczestnik ma model mentalny i praktyczną ścieżkę „router + lokalny model + agent”.
- Router to warstwa pośrodku: agent nie musi znać adresów serwerów modeli.

---

## Slajd 2 — Plan warsztatu

*Podczas warsztatu skonfigurujemy agenta tak, aby korzystał z lokalnych modeli przez jedno API.*

1. Po co router: zadania łatwe i trudne, jeden adres dla agenta
2. Uruchamiamy serwer modelu, konfigurujemy `models.json` i startujemy router
3. Łączymy Codex CLI i Claude Code z routerem
4. Czytamy logi: dlaczego router wybrał właśnie ten model?
5. Szukamy przyczyn typowych błędów
6. Co dalej: wiedza projektu (`agentic_knowledge`) i pomiar efektu (`ak-bench`)
7. Pytania i materiały do dalszej pracy

**Notatki prelegenta:**

- Najpierw sens architektury, potem konfiguracja, potem podpięcie agentów i debug.
- Część „co dalej” to teaser/roadmapa, nie osobne live demo.

---

## Slajd 3 — Jeden model do wszystkiego? Agent ma zadania łatwe i trudne

- Tytuł rozmowy szybki model nada w sekundę. Znalezienie przyczyny błędu wymaga modelu, który dobrze rozumuje.
- Przy planowaniu i diagnozowaniu błędów liczą się trafne wnioski i niezawodne wywołania narzędzi.
- Do testów, pracy z Gitem i streszczania historii często wystarczy szybszy, tańszy model.
- Jeśli wszystko trafi do jednej kolejki, proste zadania będą konkurować z trudnymi nawet wtedy, gdy inne GPU są wolne.
- Klient może zawsze wysyłać ten sam alias. To router dobiera model do konkretnego żądania.

**Notatki prelegenta:**

- Więcej o tym podejściu: „Lokalni agenci, wspólna infrastruktura” na radlab.dev.
- Kompresja kontekstu nie potrzebuje tego samego modelu co trudny debugging.

---

## Slajd 4 — LLMRouter: jeden adres, różne modele do różnych zadań

- Codex CLI i Claude Code wysyłają żądania do routera, który uruchamiasz u siebie. Nie muszą znać adresów serwerów
  modeli.
- Wtyczka wybiera model: tytuł rozmowy może nadać szybki model, a diagnozę błędu można powierzyć innemu.
- Router wybiera instancję: jeśli model działa na kilku serwerach, żądanie trafia tam, gdzie jest wolne miejsce.
- Inne wtyczki z `llm-router-plugins` maskują dane, pilnują reguł bezpieczeństwa i wyszukują wiedzę projektu.
- Jeden router obsłuży m.in. llama.cpp, Ollama, vLLM, LM Studio i serwery z API zgodnym z OpenAI.

**Notatki prelegenta:**

- Strona projektu i dokumentacja: https://llm-router.cloud
- Kod: https://github.com/radlab-dev-group/llm-router oraz https://github.com/radlab-dev-group/llm-router-plugins
- Zwróć uwagę na rozdział odpowiedzialności: klient ↔ router ↔ pluginy ↔ backendy.

---

## Slajd 5 — Jak żądanie trafia do lokalnego modelu?

*Agent zna adres routera. Wybór modelu i jego instancji odbywa się po stronie serwera.*

**Przepływ (architektura):**

1. **Klient**
   - Codex CLI → `/v1/responses`
   - Claude Code → `/v1/messages`
2. **LLMRouter**
   - Wtyczka routingu: dobiera model do zadania.
   - Strategia równoważenia: wybiera instancję z wolnym slotem.
3. **Silnik / backend**
   - Ollama — serwer lokalny
   - llama.cpp — serwer lokalny
   - vLLM — serwer lokalny
4. **Redis**
   - wspólny stan slotów

**Notatki prelegenta:**

- To najważniejszy slajd mentalny: klient widzi jeden adres, reszta decyzji dzieje się po stronie routera.
- „plugin wybiera model, strategia wybiera instancję”.

---

## Slajd 6 — Który model wykona zadanie i gdzie je uruchomić?

*Trafny wybór modelu nie skróci kolejki, jeśli każde żądanie trafi na ten sam serwer.*

| Wtyczka wybiera model                                                                                                   | Router wybiera instancję                                                                   |
|-------------------------------------------------------------------------------------------------------------------------|--------------------------------------------------------------------------------------------|
| Odczytuje tryb pracy, klasę żądania i sygnały o fazie zadania.                                                          | Ten sam model 27B działa na Lab2 i Lab5. Który serwer ma wolne miejsce?                    |
| W razie potrzeby stosuje heurystyki lub analizę semantyczną.                                                            | Każdy serwer obsługuje jednocześnie ograniczoną liczbę żądań. Router liczy zajęte miejsca. |
| Zastępuje `auto_codex` nazwą modelu, np. `qwen/Qwen3.8-Flash-Next` lub `qwen/Qwen3.8-27B`, i zapisuje metadane decyzji. | Dzięki Redisowi wszystkie procesy routera widzą tę samą liczbę zajętych miejsc.            |

**Notatki prelegenta:**

- Wybór modelu logicznego ≠ wybór wolnego providera/slotu.
- Przy wielu workerach Gunicorna bez Redisa każdy proces miałby własny obraz zajętości.

---

## Slajd 7 — Instalacja routera i wtyczek

*Użyj Pythona 3.10 lub nowszego. Zainstaluj router i wtyczki w tym samym środowisku.*

**Fragment pokazany na slajdzie:**

```bash
mkdir -p ~/llm-router-local && cd ~/llm-router-local
python3 -m venv .venv
source .venv/bin/activate

python -m pip install 'radlab-llm-router[api,metrics]'
python -m pip install 'llm-router-plugins[memory]'
mkdir -p local-config
```

**Pełny przykład (z notatek slajdu):**

```bash
mkdir -p ~/llm-router-local && cd ~/llm-router-local
python3 -m venv .venv
source .venv/bin/activate

# Router z API i metrykami
python -m pip install 'radlab-llm-router[api,metrics]'

# Wtyczki wyboru modelu z obsługą pamięci w Redisie
python -m pip install 'llm-router-plugins[memory]'

# Aby włączyć analizę semantyczną dla Codexa (wektory i FAISS):
# python -m pip install 'llm-router-plugins[ml,memory]'

mkdir -p local-config
```

**Notatki prelegenta:**

- Opcjonalnie doinstaluj `llm-router-plugins[ml,memory]`, aby włączyć analizę semantyczną.

---

## Slajd 8 — Najpierw sprawdź sam serwer modelu

*Wpisz ten sam alias w polu `model_path` w `models.json`. Przy `--parallel 1` ustaw zwykle `nworkers` na 1.*

```bash
# llama.cpp: podaj ścieżki do modelu i szablonu obsługującego narzędzia.
./llama-server \
  --model /path/to/model.gguf \
  --alias qwen/Qwen3.8-27B \
  --chat-template-file .../chat-template.jinja \
  --ctx-size 300000 \
  --parallel 1 \
  --n-gpu-layers 999 \
  --flash-attn on \
  --host 0.0.0.0 --port 7000
```

**Notatki prelegenta:**

- Bez routera sprawdź zwykłą odpowiedź, transmisję strumieniową i pełny cykl: wywołanie narzędzia, zwrot wyniku,
  odpowiedź modelu.
- Jeśli backend nie działa sam, router nie naprawi problemu z szablonem narzędzi czy kontekstem.

---

## Slajd 9 — Jak uruchomić model w Ollama lub vLLM?

*Wybierz jeden z dwóch wariantów. Zacznij od zainstalowanego silnika; dla vLLM użyj zgodnego GPU.*

```bash
# Ollama · terminal 1 (pomiń, jeśli usługa już działa)
ollama serve
# Terminal 2: pobierz model i sprawdź, czy jest na liście
ollama pull qwen2.5:1.5b
curl -fsS http://127.0.0.1:11434/api/tags

# vLLM · terminal 1
vllm serve Qwen/Qwen2.5-1.5B-Instruct --host 127.0.0.1 --port 8000
# Terminal 2: po załadowaniu modelu sprawdź jego identyfikator
curl -fsS http://127.0.0.1:8000/v1/models
```

**Notatki prelegenta:**

- W `models.json` ustaw `api_type` na `"ollama"` lub `"vllm"`, podaj `api_host` serwera, a jako `model_path` wpisz nazwę
  z odpowiedzi: pole `name` (Ollama) lub `id` (vLLM).
- To slajd praktyczny: celem jest pokazać, że router jest niezależny od konkretnego silnika.

---

## Slajd 10 — `models.json`: alias, modele i ich serwery

*Flash-Next działa na Lab3. Jego model zapasowy, 27B, ma dwie równorzędne instancje.*

**Fragment pokazany na slajdzie:**

```json
"qwen/Qwen3.8-27B": {
   "providers": [
      {
         "id": "lab2-qwen-27b",
         "api_type": "llama.cpp",
         "api_host": "http://lab2:7000",
         "model_path": "qwen/Qwen3.8-27B",
         "input_size": 256000,
         "tool_calling": true,
         "nworkers": 1
      },
      {
         "id": "lab5-qwen-27b",
         "api_host": "http://lab5:7000"
         …
      }
   ]
}
```

**Pełny przykład (z notatek slajdu):**

```json
{
   "semantic_routing": {
      "auto_codex": {
         "providers": [
            {
               "id": "routing-auto-codex",
               "api_type": "builtin",
               "api_host": null,
               "api_token": "",
               "model_path": ""
            }
         ]
      }
   },
   "qwen_models": {
      "qwen/Qwen3.8-Flash-Next": {
         "providers": [
            {
               "id": "lab3-flash-next",
               "api_type": "llama.cpp",
               "api_host": "http://lab3:7000",
               "model_path": "qwen/Qwen3.8-Flash-Next",
               "input_size": 256000,
               "tool_calling": true,
               "nworkers": 1
            }
         ],
         "fallback_model": "qwen/Qwen3.8-27B"
      },
      "qwen/Qwen3.8-27B": {
         "providers": [
            {
               "id": "lab2-qwen-27b",
               "api_type": "llama.cpp",
               "api_host": "http://lab2:7000",
               "model_path": "qwen/Qwen3.8-27B",
               "input_size": 256000,
               "tool_calling": true,
               "nworkers": 1
            },
            {
               "id": "lab5-qwen-27b",
               "api_type": "llama.cpp",
               "api_host": "http://lab5:7000",
               "model_path": "qwen/Qwen3.8-27B",
               "input_size": 256000,
               "tool_calling": true,
               "nworkers": 1
            }
         ]
      }
   },
   "active_models": {
      "semantic_routing": [
         "auto_codex"
      ],
      "qwen_models": [
         "qwen/Qwen3.8-Flash-Next",
         "qwen/Qwen3.8-27B"
      ]
   }
}
```

**Notatki prelegenta:**

- `input_size` to limit wejścia przyjęty przez router. Ustaw go poniżej najmniejszego `--ctx-size` wśród serwerów danego
  modelu.
- `model_path` musi odpowiadać nazwie/aliasowi widzianemu przez backend.

---

## Slajd 11 — Ten sam model na dwóch serwerach. Który dostanie żądanie?

- **balanced** — wybiera serwer, któremu dotąd przydzielono najmniej żądań, niezależnie od tego, ile z nich nadal trwa.
- **weighted** — dzieli ruch według stałych wag, np. 70% żądań na Lab5 i 30% na Lab2.
- **dynamic_weighted** — działa jak weighted, ale wagi można zmieniać w trakcie pracy routera.
- **first_available** — sprawdza serwery w kolejności z konfiguracji i zajmuje pierwszy wolny.
- **first_available_optim** — najpierw próbuje ponownie użyć ostatnio wybranego serwera. Jeśli jest zajęty, szuka
  innego.
- **first_available_optim_nworkers** — spośród sprawnych serwerów z wolnym miejscem wybiera ten, który ma najmniej
  zajętych miejsc.

**Notatki prelegenta:**

- Na warsztacie używamy `first_available_optim_nworkers`. Przy `nworkers = 1`, gdy Lab2 jeszcze generuje, a Lab5 już
  skończył, następne żądanie trafi na Lab5.
- To dobry moment, żeby odróżnić „liczbę żądań w historii” od „liczby aktualnie zajętych slotów”.

---

## Slajd 12 — Uruchomienie routera z obiema wtyczkami

*Rozdziel ustawienia zajętości, uwierzytelniania i pamięci faz. Wtyczka Codexa nie dziedziczy ustawień Redisa od
strategii wyboru serwera.*

**Fragment pokazany na slajdzie:**

```bash
export LLM_ROUTER_MODELS_CONFIG="$PWD/local-config/models.json"
export LLM_ROUTER_UTILS_PLUGINS_PIPELINE=\
'agentic_routing_codex,agentic_routing_claude_code'
export LLM_ROUTER_BALANCE_STRATEGY='first_available_optim_nworkers'

# Po ustawieniu parametrów serwera i Redisa (patrz notatki):
bash ./run-rest-api-gunicorn.sh
```

**Pełny przykład (z notatek slajdu):**

```bash
export LLM_ROUTER_MODELS_CONFIG="$PWD/local-config/models.json"
export LLM_ROUTER_UTILS_PLUGINS_PIPELINE='agentic_routing_codex,agentic_routing_claude_code'
export LLM_ROUTER_BALANCE_STRATEGY='first_available_optim_nworkers'

export LLM_ROUTER_SERVER_TYPE='gunicorn'
export LLM_ROUTER_SERVER_HOST='127.0.0.1'
export LLM_ROUTER_SERVER_PORT=8081
export LLM_ROUTER_SERVER_WORKERS_COUNT=4

# Redis dla routera; pamięć faz ma osobne ustawienia.
export LLM_ROUTER_REDIS_HOST='127.0.0.1'
export LLM_ROUTER_REDIS_PORT=6379
export LLM_ROUTER_REDIS_DB=0

export LLM_ROUTER_ROUTING_SEMANTIC_AGENTIC_CODEX_MEMORY_ENABLED=true
export LLM_ROUTER_ROUTING_SEMANTIC_AGENTIC_CODEX_REDIS_DB=1

bash ./run-rest-api-gunicorn.sh
```

**Notatki prelegenta:**

- W produkcji użyj TLS i odwrotnego proxy, dobierz limity czasu i trzymaj klucze poza repozytorium.
- Pamięć faz Codexa ma osobny prefiks konfiguracyjny Redis.

---

## Slajd 13 — Codex CLI: konfiguracja połączenia z routerem

*Wybierz `wire_api = "responses"`: wtyczka Codexa rozpoznaje pola żądań w formacie Responses.*

**Fragment pokazany na slajdzie:**

```toml
# ~/.codex/config.toml
model = "auto_codex"
model_provider = "llm_router"

[model_providers.llm_router]
name = "LLM Router"
base_url = "http://127.0.0.1:8081/v1"
wire_api = "responses"
env_key = "LLM_ROUTER_API_KEY"
```

**Pełny przykład (z notatek slajdu):**

```toml
# ~/.codex/config.toml
model = "auto_codex"
model_provider = "llm_router"
model_context_window = 256000
model_max_output_tokens = 32768

[model_providers.llm_router]
name = "LLM Router"
base_url = "http://127.0.0.1:8081/v1"
wire_api = "responses"
env_key = "LLM_ROUTER_API_KEY"

# Po zapisaniu pliku wykonaj w terminalu:
export LLM_ROUTER_API_KEY = "<klucz-routera>"
codex
```

**Notatki prelegenta:**

- W terminalu ustaw `LLM_ROUTER_API_KEY` na klucz routera, a następnie uruchom `codex`.
- `model_context_window` ustaw wg najmniejszego budżetu spośród modeli docelowych.

---

## Slajd 14 — Claude Code: adres routera i klucz dostępu

*Claude Code używa `/v1/messages`, a Codex CLI używa `/v1/responses`. Oba żądania obsługuje ten sam router.*

```bash
# W terminalu, z którego uruchamiasz Claude Code:
export ANTHROPIC_BASE_URL='http://127.0.0.1:8081'   # bez /anthropic
export ANTHROPIC_AUTH_TOKEN="$LLM_ROUTER_API_KEY"

claude

# Zachowaj odrębne nazwy z rodzin claude-sonnet, claude-opus i claude-haiku.
# Jeśli wszystkie będą identyczne, router nie odróżni rodzin.
# Sufiks [1m] nie zwiększa okna kontekstu lokalnego modelu.
```

**Notatki prelegenta:**

- Dla Claude Code wystarczy sprawdzić regułę przypisaną do nazwy. Nie trzeba rozpoznawać fazy pracy.
- Nie ustawiaj wszystkich tierów na tę samą nazwę, jeśli chcesz zachować sygnał routingu.

---

## Slajd 15 — Jak sprawdzić w logach, który model wybrał router?

*Po teście serwera modelu wyślij żądania do routera. Obserwuj jego logi w drugim terminalu, a potem powtórz próbę z
agentem.*

**Fragment pokazany na slajdzie:**

```text
# Codex: żądanie z jawnym trybem planowania
Codex routing: mode=plan source=explicit model=...

# Claude Code: żądanie z nazwą z rodziny Sonnet
Claude Code model swap: claude-sonnet-4-5 -> ...
```

**Pełny przykład (z notatek slajdu):**

```bash
# Codex: jawnie wybierz tryb planowania.
curl --fail-with-body http://127.0.0.1:8081/v1/responses \
  -H "Authorization: Bearer $LLM_ROUTER_API_KEY" \
  -H 'Content-Type: application/json' \
  -d '{"model":"auto_codex","agent_mode":"plan","input":"Zaplanuj endpoint /health.","stream":false}'

# Szukaj w logu:
# Codex routing: mode=plan source=explicit model=... similarity=1.000 class=main

# Claude Code: podaj nazwę z rodziny Sonnet.
curl --fail-with-body http://127.0.0.1:8081/v1/messages \
  -H "x-api-key: $LLM_ROUTER_API_KEY" \
  -H 'anthropic-version: 2023-06-01' -H 'Content-Type: application/json' \
  -d '{"model":"claude-sonnet-4-5","max_tokens":128,"messages":[{"role":"user","content":"Czym jest routing?"}]}'

# Szukaj w logu:
# Claude Code model swap: claude-sonnet-4-5 -> ... (mode=sonnet, matched=..., match_type=literal)
```

**Notatki prelegenta:**

- W regule deterministycznej `similarity=1.0` oznacza dopasowanie reguły, a nie ocenę pewności modelu.

---

## Slajd 16 — Codex wysyła jeden alias, router dobiera model do zadania

- Ustaw `model = "auto_codex"`. Wtyczka `agentic_routing_codex` zastąpi alias nazwą modelu przed wysłaniem żądania do
  serwera.
- Wtyczka rozpoznaje klasę żądania po strukturze danych, nie po temacie rozmowy.
- `compaction` (skrócenie historii) i `aux_title` (tytuł rozmowy) to żądania pomocnicze. Trafiają do 27B, nawet jeśli
  rozmowa dotyczy trudnego błędu.
- `main` to zwykła tura agenta. Tutaj o modelu decyduje tryb pracy.
- Przykład: `plan`, `implement`, `review` i `debug` obsługuje Flash-Next z pełnym rozumowaniem; `test` i `git_review` —
  27B z wyłączonym rozumowaniem.

**Notatki prelegenta:**

- Tryby i przypisane im modele zmienisz w konfiguracji JSON lub w zmiennych środowiskowych, bez zmian w kliencie. To
  przykład konfiguracji, nie ranking modeli.
- `auto_codex` jest nazwą-wyzwalaczem, nie „magicznym modelem”.

---

## Slajd 17 — Codex: w jakiej kolejności wtyczka sprawdza reguły?

1. **Tryb podany wprost**: `agent_mode`, `codex_mode` lub `metadata.agent_mode`.
2. **Żądanie pomocnicze**: najpierw `compaction`, potem `aux_title`.
3. **Tryb planowania** w znaczniku `<collaboration_mode>` klienta.
4. **Użyte narzędzie i jego wynik**, np. uruchomienie `pytest`, `git diff` lub zastosowanie poprawki. Sama lista
   narzędzi nie wystarcza.
5. **Faza zapisana w Redisie**, jeśli pamięć jest włączona, a wpis nadal wiarygodny.
6. **Heurystyki** dla `test`, `git_review`, `review` i `debug`.
7. **Opcjonalne dopasowanie semantyczne** (wektory i FAISS). Bez rozstrzygnięcia: tryb domyślny, zwykle `implement`.

**Notatki prelegenta:**

- Decyduje pierwsza pasująca reguła. `git status` jest neutralny, a dawny błąd nie określa fazy po nowym poleceniu.
  Heurystyki i dopasowanie semantyczne wymagają przekroczenia progu i przewagi nad kolejnym wynikiem.

---

## Slajd 18 — Claude Code: od nazwy rodziny do lokalnego modelu

- `agentic_routing_claude_code` rozpoznaje nazwy z rodzin `claude-sonnet-*`, `claude-opus-*` i `claude-haiku-*`.
  Domyślnie nie oczekuje aliasu `auto_claude`.
- Wtyczka normalizuje nazwę. Sprawdza kolejno: nazwę dosłowną, postać znormalizowaną, wzorzec z gwiazdką i rodzinę
  modelu.
- Klient nadal wybiera np. Sonnet albo Haiku. Przypisanie lokalnego modelu zmieniasz na serwerze, nie na każdym laptopie
  i w każdym zadaniu CI.
- Zmiana nazwy kieruje żądanie na inny serwer. Nie nadaje lokalnemu modelowi jakości ani możliwości oryginału.

**Notatki prelegenta:**

- To celowo prostsza wtyczka niż Codex: centralne mapowanie tierów, nie klasyfikator faz.
- Warto powiedzieć to uczciwie: to routing infrastruktury, nie emulacja modelu Anthropic/OpenAI.

---

## Slajd 19 — Od objawu do przyczyny: co sprawdzić najpierw?

*Gdy wtyczka nie rozpozna żądania, przepuszcza je bez podmiany. Nie gwarantuje to poprawnej odpowiedzi.*

- W logu nadal widać `auto_codex`? Sprawdź, czy wtyczka jest włączona, alias jest aktywny, a żądanie spełnia warunek
  podmiany.
- `model not found` po podmianie: sprawdź nazwę modelu docelowego i listę `active_models` w `models.json`.
- `401` lub `403`: sprawdź klucz routera oraz uprawnienia do modelu i ścieżki API, zanim zmienisz token serwera modelu.
- `404` dla Messages: użyj `/v1/messages` bez dodatkowego prefiksu.
- Codex nie pamięta fazy? Sprawdź ustawienia `LLM_ROUTER_ROUTING_SEMANTIC_AGENTIC_CODEX_REDIS_*`.
- Model odpowiada tekstem, ale agent nie działa? Sprawdź szablon rozmowy, format wywołań narzędzi, strumień SSE i limit
  kontekstu.
- Zmiana modelu nie przenosi pamięci podręcznej KV. Porównuj czas całego zadania, nie tylko czas generowania tokenu.

**Notatki prelegenta:**

- Debuguj warstwami: backend → router → klient/agent.
- `fail-open` wtyczki routingu to ochrona przepływu, nie obietnica dobrej odpowiedzi.

---

## Slajd 20 — Co dalej po wyborze modelu?

*Sekcja przejściowa (rozdział).*

**`agentic_knowledge` dostarcza wiedzę projektu, a `ak-bench` pozwala sprawdzić, czy ta wiedza pomaga.**

**Notatki prelegenta:**

- ZapowiedŹ: to krótki teaser, 2 narzędzia, jeden sensowny kierunek po warsztacie.

---

## Slajd 21 — `agentic_knowledge`: skąd agent ma znać procedury zespołu?

- Nawet dobrze dobrany model nie musi wiedzieć, jak w tym repozytorium naprawia się konkretny błąd.
- Wtyczka wyszukuje podczas pracy agenta potrzebną instrukcję, opis podobnej naprawy lub fragment dokumentacji.
- Punktem wyjścia może być historia Gita. Etykiety oraz informacja, czy zespół przyjął poprawkę, czy ją wycofał,
  pomagają dobierać kolejne podpowiedzi.
- Wiedzę projektu dołączasz przez ten sam mechanizm wtyczek. Reguły wyboru modelu nadal działają niezależnie.

**Notatki prelegenta:**

- Po warsztacie: dokumentacja `docs/knowledge` i historia zmian w `llm-router-plugins`.

---

## Slajd 22 — `ak-bench`: jak porównać dwie konfiguracje?

- Agentic Knowledge Benchmark uruchamia te same zadania i niezależnie sprawdza wyniki. Możesz wymieniać agenta, router,
  model lub wtyczkę.
- W deskryptorach opisujesz konfiguracje i eksperymenty. Wyniki trafiają do SQLite lub PostgreSQL; możesz je porównać w
  interfejsie użytkownika.
- Najpierw porównaj jeden stały model z doborem modelu przez router. Potem zostaw te same reguły i włącz
  `agentic_knowledge`.
- W osobnych próbach porównaj dwa modele albo środowisko zarządzane przez benchmark ze środowiskiem zewnętrznym.

**Notatki prelegenta:**

- Benchmark do samodzielnej próby po warsztacie: https://github.com/radlab-dev-group/ak-bench
- Bez pomiaru „wydaje się lepiej” nie wystarczy.

---

## Slajd 23 — Od czego zacząć we własnym projekcie?

*Zmieniaj jeden element naraz, żeby odróżnić wpływ modelu od wpływu dodatkowej wiedzy.*

- Zapisz w routerze dwie osobne reguły: kiedy wybrać dany model i której instancji przekazać żądanie. Router nie jest
  kolejnym modelem.
- Zacznij od reguł deterministycznych. Dodaj pamięć faz lub dopasowanie semantyczne, gdy wyniki pokażą, gdzie proste
  reguły zawodzą.
- Testuj od środka: najpierw serwer modelu, potem API routera, na końcu klienta z narzędziami.
- Przy zmianie modelu uwzględnij utratę pamięci KV i spójność kolejnych odpowiedzi. Mierz wynik i czas od początku do
  końca zadania.
- Jeśli brakuje wiedzy projektu, dołącz `agentic_knowledge` i porównaj wyniki z wcześniejszą konfiguracją w `ak-bench`.

**Notatki prelegenta:**

- To slajd „co zabrać do domu”. Jedna zmiana naraz, jeden pomiar naraz.
- Najlepszy pierwszy krok po warsztacie: router + curl + logi, dopiero potem pełny agent.

---

## Slajd 24 — Gdzie znaleźć kod i przykłady?

*Dziękuję za udział. Jakie macie pytania?*

- Strona projektu: https://llm-router.cloud/
- Router: https://github.com/radlab-dev-group/llm-router
- Wtyczki: https://github.com/radlab-dev-group/llm-router-plugins
- Artykuł „Lokalni agenci, wspólna infrastruktura”: https://radlab.dev/2026-10-27/lokalni-agenci-auto-codex-auto-claude/
- Porównywanie konfiguracji: https://github.com/radlab-dev-group/ak-bench
- Materiały z warsztatu: https://github.com/radlab-dev-group/varia/tree/main/conf/DSS_20261126

**Notatki prelegenta:**

- Warto mieć otwarty też katalog `conf/DSS_20261126` i repo `llm-router-log-viz` jako live demo / follow-up.
