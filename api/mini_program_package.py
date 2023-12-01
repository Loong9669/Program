from sqlalchemy.orm import Session
from models.mini_program_package import MiniProgramPackage


def get_mini_program_package_by_uuid(db: Session,
                                  uuid: str):
    mini_program_package = db.query(MiniProgramPackage).filter(MiniProgramPackage.mini_program_uuid == uuid).first()
    package = {}
    if mini_program_package:
        package['h5_download_url'] = mini_program_package.h5_download_url
        package['control_page'] = mini_program_package.control_page
        package['setting_page'] = mini_program_package.setting_page
    return package

