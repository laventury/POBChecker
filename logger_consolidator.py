#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Arquivo: logger_consolidator.py
Descrição: Sistema de logs para o consolidador
"""

import logging
import os
from datetime import datetime
from pathlib import Path

class ConsolidatorLogger:
    """Sistema de logs para o consolidador"""
    
    def __init__(self, log_dir="logs"):
        """Inicializa o sistema de logs"""
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        # Configura diferentes tipos de logs
        self.setup_loggers()
    
    def setup_loggers(self):
        """Configura os diferentes loggers"""
        # Logger geral do consolidador
        self.consolidator_logger = self._create_logger(
            'consolidator',
            self.log_dir / 'consolidator.log'
        )
        
        # Logger de sincronização
        self.sync_logger = self._create_logger(
            'sync',
            self.log_dir / 'sync.log'
        )
        
        # Logger de correlação
        self.correlation_logger = self._create_logger(
            'correlation',
            self.log_dir / 'correlation.log'
        )
    
    def _create_logger(self, name, log_file):
        """Cria um logger específico"""
        logger = logging.getLogger(name)
        logger.setLevel(logging.INFO)
        
        # Remove handlers existentes
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)
        
        # Handler para arquivo
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.INFO)
        
        # Formato do log
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        
        logger.addHandler(file_handler)
        return logger
    
    def log_consolidator(self, message, level='info'):
        """Log geral do consolidador"""
        if level == 'info':
            self.consolidator_logger.info(message)
        elif level == 'warning':
            self.consolidator_logger.warning(message)
        elif level == 'error':
            self.consolidator_logger.error(message)
    
    def log_sync(self, terminal_id, action, status, details=None):
        """Log de sincronização"""
        message = f"Terminal {terminal_id} - {action} - {status}"
        if details:
            message += f" - {details}"
        self.sync_logger.info(message)
    
    def log_correlation(self, event_id, correlation_type, status, details=None):
        """Log de correlação"""
        message = f"Event {event_id} - {correlation_type} - {status}"
        if details:
            message += f" - {details}"
        self.correlation_logger.info(message)
    
    def get_log_content(self, log_type):
        """Retorna o conteúdo de um log específico"""
        log_files = {
            'consolidator': self.log_dir / 'consolidator.log',
            'sync': self.log_dir / 'sync.log',
            'correlation': self.log_dir / 'correlation.log'
        }
        
        log_file = log_files.get(log_type)
        if log_file and log_file.exists():
            with open(log_file, 'r', encoding='utf-8') as f:
                return f.read()
        return None
    
    def get_recent_logs(self, log_type, lines=50):
        """Retorna as últimas linhas de um log"""
        content = self.get_log_content(log_type)
        if content:
            lines_list = content.split('\n')
            return '\n'.join(lines_list[-lines:])
        return None
    
    def clear_logs(self):
        """Limpa todos os logs"""
        for log_file in self.log_dir.glob('*.log'):
            log_file.unlink()
    
    def get_log_stats(self):
        """Retorna estatísticas dos logs"""
        stats = {}
        
        for log_type in ['consolidator', 'sync', 'correlation']:
            log_file = self.log_dir / f'{log_type}.log'
            if log_file.exists():
                with open(log_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    stats[log_type] = {
                        'exists': True,
                        'lines': len(lines),
                        'size': log_file.stat().st_size,
                        'last_modified': datetime.fromtimestamp(log_file.stat().st_mtime).strftime('%Y-%m-%d %H:%M:%S')
                    }
            else:
                stats[log_type] = {
                    'exists': False,
                    'lines': 0,
                    'size': 0,
                    'last_modified': None
                }
        
        return stats

# Instância global do logger
consolidator_logger = ConsolidatorLogger()

# Funções de conveniência
def log_consolidator(message, level='info'):
    """Log geral do consolidador"""
    consolidator_logger.log_consolidator(message, level)

def log_sync(terminal_id, action, status, details=None):
    """Log de sincronização"""
    consolidator_logger.log_sync(terminal_id, action, status, details)

def log_correlation(event_id, correlation_type, status, details=None):
    """Log de correlação"""
    consolidator_logger.log_correlation(event_id, correlation_type, status, details)

if __name__ == "__main__":
    # Teste do sistema de logs
    print("Testando sistema de logs...")
    
    # Cria alguns logs de teste
    log_consolidator("Consolidador iniciado", 'info')
    log_sync("Terminal-001", "sync_data", "success", "20 registros sincronizados")
    log_correlation("Event-001", "auto_correlation", "success", "3 eventos correlacionados")
    
    # Mostra estatísticas
    stats = consolidator_logger.get_log_stats()
    print("\nEstatísticas dos logs:")
    for log_type, stat in stats.items():
        if stat['exists']:
            print(f"  {log_type}: {stat['lines']} linhas, {stat['size']} bytes")
        else:
            print(f"  {log_type}: não existe")
    
    print("\nLogs criados com sucesso!")
