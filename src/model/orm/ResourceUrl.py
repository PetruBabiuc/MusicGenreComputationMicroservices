from sqlalchemy import Column, Integer, String, ForeignKey

from src.model.orm.OrmUtils import Base


class ResourceUrl(Base):
    __tablename__ = 'resources_urls'

    resource_url_id = Column(Integer, primary_key=True)
    resource_url = Column(String)
    user_id = Column(Integer, ForeignKey('crawler_states.user_id'))

    def __init__(self, resource_url, user_id):
        self.resource_url = resource_url
        self.user_id = user_id
