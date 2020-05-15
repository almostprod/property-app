{% macro grant_select_on_schemas(
        schemas,
        group
    ) %}
    {% if target.name == 'ci' %}
        {% for schema in schemas %}
            grant usage
            on schema {{ schema }} to group {{ group }};
grant
        select
            on all tables in schema {{ schema }} to group {{ group }};
alter default privileges in schema {{ schema }} grant
        select
            on tables to group {{ group }};
grant usage,
        select
            on all sequences in schema {{ schema }} to group {{ group }};
alter default privileges in schema {{ schema }} grant usage,
        select
            on sequences to group {{ group }};
        {% endfor %}
    {% endif %}
{% endmacro %}
