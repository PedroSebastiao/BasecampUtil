"""
To-Do Events

"""

from basecampy3.endpoints._base import BasecampEndpoint, BasecampObject
from basecampy3.endpoints import util
import six


class RecordingEvent(BasecampObject):

    def __str__(self):
        try:
            return "[{action}] '{id}'".format(self.action, title=self.id)
        except Exception:
            return super(RecordingEvent, self).__str__()

    def __repr__(self):
        try:
            return "RecordingEvent('{0.id}', action={0.action})"
        except Exception:
            return super(RecordingEvent, self).__repr__()


class RecordingEvents(BasecampEndpoint):
    OBJECT_CLASS = RecordingEvent
    LIST_URL = "{base_url}/buckets/{project_id}/recordings/{recording_id}/events.json"

    def list(self, recording, project=None):
        project_id, recording_id = util.project_or_object(project, recording)
        url = self.LIST_URL.format(base_url=self.url, recording_id=recording_id, project_id=project_id)
        return self._get_list(url)

    @staticmethod
    def _normalize_date(somedate):
        """
        Take a date or datetime and turn them into the string YYYY-MM-DD. If `somedate` is None, returns an
        empty string.

        :param somedate: the date to be coerced into a YYYY-MM-DD format
        :type somedate: datetime.date|datetime.datetime|str
        :return: a string in the format YYYY-MM-DD
        :rtype: str
        """
        if somedate is None:
            return ""

        try:
            somedate = somedate.strftime("%Y-%m-%d")
        except AttributeError:
            pass

        return somedate
