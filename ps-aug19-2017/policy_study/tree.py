from collections import OrderedDict, Callable
from utils import listify

class DefaultOrderedDict(OrderedDict):
    def __init__(self, default_factory=None, *a, **kw):
        if (default_factory is not None and
            not isinstance(default_factory, Callable)):
            raise TypeError('first argument must be callable')
        OrderedDict.__init__(self, *a, **kw)
        self.default_factory = default_factory

    def __getitem__(self, key):
        try:
            return OrderedDict.__getitem__(self, key)
        except KeyError:
            return self.__missing__(key)

    def __missing__(self, key):
        if self.default_factory is None:
            raise KeyError(key)
        self[key] = value = self.default_factory(data=key)
        return value

    def __reduce__(self):
        if self.default_factory is None:
            args = tuple()
        else:
            args = self.default_factory,
        return type(self), args, None, None, self.items()

    def copy(self):
        return self.__copy__()

    def __copy__(self):
        return type(self)(self.default_factory, self)

    def __deepcopy__(self, memo):
        import copy
        return type(self)(self.default_factory,
                          copy.deepcopy(self.items()))
    def __repr__(self):
        return 'OrderedDefaultDict(%s, %s)' % (self.default_factory,
                                        OrderedDict.__repr__(self))

    def previous_child(self, akey):
        prev = None
        for k in self:
            if k == akey:
                return prev
            prev = self[k]
        raise KeyError(akey)

    def next_child(self, akey):
        getnext = False
        for k in self:
            if getnext:
                return self[k]
            if k == akey:
                getnext = True
        if not getnext:
            raise KeyError(akey)
        return None


from json import loads, dumps

class Tree(DefaultOrderedDict):
    def __init__(self, inp=None, parent=None, data=None):
        self.data = data
        self.parent = parent
        DefaultOrderedDict.__init__(self, lambda data=None: Tree(None, self, data=data))
        if inp is not None:
            if isinstance(inp, basestring):
                self.update(loads(inp))
            else:
                self.update(inp)

    def __setitem__(self, key, value):
        if isinstance(value, Tree):
            value.parent = self
            value.data = key
        DefaultOrderedDict.__setitem__(self, key, value)

    def __str__(self, *args, **kwargs):
        return dumps(self, sort_keys=True, indent=4)

    def __repr__(self):
        return 'Tree(%s, %s)' % (self.default_factory,
                                 DefaultOrderedDict.__repr__(self))



def build_tree(xdict, key, keys=[], parent=None):
    parent = Tree(parent=parent)
    if key in xdict:
        parent.data = xdict[key]
    for k in keys:
        for item in listify(xdict.get(k, [])):
            parent[item[key]] = build_tree(item, key, keys=keys, parent=parent)
    return parent

def get_prev_child_of_parent(treenode):
    parent = treenode.parent
    if not parent:
        return None
    prev_child = parent.previous_child(treenode.data)
    if prev_child != None:
        return prev_child
    else:
        return get_prev_child_of_parent(parent)

def get_next_child_of_parent(treenode):
    parent = treenode.parent
    if not parent:
        return None
    next_child = parent.next_child(treenode.data)
    if next_child != None:
        return next_child
    else:
        return get_next_child_of_parent(parent)

def treesearch(key, root):
    for k,v in root.items():
        if str(k) == str(key):
            return v
        res = treesearch(key, v)
        if res != None:
            return res
