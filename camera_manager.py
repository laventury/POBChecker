# -*- coding: utf-8 -*-
"""
camera_manager.py - Gerenciador de câmera para detecção de QR codes
"""

import cv2
import threading
import time
from PIL import Image
import customtkinter as ctk


class CameraManager:
    """Gerenciador de câmera com detecção de QR codes e display de vídeo."""
    
    def __init__(self, video_canvas, on_qr_detected=None):
        """
        Inicializa o gerenciador de câmera.
        
        Args:
            video_canvas: Widget CTkLabel onde o vídeo será exibido
            on_qr_detected: Callback chamado quando QR code é detectado (função que recebe o conteúdo do QR)
        """
        self.video_canvas = video_canvas
        self.on_qr_detected = on_qr_detected
        
        # Configurações da câmera
        self.cap = None
        self.camera_active = False
        self.camera_thread = None
        
        # Detector de QR Code
        self.qr_detector = cv2.QRCodeDetector()
        
        # Controle de detecção de QR (evita múltiplas detecções)
        self.last_scanned_qr = None
        self.last_scan_time = 0
        self.scan_cooldown = 3  # segundos
        
        # Estatísticas
        self.frame_count = 0
        self.fps_target = 30
        
    def init_camera(self):
        """Inicializa a câmera com tratamento robusto de erros."""
        print("CameraManager: Inicializando câmera...")
        
        try:
            # Libera qualquer câmera que possa estar em uso
            if self.cap is not None and self.cap.isOpened():
                self.cap.release()
                
            # Aguarda um pouco para garantir que a câmera seja liberada
            time.sleep(0.5)
                
            # Configurações de câmera para tentar (índice, backend)
            camera_configs = [
                (0, cv2.CAP_DSHOW),  # DirectShow no Windows
                (0, cv2.CAP_MSMF),   # Media Foundation no Windows  
                (0, cv2.CAP_ANY),    # Qualquer backend disponível
                (1, cv2.CAP_DSHOW),  # Segunda câmera com DirectShow
                (1, cv2.CAP_MSMF),   # Segunda câmera com Media Foundation
                (0, None),           # Sem backend específico
                (1, None),           # Segunda câmera sem backend específico
            ]
            
            for config in camera_configs:
                index, backend = config
                print(f"CameraManager: Tentando câmera {index} com backend {backend}...")
                
                try:
                    if backend is not None:
                        self.cap = cv2.VideoCapture(index, backend)
                    else:
                        self.cap = cv2.VideoCapture(index)
                    
                    if self.cap.isOpened():
                        # Configura propriedades otimizadas da câmera
                        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                        self.cap.set(cv2.CAP_PROP_FPS, self.fps_target)
                        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # Reduz latência
                        
                        # Testa se consegue ler um frame
                        ret, frame = self.cap.read()
                        if ret and frame is not None and frame.size > 0:
                            print(f"CameraManager: ✓ Câmera inicializada (índice {index}, backend {backend})")
                            print(f"CameraManager: Resolução: {frame.shape[1]}x{frame.shape[0]}")
                            return True
                        else:
                            print(f"CameraManager: Câmera {index} abre mas não lê frames válidos")
                            self.cap.release()
                    else:
                        print(f"CameraManager: Não foi possível abrir câmera {index}")
                        
                except Exception as e:
                    print(f"CameraManager: Erro ao tentar câmera {index}: {e}")
                    if self.cap:
                        self.cap.release()
                    
            # Se chegou aqui, nenhuma câmera funcionou
            print("CameraManager: ✗ Nenhuma câmera funcional encontrada")
            self.cap = None
            return False
            
        except Exception as e:
            print(f"CameraManager: Erro crítico ao inicializar câmera: {e}")
            import traceback
            traceback.print_exc()
            self.cap = None
            return False
    
    def start_camera(self):
        """Inicia a captura de vídeo da câmera."""
        if not self.init_camera():
            self._show_error_message("Câmera não encontrada ou não pôde ser inicializada.")
            return False
            
        self.camera_active = True
        self.camera_thread = threading.Thread(target=self._video_loop, daemon=True)
        self.camera_thread.start()
        print("CameraManager: Thread de vídeo iniciada")
        return True
    
    def stop_camera(self):
        """Para a captura de vídeo e libera recursos."""
        print("CameraManager: Parando câmera...")
        self.camera_active = False
        
        # Aguarda a thread finalizar
        if self.camera_thread and self.camera_thread.is_alive():
            self.camera_thread.join(timeout=2.0)
            
        # Libera a câmera
        if self.cap is not None:
            try:
                if self.cap.isOpened():
                    self.cap.release()
                    print("CameraManager: ✓ Câmera liberada")
            except Exception as e:
                print(f"CameraManager: Erro ao liberar câmera: {e}")
        
        self.cap = None
        print("CameraManager: Câmera parada")
    
    def _video_loop(self):
        """Loop principal de captura e processamento de vídeo."""
        print("CameraManager: Iniciando loop de vídeo...")
        
        if self.cap is None or not self.cap.isOpened():
            self._show_error_message("Erro: Câmera não está disponível.")
            return

        print("CameraManager: Loop de vídeo ativo")
        consecutive_errors = 0
        max_consecutive_errors = 10
        
        while self.camera_active:
            try:
                ret, frame = self.cap.read()
                
                if not ret or frame is None:
                    consecutive_errors += 1
                    if consecutive_errors >= max_consecutive_errors:
                        print(f"CameraManager: Muitos erros consecutivos ({consecutive_errors}), parando...")
                        break
                    time.sleep(0.1)
                    continue
                
                # Reset contador de erros se frame foi lido com sucesso
                consecutive_errors = 0
                self.frame_count += 1
                
                # Log de status a cada 30 frames (aproximadamente 1 segundo)
                if self.frame_count % 30 == 0:
                    print(f"CameraManager: Frame {self.frame_count} processado")

                # Detecta QR Code
                self._detect_qr_code(frame)
                
                # Atualiza display de vídeo
                self._update_video_display(frame)
                
                # Controle de FPS
                time.sleep(1.0 / self.fps_target)
                
            except Exception as e:
                print(f"CameraManager: Erro no loop de vídeo: {e}")
                consecutive_errors += 1
                if consecutive_errors >= max_consecutive_errors:
                    break
                time.sleep(0.1)
        
        print("CameraManager: Loop de vídeo finalizado")
    
    def _detect_qr_code(self, frame):
        """Detecta QR codes no frame."""
        try:
            qr_data, points, _ = self.qr_detector.detectAndDecode(frame)
            
            if qr_data:
                current_time = time.time()
                
                # Verifica se é um novo QR ou se passou o tempo de cooldown
                if (qr_data != self.last_scanned_qr or 
                    (current_time - self.last_scan_time) > self.scan_cooldown):
                    
                    self.last_scanned_qr = qr_data
                    self.last_scan_time = current_time
                    
                    print(f"CameraManager: QR Code detectado: {qr_data}")
                    
                    # Chama callback se definido
                    if self.on_qr_detected:
                        # Executa callback na thread principal
                        self.video_canvas.after(0, lambda: self.on_qr_detected(qr_data))
                        
        except Exception as e:
            print(f"CameraManager: Erro ao detectar QR Code: {e}")
    
    def _update_video_display(self, frame):
        """Atualiza o display de vídeo na interface."""
        try:
            # Converte frame para formato compatível com CustomTkinter
            img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img_pil = Image.fromarray(img_rgb)
            
            # Cria imagem CustomTkinter
            img_ctk = ctk.CTkImage(
                light_image=img_pil, 
                dark_image=img_pil, 
                size=(480, 360)
            )
            
            # Atualiza na thread principal
            self.video_canvas.after(0, lambda: self._set_canvas_image(img_ctk))
            
        except Exception as e:
            print(f"CameraManager: Erro ao atualizar display: {e}")
    
    def _set_canvas_image(self, img_ctk):
        """Define a imagem no canvas (executado na thread principal)."""
        try:
            self.video_canvas.configure(image=img_ctk)
            self.video_canvas.image = img_ctk  # Mantém referência
        except Exception as e:
            print(f"CameraManager: Erro ao definir imagem no canvas: {e}")
    
    def _show_error_message(self, message):
        """Mostra mensagem de erro no canvas."""
        print(f"CameraManager: {message}")
        self.video_canvas.after(0, lambda: self.video_canvas.configure(text=message))
    
    def is_active(self):
        """Retorna se a câmera está ativa."""
        return self.camera_active and self.cap is not None and self.cap.isOpened()
    
    def get_stats(self):
        """Retorna estatísticas da câmera."""
        return {
            'frame_count': self.frame_count,
            'is_active': self.is_active(),
            'camera_available': self.cap is not None and self.cap.isOpened()
        }


# Função utilitária para testar o gerenciador de câmera
def test_camera_manager():
    """Testa o gerenciador de câmera independentemente."""
    import customtkinter as ctk
    
    print("=== TESTE DO CAMERA MANAGER ===")
    
    # Cria janela de teste
    root = ctk.CTk()
    root.title("Teste Camera Manager")
    root.geometry("600x500")
    
    # Canvas para vídeo
    video_label = ctk.CTkLabel(root, text="Inicializando câmera...")
    video_label.pack(pady=20, padx=20, fill="both", expand=True)
    
    # Callback para QR codes detectados
    def on_qr_detected(qr_data):
        print(f"QR detectado no teste: {qr_data}")
        root.title(f"QR: {qr_data}")
    
    # Cria gerenciador de câmera
    camera_manager = CameraManager(video_label, on_qr_detected)
    
    def start_test():
        if camera_manager.start_camera():
            start_button.configure(text="Câmera Ativa", state="disabled")
            stop_button.configure(state="normal")
        else:
            video_label.configure(text="Falha ao inicializar câmera")
    
    def stop_test():
        camera_manager.stop_camera()
        start_button.configure(text="Iniciar Câmera", state="normal")
        stop_button.configure(state="disabled")
        video_label.configure(text="Câmera parada")
    
    # Botões de controle
    button_frame = ctk.CTkFrame(root)
    button_frame.pack(pady=10)
    
    start_button = ctk.CTkButton(button_frame, text="Iniciar Câmera", command=start_test)
    start_button.pack(side="left", padx=5)
    
    stop_button = ctk.CTkButton(button_frame, text="Parar Câmera", command=stop_test, state="disabled")
    stop_button.pack(side="left", padx=5)
    
    # Cleanup ao fechar
    def on_closing():
        camera_manager.stop_camera()
        root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    
    # Inicia teste automaticamente
    root.after(1000, start_test)
    
    root.mainloop()


if __name__ == "__main__":
    test_camera_manager()
