import torch

#Get embedding
def get_embedding(description,tokenizer,modelo):
    tokens_desc=tokenizer(text=description,return_tensors="pt")["input_ids"]
    
    with torch.no_grad():
        tokens_emb=modelo.get_text_features(tokens_desc).squeeze(0)
        
    return tokens_emb.numpy().tolist()
