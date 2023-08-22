icepyx Internals
==================

Authentication
--------------
Authentication in icepyx is handled using a Mixin class. A Mixin class is a class
which defines functionality that may be desired by multiple other classes within 
a library. For example, at this time both the Query and Variables classes need
to be able to authenticate. Instead of defining the same properties and
functionality twice, icepyx has an EarthdataAuthMixin class that is inherited
by both modules.

**Property Access**

Even though they aren't explicity defined in the init method, properties
like ``.session`` are accessible on a Query object because they are inherited. The
code that indicates this to Python is ``EarthdataAuthMixin.__init__(self)``.

For example:

.. code-block:: python

    import icepyx as ipx

    region_a = ipx.Query('ATL06',[-45, 74, -44,75],['2019-11-30','2019-11-30'], \
                               start_time='00:00:00', end_time='23:59:59')

    # authentication can be accessed via the Query object
    region_a.session
    region_a.s3login_credentials


**Adding authentication to a new class**

To add authentication to an additional icepyx class, one needs to add the Mixin
to the class. To do this:

1. Add the EarthdataAuthMixin class to the ``class`` constructor (and import the mixin)
2. Add the EarthdataAuthMixin init method with in the init method of the new class ``EarthdataAuthMixin.__init__(self)``
3. Access the properties using the **public** properties (Ex. ``self.session``, not ``self._session``.)

A minimal example of the new class (saved in ``icepyx/core/newclass.py``) would be:

.. code-block:: python

    from icepyx.core.auth import EarthdataAuthMixin

    class MyNewClass(EarthdataAuthMixin):
        def __init__(self):
            self.mynewclassproperty = True

            EarthdataAuthMixin.__init__(self)

        def my_exciting_new_method(self):
            # This method requires login
            s = self.session
            print(s)
            return 'We authenticated inside the method!'


The class would then be accessible with:

.. code-block:: python

    from icepyx.core.newclass import MyNewClass

    n = MyNewClass()

    n.session
