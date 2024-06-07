from pocket import Pocket
import random

class PocketBot:
    def __init__(self, consumer_key, access_token):
        self._pocket = Pocket(consumer_key=consumer_key, access_token=access_token)
        
    def get_message_of_type(self, state):
        res = self._pocket.retrieve(contentType='article', state=state)
        if res['complete'] != 1:
            print(res)
            raise RuntimeError("Encountered an error getting unread articles")
        articles = res['list']
        random_article = articles[random.choice(list(articles.keys()))]
        print(random_article)
        total_minutes = int(sum((article.get('time_to_read', int(article['word_count']) / 200) for article in articles.values())))
        return len(articles), total_minutes, random_article['resolved_title']
    
    def get_unread_msg(self):
        num_articles, total_minutes, random_article = self.get_message_of_type('unread')
        return f"{num_articles} articles left which will take {total_minutes} minutes to finish reading.\n\tConsider reading: {random_article}"
    
    def get_read_msg(self):
        num_articles, total_minutes, random_article = self.get_message_of_type('archive')
        msg = f"{num_articles} articles read which took {total_minutes} minutes.\n\tSomething you read: {random_article}"
    
        return msg
    
    def get_msg(self, scheduled=False):
        if scheduled:
            PREFIX = 'Your morning reading update!'
        else:
            PREFIX = 'Here is your reading status!'
        msg = f"""{PREFIX}
        {self.get_read_msg()}
        
        {self.get_unread_msg()}
        """
    
        return msg
