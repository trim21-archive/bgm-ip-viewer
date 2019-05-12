import json

import peewee
import peewee as pw

import bgm.settings


class MyJSONField(pw.TextField):
    def python_value(self, value):
        if value is not None:
            try:
                return json.loads(value)
            except (TypeError, ValueError):
                return value

    def db_value(self, value):
        if value is not None:
            return json.dumps(value)


db = peewee.MySQLDatabase(
    bgm.settings.MYSQL_DBNAME,
    host=bgm.settings.MYSQL_HOST,
    charset='utf8mb4',
    user=bgm.settings.MYSQL_USER,
    password=bgm.settings.MYSQL_PASSWORD,
)


class S:
    class BgmIpViewer(pw.Model):
        class Meta:
            database = db


class Subject(S.BgmIpViewer):
    id = pw.IntegerField(primary_key=True, index=True)
    name = pw.CharField()
    image = pw.CharField()
    subject_type = pw.CharField()
    name_cn = pw.CharField()
    locked = pw.BooleanField(default=False)

    tags = pw.TextField()
    info = MyJSONField()
    score_details = MyJSONField()

    score = pw.CharField()
    wishes = pw.IntegerField(default=0)
    done = pw.IntegerField(default=0)
    doings = pw.IntegerField(default=0)
    on_hold = pw.IntegerField(default=0)
    dropped = pw.IntegerField(default=0)

    map = pw.IntegerField(index=True, default=0)


class Relation(S.BgmIpViewer):
    id = pw.CharField(primary_key=True, index=True)
    relation = pw.CharField()
    source = pw.IntegerField()
    target = pw.IntegerField()
    map = pw.IntegerField(index=True, default=0)
    removed = pw.BooleanField(default=False)
    pass

    @classmethod
    def get_relation_of_subject(cls, subject_id):
        return cls.select().where(((cls.source == subject_id)
                                   | (cls.target == subject_id))
                                  & (cls.removed == 0))


class Tag(S.BgmIpViewer):
    subject_id = pw.IntegerField(primary_key=True)
    text = pw.FixedCharField(max_length=32)
    count = pw.IntegerField()


class LongTextField(pw._StringField):
    field_type = 'LONGTEXT'


class SubjectJson(S.BgmIpViewer):
    id = pw.IntegerField(primary_key=True, index=True)
    info = LongTextField()


class Map(S.BgmIpViewer):
    id = pw.AutoField(primary_key=True)


class Topic(S.BgmIpViewer):
    id = pw.IntegerField()


Subject.create_table()
Relation.create_table()
SubjectJson.create_table()
Tag.create_table()
Map.create_table()
if __name__ == '__main__':
    Relation.get_relation_of_subject()
