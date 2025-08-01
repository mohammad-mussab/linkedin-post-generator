import pandas as pd
import json


class FewShotPosts:
    def __init__(self, file_path="data/cleaned_linkedin_posts.json"):
        self.df = None
        self.unique_tags = None
        self.load_posts(file_path)

    def load_posts(self, file_path):
        with open(file_path, encoding="utf-8") as f:
            posts_dict = json.load(f)
            posts = posts_dict["posts"]  # <-- get the list of posts
            self.df = pd.json_normalize(posts)
            self.df['length'] = self.df['line_count'].apply(self.categorize_length)
            all_tags = self.df['tags'].apply(lambda x: x).sum()
            all_tags = self.df['tags'].apply(lambda tags: [tag.strip('"').strip("'") for tag in tags]).sum()
            self.unique_tags = list(set(all_tags))

    def get_filtered_posts(self, length, language, tag):
        df_filtered = self.df[
            (self.df['tags'].apply(lambda tags: tag in tags)) &  # Tags contain 'Influencer'
            (self.df['language'] == language) &  # Language is 'English'
            (self.df['length'] == length)  # Line count is less than 5
        ]
        return df_filtered.to_dict(orient='records')

    def categorize_length(self, line_count):
        if line_count < 5:
            return "Short"
        elif 5 <= line_count <= 10:
            return "Medium"
        else:
            return "Long"

    def get_tags(self):
        return self.unique_tags


if __name__ == "__main__":
    fs = FewShotPosts()
    # print(fs.get_tags())
    #load_posts = fs.load_posts()
    posts = fs.get_filtered_posts("Medium","Urduish","Financial Planning")
    print(posts)