import torch
import pandas as pd

class Dataset(torch.utils.data.Dataset):
  def __init__(self,path_dataset):
    self.data_df=pd.read_csv(path_dataset)

  def __len__(self):
    return len(self.data_df)

  def __getitem__(self,idx):
    title,description=self.data_df.iloc[idx]["title"],self.data_df.iloc[idx]["description"]
    return title,description
