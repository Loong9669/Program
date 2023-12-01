from sqlalchemy import Column, String, Integer, TIMESTAMP, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class BlueDevice(Base):
    __tablename__ = 'blue_device'

    id = Column(Integer, primary_key=True, autoincrement=True)
    uuid = Column(String(32), nullable=True, comment='蓝牙设备的唯一 id，对应蓝牙名称')
    mini_program_uuid = Column(String(32), nullable=True, comment='对应的子程序的 uuid')
    create_time = Column(TIMESTAMP, nullable=True, server_default=None)
    update_time = Column(TIMESTAMP, nullable=True, server_default=None, onupdate=TIMESTAMP)
