def populate(title_slide, section_slide, content_slide, code_slide, two_col_slide, architecture_slide):
    title_slide(
        'LLMRouter w praktyce: lokalne LLM-y dla Codex i Claude Code',
        'Od uruchomienia routera i konfiguracji modeli po działających agentów AI korzystających z Ollama, llama.cpp i vLLM.',
        'Paweł Kędzia'
    )

    content_slide('Plan warsztatu', [
        'Po co router: zadania łatwe i trudne, jeden adres dla agenta',
        'Uruchamiamy serwer modelu, konfigurujemy models.json i startujemy router',
        'Łączymy Codex CLI i Claude Code z routerem',
        'Czytamy logi: dlaczego router wybrał właśnie ten model?',
        'Szukamy przyczyn typowych błędów',
        'Co dalej: wiedza projektu (agentic_knowledge) i pomiar efektu (ak-bench)',
        'Pytania i materiały do dalszej pracy',
    ], subtitle='Podczas warsztatu skonfigurujemy agenta tak, aby korzystał z lokalnych modeli przez jedno API.')

    content_slide('Jeden model do wszystkiego? Agent ma zadania łatwe i trudne', [
        'Tytuł rozmowy szybki model nada w sekundę. Znalezienie przyczyny błędu wymaga modelu, który dobrze rozumuje.',
        'Przy planowaniu i diagnozowaniu błędów liczą się trafne wnioski i niezawodne wywołania narzędzi.',
        'Do testów, pracy z Gitem i streszczania historii często wystarczy szybszy, tańszy model.',
        'Jeśli wszystko trafi do jednej kolejki, proste zadania będą konkurować z trudnymi nawet wtedy, gdy inne GPU są wolne.',
        'Klient może zawsze wysyłać ten sam alias. To router dobiera model do konkretnego żądania.',
    ], note='Więcej o tym podejściu: „Lokalni agenci, wspólna infrastruktura” na radlab.dev.')

    content_slide('LLMRouter: jeden adres, różne modele do różnych zadań', [
        'Codex CLI i Claude Code wysyłają żądania do routera, który uruchamiasz u siebie. Nie muszą znać adresów serwerów modeli.',
        'Wtyczka wybiera model: tytuł rozmowy może nadać szybki model, a diagnozę błędu można powierzyć innemu.',
        'Router wybiera instancję: jeśli model działa na kilku serwerach, żądanie trafia tam, gdzie jest wolne miejsce.',
        'Inne wtyczki z llm-router-plugins maskują dane, pilnują reguł bezpieczeństwa i wyszukują wiedzę projektu.',
        'Jeden router obsłuży m.in. llama.cpp, Ollama, vLLM, LM Studio i serwery z API zgodnym z OpenAI.',
    ], note='Strona projektu i dokumentacja: llm-router.cloud. Kod: github.com/radlab-dev-group/llm-router oraz llm-router-plugins.')

    architecture_slide()

    two_col_slide(
        'Który model wykona zadanie i gdzie je uruchomić?',
        'Wtyczka wybiera model', [
            'Odczytuje tryb pracy, klasę żądania i sygnały o fazie zadania.',
            'W razie potrzeby stosuje heurystyki lub analizę semantyczną.',
            'Zastępuje auto_codex nazwą modelu, np. qwen/Qwen3.8-Flash-Next lub qwen/Qwen3.8-27B, i zapisuje metadane decyzji.',
        ],
        'Router wybiera instancję', [
            'Ten sam model 27B działa na Lab2 i Lab5. Który serwer ma wolne miejsce?',
            'Każdy serwer obsługuje jednocześnie ograniczoną liczbę żądań. Router liczy zajęte miejsca.',
            'Dzięki Redisowi wszystkie procesy routera widzą tę samą liczbę zajętych miejsc.',
        ], subtitle='Trafny wybór modelu nie skróci kolejki, jeśli każde żądanie trafi na ten sam serwer.'
    )

    code_slide('Instalacja routera i wtyczek', '''mkdir -p ~/llm-router-local && cd ~/llm-router-local
python3 -m venv .venv
source .venv/bin/activate

# Router z API i metrykami
python -m pip install 'radlab-llm-router[api,metrics]'

# Wtyczki wyboru modelu z obsługą pamięci w Redisie
python -m pip install 'llm-router-plugins[memory]'

# Aby włączyć analizę semantyczną dla Codexa (wektory i FAISS):
# python -m pip install 'llm-router-plugins[ml,memory]'

mkdir -p local-config''',
        subtitle='Użyj Pythona 3.10 lub nowszego. Zainstaluj router i wtyczki w tym samym środowisku.',
        note='Opcjonalnie doinstaluj llm-router-plugins[ml,memory], aby włączyć analizę semantyczną.',
        excerpt='''mkdir -p ~/llm-router-local && cd ~/llm-router-local
python3 -m venv .venv
source .venv/bin/activate

python -m pip install 'radlab-llm-router[api,metrics]'
python -m pip install 'llm-router-plugins[memory]'
mkdir -p local-config''')

    code_slide('Najpierw sprawdź sam serwer modelu', r'''# llama.cpp: podaj ścieżki do modelu i szablonu obsługującego narzędzia.
./llama-server \
  --model /path/to/model.gguf \
  --alias qwen/Qwen3.8-27B \
  --chat-template-file .../chat-template.jinja \
  --ctx-size 300000 \
  --parallel 1 \
  --n-gpu-layers 999 \
  --flash-attn on \
  --host 0.0.0.0 --port 7000''',
        subtitle='Wpisz ten sam alias w polu model_path w models.json. Przy --parallel 1 ustaw zwykle nworkers na 1.',
        note='Bez routera sprawdź zwykłą odpowiedź, transmisję strumieniową i pełny cykl: wywołanie narzędzia, zwrot wyniku, odpowiedź modelu.')

    code_slide('Jak uruchomić model w Ollama lub vLLM?', '''# Ollama · terminal 1 (pomiń, jeśli usługa już działa)
ollama serve
# Terminal 2: pobierz model i sprawdź, czy jest na liście
ollama pull qwen2.5:1.5b
curl -fsS http://127.0.0.1:11434/api/tags

# vLLM · terminal 1
vllm serve Qwen/Qwen2.5-1.5B-Instruct --host 127.0.0.1 --port 8000
# Terminal 2: po załadowaniu modelu sprawdź jego identyfikator
curl -fsS http://127.0.0.1:8000/v1/models''',
        subtitle='Wybierz jeden z dwóch wariantów. Zacznij od zainstalowanego silnika; dla vLLM użyj zgodnego GPU.',
        note='W models.json ustaw api_type na "ollama" lub "vllm", podaj api_host serwera, a jako model_path wpisz nazwę z odpowiedzi: pole name (Ollama) lub id (vLLM).')

    code_slide('models.json: alias, modele i ich serwery', '''{
  "semantic_routing": {
    "auto_codex": {"providers": [{"id": "routing-auto-codex",
      "api_type": "builtin", "api_host": null, "api_token": "", "model_path": ""}]}
  },
  "qwen_models": {
    "qwen/Qwen3.8-Flash-Next": {"providers": [{"id": "lab3-flash-next",
      "api_type": "llama.cpp", "api_host": "http://lab3:7000", "model_path": "qwen/Qwen3.8-Flash-Next",
      "input_size": 256000, "tool_calling": true, "nworkers": 1}], "fallback_model": "qwen/Qwen3.8-27B"},
    "qwen/Qwen3.8-27B": {"providers": [
      {"id": "lab2-qwen-27b", "api_type": "llama.cpp", "api_host": "http://lab2:7000",
       "model_path": "qwen/Qwen3.8-27B", "input_size": 256000, "tool_calling": true, "nworkers": 1},
      {"id": "lab5-qwen-27b", "api_type": "llama.cpp", "api_host": "http://lab5:7000",
       "model_path": "qwen/Qwen3.8-27B", "input_size": 256000, "tool_calling": true, "nworkers": 1}]}
  },
  "active_models": {"semantic_routing": ["auto_codex"], "qwen_models": ["qwen/Qwen3.8-Flash-Next", "qwen/Qwen3.8-27B"]}
}''', subtitle='Flash-Next działa na Lab3. Jego model zapasowy, 27B, ma dwie równorzędne instancje.',
        note='input_size to limit wejścia przyjęty przez router. Ustaw go poniżej najmniejszego --ctx-size wśród serwerów danego modelu.',
        excerpt='''"qwen/Qwen3.8-27B": {
  "providers": [{
    "id": "lab2-qwen-27b", "api_type": "llama.cpp",
    "api_host": "http://lab2:7000", "model_path": "qwen/Qwen3.8-27B",
    "input_size": 256000, "tool_calling": true, "nworkers": 1
  }, {
    "id": "lab5-qwen-27b", "api_host": "http://lab5:7000", …
  }]
}''')

    content_slide('Ten sam model na dwóch serwerach. Który dostanie żądanie?', [
        'balanced — wybiera serwer, któremu dotąd przydzielono najmniej żądań, niezależnie od tego, ile z nich nadal trwa.',
        'weighted — dzieli ruch według stałych wag, np. 70% żądań na Lab5 i 30% na Lab2.',
        'dynamic_weighted — działa jak weighted, ale wagi można zmieniać w trakcie pracy routera.',
        'first_available — sprawdza serwery w kolejności z konfiguracji i zajmuje pierwszy wolny.',
        'first_available_optim — najpierw próbuje ponownie użyć ostatnio wybranego serwera. Jeśli jest zajęty, szuka innego.',
        'first_available_optim_nworkers — spośród sprawnych serwerów z wolnym miejscem wybiera ten, który ma najmniej zajętych miejsc.',
    ], note='Na warsztacie używamy first_available_optim_nworkers. Przy nworkers = 1, gdy Lab2 jeszcze generuje, a Lab5 już skończył, następne żądanie trafi na Lab5.')

    code_slide('Uruchomienie routera z obiema wtyczkami', '''export LLM_ROUTER_MODELS_CONFIG="$PWD/local-config/models.json"
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

bash ./run-rest-api-gunicorn.sh''',
        subtitle='Rozdziel ustawienia zajętości, uwierzytelniania i pamięci faz. Wtyczka Codexa nie dziedziczy ustawień Redisa od strategii wyboru serwera.',
        note='W produkcji użyj TLS i odwrotnego proxy, dobierz limity czasu i trzymaj klucze poza repozytorium.',
        excerpt=r'''export LLM_ROUTER_MODELS_CONFIG="$PWD/local-config/models.json"
export LLM_ROUTER_UTILS_PLUGINS_PIPELINE=\
'agentic_routing_codex,agentic_routing_claude_code'
export LLM_ROUTER_BALANCE_STRATEGY='first_available_optim_nworkers'

# Po ustawieniu parametrów serwera i Redisa (patrz notatki):
bash ./run-rest-api-gunicorn.sh''')

    code_slide('Codex CLI: konfiguracja połączenia z routerem', '''# ~/.codex/config.toml
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
export LLM_ROUTER_API_KEY="<klucz-routera>"
codex''', subtitle='Wybierz wire_api = "responses": wtyczka Codexa rozpoznaje pola żądań w formacie Responses.',
        note='W terminalu ustaw LLM_ROUTER_API_KEY na klucz routera, a następnie uruchom codex.',
        excerpt='''# ~/.codex/config.toml
model = "auto_codex"
model_provider = "llm_router"

[model_providers.llm_router]
name = "LLM Router"
base_url = "http://127.0.0.1:8081/v1"
wire_api = "responses"
env_key = "LLM_ROUTER_API_KEY"''')

    code_slide('Claude Code: adres routera i klucz dostępu', '''# W terminalu, z którego uruchamiasz Claude Code:
export ANTHROPIC_BASE_URL='http://127.0.0.1:8081'   # bez /anthropic
export ANTHROPIC_AUTH_TOKEN="$LLM_ROUTER_API_KEY"

claude

# Zachowaj odrębne nazwy z rodzin claude-sonnet, claude-opus i claude-haiku.
# Jeśli wszystkie będą identyczne, router nie odróżni rodzin.
# Sufiks [1m] nie zwiększa okna kontekstu lokalnego modelu.''',
        subtitle='Claude Code używa /v1/messages, a Codex CLI używa /v1/responses. Oba żądania obsługuje ten sam router.',
        note='Dla Claude Code wystarczy sprawdzić regułę przypisaną do nazwy. Nie trzeba rozpoznawać fazy pracy.')

    code_slide('Jak sprawdzić w logach, który model wybrał router?', r'''# Codex: jawnie wybierz tryb planowania.
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
# Claude Code model swap: claude-sonnet-4-5 -> ... (mode=sonnet, matched=..., match_type=literal)''',
        subtitle='Po teście serwera modelu wyślij żądania do routera. Obserwuj jego logi w drugim terminalu, a potem powtórz próbę z agentem.',
        note='W regule deterministycznej similarity=1.0 oznacza dopasowanie reguły, a nie ocenę pewności modelu.',
        excerpt='''# Codex: żądanie z jawnym trybem planowania
Codex routing: mode=plan source=explicit model=...

# Claude Code: żądanie z nazwą z rodziny Sonnet
Claude Code model swap: claude-sonnet-4-5 -> ...
''')

    content_slide('Codex wysyła jeden alias, router dobiera model do zadania', [
        'Ustaw model = "auto_codex". Wtyczka agentic_routing_codex zastąpi alias nazwą modelu przed wysłaniem żądania do serwera.',
        'Wtyczka rozpoznaje klasę żądania po strukturze danych, nie po temacie rozmowy.',
        'compaction (skrócenie historii) i aux_title (tytuł rozmowy) to żądania pomocnicze. Trafiają do 27B, nawet jeśli rozmowa dotyczy trudnego błędu.',
        'main to zwykła tura agenta. Tutaj o modelu decyduje tryb pracy.',
        'Przykład: plan, implement, review i debug obsługuje Flash-Next z pełnym rozumowaniem; test i git_review — 27B z wyłączonym rozumowaniem.',
    ], note='Tryby i przypisane im modele zmienisz w konfiguracji JSON lub w zmiennych środowiskowych, bez zmian w kliencie. To przykład konfiguracji, nie ranking modeli.')

    content_slide('Codex: w jakiej kolejności wtyczka sprawdza reguły?', [
        '1. Tryb podany wprost: agent_mode, codex_mode lub metadata.agent_mode.',
        '2. Żądanie pomocnicze: najpierw compaction, potem aux_title.',
        '3. Tryb planowania w znaczniku <collaboration_mode> klienta.',
        '4. Użyte narzędzie i jego wynik, np. uruchomienie pytest, git diff lub zastosowanie poprawki. Sama lista narzędzi nie wystarcza.',
        '5. Faza zapisana w Redisie, jeśli pamięć jest włączona, a wpis nadal wiarygodny.',
        '6. Heurystyki dla test, git_review, review i debug.',
        '7. Opcjonalne dopasowanie semantyczne (wektory i FAISS). Bez rozstrzygnięcia: tryb domyślny, zwykle implement.',
    ], note='Decyduje pierwsza pasująca reguła. git status jest neutralny, a dawny błąd nie określa fazy po nowym poleceniu. Heurystyki i dopasowanie semantyczne wymagają przekroczenia progu i przewagi nad kolejnym wynikiem.')

    content_slide('Claude Code: od nazwy rodziny do lokalnego modelu', [
        'agentic_routing_claude_code rozpoznaje nazwy z rodzin claude-sonnet-*, claude-opus-* i claude-haiku-*. Domyślnie nie oczekuje aliasu auto_claude.',
        'Wtyczka normalizuje nazwę. Sprawdza kolejno: nazwę dosłowną, postać znormalizowaną, wzorzec z gwiazdką i rodzinę modelu.',
        'Klient nadal wybiera np. Sonnet albo Haiku. Przypisanie lokalnego modelu zmieniasz na serwerze, nie na każdym laptopie i w każdym zadaniu CI.',
        'Zmiana nazwy kieruje żądanie na inny serwer. Nie nadaje lokalnemu modelowi jakości ani możliwości oryginału.',
    ])

    content_slide('Od objawu do przyczyny: co sprawdzić najpierw?', [
        'W logu nadal widać auto_codex? Sprawdź, czy wtyczka jest włączona, alias jest aktywny, a żądanie spełnia warunek podmiany.',
        'model not found po podmianie: sprawdź nazwę modelu docelowego i listę active_models w models.json.',
        '401 lub 403: sprawdź klucz routera oraz uprawnienia do modelu i ścieżki API, zanim zmienisz token serwera modelu.',
        '404 dla Messages: użyj /v1/messages bez dodatkowego prefiksu.',
        'Codex nie pamięta fazy? Sprawdź ustawienia LLM_ROUTER_ROUTING_SEMANTIC_AGENTIC_CODEX_REDIS_*.',
        'Model odpowiada tekstem, ale agent nie działa? Sprawdź szablon rozmowy, format wywołań narzędzi, strumień SSE i limit kontekstu.',
        'Zmiana modelu nie przenosi pamięci podręcznej KV. Porównuj czas całego zadania, nie tylko czas generowania tokenu.',
    ], subtitle='Gdy wtyczka nie rozpozna żądania, przepuszcza je bez podmiany. Nie gwarantuje to poprawnej odpowiedzi.')

    section_slide('Co dalej po wyborze modelu?', 'agentic_knowledge dostarcza wiedzę projektu, a ak-bench pozwala sprawdzić, czy ta wiedza pomaga.')

    content_slide('agentic_knowledge: skąd agent ma znać procedury zespołu?', [
        'Nawet dobrze dobrany model nie musi wiedzieć, jak w tym repozytorium naprawia się konkretny błąd.',
        'Wtyczka wyszukuje podczas pracy agenta potrzebną instrukcję, opis podobnej naprawy lub fragment dokumentacji.',
        'Punktem wyjścia może być historia Gita. Etykiety oraz informacja, czy zespół przyjął poprawkę, czy ją wycofał, pomagają dobierać kolejne podpowiedzi.',
        'Wiedzę projektu dołączasz przez ten sam mechanizm wtyczek. Reguły wyboru modelu nadal działają niezależnie.',
    ], note='Po warsztacie: dokumentacja docs/knowledge i historia zmian w llm-router-plugins.')

    content_slide('ak-bench: jak porównać dwie konfiguracje?', [
        'Agentic Knowledge Benchmark uruchamia te same zadania i niezależnie sprawdza wyniki. Możesz wymieniać agenta, router, model lub wtyczkę.',
        'W deskryptorach opisujesz konfiguracje i eksperymenty. Wyniki trafiają do SQLite lub PostgreSQL; możesz je porównać w interfejsie użytkownika.',
        'Najpierw porównaj jeden stały model z doborem modelu przez router. Potem zostaw te same reguły i włącz agentic_knowledge.',
        'W osobnych próbach porównaj dwa modele albo środowisko zarządzane przez benchmark ze środowiskiem zewnętrznym.',
    ], note='Benchmark do samodzielnej próby po warsztacie: github.com/radlab-dev-group/ak-bench.')

    content_slide('Od czego zacząć we własnym projekcie?', [
        'Zapisz w routerze dwie osobne reguły: kiedy wybrać dany model i której instancji przekazać żądanie. Router nie jest kolejnym modelem.',
        'Zacznij od reguł deterministycznych. Dodaj pamięć faz lub dopasowanie semantyczne, gdy wyniki pokażą, gdzie proste reguły zawodzą.',
        'Testuj od środka: najpierw serwer modelu, potem API routera, na końcu klienta z narzędziami.',
        'Przy zmianie modelu uwzględnij utratę pamięci KV i spójność kolejnych odpowiedzi. Mierz wynik i czas od początku do końca zadania.',
        'Jeśli brakuje wiedzy projektu, dołącz agentic_knowledge i porównaj wyniki z wcześniejszą konfiguracją w ak-bench.',
    ], subtitle='Zmieniaj jeden element naraz, żeby odróżnić wpływ modelu od wpływu dodatkowej wiedzy.')

    content_slide('Gdzie znaleźć kod i przykłady?', [
        'Strona projektu: https://llm-router.cloud/',
        'Router: https://github.com/radlab-dev-group/llm-router',
        'Wtyczki: https://github.com/radlab-dev-group/llm-router-plugins',
        'Artykuł „Lokalni agenci, wspólna infrastruktura”: https://radlab.dev/2026-10-27/lokalni-agenci-auto-codex-auto-claude/',
        'Porównywanie konfiguracji: https://github.com/radlab-dev-group/ak-bench',
        'Materiały z warsztatu: https://github.com/radlab-dev-group/varia/tree/main/conf/DSS_20261126',
    ], subtitle='Dziękuję za udział. Jakie macie pytania?')
