"""
This command is responsible for updating the state of meetings
based on the defined rules. This rules are partially documented
on apps.meetings.states module.
"""
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils.timezone import now
from django.db.models import Q, F

from apps.meetings.models import Meeting
from apps.profiles.models import User


class Command(BaseCommand):
    help = 'Updates meeting state.'

    def handle(self, *args, **kwargs):
        # 1. flag all reserved or confirmed meetings after 1 hr
        #    of datetime as waiting_reply
        used_meetings = Meeting.objects.filter(
            Q(state='reserved') | Q(state='confirmed'))

        for meeting in used_meetings:
            if meeting.is_in_past():
                trans_name = 'flag_waiting_reply_{}'.format(meeting.state)
                meeting.get_state_info().make_transition(trans_name)
                # TODO: send 'how was your meeting email'


        # 2. flag unused meetings
        unused_meetings = Meeting.objects.filter(state='available')

        for meeting in unused_meetings:
            if meeting.is_in_past():
                meeting.get_state_info().make_transition('flag_unused')


        # 3. create meetings for all users
        users = User.objects.filter(is_active=True)

        for u in users:
            u.create_meeting_slot()
            # TODO: send tweet saying meeting created
            # TODO: send email to followers


