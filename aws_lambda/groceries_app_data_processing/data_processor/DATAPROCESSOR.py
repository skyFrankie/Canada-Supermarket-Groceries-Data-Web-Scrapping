from dataclasses import dataclass, field
import pandas as pd
from data_processor.LOBLAWS_PROCESSOR import loblaws_cleansing

@dataclass
class DATAPROCESSOR:
    store: str
    df: pd.DataFrame
    cleansing_func_map = {
        'Loblaws': loblaws_cleansing
    }

    def data_cleansing(self):
        return self.cleansing_func_map.get(self.store, None)(self.df)
