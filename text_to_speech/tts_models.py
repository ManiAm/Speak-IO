
from engine_coqui import CoquiEngine
from engine_piper import PiperEngine
from engine_bark import BarkEngine
from engine_chatterbox import ChatterBoxEngine


MODELS = {
    "coqui": CoquiEngine(),
    "piper": PiperEngine(),
    "bark": BarkEngine(),
    "chatterbox": ChatterBoxEngine()
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


def synthesize(text, engine, model_name, *args, **kwargs):

    if engine not in MODELS:
        return False, f"Engine '{engine}' not supported"

    model_handler = MODELS[engine]

    try:
        return model_handler.synthesize(text, model_name, *args, **kwargs)
    except Exception as e:
        return False, f"Failed to synthesize: {str(e)}"
