from sqlalchemy import Column, String, Integer, TIMESTAMP, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class BlueDevice(Base):
    __tablename__ = 'blue_device'

    id = Column(Integer, primary_key=True, autoincrement=True)
    uuid = Column(String(32), nullable=True, comment='蓝牙设备的唯一 id，对应蓝牙名称')
    mini_program_uuid = Column(String(32), nullable=True, comment='对应的子程序的 uuid')
    create_time = Column(TIMESTAMP, server_default='CURRENT_TIMESTAMP', comment='创建时间')
    update_time = Column(
        TIMESTAMP, server_default='CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP', comment='更新时间'
    )
