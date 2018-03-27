class UserNotFoundError(Exception):
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return "User " + self.name + " not found."


class ConfigItemNotFoundError(Exception):
    def __init__(self, key):
        self.key = key

    def __str__(self):
        return "Config does not contain " + self.key

class PSError(Exception):
    def __init__(self, errstr):
        self.errstr = errstr
    def __str__(self):
        return self.errstr

class InstantiationError(Exception):
    def __init__(self, ttype, obj):
        self.ttype = ttype
        self.obj = obj

    def __str__(self):
        return "Could not instantiate {0} with obj {1}".format(self.ttype, self.obj)

class UnsupportedCloningError(Exception):
    def __init__(self, q, opt):
        self.q = q
        self.opt = opt
    def __str__(self):
        return "Cloning in question {0} on opt {1} is not supported".format(self.q, self.opt)


class IDError(Exception):
    def __init__(self, problem_id):
        self.problem_id = problem_id
    def __str__(self):
        return "Problem with id:{0} unexpected format".format(self.problem_id)
