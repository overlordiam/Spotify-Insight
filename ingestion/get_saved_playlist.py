from retrieve_objects import MinioRetriever,MinioUploader
import pandas as pd
from utils import TOPIC_CONFIG
class RetrieveSavedPlaylist(MinioRetriever,MinioUploader):

    def __init__(self,user, topic,container) -> None:
        MinioRetriever.__init__(self,user, topic)
        MinioUploader.__init__(container, user, topic)

    def get_user_recent_plays(self):
        playlists = []
        results = MinioRetriever.retrieve_object(self)
        print(results)
        for result in results:
            item = result["items"][0]
            playlists.append({
                'playlist_name': item['name'],
                'playlist_id': item['id'],
                'playlist_uri': item['uri'],
                'owner_name': item['owner']['display_name'],
                'owner_id': item['owner']['id'],
                'is_public': item['public'],
                'is_collaborative': item['collaborative'],
                'total_tracks': item['tracks']['total'],
                'description': item['description']
            })
        # Convert to DataFrame
        df_playlist = pd.DataFrame(playlists)
        MinioUploader.upload_files(self,data=df_playlist)
        print("Object uploaded")
    


if __name__ == "__main__":
    ob = RetrieveSavedPlaylist("suhaas",TOPIC_CONFIG["saved_playlists"]["topic"],"processed")
    ob.get_liked_songs()