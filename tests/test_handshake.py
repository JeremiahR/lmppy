from lmp.handshake import return_one


# just make sure tests are working
def test_return_one():
    assert return_one() == 1
