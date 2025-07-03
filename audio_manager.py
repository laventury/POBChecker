# Arquivo: audio_manager.py
# Gerenciador de áudio multiplataforma para POBChecker

import platform
import subprocess
import os

class AudioManager:
    """
    Classe para gerenciar reprodução de áudio em diferentes sistemas operacionais.
    Fornece uma interface unificada para reproduzir sons de alerta.
    """
    
    def __init__(self):
        """
        Inicializa o gerenciador de áudio e detecta o sistema operacional.
        """
        self.system = platform.system()
        self.audio_available = self._check_audio_availability()
        
    def _check_audio_availability(self):
        """
        Verifica se o sistema tem capacidades de áudio disponíveis.
        Retorna True se pelo menos um método de reprodução estiver disponível.
        """
        if self.system == "Windows":
            try:
                import winsound
                return True
            except ImportError:
                return False
                
        elif self.system == "Linux":
            # Verifica se paplay ou aplay estão disponíveis
            for cmd in ['paplay', 'aplay', 'beep']:
                try:
                    result = subprocess.run(['which', cmd], 
                                          capture_output=True, text=True)
                    if result.returncode == 0:
                        return True
                except:
                    continue
            return False
            
        elif self.system == "Darwin":  # macOS
            try:
                result = subprocess.run(['which', 'afplay'], 
                                      capture_output=True, text=True)
                return result.returncode == 0
            except:
                return False
                
        return False
    
    def play_beep(self, frequency=1000, duration=500):
        """
        Reproduz um som de beep com frequência e duração especificadas.
        
        Args:
            frequency (int): Frequência do som em Hz (padrão: 1000)
            duration (int): Duração do som em milissegundos (padrão: 500)
        
        Returns:
            bool: True se o som foi reproduzido com sucesso, False caso contrário
        """
        if not self.audio_available:
            print(f"BEEP! (Áudio não disponível no sistema {self.system})")
            return False
            
        try:
            if self.system == "Windows":
                return self._play_windows_beep(frequency, duration)
            elif self.system == "Linux":
                return self._play_linux_sound(frequency, duration)
            elif self.system == "Darwin":
                return self._play_macos_sound()
            else:
                print(f"BEEP! (Sistema {self.system} não suportado)")
                return False
                
        except Exception as e:
            print(f"BEEP! (Erro ao reproduzir som: {e})")
            return False
    
    def _play_windows_beep(self, frequency, duration):
        """
        Reproduz som usando winsound no Windows.
        """
        try:
            import winsound
            winsound.Beep(frequency, duration)
            return True
        except ImportError:
            print("BEEP! (winsound não disponível)")
            return False
        except Exception as e:
            print(f"BEEP! (Erro no Windows: {e})")
            return False
    
    def _play_linux_sound(self, frequency, duration):
        """
        Reproduz som no Linux usando diferentes métodos.
        Tenta paplay primeiro, depois aplay, e por último beep.
        """
        # Método 1: Tentar paplay com arquivo de som do sistema
        sound_files = [
            '/usr/share/sounds/alsa/Front_Left.wav',
            '/usr/share/sounds/sound-icons/bell.wav',
            '/usr/share/sounds/generic.wav',
            '/usr/share/sounds/KDE-Sys-Bell.ogg'
        ]
        
        for sound_file in sound_files:
            if os.path.exists(sound_file):
                try:
                    result = subprocess.run(['paplay', sound_file], 
                                          check=False, capture_output=True, timeout=2)
                    if result.returncode == 0:
                        return True
                except:
                    continue
        
        # Método 2: Tentar aplay
        for sound_file in sound_files:
            if os.path.exists(sound_file) and sound_file.endswith('.wav'):
                try:
                    result = subprocess.run(['aplay', sound_file], 
                                          check=False, capture_output=True, timeout=2)
                    if result.returncode == 0:
                        return True
                except:
                    continue
        
        # Método 3: Tentar comando beep
        try:
            duration_ms = duration // 1000 if duration > 1000 else 1
            result = subprocess.run(['beep', '-f', str(frequency), '-l', str(duration_ms)], 
                                  check=False, capture_output=True, timeout=2)
            if result.returncode == 0:
                return True
        except:
            pass
        
        # Método 4: Fallback usando printf (funciona na maioria dos terminais)
        try:
            subprocess.run(['printf', '\a'], check=False, capture_output=True)
            return True
        except:
            pass
            
        print("BEEP! (Nenhum método de áudio funcionou no Linux)")
        return False
    
    def _play_macos_sound(self):
        """
        Reproduz som no macOS usando afplay.
        """
        sound_files = [
            '/System/Library/Sounds/Glass.aiff',
            '/System/Library/Sounds/Ping.aiff',
            '/System/Library/Sounds/Pop.aiff',
            '/System/Library/Sounds/Tink.aiff'
        ]
        
        for sound_file in sound_files:
            if os.path.exists(sound_file):
                try:
                    result = subprocess.run(['afplay', sound_file], 
                                          check=False, capture_output=True, timeout=2)
                    if result.returncode == 0:
                        return True
                except:
                    continue
        
        print("BEEP! (Nenhum som do sistema encontrado no macOS)")
        return False
    
    def play_success_sound(self):
        """
        Reproduz um som de sucesso (frequência mais alta, duração curta).
        """
        return self.play_beep(frequency=1200, duration=300)
    
    def play_error_sound(self):
        """
        Reproduz um som de erro (frequência mais baixa, duração longa).
        """
        return self.play_beep(frequency=800, duration=800)
    
    def play_alert_sound(self):
        """
        Reproduz um som de alerta padrão.
        """
        return self.play_beep(frequency=1000, duration=500)
    
    def get_audio_info(self):
        """
        Retorna informações sobre o sistema de áudio.
        
        Returns:
            dict: Informações sobre o sistema de áudio
        """
        return {
            'system': self.system,
            'audio_available': self.audio_available,
            'methods_available': self._get_available_methods()
        }
    
    def _get_available_methods(self):
        """
        Retorna uma lista dos métodos de áudio disponíveis no sistema.
        """
        methods = []
        
        if self.system == "Windows":
            try:
                import winsound
                methods.append('winsound')
            except ImportError:
                pass
                
        elif self.system == "Linux":
            for cmd in ['paplay', 'aplay', 'beep']:
                try:
                    result = subprocess.run(['which', cmd], 
                                          capture_output=True, text=True)
                    if result.returncode == 0:
                        methods.append(cmd)
                except:
                    continue
                    
        elif self.system == "Darwin":
            try:
                result = subprocess.run(['which', 'afplay'], 
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    methods.append('afplay')
            except:
                pass
        
        return methods

# Instância global para facilitar o uso
audio_manager = AudioManager()

# Funções de conveniência para manter compatibilidade com código existente
def play_beep_sound():
    """
    Função de conveniência para reproduzir som de alerta.
    Mantém compatibilidade com o código existente.
    """
    return audio_manager.play_alert_sound()

def play_success_sound():
    """Reproduz som de sucesso."""
    return audio_manager.play_success_sound()

def play_error_sound():
    """Reproduz som de erro."""
    return audio_manager.play_error_sound()

# Teste da funcionalidade (só executa se o script for chamado diretamente)
if __name__ == "__main__":
    print("=== Teste do AudioManager ===")
    print(f"Sistema: {audio_manager.system}")
    print(f"Áudio disponível: {audio_manager.audio_available}")
    print(f"Métodos disponíveis: {audio_manager._get_available_methods()}")
    print()
    
    print("Testando som de alerta...")
    success = audio_manager.play_alert_sound()
    print(f"Sucesso: {success}")
    
    import time
    time.sleep(1)
    
    print("Testando som de sucesso...")
    success = audio_manager.play_success_sound()
    print(f"Sucesso: {success}")
    
    time.sleep(1)
    
    print("Testando som de erro...")
    success = audio_manager.play_error_sound()
    print(f"Sucesso: {success}")
