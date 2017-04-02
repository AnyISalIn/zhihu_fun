from zhihu_fun.go import UrlGenerator, QuestionParser, basedir
from zhihu_fun.toollib.logger import Logger
from zhihu_fun.config import config
from multiprocessing import Queue, Process
import json
import os


def url_generator(q):
    try:
        g = UrlGenerator(q, keyword_number=config.get('key_number'))
        g.run(config.get('url_generate_time'))
    except KeyboardInterrupt:
        g.driver.close()
        Logger.warning('Handle KeyboardInterrupt, Stopping app...')
    except Exception as e:
        g.driver.close()
        Logger.warning('Handle Exception {}'.format(e))
    finally:
        Logger.info('Summary: {} Record'.format(len(g.info)))
        Logger.info('Keyword Matched \n' + json.dumps(g.macthed_keys, indent=4, ensure_ascii=False))
        with open(os.path.join(basedir, 'result.json'), 'w') as json_file:
            json.dump(g.info, json_file, indent=4, ensure_ascii=False)
            Logger.info('Dump to File {}'.format(json_file.name))


def question_parser(q):
    try:
        qe = QuestionParser(q)
        qe.run()
    except Exception as e:
        qe.driver.close()
        Logger.warning('Handle Exception {}'.format(e))


if __name__ == '__main__':
    q = Queue()
    ps = [Process(target=fn, args=(q,), name=fn.__name__) for fn in (question_parser, url_generator)]
    [p.start() for p in ps]
    [p.join() for p in ps]
