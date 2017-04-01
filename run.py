from zhihu_fun.go import UrlGenerator, QuestionParser
from zhihu_fun.toollib.logger import Logger
from multiprocessing import Queue, Process
import json


def url_generator(q):
    try:
        g = UrlGenerator(q, keyword_number=2)
        g.run(30)
    except KeyboardInterrupt:
        g.driver.close()
        Logger.warning('Handle KeyboardInterrupt, Stopping app...')
    except Exception as e:
        g.driver.close()
        Logger.warning('Handle Exception {}'.format(e))
    with open('result.json', 'w') as f:
        Logger.info('Summary: {} Record'.format(len(g.info)))
        Logger.info('Keyword Matched \n' + json.dumps(g.macthed_keys, indent=4, ensure_ascii=False))
        json.dump(g.info, f, indent=4, ensure_ascii=False)
        Logger.info('Dump to File {}'.format(f.name))


def question_parser(q):
    try:
        qe = QuestionParser(q)
        qe._run()
    except Exception as e:
        qe.driver.close()
        Logger.warning('Handle Exception {}'.format(e))


if __name__ == '__main__':
    q = Queue()
    ps = [Process(target=fn, args=(q,), name=fn.__name__) for fn in (question_parser, url_generator)]
    [p.start() for p in ps]
    [p.join() for p in ps]
