from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from models.blue_device import BlueDevice

def insert_one_device(db: Session,
                      uuid: str,
                      mini_program_uuid: str):
    try:
        new_device = BlueDevice(uuid=uuid, mini_program_uuid=mini_program_uuid)
        db.add(new_device)
        db.commit()
        return True
    except IntegrityError as e:
        db.rollback()
        return False
    except Exception as e:
        db.rollback()
        raise e


def delete_device_by_id(db: Session,
                        id: int):
    try:
        delete_device = db.query(BlueDevice).filter(BlueDevice.id == id).first()
        if delete_device:
            db.delete(delete_device)
            db.commit()
            return True
        else:
            return f"ID 为 {id} 的设备不存在"
    except Exception as e:
        db.rollback()
        return False


def query_device_by_limit(db: Session,
                          current: int,
                          pageSize: int):
    if current < 1:
        current = 1
    offset = (current - 1) * pageSize
    devices = db.query(BlueDevice).offset(offset).limit(pageSize).all()
    res = {}
    if devices:
        res['count'] = len(devices)
        data = []
        for device in devices:
            tmp = {}
            tmp['id'] = device.id
            tmp['uuid'] = device.uuid
            tmp['mini_program_uuid'] = device.mini_program_uuid
            data.append(tmp)
        res['data'] = data
    return res

