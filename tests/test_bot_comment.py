import pytest
import responses

from instabot.api.config import API_URL

from .test_bot import TestBot
from .test_variables import TEST_CAPTION_ITEM, TEST_COMMENT_ITEM, TEST_PHOTO_ITEM, TEST_USERNAME_INFO_ITEM

try:
    from unittest.mock import patch
except ImportError:
    from mock import patch


class TestBotGet(TestBot):
    @responses.activate
    @pytest.mark.parametrize(
        "blocked_actions_protection,blocked_actions",
        [(True, True), (True, False), (False, True), (False, False)],
    )
    @patch("time.sleep", return_value=None)
    def test_comment_feedback(
        self, patched_time_sleep, blocked_actions_protection, blocked_actions
    ):
        self.bot.blocked_actions_protection = blocked_actions_protection
        self.bot.blocked_actions["comments"] = blocked_actions
        media_id = 1234567890
        comment_txt = "Yeah great!"

        TEST_COMMENT_ITEM["user"]["pk"] = self.bot.user_id + 1

        results = 3
        response_data = {
            "caption": TEST_CAPTION_ITEM,
            "caption_is_edited": False,
            "comment_count": results,
            "comment_likes_enabled": True,
            "comments": [TEST_COMMENT_ITEM for _ in range(results)],
            "has_more_comments": False,
            "has_more_headload_comments": False,
            "media_header_display": "none",
            "preview_comments": [],
            "status": "ok",
        }
        responses.add(
            responses.GET,
            "{api_url}media/{media_id}/comments/?".format(
                api_url=API_URL, media_id=media_id
            ),
            json=response_data,
            status=200,
        )

        response_data = {
            "message": "feedback_required",
            "spam": True,
            "feedback_title": "Sorry, this feature isn't available right now",
            "feedback_message": "An error occurred while processing this " +
            "request. Please try again later. We restrict certain content " +
            "and actions to protect our community. Tell us if you think we " +
            "made a mistake.",
            "feedback_url": "repute/report_problem/instagram_comment/",
            "feedback_appeal_label": "Report problem",
            "feedback_ignore_label": "OK",
            "feedback_action": "report_problem",
            "status": "fail",
        }
        responses.add(
            responses.POST,
            "{api_url}media/{media_id}/comment/".format(
                api_url=API_URL, media_id=media_id
            ),
            json=response_data,
            status=400,
        )

        assert not self.bot.comment(media_id, comment_txt)

    @responses.activate
    @pytest.mark.parametrize(
        "blocked_actions_protection,blocked_actions",
        [(True, False), (False, False)]
    )
    @patch("time.sleep", return_value=None)
    def test_comment(
        self, patched_time_sleep, blocked_actions_protection, blocked_actions
    ):
        self.bot.blocked_actions_protection = blocked_actions_protection
        self.bot.blocked_actions["comments"] = blocked_actions
        media_id = 1234567890
        comment_txt = "Yeah great!"

        TEST_COMMENT_ITEM["user"]["pk"] = self.bot.user_id + 1

        results = 3
        response_data = {
            "caption": TEST_CAPTION_ITEM,
            "caption_is_edited": False,
            "comment_count": results,
            "comment_likes_enabled": True,
            "comments": [TEST_COMMENT_ITEM for _ in range(results)],
            "has_more_comments": False,
            "has_more_headload_comments": False,
            "media_header_display": "none",
            "preview_comments": [],
            "status": "ok",
        }
        responses.add(
            responses.GET,
            "{api_url}media/{media_id}/comments/?".format(
                api_url=API_URL, media_id=media_id
            ),
            json=response_data,
            status=200,
        )

        response_data = {"status": "ok"}
        responses.add(
            responses.POST,
            "{api_url}media/{media_id}/comment/".format(
                api_url=API_URL, media_id=media_id
            ),
            json=response_data,
            status=200,
        )

        assert self.bot.comment(media_id, comment_txt)

    @responses.activate
    @pytest.mark.parametrize(
        "blocked_actions_protection,blocked_actions",
        [(True, False), (False, False)]
    )
    @pytest.mark.parametrize("comment_txt",
                             ["Yeah!", "@test_user Yeah!", "@dude Yeah!"])
    @pytest.mark.parametrize("max_per_day", [0, 10])
    @patch("time.sleep", return_value=None)
    def test_reply_to_comment(
            self, patched_time_sleep,
            blocked_actions_protection, blocked_actions,
            comment_txt, max_per_day
    ):
        self.bot.blocked_actions_protection = blocked_actions_protection
        self.bot.blocked_actions["comments"] = blocked_actions
        media_id = 1234567890
        comment_txt = comment_txt
        self.bot.max_per_day["comments"] = max_per_day

        TEST_COMMENT_ITEM["user"]["pk"] = self.bot.user_id + 1

        results = 3
        response_data = {
            "caption": TEST_CAPTION_ITEM,
            "caption_is_edited": False,
            "comment_count": results,
            "comment_likes_enabled": True,
            "comments": [TEST_COMMENT_ITEM for _ in range(results)],
            "has_more_comments": False,
            "has_more_headload_comments": False,
            "media_header_display": "none",
            "preview_comments": [],
            "status": "ok",
        }
        parent_comment_id = response_data["comments"][0]["pk"]

        responses.add(
            responses.GET,
            "{api_url}media/{media_id}/comments/?".format(
                api_url=API_URL, media_id=media_id,
            ),
            json=response_data,
            status=200,
        )

        responses.add(
            responses.POST,
            "{api_url}media/{media_id}/comment/".format(
                api_url=API_URL, media_id=media_id
            ),
            json={"status": "ok"},
            status=200,
        )

        responses.add(
            responses.GET,
            "{api_url}media/{media_id}/info/".format(
                api_url=API_URL, media_id=media_id
            ),
            json={
                "auto_load_more_enabled": True,
                "num_results": 1,
                "status": "ok",
                "more_available": False,
                "items": [TEST_PHOTO_ITEM],
            },
            status=200,
        )

        responses.add(
            responses.GET,
            "{api_url}users/{user_id}/info/".format(
                api_url=API_URL,
                user_id=19
            ),
            status=200,
            json={"status": "ok", "user": TEST_USERNAME_INFO_ITEM},
        )

        if comment_txt == "@dude Yeah!" and max_per_day != 0:
            assert self.bot.reply_to_comment(
                media_id, comment_txt, parent_comment_id)
        else:
            assert not self.bot.reply_to_comment(
                media_id, comment_txt, parent_comment_id)

    @responses.activate
    @pytest.mark.parametrize(
        "is_commented, expected", [(True, True), (False, False)]
    )
    @patch("time.sleep", return_value=None)
    def test_is_commented(
            self, patched_time_sleep, is_commented, expected
    ):
        media_id = 1234567890

        if is_commented is True:
            TEST_COMMENT_ITEM["user"]["pk"] = self.bot.user_id
        else:
            TEST_COMMENT_ITEM["user"]["pk"] = self.bot.user_id + 1

        results = 3
        response_data = {
            "caption": TEST_CAPTION_ITEM,
            "caption_is_edited": False,
            "comment_count": results,
            "comment_likes_enabled": True,
            "comments": [TEST_COMMENT_ITEM for _ in range(results)],
            "has_more_comments": False,
            "has_more_headload_comments": False,
            "media_header_display": "none",
            "preview_comments": [],
            "status": "ok",
        }
        responses.add(
            responses.GET,
            "{api_url}media/{media_id}/comments/?".format(
                api_url=API_URL, media_id=media_id
            ),
            json=response_data,
            status=200,
        )

        assert self.bot.is_commented(media_id) == expected

    @responses.activate
    @pytest.mark.parametrize(
        "has_comments, expected", [(True, True), (False, False)]
    )
    @patch("time.sleep", return_value=None)
    def test_has_comments(
            self, patched_time_sleep, has_comments, expected
    ):
        media_id = 1234567890

        comments = []
        if has_comments is True:
            comments = [TEST_COMMENT_ITEM for _ in range(3)]

        response_data = {
            "caption": TEST_CAPTION_ITEM,
            "caption_is_edited": False,
            "comment_count": 3,
            "comment_likes_enabled": True,
            "comments": comments,
            "has_more_comments": False,
            "has_more_headload_comments": False,
            "media_header_display": "none",
            "preview_comments": [],
            "status": "ok",
        }
        responses.add(
            responses.GET,
            "{api_url}media/{media_id}/comments/?".format(
                api_url=API_URL, media_id=media_id
            ),
            json=response_data,
            status=200,
        )

        assert self.bot.has_comments(media_id) == expected

    '''@responses.activate
    @pytest.mark.parametrize(
        "blocked_actions_protection,blocked_actions",
        [(True, False), (False, False)]
    )
    @pytest.mark.parametrize("max_per_day", [0, 10])
    @patch("time.sleep", return_value=None)
    def test_comment_medias(
            self, patched_time_sleep,
            blocked_actions_protection, blocked_actions, max_per_day
    ):
        self.bot.blocked_actions_protection = blocked_actions_protection
        self.bot.blocked_actions["comments"] = blocked_actions
        media_ids = [12345678901, 12345678902]
        self.bot.max_per_day["comments"] = max_per_day

        #TEST_COMMENT_ITEM["user"]["pk"] = self.bot.user_id + 1

        results = 3
        response_data = {
            "caption": TEST_CAPTION_ITEM,
            "caption_is_edited": False,
            "comment_count": results,
            "comment_likes_enabled": True,
            "comments": [TEST_COMMENT_ITEM for _ in range(results)],
            "has_more_comments": False,
            "has_more_headload_comments": False,
            "media_header_display": "none",
            "preview_comments": [],
            "status": "ok",
        }

        # get comment
        responses.add(
            responses.GET,
            "{api_url}media/{media_id}/comments/?".format(
                api_url=API_URL, media_id=media_ids[0],
            ),
            json=response_data,
            status=200,
        )
        responses.add(
            responses.GET,
            "{api_url}media/{media_id}/comments/?".format(
                api_url=API_URL, media_id=media_ids[1],
            ),
            json=response_data,
            status=200,
        )

        #post comment
        responses.add(
            responses.POST,
            "{api_url}media/{media_id}/comment/".format(
                api_url=API_URL, media_id=media_ids[0]
            ),
            json={"status": "ok"},
            status=200,
        )
        responses.add(
            responses.POST,
            "{api_url}media/{media_id}/comment/".format(
                api_url=API_URL, media_id=media_ids[1]
            ),
            json={"status": "ok"},
            status=200,
        )

        # get media infos
        TEST_PHOTO_ITEM["like_count"] = 80
        responses.add(
            responses.GET,
            "{api_url}media/{media_id}/info/".format(
                api_url=API_URL, media_id=media_ids[0]
            ),
            json={
                "auto_load_more_enabled": True,
                "num_results": 1,
                "status": "ok",
                "more_available": False,
                "items": [TEST_PHOTO_ITEM],
            },
            status=200,
        )
        responses.add(
            responses.GET,
            "{api_url}media/{media_id}/info/".format(
                api_url=API_URL, media_id=media_ids[1]
            ),
            json={
                "auto_load_more_enabled": True,
                "num_results": 1,
                "status": "ok",
                "more_available": False,
                "items": [TEST_PHOTO_ITEM],
            },
            status=200,
        )

        responses.add(
            responses.GET,
            "{api_url}users/{user_id}/info/".format(
                api_url=API_URL, user_id=19),
            json={
                "status": "ok",
                "user": TEST_USERNAME_INFO_ITEM,
            },
            status=200,
        )

        #print(self.bot.comment_medias(media_ids))
        if self.bot.max_per_day["comments"] > 0:
            assert self.bot.comment_medias(media_ids) == []
        else:
            assert self.bot.comment_medias(media_ids) == media_ids'''
