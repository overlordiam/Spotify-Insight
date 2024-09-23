import sys,os
import site
from datetime import datetime

sys.path.extend(site.getsitepackages())
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
from ingestion.retrieve_objects import MinioRetriever,MinioUploader
from ingestion.utils import TOPIC_CONFIG


class RetrieveLikedSongs():

    def __init__(self,user, topic,raw, processed) -> None:

        self.retriever = MinioRetriever(user, topic, raw)
        self.uploader = MinioUploader(user,topic, processed)
        self.processed = processed

        self.dtype_dict = {
            'like_id': 'int64',
            'artist_id': str,
            'album_id': str,
            'track_id': str,
            'added_at': str,
            'time_id': str
        }
        
    def get_user_liked_songs(self):

        try:
            tracks = []
            results= self.retriever.retrieve_object()

            for count, result in enumerate(results):
                item=result["items"]
                track = item[0]['track']
                tracks.append({
                    'like_id': count,
                    'artist_id': track['artists'][0]['id'],
                    'album_id': track['album']['id'],
                    'track_id': track['id'],
                    'added_at': item[0]['added_at']
                })

            # Convert to DataFrame
            df_tracks= pd.DataFrame(tracks)
            df_tracks['added_at'] = pd.to_datetime(df_tracks['added_at']) # data type is TIMESTAMP
            df_tracks['time_id'] = df_tracks['added_at'].apply(lambda val: val.strftime('%Y%m%d%H%M%S'))
            df_tracks['ingested_on'] = datetime.now().strftime("%Y%m%d%H%M%S")

            df_tracks = df_tracks.astype(self.dtype_dict)
            df_tracks.drop_duplicates(inplace=True)
            df_tracks = df_tracks.reset_index(drop=True)

            self.uploader.upload_files(data=df_tracks)
            print(f"Successfully uploaded to '{self.processed}' container!!")
        
        except Exception as e:
            print(f"Encountered an exception here!!: {e}")


def run_retrieve_liked_songs():
    ob = RetrieveLikedSongs("suhaas", \
                            TOPIC_CONFIG["liked_songs"]["topic"], \
                            "raw", \
                            "processed")
    ob.get_user_liked_songs()

    

if __name__ == "__main__":
    run_retrieve_liked_songs()