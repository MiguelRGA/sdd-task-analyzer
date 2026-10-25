"""
Suíte de Testes Automatizados (Test Harness) utilizando pytest.
Mapeia os Cenários 1, 2 e Casos de Borda da especificação SDD.
"""

from datetime import datetime, timedelta
import pytest

from src.task_analyzer import (
    TaskItem,
    TaskPriority,
    TaskStatus,
    TaskValidationError,
    analyze_tasks,
)


def test_cenario_1_sucesso_calculo_metricas():
    """Valida o cálculo correto das métricas com tarefas válidas (Cenário 1)."""
    base_time = datetime(2026, 5, 10, 8, 0, 0)

    tasks = [
        # Tarefa 1: Concluída em 10h, sem atraso
        TaskItem(
            id="1",
            titulo="Task 1",
            prioridade=TaskPriority.ALTA,
            status=TaskStatus.CONCLUIDA,
            data_criacao=base_time,
            data_prazo=base_time + timedelta(hours=24),
            data_conclusao=base_time + timedelta(hours=10),
        ),
        # Tarefa 2: Concluída em 20h, com atraso (prazo era 15h)
        TaskItem(
            id="2",
            titulo="Task 2",
            prioridade=TaskPriority.ALTA,
            status=TaskStatus.CONCLUIDA,
            data_criacao=base_time,
            data_prazo=base_time + timedelta(hours=15),
            data_conclusao=base_time + timedelta(hours=20),
        ),
        # Tarefa 3: Pendente
        TaskItem(
            id="3",
            titulo="Task 3",
            prioridade=TaskPriority.BAIXA,
            status=TaskStatus.PENDENTE,
            data_criacao=base_time,
            data_prazo=base_time + timedelta(hours=48),
        ),
    ]

    result = analyze_tasks(tasks)

    assert result["total_tarefas"] == 3
    assert result["total_concluidas"] == 2
    assert result["total_pendentes"] == 1
    assert result["tempo_medio_conclusao_horas"] == 15.0
    assert result["tempo_medio_por_prioridade"]["ALTA"] == 15.0
    assert result["taxa_atraso_percentual"] == 50.0
    assert result["taxa_atraso_por_prioridade"]["ALTA"] == 50.0


def test_cenario_2_excecao_data_inconsistente():
    """Valida o disparo de TaskValidationError quando data_conclusao < data_criacao (Cenário 2)."""
    base_time = datetime(2026, 5, 10, 8, 0, 0)

    invalid_tasks = [
        TaskItem(
            id="ERR-01",
            titulo="Task Invalida",
            prioridade=TaskPriority.MEDIA,
            status=TaskStatus.CONCLUIDA,
            data_criacao=base_time,
            data_prazo=base_time + timedelta(days=1),
            data_conclusao=base_time - timedelta(days=2),  # Inconsistência
        )
    ]

    with pytest.raises(TaskValidationError) as exc_info:
        analyze_tasks(invalid_tasks)

    assert "data_conclusao é anterior à data_criacao" in str(exc_info.value)


def test_caso_borda_lote_vazio():
    """Caso de borda: Lote sem tarefas deve retornar 0.0 para médias sem exceção não tratada."""
    result = analyze_tasks([])

    assert result["total_tarefas"] == 0
    assert result["total_concluidas"] == 0
    assert result["tempo_medio_conclusao_horas"] == 0.0
    assert result["taxa_atraso_percentual"] == 0.0


def test_caso_borda_apenas_tarefas_pendentes():
    """Caso de borda: Lote apenas com tarefas pendentes deve retornar 0.0 para médias."""
    base_time = datetime(2026, 5, 10, 8, 0, 0)

    pending_tasks = [
        TaskItem(
            id="P1",
            titulo="Pendente 1",
            prioridade=TaskPriority.BAIXA,
            status=TaskStatus.PENDENTE,
            data_criacao=base_time,
            data_prazo=base_time + timedelta(days=1),
        )
    ]

    result = analyze_tasks(pending_tasks)

    assert result["total_tarefas"] == 1
    assert result["total_concluidas"] == 0
    assert result["total_pendentes"] == 1
    assert result["tempo_medio_conclusao_horas"] == 0.0
    assert result["taxa_atraso_percentual"] == 0.0