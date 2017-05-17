Virtual Museums Framework
=========================
Made as Engineering Thesis for the degree of **Civil Computer Engineering** and
part of the Practice-driven Advance of Studies and Exchange between
the University of Duisburg-Essen and the University of Chile (**PRASEDEC**).

The Virtual Museums Framework (now referee as Framework) has the purpose of
bring a stable, maintainable, scalable and extensible python web server to display
different kinds of Virtual Museums, allowing the users to easily incorporate new pieces
of code (from templates) to add whatever kind of exhibit they want to display.

In addition, it has a group permission system to distribute roles on a big team.
Using a interface separately from the Visitor interface, who is read-only except for
the _Send Opinion_ functionality, that allow the visitor to send an opinion/comment
to the museum team about specific exhibits. To prevent spam, the visitor has to validated
his opinion using a valid email direction clicking a corroboration automatic-sent email.

Version
-------
1.0.0

Tech
----
The Framework was made using Python and particularly [Django] (_version 1.9.4_) for the web
server. For management of JavaScript libraries the Framework use [Bower]
(the specific libraries will be listed next).

For the dynamism of Django, the database technologies are not specially relevant.
In the prototyping version the Framework used [SQLite] but lately it was tested
using [PostgreSQL].


The Framework uses the following JavaScript libraries (As indicated on
the ```bower.json``` file):
* [Bootstrap] 3.3.7 - HTML, CSS and JS Framework for developing responsive and visual.
* [Font Awesome] 4.7.0 - The iconic font and CSS toolkit.
* [Roboto] 0.4.5 - Google Font.
* [jQuery] 3.1.1 - Fast, small, and feature-rich JavaScript library.
* [jQuery Backstretch] 2.1.15 - A simple jQuery plugin that allows you to add a dynamically-resized, slideshow-capable background image to any page or element
* [jQuery UI] 1.12 - A curated set of user interface interactions, effects, widgets, and themes built on top of the jQuery JavaScript Library.
* [jQuery Bar Rating] 1.2.2 - Minimal, light-weight jQuery ratings.

The project itself is open source with a [public repository][virtualmuseum] on GitHub.


Run & Configuration
-------------------

The project itself was made using [Pycharm], but It can be run directly from console.

```sh
$ python manage.py runserver PORT
```

But first we need to configure ```VirtualMuseumsFramework/settings.py```.
Specifically the changes are the next:

1. ```SECRET_KEY``` of the Django project.
2. The ```DEBUG``` flag.
3. The ```DATABASES``` configurations, indicating the engine, the route, the credentials, etc.
4. The ```WEBSITE_``` variables of the server.

After that, the basic elements (or fixtures) of the server need to be loaded.
For that purpose the Framework incorporate two files called ```firstRun```
(on Windows & Unix flavors) with the initial scripts to load the default fixtures.


Development
-----------

Made by [Michel Llorens](https://github.com/Michotastico).

License
----

GPL

[Django]: <https://www.djangoproject.com>
[Bower]: <https://bower.io>
[SQLite]: <https://www.sqlite.org>
[PostgreSQL]: <https://www.postgresql.org>

[Bootstrap]: <http://getbootstrap.com>
[Font Awesome]: <http://fontawesome.io>
[Roboto]: <https://fonts.google.com/specimen/Roboto>
[jQuery]: <https://jQuery.com>
[jQuery Backstretch]: <http://www.jQuery-backstretch.com>
[jQuery UI]: <https://jQueryui.com>
[jQuery Bar Rating]: <https://github.com/antennaio/jquery-bar-rating>

[Pycharm]: <https://www.jetbrains.com/pycharm>
[virtualmuseum]: <https://github.com/Michotastico/Memoria>