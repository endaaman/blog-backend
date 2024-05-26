class GlobalStore:
    def __init__(self):
        self.blog_data = None

    def set_blog_data(self, blog_data):
        self.blog_data = blog_data

global_store = GlobalStore()
