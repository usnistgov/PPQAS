from clones import inc_clone, clone_num, dec_clone





def test_inc_clone():
    ret = inc_clone("q.1.2.3clone1>q.1.2.3.A.bclone1")
    assert ret == "q.1.2.3clone2>q.1.2.3.A.bclone2"

def test_inc_clone2():
    ret = inc_clone("q.1.2.3>q.1.2.3.A.b")
    assert ret == "q.1.2.3clone1>q.1.2.3.A.bclone1"

def test_clone_num():
    ret = clone_num("q.1.2.3clone1>q.1.2.3.A.bclone1")
    assert ret == 1

def test_dec_clone():
    ret = dec_clone("q.1.2.3clone1>q.1.2.3.A.bclone1")
    assert ret == "q.1.2.3>q.1.2.3.A.b"

def test_dec_clone2():
    ret = dec_clone("q.1.2.3clone2>q.1.2.3.A.bclone2")
    assert ret == "q.1.2.3clone1>q.1.2.3.A.bclone1"
