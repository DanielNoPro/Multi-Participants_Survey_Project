# Generated by Django 3.2.23 on 2024-01-13 15:33

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("surveys", "0005_alter_answer_unique_together"),
    ]

    operations = [
        migrations.RunSQL(
            """
CREATE OR REPLACE FUNCTION public.get_survey_answer_statistics(
	IN survey_id_input bigint, 
	IN question_id_input bigint
)
    RETURNS table (
		option_content text,
		text_content text,
		frequency bigint
	) 
    LANGUAGE 'plpgsql'
AS $BODY$
begin
	return query 
		SELECT 
			sqo.content AS option_content, 
			sa.content AS text_content,
			COUNT(*) AS frequency
		FROM public.surveys_answer sa
			FULL OUTER JOIN public.surveys_questionoption AS sqo ON sqo.id = sa.option_id
		WHERE sa.question_id=question_id_input AND sa.survey_id=survey_id_input
		GROUP BY 
			sa.content,
			sqo.id;
end;$BODY$;"""
        )
    ]
