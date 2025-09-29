from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0019_alter_option_option_kg_alter_question_question_kg'),
    ]

    operations = [
        migrations.RunSQL(
            """
            CREATE OR REPLACE FUNCTION check_singleton_id()
            RETURNS trigger AS $$
            BEGIN
                IF NEW.id <> 1 THEN
                    RAISE EXCEPTION 'Only one Settings record allowed with id = 1';
                END IF;
                RETURN NEW;
            END;
            $$ LANGUAGE plpgsql;
            """,
            reverse_sql="DROP FUNCTION IF EXISTS check_singleton_id();"
        ),
        migrations.RunSQL(
            """
            DO $$
            BEGIN
                IF NOT EXISTS (
                    SELECT 1 FROM pg_trigger WHERE tgname = 'enforce_singleton_id'
                ) THEN
                    CREATE TRIGGER enforce_singleton_id
                    BEFORE INSERT ON main_settings
                    FOR EACH ROW EXECUTE FUNCTION check_singleton_id();
                END IF;
            END;
            $$;
            """,
            reverse_sql="""
            DROP TRIGGER IF EXISTS enforce_singleton_id ON main_settings;
            """
        ),
    ]

