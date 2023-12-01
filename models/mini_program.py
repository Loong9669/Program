from sqlalchemy import Column, Integer, String, Text, TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class MiniProgram(Base):
    __tablename__ = 'mini_program'

    uuid = Column(String(32), primary_key=True, comment='子程序的 id，32 位 uuid，对应二维码')
    icon = Column(Text, comment='子程序图标地址')
    device_uuid = Column(String(50), comment='蓝牙设备的 uuid，可以获取到对应的子程序类型')
    state = Column(String(15), nullable=False, default='preview', comment='子程序状态preview/release')
    version_code = Column(Integer, comment='版本 code')
    version_name = Column(String(30), comment='版本名称')
    create_time = Column(TIMESTAMP, server_default='CURRENT_TIMESTAMP', comment='创建时间')
    update_time = Column(
        TIMESTAMP, server_default='CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP', comment='更新时间'
    )

