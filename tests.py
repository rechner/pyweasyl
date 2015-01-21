#!/usr/bin/env python
# So far can only test unauthenticated API actions

import unittest
from weasyl import Weasyl

# A list of all the version numbers reported by Weasyl known to work
# with this API binding:    <`0`>
SUPPORTED_VERSIONS = ('c759381', 'cc4630e')

class TestWeasylAPI(unittest.TestCase):
    def setUp(self):
        self.api = Weasyl()
        pass

    def test_version(self):
        self.assertTrue(self.api.version() in SUPPORTED_VERSIONS)

    def test_avatar(self):
        self.assertEquals(self.api.useravatar('rechner'),
                          'https://www.weasyl.com/~rechner/avatar')

    def test_session_unsigned(self):
        try:
            self.api.whoami()
        except Weasyl.Unauthorized as e:
            self.assertEquals(e.error, 'Session unsigned')

        try:
            self.api.message_submissions()
        except Weasyl.Unauthorized as e:
            self.assertEquals(e.error, 'Session unsigned')

        try:
            self.api.message_summary()
        except Weasyl.Unauthorized as e:
            self.assertEquals(e.error, 'Session unsigned')

    def test_submission_exists(self):
        submission = self.api.view_submission(602979)
        self.assertGreater(len(submission['media']), 0)
        self.assertEquals(submission['posted_at'], '2014-05-13T04:24:35+00:00Z')
        self.assertEquals(submission['rating'], 'general')
        self.assertEquals(submission['submitid'], 602979)
        self.assertEquals(submission['subtype'], 'visual')
        self.assertTrue('secret_societies' in submission['tags'])
        self.assertGreaterEqual(submission['views'], 3)

    def test_submission_dne(self):
        try:
            self.api.view_submission(999999)
        except Weasyl.Forbidden as e:
            self.assertEquals(e.error, 'submissionRecordMissing')

    def test_rating_exceeded(self):
        try:
            self.api.view_submission(735256)
        except Weasyl.Forbidden as e:
            self.assertEquals(e.error, 'RatingExceeded')

    def test_frontpage(self):
        page = self.api.frontpage(count=10)
        self.assertEquals(len(page), 10)
        self.assertTrue('rating' in page[0].keys())
        self.assertTrue('media' in page[0].keys())
        self.assertTrue('owner' in page[0].keys())
        self.assertTrue('submitid' in page[0].keys())

    def test_view_user(self):
        user = self.api.view_user('rechner')
        self.assertEquals(user['created_at'], '2014-05-03T02:20:29Z')
        self.assertFalse(user['suspended'])
        self.assertGreater(len(user['recent_submissions']), 0)

    def test_user_gallery(self):
        gallery = self.api.user_gallery('rechner')
        self.assertTrue('backid' in gallery.keys())
        self.assertTrue('nextid' in gallery.keys())
        self.assertTrue('submissions' in gallery.keys())
        self.assertGreater(len(gallery['submissions']), 0)
        self.assertTrue('rating' in gallery['submissions'][0].keys())


if __name__ == '__main__':
    unittest.main()
