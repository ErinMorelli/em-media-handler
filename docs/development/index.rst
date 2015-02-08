For Developers
============================================

This section contains information for developers on each of the EM Media Handler python modules. Read on if you wish to extend EM Media Handler's functionality, contribute to the project, or integrate functionality within your own projects.

You can explore the code further on either `GitHub <https://github.com/ErinMorelli/em-media-handler>`_ or `BitBucket <http://code.erinmorelli.com/em-media-handler>`_, as well as fork your own copy to work with.

Testing Suite
*************

EM Media Handler comes with a full set of unit tests. To run the suite, use: ::

    python setup.py test

.. note:: If tests are failing on your system, it usually due to a lack of dependencies. See :doc:`/configuration/requirements` for more information.

.. toctree::
   :glob:

   object
   handler
   types*
   util*
