from sqlalchemy import Column, String, Text, Integer, DateTime

from modules.persistence import Base, getModelBase

ModelBase = getModelBase('poem')


class Poem(Base, ModelBase):
    submitted_by = Column(String(255))
    submitted_time = Column(DateTime)
    poem_type = Column(String(25))
    deletion_key = Column(String(25))
    content = Column(Text)
    times_served = Column(Integer, default=0)
    last_served = Column(DateTime)

    def get_display_message(self, include_deletion_key=False):
        deletion_message = ''
        if include_deletion_key:
            deletion_message = ' (Deletion Key: {})'.format(self.deletion_key)

        return '{} -- submitted by {}{}'.format(
            self.content,
            self.submitted_by,
            deletion_message
        )
