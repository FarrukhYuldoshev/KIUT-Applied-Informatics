import enum


class DegreesEn(str, enum.Enum):
    Bsc = "Bachelor's Degree"
    Dsc = "Doctor of Science"
    Phd = "Doctor of Philosophy"
    Msc = "Master of Science"


class DegreesRu(str, enum.Enum):
    Bsc = "Бакалавр (Степень бакалавра)"
    Msc = "Магистр (Степень магистра)"
    Phd = "Доктор философии"
    Dsc = "Доктор наук"


class DegreesUz(str, enum.Enum):
    Bsc = "Bakalavr (Bakalavr darajasi)"
    Msc = "Magistr (Magistr darajasi)"
    Phd = "Falsafa doktori"
    Dsc = "Fan doktori"


combined_values = (
    [member.value for member in DegreesUz]
    + [member.value for member in DegreesRu]
    + [member.value for member in DegreesEn]
)
Degrees = enum.Enum("Degrees", {value: value for value in combined_values}, type=str)
