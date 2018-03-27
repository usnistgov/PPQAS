from tree import get_prev_child_of_parent, get_next_child_of_parent
from policy_study import elements




def test_get_prev_child_of_parent():
    from tree import Tree
    a = Tree()
    a["a"]["aa"]["aaa"] = Tree()
    a["b"]["ba"]["baa"] = Tree()
    a["a"]["ab"]["aba"] = Tree()
    assert get_prev_child_of_parent(a["a"]["ab"]).data == "aa"
    assert get_prev_child_of_parent(a["b"]["ba"]["baa"]).data == "a"


    from policy_study import app
    app.config["INPUT_FILE"] = "resources/pp_test.xml"
    from policy_study import views
    views.initialize()
    ti = elements.get_index_tree(views.qindex)
    assert get_prev_child_of_parent(ti["Creating Passwords"]["Lengths"]).data == "Communicate"

def test_get_next_child_of_parent():
    from tree import Tree
    a = Tree()
    a["a"]["aa"]["aaa"] = Tree()
    a["b"]["ba"]["baa"] = Tree()
    a["a"]["ab"]["aba"] = Tree()
    assert get_next_child_of_parent(a["a"]["aa"]).data == "ab"

    from policy_study import app
    app.config["INPUT_FILE"] = "resources/pp_test.xml"
    from policy_study import views
    views.initialize()
    ti = elements.get_index_tree(views.qindex)
    print ti
    assert get_next_child_of_parent(ti["Communicate"]["Communicate How"]["Specific Methods"]["Any Network"]).data == "Internet or Wide-Area Network(WAN)"
