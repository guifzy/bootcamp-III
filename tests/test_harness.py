"""Test Harness rastreável aos cenários SDD e aos refinamentos da Fase 2."""
from copy import deepcopy
from datetime import datetime, timedelta, timezone
import importlib.util
from pathlib import Path
import pytest

SPEC = importlib.util.spec_from_file_location(
    "task_analyzer", Path(__file__).parents[1] / "src" / "task_analyzer.py")
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)
analyze_tasks = MODULE.analyze_tasks
TaskValidationError = MODULE.TaskValidationError
BASE = datetime(2026, 10, 17, tzinfo=timezone.utc)


def task(identifier: int = 1, priority: str = "alta", hours: int = 4,
         status: str = "concluído") -> dict[str, object]:
    """Produz fixture com duração conhecida e prazo de três horas."""
    return {"id_tarefa": identifier, "prioridade": priority, "status": status,
            "data_criacao": BASE, "data_inicio": BASE + timedelta(hours=1),
            "prazo": BASE + timedelta(hours=3),
            "data_conclusao": BASE + timedelta(hours=hours + 1)
            if status == "concluído" else None}


def test_success() -> None:
    """Cenário 1: confirma totais, médias e atrasos calculados à mão."""
    tasks = [task(), task(2, "baixa", 2), task(3, "média", status="pendente"),
             {"status": "cancelado"}]
    original = deepcopy(tasks)
    result = analyze_tasks(tasks)
    assert result["total_tarefas"] == 3
    assert result["total_concluidas"] == 2
    assert result["total_pendentes"] == 1
    assert result["tempo_medio_conclusao_horas"] == pytest.approx(3.0)
    assert result["taxa_atraso_percentual"] == pytest.approx(50.0)
    groups = result["indicadores_por_prioridade"]
    assert groups["alta"]["tempo_medio_conclusao_horas"] == 4.0
    assert groups["alta"]["taxa_atraso_percentual"] == 100.0
    assert groups["baixa"]["tempo_medio_conclusao_horas"] == 2.0
    assert groups["baixa"]["taxa_atraso_percentual"] == 0.0
    assert groups["média"]["total_pendentes"] == 1
    assert tasks == original


@pytest.mark.parametrize("field,value", [
    ("data_conclusao", BASE - timedelta(hours=1)),
    ("data_conclusao", BASE),
    ("data_inicio", BASE - timedelta(hours=1)),
    ("prazo", BASE - timedelta(hours=1)),
    ("data_conclusao", None),
    ("data_criacao", BASE.replace(tzinfo=None)),
    ("prazo", BASE.astimezone(timezone(timedelta(hours=-3)))),
    ("data_inicio", "17/10/2026"),
])
def test_invalid_dates(field: str, value: object) -> None:
    """Cenário 2: datas inconsistentes ou fora de UTC são rejeitadas."""
    item = task(); item[field] = value
    with pytest.raises(TaskValidationError):
        analyze_tasks([item])


@pytest.mark.parametrize("field,value", [
    ("id_tarefa", 0), ("id_tarefa", True), ("prioridade", "urgente"),
    ("status", "desconhecido"), ("prioridade", ["alta"]),
])
def test_invalid_fields(field: str, value: object) -> None:
    """Rejeita campos fora do contrato."""
    item = task(); item[field] = value
    with pytest.raises(TaskValidationError):
        analyze_tasks([item])


@pytest.mark.parametrize("items", [[], [task(status="pendente")],
                                    [{"status": "cancelado"}]])
def test_empty_pending(items: list[dict[str, object]]) -> None:
    """Bordas obrigatórias retornam 0.0 sem divisão por zero."""
    result = analyze_tasks(items)
    assert result["tempo_medio_conclusao_horas"] == 0.0
    assert result["taxa_atraso_percentual"] == 0.0
    assert result["total_concluidas"] == 0


def test_priority_groups() -> None:
    """Grupos vazios e aliases permanecem presentes e consistentes."""
    result = analyze_tasks([task()])
    assert result["quantidade_tarefas"] == result["total_tarefas"]
    assert result["tempo_medio_conclusao"] == 4.0
    for priority in ("baixa", "média"):
        assert result["indicadores_por_prioridade"][priority]["total_tarefas"] == 0
        assert result["indicadores_por_prioridade"][priority]["tempo_medio_conclusao_horas"] == 0.0


def test_fallback_and_deadline() -> None:
    """Sem início usa criação; igualdade ao prazo não é atraso."""
    item = task(hours=2); del item["data_inicio"]
    result = analyze_tasks([item])
    assert result["tempo_medio_conclusao_horas"] == 3.0
    assert result["taxa_atraso_percentual"] == 0.0


@pytest.mark.parametrize("items", [None, {}, [42], [task(), task()],
                                    [dict(task(status="pendente"), data_conclusao=BASE)]])
def test_invalid_container(items: object) -> None:
    """Containers, IDs repetidos e pendentes concluídas são inválidos."""
    with pytest.raises(TaskValidationError):
        analyze_tasks(items)
