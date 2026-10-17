"""Métricas de tarefas em UTC conforme o contrato SDD v1.1."""
import logging
from datetime import datetime, timedelta
from statistics import mean

LOGGER = logging.getLogger(__name__)
PRIORIDADES = ("baixa", "média", "alta")


class TaskValidationError(ValueError):
    """Indica violação do contrato de entrada de tarefas."""


def _date(task: dict[str, object], field: str) -> datetime:
    """Obtém uma data UTC válida.

    Args:
        task: Tarefa a validar.
        field: Campo datetime obrigatório.

    Returns:
        Data UTC informada.

    Raises:
        TaskValidationError: Se o valor não for datetime UTC.
    """
    value = task.get(field)
    if not isinstance(value, datetime) or value.utcoffset() != timedelta(0):
        raise TaskValidationError(f"{field} deve ser datetime com fuso UTC.")
    return value


def _validate(task: dict[str, object], seen: set[int]) -> None:
    """Valida campos e sequência temporal.

    Args:
        task: Tarefa não cancelada.
        seen: Identificadores já encontrados.

    Raises:
        TaskValidationError: Quando um campo viola o contrato.
    """
    identifier = task.get("id_tarefa")
    if type(identifier) is not int or identifier <= 0 or identifier in seen:
        raise TaskValidationError("id_tarefa deve ser inteiro positivo e único.")
    seen.add(identifier)
    if task.get("prioridade") not in PRIORIDADES:
        raise TaskValidationError("prioridade deve ser baixa, média ou alta.")
    if task.get("status") not in ("concluído", "pendente"):
        raise TaskValidationError("status deve ser concluído, pendente ou cancelado.")
    created = _date(task, "data_criacao")
    if _date(task, "prazo") < created:
        raise TaskValidationError("prazo não pode preceder data_criacao.")
    start = _date(task, "data_inicio") if task.get("data_inicio") is not None else created
    if start < created:
        raise TaskValidationError("data_inicio não pode preceder data_criacao.")
    if task["status"] == "concluído":
        finished = _date(task, "data_conclusao")
        if finished < created or finished < start:
            raise TaskValidationError("data_conclusao não pode preceder criação ou início.")
    elif task.get("data_conclusao") is not None:
        raise TaskValidationError("Tarefa pendente não deve ter data_conclusao.")


def _metrics(tasks: list[dict[str, object]]) -> dict[str, object]:
    """Calcula métricas de um grupo validado.

    Args:
        tasks: Grupo de tarefas válidas e não canceladas.

    Returns:
        Totais, duração média em horas e percentual de atraso.
    """
    done = [task for task in tasks if task["status"] == "concluído"]
    durations = [(_date(t, "data_conclusao") -
                  (_date(t, "data_inicio") if t.get("data_inicio") is not None
                   else _date(t, "data_criacao"))).total_seconds() / 3600 for t in done]
    average = mean(durations) if durations else 0.0
    late = sum(_date(t, "data_conclusao") > _date(t, "prazo") for t in done)
    return {"total_tarefas": len(tasks), "total_concluidas": len(done),
            "total_pendentes": len(tasks) - len(done),
            "tempo_medio_conclusao_horas": float(average),
            "taxa_atraso_percentual": late / len(done) * 100 if done else 0.0,
            "quantidade_tarefas": len(tasks), "tempo_medio_conclusao": float(average)}


def analyze_tasks(tasks: list[dict[str, object]]) -> dict[str, object]:
    """Analisa tarefas sem modificar ou persistir a entrada.

    Args:
        tasks: Lista de dicionários conforme specs/task_analyzer_spec.md.

    Returns:
        Métricas gerais e indicadores das três prioridades.

    Raises:
        TaskValidationError: Se a entrada ou uma tarefa for inválida.
    """
    if not isinstance(tasks, list):
        raise TaskValidationError("A entrada deve ser uma lista de tarefas.")
    valid: list[dict[str, object]] = []
    seen: set[int] = set()
    for task in tasks:
        if not isinstance(task, dict):
            raise TaskValidationError("Cada tarefa deve ser um dicionário.")
        if task.get("status") == "cancelado":
            continue
        _validate(task, seen)
        valid.append(task)
    result = _metrics(valid)
    result["indicadores_por_prioridade"] = {
        priority: _metrics([t for t in valid if t["prioridade"] == priority])
        for priority in PRIORIDADES}
    LOGGER.info("tasks_analyzed", extra={"total_tarefas": len(valid),
                                         "total_ignoradas": len(tasks) - len(valid)})
    return result
