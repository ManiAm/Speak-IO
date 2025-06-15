
import os
import sys
import shutil
from typing import List, Optional, Union
import utility


class WhisperCppEngine:

    def __init__(self):

        self.models = {}

        self.whisper_cpp_path = os.getenv("WHISPER_CPP_PATH", None)
        if not self.whisper_cpp_path:
            print("WHISPER_CPP_PATH is not set")
            sys.exit(1)

        self.model_dir = os.path.join(self.whisper_cpp_path, "models")
        if not os.path.exists(self.model_dir):
            print("whisper-cpp model directory cannot be accessed")
            sys.exit(1)

        self.download_ggml_model_script = os.path.join(self.model_dir, "download-ggml-model.sh")
        if not os.path.exists(self.download_ggml_model_script):
            print("download-ggml-model.sh cannot be accessed")
            sys.exit(1)

        self.whisper_binary_path = shutil.which("whisper-cli")
        if not self.whisper_binary_path:
            print("Cannot access whisper-cli binary")
            sys.exit(1)


    def get_models(self):

        cmd = f"{self.download_ggml_model_script} -h 2>&1 || true"

        status, output = utility.runProcessBlocking(cmd, shell=True)
        if not status:
            print(f"Error: {output}")
            return []

        models = []
        collect = False

        for line in output.splitlines():
            if "Available models:" in line:
                collect = True
                continue
            if collect:
                line = line.strip()
                if not line:
                    break  # stop at first empty line after start
                models += line.split()

        return models


    def load_model(self, model_name):

        if model_name not in self.models:

            cmd = ["sh", self.download_ggml_model_script, model_name]

            status, output = utility.runProcessBlocking(cmd, cwd=self.whisper_cpp_path)
            if not status:
                return False, output

            model_name_full = f"ggml-{model_name}.bin"
            model_path = os.path.join(self.model_dir, model_name_full)
            self.models[model_name] = model_path

        return True, f"Loaded Whisper-CPP model '{model_name}'"


    # whisper-cli -m /opt/whisper.cpp/models/ggml-small.en.bin -f /opt/whisper.cpp/samples/jfk.wav
    def transcribe(self, audio_path, model_name):

        if model_name not in self.models:
            return False, f"Model '{model_name}' not loaded"

        model_path = self.models[model_name]

        return self.run_whisper_cpp(
            audio_path=audio_path,
            model_path=model_path,
            options={"-nt": None, "-np": None, "-ml": 500, "-mc": 4})


    def run_whisper_cpp(
        self,
        audio_path,
        model_path,
        options: Optional[Union[List[str], dict]] = None
    ):
        """
        Run whisper-cli with dynamic options.

        :param audio_path: Path to the input audio file
        :param model_path: Path to the model file
        :param binary_path: Path to the whisper-cli binary
        :param options: List of extra CLI arguments (e.g. ["-nt", "-ml", "500"]) or dict (e.g. {"-ml": "500"})

        -nt (--no-timestamps): Disables timestamps in the transcription output
        -np (--no-prints): Suppresses CLI output except the actual transcript
        -ml 500 (--max-len 500): Limits max segment length to 500 characters
        -mc 4 (--max-context 4): Keeps context for up to 4 segments across windowed inference steps
        """

        cmd = [self.whisper_binary_path, "-m", model_path, "-f", audio_path]

        if options:
            if isinstance(options, dict):
                for key, value in options.items():
                    cmd.append(str(key))
                    if value is not None and value != "":
                        cmd.append(str(value))
            elif isinstance(options, list):
                cmd.extend(map(str, options))

        status, output = utility.runProcessBlocking(cmd)
        if not status:
            return False, output

        transcript = output.strip()

        return True, transcript
