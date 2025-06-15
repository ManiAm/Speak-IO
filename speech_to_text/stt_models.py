
from engine_openai_whisper import OpenAIWhisperEngine
from engine_faster_whisper import FasterWhisperEngine
from engine_whisper_cpp import WhisperCppEngine


MODELS = {
    "openai_whisper": OpenAIWhisperEngine(),
    "faster_whisper": FasterWhisperEngine(),
    "whisper.cpp": WhisperCppEngine()
}


def get_models_engine(engine):

    if engine not in MODELS:
        return False, f"Engine '{engine}' not supported"

    model_handler = MODELS[engine]

    try:
        models = model_handler.get_models()
        return True, models
    except Exception as e:
        return False, f"Failed to load model: {str(e)}"


def get_models():

    models_dict = {}

    for engine, model_handler in MODELS.items():

        try:
            models_dict[engine] = model_handler.get_models()
        except Exception as e:
            return False, f"Failed to get models: {str(e)}"

    return True, models_dict


def load_model_for_engine(engine, model_name):

    if engine not in MODELS:
        return False, f"Engine '{engine}' not supported"

    model_handler = MODELS[engine]

    try:
        return model_handler.load_model(model_name)
    except Exception as e:
        return False, f"Failed to load model: {str(e)}"


def transcribe(audio_path, engine, model_name):

    if engine not in MODELS:
        return False, f"Engine '{engine}' not supported"

    model_handler = MODELS[engine]

    try:
        return model_handler.transcribe(audio_path, model_name)
    except Exception as e:
        return False, f"Failed to transcribe: {str(e)}"
