from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text


Base = declarative_base()


class Notification(Base):
    """
    A notification received from the EVE API.

    Each row collects the information from char/Notifications and
    char/NotificationTexts APIs.
    """

    __tablename__ = 'notification'

    # autoincrement; can store this value as a cursor to track seen rows
    sequence_id = Column(Integer, primary_key=True)

    # A character we saw this notification on. Multiple characters can receive
    # the same notification, this will just keep one of them.
    recip_id = Column(Integer, nullable=False)

    # from char/Notifications
    notif_id = Column(Integer, nullable=False, index=True, unique=True)
    type = Column(Integer, nullable=False)
    sender_id = Column(Integer, nullable=False)
    sender_name = Column(String, nullable=False)
    sent_date = Column(DateTime, nullable=False)

    # from char/NotificationTexts
    text = Column(Text, nullable=False)
