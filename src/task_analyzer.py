"""
Módulo TaskAnalyzer - Engine de Análise de Métricas de Tarefas.
Gerado via assistente de IA sob o contrato SDD e diretrizes do CONTEXT_RULES.md.
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional
import logging

# Configuração de logging estruturado
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class TaskPriority(str, Enum):
    BAIXA = "BAIXA"
    MEDIA = "MEDIA"
    ALTA = "ALTA"


class TaskStatus(str, Enum):
    PENDENTE = "PENDENTE"
    EM_ANDAMENTO = "EM_ANDAMENTO"
    CONCLUIDA = "CONCLUIDA"
    CANCELADA = "CANCELADA"


class TaskValidationError(Exception):
    """Exceção customizada lançada quando há inconsistência nos dados de uma tarefa."""
    pass


@dataclass
class TaskItem:
    id: str
    titulo: str
    prioridade: TaskPriority
    status: TaskStatus
    data_criacao: datetime
    data_prazo: datetime
    data_conclusao: Optional[datetime] = None


def analyze_tasks(tasks: List[TaskItem]) -> Dict[str, object]:
    """
    Analisa um lote de tarefas e calcula métricas de produtividade e atraso.

    Args:
        tasks: Lista de objetos TaskItem a serem analisados.

    Returns:
        Dicionário contendo as métricas consolidadas.

    Raises:
        TaskValidationError: Se alguma tarefa apresentar inconsistência temporal.
    """
    logger.info("Iniciando análise de %d tarefas.", len(tasks))

    total_tarefas = len(tasks)
    if total_tarefas == 0:
        logger.warning("Lote vazio recebido. Retornando métricas zeradas.")
        return _build_empty_report(0)

    # Contadores e acumuladores
    total_concluidas = 0
    total_pendentes = 0
    
    concluidas_por_prioridade: Dict[str, int] = {"BAIXA": 0, "MEDIA": 0, "ALTA": 0}
    atrasos_por_prioridade: Dict[str, int] = {"BAIXA": 0, "MEDIA": 0, "ALTA": 0}
    tempo_total_horas_geral: float = 0.0
    tempo_total_horas_por_prioridade: Dict[str, float] = {"BAIXA": 0.0, "MEDIA": 0.0, "ALTA": 0.0}
    atrasos_total_geral: int = 0

    for task in tasks:
        # Validação temporal rígida
        if task.data_prazo < task.data_criacao:
            raise TaskValidationError(f"Tarefa {task.id}: data_prazo é anterior à data_criacao.")

        if task.status == TaskStatus.CONCLUIDA:
            if not task.data_conclusao:
                raise TaskValidationError(f"Tarefa {task.id}: status CONCLUIDA exige data_conclusao.")
            
            if task.data_conclusao < task.data_criacao:
                raise TaskValidationError(f"Tarefa {task.id}: data_conclusao é anterior à data_criacao.")

            total_concluidas += 1
            prio = task.prioridade.value
            concluidas_por_prioridade[prio] += 1

            # Tempo de execução em horas
            duracao_horas = (task.data_conclusao - task.data_criacao).total_seconds() / 3600.0
            tempo_total_horas_geral += duracao_horas
            tempo_total_horas_por_prioridade[prio] += duracao_horas

            # Checagem de atraso
            if task.data_conclusao > task.data_prazo:
                atrasos_total_geral += 1
                atrasos_por_prioridade[prio] += 1

        elif task.status in (TaskStatus.PENDENTE, TaskStatus.EM_ANDAMENTO):
            total_pendentes += 1

    # Tratamento de caso de borda: Sem tarefas concluídas -> retorna 0.0 para médias
    if total_concluidas == 0:
        logger.warning("Nenhuma tarefa concluída no lote. Retornando médias zeradas (0.0).")
        return _build_empty_report(total_tarefas, total_pendentes=total_pendentes)

    # Cálculo das médias e taxas
    tempo_medio_geral = round(tempo_total_horas_geral / total_concluidas, 2)
    taxa_atraso_geral = round((atrasos_total_geral / total_concluidas) * 100.0, 2)

    tempo_medio_por_prio: Dict[str, float] = {}
    taxa_atraso_por_prio: Dict[str, float] = {}

    for prio_key in ["BAIXA", "MEDIA", "ALTA"]:
        qtd_prio = concluidas_por_prioridade[prio_key]
        if qtd_prio > 0:
            tempo_medio_por_prio[prio_key] = round(tempo_total_horas_por_prioridade[prio_key] / qtd_prio, 2)
            taxa_atraso_por_prio[prio_key] = round((atrasos_por_prioridade[prio_key] / qtd_prio) * 100.0, 2)
        else:
            tempo_medio_por_prio[prio_key] = 0.0
            taxa_atraso_por_prio[prio_key] = 0.0

    logger.info("Análise concluída com sucesso.")
    return {
        "total_tarefas": total_tarefas,
        "total_concluidas": total_concluidas,
        "total_pendentes": total_pendentes,
        "tempo_medio_conclusao_horas": tempo_medio_geral,
        "tempo_medio_por_prioridade": tempo_medio_por_prio,
        "taxa_atraso_percentual": taxa_atraso_geral,
        "taxa_atraso_por_prioridade": taxa_atraso_por_prio,
    }


def _build_empty_report(total_tarefas: int, total_pendentes: int = 0) -> Dict[str, object]:
    """Gera relatório padrão zerado para casos de borda sem tarefas concluídas."""
    return {
        "total_tarefas": total_tarefas,
        "total_concluidas": 0,
        "total_pendentes": total_pendentes,
        "tempo_medio_conclusao_horas": 0.0,
        "tempo_medio_por_prioridade": {"BAIXA": 0.0, "MEDIA": 0.0, "ALTA": 0.0},
        "taxa_atraso_percentual": 0.0,
        "taxa_atraso_por_prioridade": {"BAIXA": 0.0, "MEDIA": 0.0, "ALTA": 0.0},
    }