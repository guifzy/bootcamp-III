# TaskAnalyzer — Contrato SDD v1.1 (Fase 2)
## Continuidade e decisões explícitas
A especificação original está em especificacao_fase1.pdf e no DOCX preservado.
Os dois cenários Dado–Quando–Então da Fase 1 são mantidos: métricas corretas
para dados válidos e erro específico para datas inconsistentes.
A instrução intermediária prevalece sobre a menção inicial a erro por divisão
por zero: listas vazias ou sem concluídas retornam médias e taxas 0.0.
Unidade escolhida: horas. Taxa de atraso: concluídas após prazo / concluídas * 100.
Tarefas pendentes entram nos totais, não nas médias nem no denominador da taxa.
Canceladas são ignoradas em todos os indicadores, antes de validar outros campos.
## Entradas
analyze_tasks(tasks: list[dict[str, object]]) -> dict[str, object].
Cada tarefa não cancelada: id_tarefa int positivo e único, data_criacao e prazo
como datetime com fuso UTC (offset zero), prioridade baixa/média/alta, status
concluído/pendente. data_inicio é opcional (datetime UTC quando presente).
Concluídas exigem data_conclusao datetime UTC. Duração = conclusão - início,
ou conclusão - criação quando início ausente. Esse fallback resolve o campo
opcional da Fase 1 sem perder o cálculo a partir do início quando fornecido.
Início não pode preceder criação. Conclusão não pode preceder criação nem início.
Pendentes não podem ter conclusão preenchida. Prazo anterior à criação é inválido.
Campos extras são ignorados; entrada não é modificada. Datas em string e datas
sem fuso são rejeitadas, sem conversões implícitas. Erros: TaskValidationError.
## Saídas
Dicionário com total_tarefas, total_concluidas, total_pendentes,
tempo_medio_conclusao_horas, taxa_atraso_percentual,
quantidade_tarefas (alias de total_tarefas), tempo_medio_conclusao
(alias em horas) e indicadores_por_prioridade. Cada grupo baixa/média/alta tem
as mesmas métricas escalares, inclusive quando vazio. Valores sem arredondar.
## Cenários de aceite
1. Dado conjunto válido de concluídas e pendentes, quando analyze_tasks executa,
então totais, duração média geral/por prioridade e atraso geral/por prioridade
correspondem ao cálculo manual, ignorando canceladas.
2. Dadas datas inconsistentes, quando executa, então TaskValidationError clara.
3. Dado vazio ou apenas pendentes, quando executa, então médias/taxas são 0.0.
## Rastreabilidade
Cenário 1: test_success. Cenário 2: test_invalid_dates e test_invalid_fields.
Bordas: test_empty_pending, test_priority_groups, test_fallback_and_deadline.
Refinamentos deste contrato são escolhas técnicas propostas pela IA,
explicitadas para revisão do estudante; não são aprovação humana já obtida.
