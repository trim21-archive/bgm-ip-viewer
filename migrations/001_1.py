from playhouse.migrate import *
from bgm.models import db

migrator = MySQLMigrator(db)

# 添加了两个列，删除一个列

migrate(
    migrator.add_column('subject', 'locked', BooleanField(default=False)),
)
