from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0021_alter_settings_options_alter_employeeuser_fio'),
    ]

    operations = [
        migrations.RunSQL(
            """
            CREATE OR REPLACE FUNCTION check_singleton_id()
            RETURNS trigger AS $$
            BEGIN
                -- Запрет вставлять id != 1
                IF TG_OP = 'INSERT' AND NEW.id <> 1 THEN
                    RAISE EXCEPTION 'Only one Settings record allowed with id = 1';
                END IF;

                -- Запрет менять id при обновлении
                IF TG_OP = 'UPDATE' AND OLD.id <> NEW.id THEN
                    RAISE EXCEPTION 'Cannot change the ID of the Settings record';
                END IF;

                RETURN NEW;
            END;
            $$ LANGUAGE plpgsql;
            """,
            reverse_sql="""
            DROP FUNCTION IF EXISTS check_singleton_id();
            """
        ),
        migrations.RunSQL(
            """
            CREATE OR REPLACE FUNCTION prevent_singleton_delete()
            RETURNS trigger AS $$
            DECLARE
                rec_count INTEGER;
            BEGIN
                -- Проверяем, что в таблице ровно одна запись
                SELECT COUNT(*) INTO rec_count FROM main_settings;
                IF rec_count = 1 THEN
                    RAISE EXCEPTION 'Deleting the only Settings record is not allowed';
                END IF;
                RETURN OLD;
            END;
            $$ LANGUAGE plpgsql;
            """,
            reverse_sql="""
            DROP FUNCTION IF EXISTS prevent_singleton_delete();
            """
        ),
        migrations.RunSQL(
            """
            DO $$
            BEGIN
                IF NOT EXISTS (
                    SELECT 1 FROM pg_trigger WHERE tgname = 'enforce_singleton_id'
                ) THEN
                    CREATE TRIGGER enforce_singleton_id
                    BEFORE INSERT OR UPDATE ON main_settings
                    FOR EACH ROW EXECUTE FUNCTION check_singleton_id();
                END IF;
            END;
            $$;

            DO $$
            BEGIN
                IF NOT EXISTS (
                    SELECT 1 FROM pg_trigger WHERE tgname = 'prevent_singleton_delete'
                ) THEN
                    CREATE TRIGGER prevent_singleton_delete
                    BEFORE DELETE ON main_settings
                    FOR EACH ROW EXECUTE FUNCTION prevent_singleton_delete();
                END IF;
            END;
            $$;
            """,
            reverse_sql="""
            DROP TRIGGER IF EXISTS enforce_singleton_id ON main_settings;
            DROP TRIGGER IF EXISTS prevent_singleton_delete ON main_settings;
            """
        ),
    ]
