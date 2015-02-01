from summary import Summary
import os


def test_summary():
    testdata = get_test_data()
    passed = 0
    failed = 0
    errors = []
    for line in testdata:
        if line.startswith('url'):
            continue

        url, img, title, desc = (line.strip().split('|') + [None]*99)[:4]
        print "Testing %(url)s %(img)s %(title)s %(desc)s" % locals()
        summ = Summary(url)
        summ.extract()

        testpassed = True
        if img:
            if summ.image.url != img:
                testpassed = False
                errors += "%(url)s bad image %(img)s" % locals()
        if title:
            if summ.title != title:
                testpassed = False
                errors += "%(url)s bad title %(title)s" % locals()
        if desc:
            if summ.description != desc:
                testpassed = False
                errors += "%(url)s bad desc %(desc)s" % locals()

        if testpassed:
            passed += 1
        else:
            failed +=1

    print "Passed %(passed)s, Failed %(failed)s" % locals()
    if errors: print errors
    assert failed == 0


def get_test_data():
    testfile = './data.txt'
    testpath = os.path.join(os.path.dirname(__file__), testfile)
    with open (testpath, 'r') as myfile:
        data = myfile.readlines()
    return data