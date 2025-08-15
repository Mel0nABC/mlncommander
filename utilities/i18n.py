import gettext

gettext.bindtextdomain("miapp", "locales")
gettext.textdomain("miapp")
_ = gettext.gettext
