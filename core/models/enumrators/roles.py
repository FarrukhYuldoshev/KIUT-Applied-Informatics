import enum


class Roles(enum.Enum):
    head_of_the_department = "Head of the department"
    professor = "Professor"
    associate_professor = "Associate professor"
    senior_lecturer = "Senior Lecturer"
    teacher = "Teacher"
    staff = "Staff"


class RolesRate(enum.Enum):
    head_of_the_department = 1
    professor = 2
    associate_professor = 3
    senior_lecturer = 4
    teacher = 5
    staff = 6


# role_level_order = case( # CASE operatorini yaratish
#     (User.role_name == RoleLevel.HEAD_OF_DEPARTMENT.role_name, RoleLevel.HEAD_OF_DEPARTMENT.level), # Agar role_name 'Head Of Department' bo'lsa, daraja 1
#     (User.role_name == RoleLevel.PROFESSOR.role_name, RoleLevel.PROFESSOR.level), # Agar role_name 'Professor' bo'lsa, daraja 2
#     (User.role_name == RoleLevel.STAFF.role_name, RoleLevel.STAFF.level), # Agar role_name 'Staff' bo'lsa, daraja 3
#     else_=4  # Boshqa rollar uchun default daraja (agar kerak bo'lsa)
