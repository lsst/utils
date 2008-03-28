// -*- lsst-c++ -*-
#if defined(SWIGPYTHON)
/*
 * don't allow user to add attributes to C-defined classes; catches a variety of
 * typos when the user _thinks_ that they're setting a C-level object, but in
 * reality they're adding a new (and irrelevent) member to the class
 */
%pythonnondynamic;
#endif

%naturalvar;                            // use const reference typemaps
%include "cpointer.i"
%include "exception.i"
%include "std_list.i"
%include "std_map.i"
%include "std_string.i"
%include "std_set.i"
%include "std_vector.i"
%include "std_iostream.i"
%include "typemaps.i"

%include "carrays.i"

// N.b. these may interfere with the use of e.g. std_list.i for primitive types;
// you will have to say e.g.
// %clear int &;
//    %template(listInt)   std::list<int>;
//    %template(mapIntInt) std::map<int,int>;
// %apply int &OUTPUT { int & };

// Removed by ktl 2007-11-06 due to interference with other code.
// No methods visible to Python are expected to return values through argument
// references; if they do, they should be appropriately handled locally.
//
// %apply int &OUTPUT { int & };
// %apply float &OUTPUT { float & };
// %apply double &OUTPUT { double & };

%array_class(float, floatArray);
%array_class(double, doubleArray);

/******************************************************************************/
/*
 * Don't expose the entire boost::shared_ptr to swig; it is complicated...
 */
namespace boost {
    template<class T>
    class shared_ptr {
    public:
        // Copy constructor *must* come before the bare pointer constructor. This is because a
        // shared_ptr<T> * is convertible to a T * via SWIG_ConvertPtr, so if the SWIG generated constructor
        // argument dispatching function doesn't first test to see if an incoming argument is a shared_ptr<T> *,
        // double deletes will occur
        shared_ptr(shared_ptr<T> const &);

        // assume ownership of bare pointers
        shared_ptr(T * DISOWN);

        ~shared_ptr();
        T *operator->() const;
        int use_count() const;
        T *get() const;
    };
}

//
// Work around a swig 1.33.1 bug wherein swig doesn't realise that python still
// owns the pointer that's now wrapped in a shared_ptr
//
#define HAVE_SMART_POINTER 1            // allow e.g. FW to know that this macro is defined
%define %smart_pointer(PTR_TYPE, NAME, TYPE...)
// The next three lines are equivalent to %extend_smart_pointer(PTR_TYPE<TYPE >);
   //%implicitconv PTR_TYPE<TYPE >;
   %apply const SWIGTYPE& SMARTPOINTER { const PTR_TYPE<TYPE >& };
   %apply SWIGTYPE SMARTPOINTER { PTR_TYPE<TYPE > };

   %template(NAME) PTR_TYPE<TYPE >;
%enddef

%define %boost_shared_ptr(NAME, TYPE...)
    %smart_pointer(boost::shared_ptr, NAME, TYPE)
%enddef

/************************************************************************************************************/
/*
 * Required forward declaration to use make_output_iterator --- swig bug?
 */
%{
    namespace swig {
        template<typename OutIter>
        PySwigIterator*
        make_output_iterator(const OutIter& current, const OutIter& begin,const OutIter& end, PyObject *seq);
    }
%}

/******************************************************************************/
/*
 * Mapping C++ exceptions to Python
 */

%pythoncode %{
    import lsst.mwi.exceptions
%}

%{
#include <new>
#include "lsst/mwi/exceptions/Exception.h"
#include "lsst/mwi/exceptions/Runtime.h"
%}

%inline %{
namespace lsst { namespace mwi { namespace exceptions { } } }
%}

// Use the Python C API to create the constructor argument tuple (a message string and a
// DataProperty corresponding to an ExceptionStack) for a Python exception class assumed to
// be derived from lsst.mwi.exceptions.LsstExceptionStack. Also obtain a class object for
// the desired exception type. Use the class object and tuple to raise a Python exception.
%{
static void raiseLsstExceptionStack(lsst::mwi::exceptions::ExceptionStack & ex) {
    PyObject * modules = PyImport_GetModuleDict();
    PyObject * module  = PyDict_GetItemString(modules, ex.getPythonModule());
    if (module == 0) {
        PyErr_Format(PyExc_ImportError, "failed to find LSST exception module '%s'", ex.getPythonModule());
        return;
    }
    PyObject * clazz  = PyDict_GetItem(PyModule_GetDict(module), PyString_FromString(ex.getPythonClass()));
    if (clazz == 0) {
        PyErr_Format(PyExc_AttributeError, "unable to find LSST exception class '%s' in module '%s'",
                     ex.getPythonClass(), ex.getPythonModule());
        return;
    }

    PyObject * args = PyTuple_New(2);
    if (args == 0) {
        PyErr_SetString(clazz, ex.what());
        return;
    }

    PyTuple_SetItem(args, 0, PyString_FromString(ex.what()));

    PyObject       * stack = 0;
    swig_type_info * tinfo = SWIG_TypeQuery("boost::shared_ptr<lsst::mwi::data::DataProperty> *");
    if (tinfo != 0) {
        void * ptr = static_cast<void *>(new lsst::mwi::data::DataProperty::PtrType(ex.getStack()));
        stack = SWIG_NewPointerObj(static_cast<void *>(ptr), tinfo, SWIG_POINTER_OWN);
    } else {
        stack = Py_None;
        Py_INCREF(stack);
    }
    PyTuple_SetItem(args, 1, stack);

    PyErr_SetObject(clazz, args);
    Py_DECREF(args);
}
%}

// Specifies the default C++ to python exception handling interface
%exception {
    try {
        $action
    } catch (lsst::mwi::exceptions::ExceptionStack &e) {
        raiseLsstExceptionStack(e);
        SWIG_fail;
    } catch (std::exception & e) {
        PyErr_SetString(PyExc_Exception, e.what());
        SWIG_fail;
    }
}


/******************************************************************************/
/*
 * Throw an exception if func returns NULL
 */
%define NOTNULL(func)
    %exception func {
        $action;
	if (result == NULL) {
	    $cleanup;
	}
    }
%enddef

/*
 * Throw an exception if func returns a negative value
 */
%define NOTNEGATIVE(func)
    %exception func {
        $action;
	if (result < 0) {
	    $cleanup;
	}
    }
%enddef

/******************************************************************************/

%define CAST(TYPE)
    %pointer_cast(void *, TYPE *, cast_ ## TYPE ## Ptr); // convert void pointer to (TYPE *)
%enddef

/******************************************************************************/
// Local Variables: ***
// eval: (setq indent-tabs-mode nil) ***
// End: ***

