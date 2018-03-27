class User:
    def __init__(self, user_obj):
        if "name" in user_obj:
            self.name = user_obj["name"]
        else:
            self.name = user_obj["hashed_id"]
        self.user_obj = user_obj

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.name

    def is_admin(self):
        return self.user_obj["isadmin"]

    def done_demo_survey(self):
        return self.user_obj["done_demographic_survey"]
