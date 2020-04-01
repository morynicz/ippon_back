import datetime
import unittest

from rest_framework.test import APITestCase
from .models import Event


class EventModelTest(APITestCase):
    def setUp(self):
        start_string = '09/19/3030 13:55:26'
        end_string = '09/19/3030 13:55:26'

        registration_start = datetime.datetime.strptime(start_string, '%m/%d/%Y %H:%M:%S')
        registration_end = datetime.datetime.strptime(end_string, '%m/%d/%Y %H:%M:%S')
        self.late_event: Event = Event(
            name="Tournament",
            description="It's very cool",
            event_owner=None,
            registration_start_time=registration_start,
            registration_end_time=registration_end
        )

        start_string = '09/19/1030 13:55:26'
        end_string = '09/19/1030 13:55:26'

        registration_start = datetime.datetime.strptime(start_string, '%m/%d/%Y %H:%M:%S')
        registration_end = datetime.datetime.strptime(end_string, '%m/%d/%Y %H:%M:%S')
        self.early_event: Event = Event(
            name="Tournament",
            description="It's very cool",
            event_owner=None,
            registration_start_time=registration_start,
            registration_end_time=registration_end
        )

        start_string = '09/19/1030 13:55:26'
        end_string = '09/19/3030 13:55:26'

        registration_start = datetime.datetime.strptime(start_string, '%m/%d/%Y %H:%M:%S')
        registration_end = datetime.datetime.strptime(end_string, '%m/%d/%Y %H:%M:%S')
        self.current_event: Event = Event(
            name="Tournament",
            description="It's very cool",
            event_owner=None,
            registration_start_time=registration_start,
            registration_end_time=registration_end
        )

    def test_late_event_registration_is_open_to_be_false(self):
        self.assertEqual(self.late_event.registration_is_open(), False)

    def test_early_event_registration_is_open_to_be_false(self):
        self.assertEqual(self.early_event.registration_is_open(), False)

    def test_current_event_registration_is_open_to_be_true(self):
        self.assertEqual(self.current_event.registration_is_open(), True)
