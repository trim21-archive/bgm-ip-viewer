from bgm.models import db
from peewee_migrate import Router

router = Router(db)

# Create migration
router.create('create_database')

# Run migration/migrations
router.run('bgm.models')

# Run all unapplied migrations
router.run(fake=True)
