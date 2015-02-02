from summary import Summary
import os


def test_summary():
    testdata = get_test_data()
    passed = 0
    failed = 0
    errors = ""
    for line in testdata:
        if line.startswith('url') or line.strip().startswith('#') or not line.strip():
            continue

        url, img, title, desc = (line.strip().split('|') + [None]*99)[:4]
        print "Testing %(url)s %(img)s %(title)s %(desc)s" % locals()
        summ = Summary(url)
        summ.extract()

        testpassed = True
        if img:
            if not summ.image or summ.image.url != unicode(img):
                testpassed = False
                errors += "%s bad image %s\n" % (url, summ.image and summ.image.url)
        if title:
            if summ.title != unicode(title, 'utf-8'):
                testpassed = False
                errors += "%s bad title %s\n" % (url, summ.title)
        if desc:
            if summ.description != unicode(desc, 'utf-8'):
                testpassed = False
                errors += "%s bad desc %s\n" % (url, summ.description)

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