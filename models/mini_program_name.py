from sqlalchemy import Column, Integer, String, TIMESTAMP, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class MiniProgramName(Base):
    __tablename__ = 'mini_program_name'

    id = Column(Integer, primary_key=True, autoincrement=True)
    # mini_program_uuid = Column(String(32), ForeignKey('mini_program.uuid', ondelete='CASCADE', onupdate='CASCADE'), index=True)
    mini_program_uuid = Column(String(32), index=True)
    lang = Column(String(5))
    name = Column(String(30))
    create_time = Column(TIMESTAMP, server_default='CURRENT_TIMESTAMP')
    update_time = Column(TIMESTAMP, server_default='CURRENT_TIMESTAMP', server_onupdate='CURRENT_TIMESTAMP')

