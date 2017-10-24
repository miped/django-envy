Motivation
==========

With the 12-factor app gaining popularity, and an increased focus on devops, there's already quite a few packages out there which can read and parse environment variables. However, django-envy makes a series of design decisions that I feel are important.

In the following, I will go over each decision in turn, and lay out the reasoning for it.


``.env`` Files Are Not Environment Variables
--------------------------------------------

The 12-factor app "manifesto" is very clear on favoring environment variables over language or OS specific config files for configuration, for a number of very good reasons.

While it's possible to interpret these reasons and conclusions in different ways, django-envy takes a very opinionated stand: **The application should know absolutely nothing about where environment variables come from.**

There are dozens of ways to set an environment variable so that it will be available to your application:

- Globally on startup for the entire instance
- For a specific user
- In your process manager, whether that be ``startup``, ``runit``, ``supervisor``, ``system.d``, ``god``, ``monit``, or something entirely different
- Using a wrapper script
- Built into your docker image
- When starting your docker image
- From a series of files using ``envdir``
- Sourcing a bash script
- Etc.

All of these are acceptable options, and each have their pros and cons. With so many ways to set environment variables, there's no reason for the application to be able to set them too.

If you need to set environment variables in development, consider something like foreman or honcho, or the built in facilities for doing so in docker, if that's what you use.


Don't Duplicate Packages
------------------------

There are a number of well-maintained packages to take care of Django-specific settings, such as database, cache or email settings:

- dj-database-url
- dj-email-url
- django-cache-url

However much the naming inconsistency annoys me, I don't see a good reason to duplicate the functionality of these packages, for the sake of fewer dependencies.

For an example of how to use any of these packages with django-envy, please see ...


Strictness And Correctnes Above Convenience
-------------------------------------------

Configuration is important, and getting a vital piece of information wrong can be devastating. That's why django-envy takes a firm stance on what values are allowed when casting between types, and will always prefer raising an error to trying to be clever.

Examples:

- There is only two acceptable values when casting to boolean: ``"true"`` and ``"false"`` (they are case insensitive though)
- Floats must always be specified using a period (``.``) as the decimal separator. There is no logic for "guessing" the thousand separator. (Though it is possible to use ``_`` for readability as in Python 3.6)
- If a cast does not seem to make sense, django-envy will throw an error. This includes trying to cast to nested collections.


Alternatives
------------

If these design decisions aren't to your liking, there are other packages out there, which have chosen a different set of tradeoffs:

- django-environ
- envparse
- python-decouple
- django12factor
- django-confy
- json_environ
