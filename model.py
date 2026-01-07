from transformers import CLIPModel, CLIPTokenizer

def get_model_and_tokz():
    #Modelo
    model_name="openai/clip-vit-base-patch32"

    #Cargar el modelo pre-entrenado
    model=CLIPModel.from_pretrained(model_name,device_map=None,low_cpu_mem_usage=False)

    #Tokenizer
    tokenizer=CLIPTokenizer.from_pretrained(model_name)

    return model,tokenizer
