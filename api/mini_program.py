from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from models.mini_program import MiniProgram


def get_mini_program_by_uuid(db: Session,
                             uuid: str,
                             state: str):
    mini_program = db.query(MiniProgram).filter(MiniProgram.uuid == uuid,
                                                MiniProgram.state == state).first()
    program_detail = {}
    if mini_program:
        program_detail['uuid'] = mini_program.uuid
        program_detail['icon'] = mini_program.icon
        program_detail['device_uuid'] = mini_program.device_uuid
        program_detail['state'] = mini_program.state
        program_detail['version_code'] = mini_program.version_code
        program_detail['version_name'] = mini_program.version_name
        program_detail['create_time'] = mini_program.create_time
        program_detail['update_time'] = mini_program.update_time
    return program_detail


def get_mini_program_by_device_uuid(db: Session,
                                    device_uuid: str,
                                    state: str):
    mini_program = db.query(MiniProgram).filter(MiniProgram.device_uuid == device_uuid,
                                                MiniProgram.state == state).first()
    program_detail = {}
    if mini_program:
        program_detail['uuid'] = mini_program.uuid
        program_detail['icon'] = mini_program.icon
        program_detail['device_uuid'] = mini_program.device_uuid
        program_detail['state'] = mini_program.state
        program_detail['version_code'] = mini_program.version_code
        program_detail['version_name'] = mini_program.version_name
        program_detail['create_time'] = mini_program.create_time
        program_detail['update_time'] = mini_program.update_time
    return program_detail


def get_mini_program_by_state(db: Session,
                              state: str):
    mini_programs = db.query(MiniProgram).filter(MiniProgram.state == state).all()
    program_detail_list = []
    if mini_programs:
        for program in mini_programs:
            program_detail = {}
            program_detail['uuid'] = program.uuid
            program_detail['icon'] = program.icon
            program_detail['device_uuid'] = program.device_uuid
            program_detail['state'] = program.state
            program_detail['version_code'] = program.version_code
            program_detail['version_name'] = program.version_name
            program_detail['create_time'] = program.create_time
            program_detail['update_time'] = program.update_time
            program_detail_list.append(program_detail)
    return program_detail_list


def get_mini_program_uuid_by_device_uuid(db: Session,
                              device_uuid: str):
    mini_program = db.query(MiniProgram).filter(MiniProgram.device_uuid == device_uuid).first()
    if mini_program:
        return mini_program.uuid
    else:
        return None


def insert_one_mini_program(db: Session,
               uuid: str,
               icon: str,
               device_uuid: str):

    try:
        new_program = MiniProgram(uuid=uuid, icon=icon, device_uuid=device_uuid)
        db.add(new_program)
        db.commit()
        return True
    except IntegrityError as e:
        db.rollback()
        return False
    except Exception as e:
        db.rollback()
        raise e


def delete_program_by_uuid(db: Session,
               uuid: str):
    try:
        delete_program = db.query(MiniProgram).filter(MiniProgram.uuid == uuid).first()
        if delete_program:
            db.delete(delete_program)
            db.commit()
            return True
    except:
        db.rollback()