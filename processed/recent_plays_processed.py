from utils import MinioRetriever, MinioUploader
import pandas as pd


class RetrieveFollowingArtists(MinioRetriever, MinioUploader):

    def __init__(self, user, topic, processed, presentation) -> None:
        MinioRetriever.__init__(self, user, topic, processed)
        MinioUploader.__init__(self, user, topic, presentation)
       

    def get_user_followed_artists(self):
        artists = []
        results = MinioRetriever.retrieve_object(self)
        print(f"results: {results}")
        for result in results:
            # Process each artist
            print(f"result: {result}")
            for item in result['artists']['items']:
                artists.append({
                    'name': item['name'],
                    'id': item['id'],
                    'uri': item['uri'],
                    'popularity': item['popularity'],
                    'genres': ', '.join(item['genres']),
                    'followers': item['followers']['total']
                })
        # Convert to DataFrame
        df_artists = pd.DataFrame(artists)
        self.upload_files(data=df_artists)
        print("done")
    
    
if __name__ == '__main__':
    ob = RetrieveFollowingArtists('suhaas', 'spotify-following-artists', 'processed', 'presentation')
    ob.get_user_followed_artists()
