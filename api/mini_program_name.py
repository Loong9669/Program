from sqlalchemy.orm import Session
from models.mini_program_name import MiniProgramName


def get_mini_program_name_by_uuid(db: Session,
                                  uuid: str):
    mini_program_name = db.query(MiniProgramName).filter(MiniProgramName.mini_program_uuid == uuid).all()
    names = {}
    if mini_program_name:
        for row in mini_program_name:
            names[row.lang] = row.name
    return names

def insert_one_program_name(db: Session,
                            uuid: str,
                            names: list):
    try:
        for row in names:
            lang = row.get('lang')
            name = row.get('name')
            program_name = MiniProgramName(mini_program_uuid=uuid, lang=lang, name=name)

            db.add(program_name)
            db.commit()
        return True
    except Exception as e:
        print(e)
        db.rollback()
        return False

def delete_program_name_by_uuid(db: Session,
                           uuid: str):
    try:
        delete_names = db.query(MiniProgramName).filter(MiniProgramName.uuid == uuid).all()
        if delete_names:
            db.delete(delete_names)
            db.commit()
    except:
        db.rollback()


