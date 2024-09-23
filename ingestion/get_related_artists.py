import sys,os
import site

sys.path.extend(site.getsitepackages())
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime
from ingestion.retrieve_objects import MinioRetriever, MinioUploader
import pandas as pd
from ingestion.utils import TOPIC_CONFIG

class RetrieveRelatedArtists():

    def __init__(self, user, topic, raw, processed) -> None:
        
        self.retriever = MinioRetriever(user, topic, raw)
        self.uploader = MinioUploader(user,topic, processed)
        self.processed = processed

        self.dtype_dict = {
            'artist_name': str,
            'artist_id': str,
            'artist_popularity': 'int64', # allows NaNs
            'artist_followers': 'int64'
        }

    def get_artist_related_artists(self):

        all_artists = []
        results = self.retriever.retrieve_object()
        try:
            for result in results:
                all_artists.append({
                'artist_id': result['id'],
                'artist_name': result['name'],
                'artist_popularity': result['popularity'],
                'artist_followers': result['followers'],
                })
                
            df_artists = pd.DataFrame(all_artists)
            df_artists['ingested_on'] = datetime.now().strftime("%Y%m%d%H%M%S")
            
            df_artists = df_artists.astype(self.dtype_dict)
            df_artists.drop_duplicates(['artist_id'], inplace=True)
            df_artists = df_artists.reset_index(drop=True)
            
            self.uploader.upload_files(data=df_artists)
            print(f"Successfully uploaded to '{self.processed}' container!!")

        except Exception as e:
            print(f"Encountered an exception here!!: {e}")
    

def run_get_artist_related_artists():
    ob = RetrieveRelatedArtists("suhaas", \
                                TOPIC_CONFIG["related_artists"]["topic"], \
                                "raw", \
                                "processed")
    ob.get_artist_related_artists()

if __name__ == "__main__":
    run_get_artist_related_artists()