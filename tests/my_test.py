from zhihu_fun.netlib.selenium import _get_driver, _open_question_load_more
from zhihu_fun.toollib.bs import _to_bs
from zhihu_fun.toollib.answer import _get_answers
import unittest

test_question_url = 'https://www.zhihu.com/question/27098131'


class TestZhihuFun(unittest.TestCase):
    def setUp(self):
        self.driver = _get_driver()

    def _get_page(self, url):
        self.driver.get(url)
        _open_question_load_more(self.driver)
        return self.driver.page_source

    def test_question_get(self):
        self.assertTrue(isinstance(self._get_page(test_question_url), str))
    #
    # def test_answer_get(self):
    #     bs_obj = _to_bs(self._get_page(test_question_url))
    #     self.answers = _get_answers(bs_obj)
    #     self.assertTrue(isinstance(self.answers, list))

    def tearDown(self):
        self.driver.close()
