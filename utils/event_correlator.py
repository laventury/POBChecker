# -*- coding: utf-8 -*-
# Arquivo: utils/event_correlator.py - Correlacionador de Eventos

from datetime import datetime, timedelta
from typing import List, Dict, Optional, Set
import json

class EventCorrelator:
    """
    Classe para correlacionar eventos de diferentes terminais baseado em janela temporal.
    """
    
    def __init__(self, tolerance_minutes=30):
        self.tolerance_minutes = tolerance_minutes
        self.correlation_history = []
    
    def correlate_events(self, terminal_events: List[Dict]) -> List[Dict]:
        """
        Correlaciona eventos de terminais diferentes baseado em janela temporal.
        Considera apenas eventos com participantes com Status = 'ACTIVE'.
        
        Args:
            terminal_events: Lista de eventos de diferentes terminais
            
        Returns:
            Lista de eventos correlacionados
        """
        if not terminal_events:
            return []
        
        # Filtra apenas eventos com participantes ativos
        active_events = []
        for event in terminal_events:
            if self._has_active_participants(event):
                active_events.append(event)
        
        if not active_events:
            return []
        
        correlated_groups = []
        processed_events = set()
        
        # Ordena eventos por timestamp
        sorted_events = sorted(active_events, key=lambda e: e.get('start_time', ''))
        
        for event in sorted_events:
            if event.get('id') in processed_events:
                continue
                
            # Busca eventos relacionados na janela temporal
            related_events = self._find_related_events(
                event, 
                sorted_events, 
                processed_events
            )
            
            if related_events:
                consolidated = self._create_consolidated_event(related_events)
                correlated_groups.append(consolidated)
                processed_events.update(str(e.get('id', '')) for e in related_events)
        
        return correlated_groups
    
    def _has_active_participants(self, event: Dict) -> bool:
        """
        Verifica se o evento tem participantes com status ACTIVE
        """
        participants = event.get('participants', [])
        if not participants:
            return False
            
        # Conta apenas participantes com status ACTIVE
        active_count = 0
        for participant in participants:
            if participant.get('status', 'ACTIVE') == 'ACTIVE':
                active_count += 1
                
        return active_count > 0
    
    def _find_related_events(self, base_event: Dict, all_events: List[Dict], processed: Set) -> List[Dict]:
        """
        Encontra eventos relacionados dentro da tolerância temporal
        """
        tolerance_delta = timedelta(minutes=self.tolerance_minutes)
        related = [base_event]
        
        try:
            base_start = datetime.fromisoformat(base_event.get('start_time', ''))
        except (ValueError, TypeError):
            # Se não conseguir parsear o timestamp, retorna apenas o evento base
            return related
        
        base_terminal = base_event.get('terminal_id', '')
        
        for event in all_events:
            event_id = str(event.get('id', ''))
            event_terminal = event.get('terminal_id', '')
            
            if (event_id not in processed and 
                event_terminal != base_terminal and
                event_id != str(base_event.get('id', ''))):
                
                try:
                    event_start = datetime.fromisoformat(event.get('start_time', ''))
                    if abs(event_start - base_start) <= tolerance_delta:
                        related.append(event)
                except (ValueError, TypeError):
                    # Se não conseguir parsear o timestamp, pula este evento
                    continue
        
        return related
    
    def _create_consolidated_event(self, events: List[Dict]) -> Dict:
        """Cria evento consolidado a partir de eventos relacionados, considerando apenas participantes ACTIVE"""
        if not events:
            raise ValueError("Lista de eventos não pode estar vazia")
        
        # Encontra o evento mais antigo como base
        base_event = min(events, key=lambda e: e.get('start_time', ''))
        
        # Calcula estatísticas considerando apenas participantes ACTIVE
        total_expected = 0
        total_present = 0
        all_active_participants = []
        
        for event in events:
            participants = event.get('participants', [])
            event_expected = 0
            event_present = 0
            
            for participant in participants:
                if participant.get('status', 'ACTIVE') == 'ACTIVE':
                    event_expected += 1
                    event_present += 1
                    all_active_participants.append({
                        'cpf': participant.get('cpf'),
                        'name': participant.get('name'),
                        'terminal': event.get('terminal_id'),
                        'timestamp': participant.get('timestamp')
                    })
            
            total_expected += event_expected
            total_present += event_present
        
        completion_percentage = (total_present / total_expected * 100) if total_expected > 0 else 0
        
        # Determina se ainda está ativo (baseado no status dos eventos originais)
        is_active = any(e.get('is_active', False) for e in events)
        
        # Determina tempo de fim
        end_time = None
        if not is_active:
            end_times = []
            for e in events:
                if e.get('end_time'):
                    try:
                        end_times.append(datetime.fromisoformat(e['end_time']))
                    except (ValueError, TypeError):
                        continue
            if end_times:
                end_time = max(end_times).isoformat()
        
        # Cria evento consolidado
        consolidated = {
            'consolidated_id': base_event.get('id'),
            'start_time': base_event.get('start_time'),
            'end_time': end_time,
            'participating_terminals': [e.get('terminal_id') for e in events],
            'original_events': events,
            'total_expected': total_expected,
            'total_present': total_present,
            'active_participants': all_active_participants,
            'completion_percentage': round(completion_percentage, 2),
            'is_active': is_active,
            'created_at': datetime.now().isoformat(),
            'correlation_method': 'temporal_window',
            'tolerance_minutes': self.tolerance_minutes,
            'status_filter': 'ACTIVE_ONLY'
        }
        
        return consolidated
    
    def get_correlation_stats(self) -> Dict:
        """Retorna estatísticas de correlação"""
        if not self.correlation_history:
            return {
                'total_correlations': 0,
                'average_input_events': 0,
                'average_correlated_groups': 0,
                'current_tolerance_minutes': self.tolerance_minutes
            }
        
        return {
            'total_correlations': len(self.correlation_history),
            'average_input_events': sum(h['input_events'] for h in self.correlation_history) / len(self.correlation_history),
            'average_correlated_groups': sum(h['correlated_groups'] for h in self.correlation_history) / len(self.correlation_history),
            'current_tolerance_minutes': self.tolerance_minutes,
            'last_correlation': self.correlation_history[-1] if self.correlation_history else None
        }
    
    def update_tolerance(self, new_tolerance_minutes: int):
        """Atualiza tolerância temporal"""
        old_tolerance = self.tolerance_minutes
        self.tolerance_minutes = new_tolerance_minutes
        
        print(f"🔄 Tolerância de correlação atualizada: {old_tolerance} -> {new_tolerance_minutes} minutos")
    
    def clear_history(self):
        """Limpa histórico de correlação"""
        self.correlation_history.clear()
        print("🧹 Histórico de correlação limpo")


def test_event_correlator():
    """Função de teste para o correlacionador de eventos"""
    correlator = EventCorrelator(tolerance_minutes=30)
    
    # Eventos de teste
    test_events = [
        {
            'id': 1,
            'terminal_id': 'terminal-01',
            'start_time': '2025-07-14T10:00:00',
            'end_time': None,
            'expected_count': 50,
            'present_count': 45,
            'is_active': True
        },
        {
            'id': 2,
            'terminal_id': 'terminal-02',
            'start_time': '2025-07-14T10:15:00',
            'end_time': None,
            'expected_count': 30,
            'present_count': 28,
            'is_active': True
        },
        {
            'id': 3,
            'terminal_id': 'terminal-03',
            'start_time': '2025-07-14T11:00:00',
            'end_time': None,
            'expected_count': 20,
            'present_count': 18,
            'is_active': True
        }
    ]
    
    print("Testando correlacionador de eventos...")
    correlated = correlator.correlate_events(test_events)
    
    print(f"Eventos de entrada: {len(test_events)}")
    print(f"Grupos correlacionados: {len(correlated)}")
    
    for i, group in enumerate(correlated):
        print(f"\nGrupo {i+1}:")
        print(f"  Terminais: {group['participating_terminals']}")
        print(f"  Total esperado: {group['total_expected']}")
        print(f"  Total presente: {group['total_present']}")
        print(f"  Percentual: {group['completion_percentage']}%")
    
    stats = correlator.get_correlation_stats()
    print(f"\nEstatísticas: {json.dumps(stats, indent=2)}")


if __name__ == "__main__":
    test_event_correlator()
