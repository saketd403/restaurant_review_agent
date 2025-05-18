import json
from datetime import datetime

from graph.state import Review
from config.paths import PATHS

class Reviews:

    def __init__(self,restaurant_id):

        self.reviews= []
        self.read_reviews(restaurant_id)

    def get_reviews(self):

        return self.reviews

    def read_reviews(self,restaurant_id):

        try:

            with open(PATHS.reviews/f"{restaurant_id}.json", "r", encoding="utf-8") as file:
                reviews_ls = json.load(file)

            for item in reviews_ls:

                time = datetime.fromisoformat(item["date"]) if item.get("date",None) else None
                review = Review(rating = item.get("rating",None),
                       content = item.get("content",None),
                       date = time)

                self.reviews.append(review)

        except Exception as e:

            print(f"Error while reading reviews:\n\n {e}")
            raise
