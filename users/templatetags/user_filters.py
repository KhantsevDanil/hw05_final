from django import template

# В template.Library зарегистрированы все теги и фильтры шаблонов
# добавляем к ним и наш фильтр
register = template.Library()


# синтаксис @register... , под которой описана функция addclass() -
# это применение "декораторов", функций, обрабатывающих функции
@register.filter
def add_class(field, css):
    return field.as_widget(attrs={"class": css})
