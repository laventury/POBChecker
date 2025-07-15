# -*- coding: utf-8 -*-
# Arquivo: models/consolidator_models.py - Modelos de Dados para o Consolidador

from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional, Dict, Any
import json

@dataclass
class ConsolidatedEvent:
    """Modelo para evento consolidado"""
    consolidated_id: int
    start_time: datetime
    end_time: Optional[datetime]
    participating_terminals: List[str]
    original_events: List[Dict]
    total_expected: int
    total_present: int
    completion_percentage: float
    is_active: bool
    created_at: datetime
    
    def get_terminal_stats(self) -> Dict[str, Dict]:
        """Retorna estatísticas por terminal"""
        stats = {}
        for terminal_id in self.participating_terminals:
            terminal_data = self.get_terminal_data(terminal_id)
            stats[terminal_id] = {
                'expected': terminal_data.get('expected', 0),
                'present': terminal_data.get('present', 0),
                'percentage': terminal_data.get('percentage', 0.0),
                'first_check': terminal_data.get('first_check'),
                'last_check': terminal_data.get('last_check')
            }
        return stats
    
    def get_terminal_data(self, terminal_id: str) -> Dict:
        """Retorna dados específicos de um terminal"""
        for event in self.original_events:
            if event.get('terminal_id') == terminal_id:
                return event
        return {}

@dataclass
class TerminalStatus:
    """Modelo para status de terminal"""
    terminal_id: str
    location: str
    status: str  # 'online', 'offline', 'error'
    last_sync: Optional[datetime]
    pob_count: int
    current_mode: str  # 'CEV', 'CIO'
    active_event_id: Optional[int]
    time_sync_status: str  # 'NTP', 'LOCAL'
    sync_stats: Dict[str, Any]
    
    def is_online(self) -> bool:
        """Verifica se terminal está online"""
        return self.status == 'online'
    
    def sync_age_minutes(self) -> Optional[int]:
        """Retorna idade da última sincronização em minutos"""
        if self.last_sync:
            return int((datetime.now() - self.last_sync).total_seconds() / 60)
        return None

@dataclass
class SyncRecord:
    """Modelo para registro de sincronização"""
    id: int
    terminal_id: str
    original_id: int
    record_type: str  # 'check_event', 'check_in_out'
    cpf: str
    name: str
    timestamp: datetime
    sync_timestamp: datetime
    data: Dict[str, Any]  # Dados específicos do tipo de registro
    
    def to_dict(self) -> Dict:
        """Converte para dicionário"""
        return {
            'id': self.id,
            'terminal_id': self.terminal_id,
            'original_id': self.original_id,
            'record_type': self.record_type,
            'cpf': self.cpf,
            'name': self.name,
            'timestamp': self.timestamp.isoformat(),
            'sync_timestamp': self.sync_timestamp.isoformat(),
            'data': self.data
        }

@dataclass
class DashboardSummary:
    """Modelo para resumo do dashboard"""
    pob_total: int
    events_active: int
    terminals_online: int
    terminals_offline: int
    last_update: datetime
    
    def to_dict(self) -> Dict:
        """Converte para dicionário"""
        return {
            'pob_total': self.pob_total,
            'events_active': self.events_active,
            'terminals_online': self.terminals_online,
            'terminals_offline': self.terminals_offline,
            'last_update': self.last_update.strftime('%d/%m/%Y %H:%M:%S')
        }

@dataclass
class ReportData:
    """Modelo para dados de relatório"""
    report_id: str
    title: str
    generated_at: datetime
    filters: Dict[str, Any]
    data: Dict[str, Any]
    format: str  # 'pdf', 'excel', 'json'
    
    def to_dict(self) -> Dict:
        """Converte para dicionário"""
        return {
            'report_id': self.report_id,
            'title': self.title,
            'generated_at': self.generated_at.isoformat(),
            'filters': self.filters,
            'data': self.data,
            'format': self.format
        }

class EventCorrelator:
    """Classe para correlacionar eventos de diferentes terminais"""
    
    def __init__(self, tolerance_minutes=30):
        self.tolerance_minutes = tolerance_minutes
    
    def correlate_events(self, terminal_events: List[Dict]) -> List[ConsolidatedEvent]:
        """
        Correlaciona eventos de terminais diferentes baseado em janela temporal
        """
        correlated_groups = []
        processed_events = set()
        
        for event in terminal_events:
            if event['id'] in processed_events:
                continue
                
            # Busca eventos relacionados na janela temporal
            related_events = self.find_related_events(
                event, 
                terminal_events, 
                processed_events
            )
            
            if related_events:
                consolidated = self.create_consolidated_event(related_events)
                correlated_groups.append(consolidated)
                processed_events.update(e['id'] for e in related_events)
        
        return correlated_groups
    
    def find_related_events(self, base_event: Dict, all_events: List[Dict], processed: set) -> List[Dict]:
        """
        Encontra eventos relacionados dentro da tolerância temporal
        """
        from datetime import timedelta
        
        tolerance_delta = timedelta(minutes=self.tolerance_minutes)
        related = [base_event]
        
        base_start = datetime.fromisoformat(base_event['start_time'])
        
        for event in all_events:
            if (event['id'] not in processed and 
                event['terminal_id'] != base_event['terminal_id']):
                
                event_start = datetime.fromisoformat(event['start_time'])
                if abs(event_start - base_start) <= tolerance_delta:
                    related.append(event)
        
        return related
    
    def create_consolidated_event(self, events: List[Dict]) -> ConsolidatedEvent:
        """Cria evento consolidado a partir de eventos relacionados"""
        if not events:
            raise ValueError("Lista de eventos não pode estar vazia")
        
        # Encontra o evento mais antigo como base
        base_event = min(events, key=lambda e: e['start_time'])
        
        # Calcula estatísticas
        total_expected = sum(e.get('expected_count', 0) for e in events)
        total_present = sum(e.get('present_count', 0) for e in events)
        completion_percentage = (total_present / total_expected * 100) if total_expected > 0 else 0
        
        # Determina se ainda está ativo
        is_active = any(e.get('is_active', False) for e in events)
        
        # Determina tempo de fim
        end_time = None
        if not is_active:
            end_times = [datetime.fromisoformat(e['end_time']) for e in events if e.get('end_time')]
            if end_times:
                end_time = max(end_times)
        
        return ConsolidatedEvent(
            consolidated_id=base_event['id'],
            start_time=datetime.fromisoformat(base_event['start_time']),
            end_time=end_time,
            participating_terminals=[e['terminal_id'] for e in events],
            original_events=events,
            total_expected=total_expected,
            total_present=total_present,
            completion_percentage=completion_percentage,
            is_active=is_active,
            created_at=datetime.now()
        )
