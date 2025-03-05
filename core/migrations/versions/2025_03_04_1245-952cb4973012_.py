"""empty message

Revision ID: 952cb4973012
Revises: 88d6e15b55bd
Create Date: 2025-03-04 12:45:43.779416

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "952cb4973012"
down_revision: Union[str, None] = "88d6e15b55bd"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Error code 23505 bu UniqueViolationError bo'ladi
    op.execute(
        """
        CREATE OR REPLACE FUNCTION check_unique_research_interest()
        RETURNS TRIGGER AS $$
        BEGIN
          IF (
            (NEW.translations ? 'uz' AND EXISTS (
              SELECT 1 FROM research_interests
              WHERE translations ? 'uz'
                AND translations->'uz'->>'title' = NEW.translations->'uz'->>'title'
            ))
            OR
            (NEW.translations ? 'ru' AND EXISTS (
              SELECT 1 FROM research_interests
              WHERE translations ? 'ru'
                AND translations->'ru'->>'title' = NEW.translations->'ru'->>'title'
            ))
            OR
            (NEW.translations ? 'en' AND EXISTS (
              SELECT 1 FROM research_interests
              WHERE translations ? 'en'
                AND translations->'en'->>'title' = NEW.translations->'en'->>'title'
            ))
          ) THEN
            RAISE EXCEPTION 'Dublicate keys error!!'
            USING ERRCODE = '23505';
          END IF;
          RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """
    )
    op.execute(
        """
    CREATE TRIGGER trigger_check_unique_research_interest
    BEFORE INSERT OR UPDATE ON research_interests
    FOR EACH ROW EXECUTE FUNCTION check_unique_research_interest();
    """
    )

    op.execute(
        """CREATE UNIQUE INDEX uniq_research_interests_titles
            ON research_interests (
            (translations->'uz'->>'title'),
            (translations->'ru'->>'title'),
            (translations->'en'->>'title')
            );"""
    )


def downgrade():
    op.execute(
        "DROP TRIGGER IF EXISTS trigger_check_unique_research_interest ON research_interests;"
    )
    op.execute("DROP FUNCTION IF EXISTS check_unique_research_interest;")
    op.execute("DROP INDEX IF EXISTS uniq_research_interests_titles;")
