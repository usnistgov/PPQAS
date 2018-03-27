from bnf import get_bnf, responses_by_only_id, responses_by_only_qid, generate_bnf_statements
from policy_study import views, db, elements
from pprint import pprint



# def test_get_bnf():
#     views.initialize()
#     qaire = db.conns["questionnaire"].find_one()
#     id_to_bnf = elements.get_id_bnf_mapping(views.questions)
#     pprint(id_to_bnf)
#     bnfs = get_bnf(qaire, views.questions, id_to_bnf)
#     pprint(bnfs)
# #    assert 1 == 2


# def test_generate_bnf_statements():
#     views.initialize()
#     qaire = db.conns["questionnaire"].find_one()
#     id_to_bnf = elements.get_id_bnf_mapping(views.questions)
#     bnfs = get_bnf(qaire, views.questions, id_to_bnf)
#     stmnts = generate_bnf_statements(bnfs, responses_by_only_id(qaire['questions']), views.idmap)
#     pprint(stmnts)
#    assert 1 == 2


def test_responses_by_only_qid():
    resps = {u'q.1.1': u'q.1.1.A',
             u'q.1.1.1': u'q.1.1.1.A',
             u'q.1.2.1': u'q.1.2.1.A',
             u'q.1.2.2.1': u'q.1.2.2.1.C',
             u'q.1.2.2.2': u'q.1.2.2.2.C',
             u'q.1.2.3': u'q.1.2.3.A',
             u'q.2.1': u'q.2.1.A',
             u'q.2.1.A.b': u'3',
             u'q.2.1>q.2.1.A.a': u'recommends',
             u'q.2.2.A.b': u'88',
             u'q.2.20': u'q.2.20.B',
             u'q.2.20.1': [u'q.2.20.1.A', u'q.2.20.1.G', u'q.2.20.1.H'],
             u'q.2.2>q.2.2.A.a': u'requires',
             u'q.2.3.1': [u'q.2.3.1.A'],
             u'q.2.3.1.1': u'q.2.3.1.1.C',
             u'q.2.3.1.2': u'q.2.3.1.2.A',
             u'q.2.3.1.2.1.b': u'2',
             u'q.2.3.1.2.1>q.2.3.1.2.1.a': u'requires',
             u'q.2.3.1.3': u'q.2.3.1.3.B',
             u'q.2.3.1.3.1.b': u'43',
             u'q.2.3.1.3.1>q.2.3.1.3.1.a': u'recommends'}

    expected = {u'q.1.1': u'q.1.1.A',
               u'q.1.1.1': u'q.1.1.1.A',
               u'q.1.2.1': u'q.1.2.1.A',
               u'q.1.2.2.1': u'q.1.2.2.1.C',
               u'q.1.2.2.2': u'q.1.2.2.2.C',
               u'q.1.2.3': u'q.1.2.3.A',
               u'q.2.1': u'q.2.1.A',
               u'q.2.1.A.b': u'3',
               u'q.2.1': u'recommends',
               u'q.2.2.A.b': u'88',
               u'q.2.20': u'q.2.20.B',
               u'q.2.20.1': [u'q.2.20.1.A', u'q.2.20.1.G', u'q.2.20.1.H'],
               u'q.2.2': u'requires',
               u'q.2.3.1': [u'q.2.3.1.A'],
               u'q.2.3.1.1': u'q.2.3.1.1.C',
               u'q.2.3.1.2': u'q.2.3.1.2.A',
               u'q.2.3.1.2.1.b': u'2',
               u'q.2.3.1.2.1': u'requires',
               u'q.2.3.1.3': u'q.2.3.1.3.B',
               u'q.2.3.1.3.1.b': u'43',
               u'q.2.3.1.3.1': u'recommends'}


    assert responses_by_only_qid(resps) == expected
#    assert 1==2

def test_responses_by_only_id():
    resps = {u'q.1.1': u'q.1.1.A',
             u'q.1.1.1': u'q.1.1.1.A',
             u'q.1.2.1': u'q.1.2.1.A',
             u'q.1.2.2.1': u'q.1.2.2.1.C',
             u'q.1.2.2.2': u'q.1.2.2.2.C',
             u'q.1.2.3': u'q.1.2.3.A',
             u'q.2.1': u'q.2.1.A',
             u'q.2.1.A.b': u'3',
             u'q.2.1>q.2.1.A.a': u'recommends',
             u'q.2.2': u'q.2.2.A',
             u'q.2.2.A.b': u'88',
             u'q.2.20': u'q.2.20.B',
             u'q.2.20.1': [u'q.2.20.1.A', u'q.2.20.1.G', u'q.2.20.1.H'],
             u'q.2.2>q.2.2.A.a': u'requires',
             u'q.2.3.1': [u'q.2.3.1.A'],
             u'q.2.3.1.1': u'q.2.3.1.1.C',
             u'q.2.3.1.2': u'q.2.3.1.2.A',
             u'q.2.3.1.2.1.b': u'2',
             u'q.2.3.1.2.1>q.2.3.1.2.1.a': u'requires',
             u'q.2.3.1.3': u'q.2.3.1.3.B',
             u'q.2.3.1.3.1.b': u'43',
             u'q.2.3.1.3.1>q.2.3.1.3.1.a': u'recommends'}

    output = responses_by_only_id(resps)
    expected = {u'q.1.1': u'q.1.1.A',
             u'q.1.1.1': u'q.1.1.1.A',
             u'q.1.2.1': u'q.1.2.1.A',
             u'q.1.2.2.1': u'q.1.2.2.1.C',
             u'q.1.2.2.2': u'q.1.2.2.2.C',
             u'q.1.2.3': u'q.1.2.3.A',
             u'q.2.1': u'q.2.1.A',
             u'q.2.1.A.b': u'3',
             u'q.2.1.A.a': u'recommends',
             u'q.2.2': u'q.2.2.A',
             u'q.2.2.A.b': u'88',
             u'q.2.20': u'q.2.20.B',
             u'q.2.20.1': [u'q.2.20.1.A', u'q.2.20.1.G', u'q.2.20.1.H'],
             u'q.2.2.A.a': u'requires',
             u'q.2.3.1': [u'q.2.3.1.A'],
             u'q.2.3.1.1': u'q.2.3.1.1.C',
             u'q.2.3.1.2': u'q.2.3.1.2.A',
             u'q.2.3.1.2.1.b': u'2',
             u'q.2.3.1.2.1.a': u'requires',
             u'q.2.3.1.3': u'q.2.3.1.3.B',
             u'q.2.3.1.3.1.b': u'43',
             u'q.2.3.1.3.1.a': u'recommends'}
    assert output == expected
