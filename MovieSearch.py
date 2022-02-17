class MovieSearch:
    def __init__(self, title, year, description,  img_url, rating=None, ranking=None, review=None):
        self.title = title
        self.year = year
        self.description = description
        self.rating = rating
        self.ranking = ranking
        self.review = review
        self.img_url = img_url
