import datetime
from rest_framework.test import APITestCase

import ippon.models.event as em


class EventModelTest(APITestCase):
    def setUp(self):
        self.late_event = self.configure_event("09/19/3030 13:55:26", "09/19/3030 13:55:26")
        self.early_event = self.configure_event("09/19/1030 13:55:26", "09/19/1030 13:55:26")
        self.current_event = self.configure_event("09/19/1030 13:55:26", "09/19/3030 13:55:26")

    @staticmethod
    def configure_event(start_string, end_string):
        registration_start = datetime.datetime.strptime(start_string, "%m/%d/%Y %H:%M:%S")
        registration_end = datetime.datetime.strptime(end_string, "%m/%d/%Y %H:%M:%S")
        event: em.Event = em.Event(
            name="Tournament",
            description="It's very cool",
            registration_start_time=registration_start,
            registration_end_time=registration_end,
        )
        return event

    def test_late_event_registration_is_open_to_be_false(self):
        self.assertEqual(self.late_event.registration_is_open, False)

    def test_early_event_registration_is_open_to_be_false(self):
        self.assertEqual(self.early_event.registration_is_open, False)

    def test_current_event_registration_is_open_to_be_true(self):
        self.assertEqual(self.current_event.registration_is_open, True)
