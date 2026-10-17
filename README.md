# TaskAnalyzer — SDD & AI Harness
Guilherme Fernades Monteiro | RA 22403229. Fase 2 do Bootcamp III.
Status: suíte local executável; publicação GitHub e homologação humana pendentes.
Nenhum build remoto/CI é alegado nesta etapa.
## Preparar e testar
Python 3.11+; runtime apenas biblioteca padrão.
```sh
python3 -m venv .venv
. .venv/bin/activate
python3 -m pip install -r requirements.txt
python3 -m pytest tests/test_harness.py -v
```
## Uso
```python
from src.task_analyzer import analyze_tasks, TaskValidationError
print(analyze_tasks([]))  # totais 0, médias e taxas 0.0
```
## Estrutura e contrato
src/task_analyzer.py contém analyze_tasks e TaskValidationError.
specs/task_analyzer_spec.md define entradas, saídas e refinamentos da Fase 2.
CONTEXT_RULES.md contém a governança transposta da Fase 1.
tests/test_harness.py cobre sucesso, erro, vazios, pendentes e regras de datas.
A taxa de atraso considera apenas concluídas; canceladas são ignoradas.
Datas são datetime UTC; duração em horas a partir do início ou criação.
Sem persistência, rede ou dependências externas de runtime.
## Processo de IA
Ver ../REGISTRO_IA.md: contexto fornecido nesta sessão, decisões e revisão pendente.
Ver ../PUBLICACAO.md para branches, push e PR. O modelo de PR está em
../PULL_REQUEST.md e exige revisão real do estudante antes de merge.
