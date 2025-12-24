import unittest
import script

class TestCheckUrl(unittest.TestCase):
    def test_returns_true_for_valid_https_url(self):
        self.assertTrue(script.check_url("https://www.domain.pl"))

    def test_returns_true_for_valid_http_url(self):
        self.assertTrue(script.check_url("http://www.domain.pl"))

    def test_returns_true_for_valid_url_with_port(self):
        self.assertTrue(script.check_url("https://www.domain.pl:8080"))

    def test_returns_false_when_protocol_is_missing(self):
        self.assertFalse(script.check_url("www.domain.pl"))

    def test_returns_true_for_ip_url(self):
        self.assertTrue(script.check_url("http://127.0.0.1"))

    def test_returns_false_when_text_is_not_url(self):
        self.assertFalse(script.check_url("domain"))

    def test_returns_false_when_param_is_not_str(self):
        self.assertFalse(script.check_url(2))

    def test_returns_false_when_param_is_none(self):
        self.assertFalse(script.check_url(None))

    def test_returns_false_when_param_is_empty_str(self):
        self.assertFalse(script.check_url(""))


if __name__ == '__main__':
    unittest.main()
