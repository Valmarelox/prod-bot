from pocket_api import PocketAPI
import random
from enum import Enum
from functools import partial
from bot import SubBot


class ContentType(Enum):
    video = "video"
    article = "article"
    image = "image"

class ItemState(Enum):
    unread = "unread"
    archive = "archive"
    all = "all"

WORDS_PER_MINUTE=200

def paginate_request(partial_request):
    offset = 0
    count = 30 # max count possible according to the API docs
    total = None
    items = {}
    while total is None or offset < total:
        res = partial_request(offset=offset, count=count)
        if res['complete'] != 1:
            raise RuntimeError("Encountered an error getting unread articles")
        items.update(res['list'])
        print(list(res.keys()))
        total = int(res['total'])
        offset += count
    return items
    

class PocketBot(SubBot):
    def __init__(self, consumer_key, access_token):
        self._pocket = PocketAPI(consumer_key=consumer_key, access_token=access_token)
        
    def get_message_of_type(self, state: ItemState, content_type: ContentType):
        articles = paginate_request(partial(self._pocket.get, contentType=content_type.value, state=state.value))
        random_article = articles[random.choice(list(articles.keys()))]
        total_minutes = int(sum((article.get('time_to_read', int(article['word_count']) / WORDS_PER_MINUTE) for article in articles.values())))
        return len(articles), total_minutes, random_article['resolved_title']

    
    def get_unread_msg(self):
        num_articles, total_minutes, random_article = self.get_message_of_type(ItemState.unread, ContentType.article)
        return f"{num_articles} articles left which will take {total_minutes} minutes to finish reading.\n\tConsider reading: {random_article}"
    
    def get_read_msg(self):
        num_articles, total_minutes, random_article = self.get_message_of_type(ItemState.archive, content_type=ContentType.article)
        return f"{num_articles} articles read which took {total_minutes} minutes.\n\tSomething you read: {random_article}"

    def get_video_times(self):
        num_unread, total_unread, _ =  self.get_message_of_type(ItemState.unread, ContentType.video)
        num_archive, total_archive, _ = self.get_message_of_type(ItemState.archive, ContentType.video)
        return f"{num_unread} videos left which will take {total_unread} minutes to finish watching.\n\t{num_archive} videos watched which took {total_archive} minutes."

    
    async def get_msg(self, scheduled):
        if scheduled:
            PREFIX = 'Your morning reading update!'
        else:
            PREFIX = 'Here is your reading status!'
        msg = f"""{PREFIX}
        {self.get_read_msg()}
        
        {self.get_unread_msg()}

        {self.get_video_times()}
        """
    
        return msg
