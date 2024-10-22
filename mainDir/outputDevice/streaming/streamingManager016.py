import logging

from PyQt6.QtCore import QObject, pyqtSignal
from mainDir.outputDevice.worker.baseWorker015 import BaseWorker015
from mainDir.outputDevice.worker.baseWorker016 import BaseWorker016

logging.basicConfig(level=logging.INFO)


class StreamerManager016(QObject):
    streamWorker: BaseWorker016
    tally_SIGNAL = pyqtSignal(dict)

    def __init__(self, openGLViewer, parent=None):
        super().__init__(parent)
        self.openGLViewer = openGLViewer

    def startStreaming(self, request):
        """
        Avvia il processo di streaming con i parametri forniti nel dizionario 'request'.
        """
        ffmpeg_command = self.generateFFMpegCommand(request)
        print(f"FFmpeg command: {ffmpeg_command}")
        self.streamWorker = BaseWorker016(
            self.openGLViewer,
            ffmpeg_command,
            "Stream",
            fps=request.get('codec', {}).get('fps', 60),  # Assicurati di passare il frame rate corretto
            resolution=(1920, 1080)
        )
        self.streamWorker.tally_SIGNAL.connect(self.getTally)
        self.streamWorker.start()

    def stopStreaming(self):
        """
        Ferma il processo di streaming.
        """
        if hasattr(self, 'streamWorker') and self.streamWorker.isRunning():
            self.streamWorker.stop()
            self.streamWorker.wait()
            logging.info("Streaming worker stopped and thread joined.")

    def generateFFMpegCommandOld(self, request):
        """
        Genera il comando FFmpeg sulla base del dizionario di configurazione fornito.

        :param request: Dizionario che contiene la configurazione di demuxer, codec e streamInfo.
        :return: Stringa del comando FFmpeg.
        """
        # Estrai informazioni dal dizionario request
        demuxer = request.get('deMuxer', {})
        codec = request.get('codec', {})
        stream_info = request.get('streamInfo', {})

        # Stream URL e Stream Key
        stream_url = stream_info.get('url', '')
        stream_key = stream_info.get('key', '')

        # Codec settings
        codec_name = codec.get('codec', 'libx264')
        profile = codec.get('profile', 'baseline')
        pixel_format = codec.get('pixelFormat', 'yuv420p')
        preset = codec.get('preset', 'ultrafast')
        rate_control = codec.get('rateControl', 'CBR')
        bitrate = codec.get('bitrate', 5000)
        buffer_size = codec.get('bufferSize', 10000)
        tune = codec.get('tune', 'None')
        keyframe_interval = codec.get('keyframeInterval', 2)

        # Risoluzione dal widget OpenGLViewer
        width = 1920
        height = 1080

        # Comando FFmpeg per input rawvideo tramite stdin
        command = [
            "ffmpeg", "-y",  # Sovrascrivi i file di output senza chiedere
            "-f", "rawvideo",  # Formato del video grezzo in input
            "-pixel_format", "bgr24",  # Formato pixel corrispondente a QImage convertito
            "-video_size", f"{width}x{height}",  # Risoluzione video
            "-framerate", "60",  # Framerate di 60 fps
            "-i", "-",  # Legge lo stream video da stdin
            # Aggiungi l'audio fittizio
            "-f", "lavfi",
            "-i", "anullsrc=channel_layout=stereo:sample_rate=44100",  # Audio nullo fittizio
            "-c:v", codec_name,  # Codec video
            "-profile:v", profile,  # Profilo codec
            "-b:v", f"{bitrate}k",  # Bitrate video
            "-preset", preset,  # Preset (ultrafast, fast, etc.)
            "-pix_fmt", pixel_format,  # Formato pixel di output
            "-c:a", "aac",  # Codec audio
            "-b:a", "128k",  # Bitrate audio
            "-ar", "44100",  # Frequenza di campionamento audio
        ]

        # Aggiunta di opzioni avanzate (tune, rate control, buffer, keyframe interval)
        if tune != "None":
            command += ["-tune", tune]
        if rate_control == "CBR":
            command += ["-maxrate", f"{bitrate}k"]
        if buffer_size:
            command += ["-bufsize", f"{buffer_size}k"]
        if keyframe_interval > 0:
            command += ["-g", f"{keyframe_interval * 30}"]

        # Output per il flusso
        command += ["-f", "flv", f"{stream_url}/{stream_key}"]
        # command += ["-f", "flv", "output_test.flv"]
        return command

    def generateFFMpegCommandold2(self, request):
        """
        Genera il comando FFmpeg sulla base del dizionario di configurazione fornito.
        """
        # Estrai informazioni dal dizionario request
        demuxer = request.get('deMuxer', {})
        codec = request.get('codec', {})
        stream_info = request.get('streamInfo', {})

        # Stream URL e Stream Key
        stream_url = stream_info.get('url', '')
        stream_key = stream_info.get('key', '')

        # Codec settings
        codec_name = codec.get('codec', 'libx264')
        profile = codec.get('profile', 'high')  # YouTube consiglia 'high'
        pixel_format = codec.get('pixelFormat', 'yuv420p')
        preset = codec.get('preset', 'veryfast')
        rate_control = codec.get('rateControl', 'CBR')
        bitrate = codec.get('bitrate', 4500)  # Bitrate consigliato per 1080p60
        buffer_size = codec.get('bufferSize', 9000)
        tune = codec.get('tune', 'zerolatency')  # 'zerolatency' per streaming
        keyframe_interval = codec.get('keyframeInterval', 2)

        # Frame rate
        fps = codec.get('fps', 60)

        # Comando FFmpeg per input rawvideo tramite stdin
        command = [
            "ffmpeg", "-y",  # Sovrascrivi i file di output senza chiedere
            "-f", "rawvideo",  # Formato del video grezzo in input
            "-pixel_format", "bgr24",  # Formato pixel corrispondente a QImage convertito
            "-video_size", f"1920x1080",  # Risoluzione video
            "-framerate", f"{fps}",  # Framerate
            "-i", "-",  # Legge lo stream video da stdin
            # Aggiungi l'audio fittizio
            "-f", "lavfi",
            "-i", "anullsrc=channel_layout=stereo:sample_rate=44100",  # Audio nullo fittizio
            "-c:v", codec_name,  # Codec video
            "-profile:v", profile,  # Profilo codec
            "-b:v", f"{bitrate}k",  # Bitrate video
            "-preset", preset,  # Preset (ultrafast, veryfast, etc.)
            "-pix_fmt", pixel_format,  # Formato pixel di output
            "-c:a", "aac",  # Codec audio
            "-b:a", "128k",  # Bitrate audio
            "-ar", "44100",  # Frequenza di campionamento audio
        ]

        # Aggiunta di opzioni avanzate (tune, rate control, buffer, keyframe interval)
        if tune != "None":
            command += ["-tune", tune]
        if rate_control == "CBR":
            command += ["-maxrate", f"{bitrate}k"]
        if buffer_size:
            command += ["-bufsize", f"{buffer_size}k"]
        if keyframe_interval > 0:
            command += ["-g", f"30"]  # Intervallo di keyframe in base al frame rate

        # Output per il flusso
        command += ["-f", "flv", f"{stream_url}/{stream_key}"]
        return command

    def generateFFMpegCommand(self, request):
        """
        Genera il comando FFmpeg per streaming e registrazione.
        """
        # Estrai informazioni dal dizionario request
        demuxer = request.get('deMuxer', {})
        codec = request.get('codec', {})
        stream_info = request.get('streamInfo', {})

        # Stream URL e Stream Key
        stream_url = stream_info.get('url', '')
        stream_key = stream_info.get('key', '')

        # Codec settings
        codec_name = 'hevc_nvenc'  # Utilizza l'encoder NVIDIA HEVC (H.265)
        profile = 'main'  # Profilo codec: main, main10, ecc.
        pixel_format = 'yuv420p'  # yuv420p, nv12, o altro supportato
        preset = 'p4'  # Preset NVENC: default 'p4' (medium), p1 (più veloce), p7 (qualità)
        rate_control = codec.get('rateControl', 'cbr').lower()  # 'cbr' o 'vbr'
        bitrate = codec.get('bitrate', 8000)  # Bitrate video a 8000k (8 Mbps)
        buffer_size = codec.get('bufferSize', 16000)  # Buffer size adeguato per il bitrate
        tune = codec.get('tune', 'hq')  # 'hq' per alta qualità, 'zerolatency' per streaming in tempo reale
        keyframe_interval = codec.get('keyframeInterval', 2)  # Intervallo keyframe in secondi

        # Frame rate
        fps = codec.get('fps', 60)

        # Calcola il valore di '-g' basato sul frame rate e keyframe interval
        g = keyframe_interval * fps  # Ad esempio, 2 sec * 60 fps = 120

        ffmpeg_command = [
            'ffmpeg',
            '-y',  # Sovrascrive il file se esiste
            '-hwaccel', 'cuda',  # Usa l'accelerazione hardware CUDA
            '-hwaccel_output_format', 'cuda',  # Imposta il formato di output per CUDA
            '-f', 'rawvideo',  # Formato in input
            '-vcodec', 'rawvideo',
            '-pix_fmt', 'bgr24',  # Formato pixel BGR
            '-s', '1920x1080',  # Risoluzione
            '-r', '50',  # Framerate
            '-vsync', '2',  # Sincronizzazione frame
            '-i', '-',  # Input da stdin
            # Aggiungi l'audio fittizio
            '-f', 'lavfi',
            '-i', 'anullsrc=channel_layout=stereo:sample_rate=44100',  # Audio nullo fittizio
            '-c:v', 'h264_nvenc',  # Codec video con H.264 NVENC (accelerazione CUDA)
            '-preset:v', 'llhq',  # Preset low latency high quality
            '-profile:v', 'baseline',  # Profilo baseline per compatibilità con YouTube
            '-b:v', '4500k',  # Bitrate video
            '-maxrate:v', '4950k',  # Bitrate massimo per il controllo del rate
            '-bufsize:v', '4500k',  # Buffer size
            '-g:v', '120',  # Intervallo keyframe (120 frame = 2 secondi a 60fps)
            '-c:a', 'aac',  # Codec audio AAC
            '-b:a', '128k',  # Bitrate audio
            '-ar', '44100',  # Frequenza di campionamento audio
            '-f', 'flv',  # Formato per lo streaming RTMP
            f'rtmp://a.rtmp.youtube.com/live2/{stream_key}'  # URL dello stream con chiave
        ]

        return ffmpeg_command

    def getTally(self, tally_data):
        """
        Aggiorna lo stato del MixBus in base ai dati ricevuti dal TallyManager.
        """
        tally_data['sender'] = 'recManager'
        cmd = tally_data.get('cmd')
        if cmd == 'info':
            self.emitTallySignal(cmd, f"from recStream: {tally_data}")
        elif cmd == 'error':
            self.emitTallySignal(cmd, f"error from recStream: {tally_data}")
        elif cmd == 'warning':
            self.emitTallySignal(cmd, f"warning from recStream: {tally_data}")

    def emitTallySignal(self, cmd, message):
        tally_status = {
            'sender': 'recManager',
            'cmd': cmd,
            'message': str(message),
        }
        self.tally_SIGNAL.emit(tally_status)
