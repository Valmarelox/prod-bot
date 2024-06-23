from pocket import Pocket
import random
from enum import StrEnum, auto

from bot import SubBot


class ContentType(StrEnum):
    video = auto()
    article = auto()
    image = auto()

class PocketBot(SubBot):
    def __init__(self, consumer_key, access_token):
        self._pocket = Pocket(consumer_key=consumer_key, access_token=access_token)
        
    def get_message_of_type(self, state, content_type: ContentType):
        res = self._pocket.retrieve(content_type, state=state)
        if res['complete'] != 1:
            raise RuntimeError("Encountered an error getting unread articles")
        articles = res['list']
        random_article = articles[random.choice(list(articles.keys()))]
        total_minutes = int(sum((article.get('time_to_read', int(article['word_count']) / 200) for article in articles.values())))
        return len(articles), total_minutes, random_article['resolved_title']

    
    def get_unread_msg(self):
        num_articles, total_minutes, random_article = self.get_message_of_type('unread', ContentType.article)
        return f"{num_articles} articles left which will take {total_minutes} minutes to finish reading.\n\tConsider reading: {random_article}"
    
    def get_read_msg(self):
        num_articles, total_minutes, random_article = self.get_message_of_type('archive', content_type=ContentType.article)
        return f"{num_articles} articles read which took {total_minutes} minutes.\n\tSomething you read: {random_article}"

    def get_video_times(self):
        num_unread, total_unread, _ =  self.get_message_of_type('unread', ContentType.video)
        num_archive, total_archive, _ = self.get_message_of_type('archive', ContentType.video)
        return f"{num_unread} videos left which will take {total_unread} minutes to finish watching.\n{num_archive} videos watched which took {total_archive} minutes."

    
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
