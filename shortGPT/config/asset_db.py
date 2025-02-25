import os
import pandas as pd
from enum import Enum
import cv2

class AssetType(Enum):
    BACKGROUND_MUSIC = "background music"
    BACKGROUND_VIDEO = "background video"
    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"

class AssetDatabase:
    _df = None

    @classmethod
    def add_local_asset(cls, name, asset_type, link):
        df = cls.get_df()
        entry_dict = {"name": name, "type": asset_type.value, "link": link, "source": "local"}
        df.loc[len(df)] = entry_dict
        cls._save_df(df)
        cls._df = df

    @classmethod
    def get_df(cls):
        if cls._df is None:
            try:
                cls._df = pd.read_csv("public/asset_db.csv")
            except:
                cls._df = pd.DataFrame(columns=["name", "type", "link", "source"])
                cls._save_df(cls._df)
        return cls._df

    @classmethod
    def _save_df(cls, df):
        if not os.path.exists('public'):
            os.makedirs('public')
        df.to_csv("public/asset_db.csv", index=False)

    @classmethod
    def get_asset_link(cls, asset_name):
        df = cls.get_df()
        asset = df[df['name'] == asset_name]
        if len(asset) == 0:
            raise ValueError(f"Asset {asset_name} not found in database")
        return asset.iloc[0]['link']

    @classmethod
    def get_asset_duration(cls, asset_name):
        df = cls.get_df()
        asset = df[df['name'] == asset_name]
        if len(asset) == 0:
            raise ValueError(f"Asset {asset_name} not found in database")
        
        link = asset.iloc[0]['link']
        source = asset.iloc[0]['source']
        
        if source == 'local':
            # Handle local video files using OpenCV
            cap = cv2.VideoCapture(link)
            if not cap.isOpened():
                raise ValueError(f"Failed to open video file: {link}")
            
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            duration = frame_count/fps
            cap.release()
            return duration
        else:
            # For non-local files, use the existing audio_duration module
            from shortGPT.audio.audio_duration import get_asset_duration
            _, duration = get_asset_duration(link)
            return duration
